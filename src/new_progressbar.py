#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 Deepin, Inc.
#               2012 Hailong Qiu
#
# Author:     Hailong Qiu <356752238@qq.com>
# Maintainer: Hailong Qiu <356752238@qq.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.



# Deein ui.
from dtk.ui.utils import alpha_color_hex_to_cairo
from dtk.ui.draw import draw_pixbuf

import gtk
import gobject
from skin import app_theme

class ProgressBar(gtk.EventBox):
    __gsignals__ = {
        "get-value-event":(gobject.SIGNAL_RUN_LAST,
                           gobject.TYPE_NONE,(gobject.TYPE_INT,gobject.TYPE_INT,))
        }    
    def __init__(self,                 
                 max_value = 100,
                 progressbar_padding_y = 4,
                 line_width = 6,
                 width = 100,
                 bg_color = app_theme.get_alpha_color("progressbar_bg"),
                 fg_color = app_theme.get_alpha_color("progressbar_fg"),
                 point_pixbuf = app_theme.get_pixbuf("slide_block.png")
                 ):
        gtk.EventBox.__init__(self)
        '''Set progresbar attr.'''
        self.set_visible_window(False)
        self.set_size_request(width, point_pixbuf.get_pixbuf().get_height() + progressbar_padding_y)
        '''Init value.'''        
        self.progressbar_state = False
        self.__max_value  = max_value
        self.__current_valeu  =  0
        self.__temp_value     = 0
        self.__drag_bool        = False
        self.__line_width     = line_width
        self.__bg_color     = bg_color
        self.__fg_color     = fg_color
        self.__point_pixbuf = point_pixbuf
        self.__progressbar_padding_y = progressbar_padding_y
        self.__progressbar_width = width
        '''Init point value.'''
        self.__point_padding_x = 0
        self.__point_show_bool   = False
        '''Init fg value.'''
        self.__fg_padding_x = 0
        '''Init progresbar event.'''
        self.add_events(gtk.gdk.ALL_EVENTS_MASK)
        self.connect("expose-event",         self.__expose_draw_progressbar)
        self.connect("button-press-event",   self.__press_point_get_x)
        self.connect("motion-notify-event",  self.__motion_drag_get_x)
        self.connect("button-release-event", self.__release_drag_bool)
        self.connect("enter-notify-event",   self.__enter_point_show)
        self.connect("leave-notify-event",   self.__leave_point_hide)
        # Init value.
        self.set_value(0)
        
    def set_value(self, value):    
        self.__current_value = value
        self.__fg_padding_x =  round(value / (float(self.__max_value) / self.__progressbar_width), 0)
        self.__point_padding_x = self.__fg_padding_x
        self.queue_draw()
        
    def get_value(self):    
        return self.__current_valeu
    
    def __get_x(self, event):    
        self.__point_padding_x = event.x        
        self.__fg_padding_x    = event.x
        self.emit("get-value-event", self.__current_value, self.progressbar_state)
        self.queue_draw()
        
    def __press_point_get_x(self, widget, event):    
        self.__get_x(event)
        self.__drag_bool = True        
        
    def __release_drag_bool(self, widget, event):
        self.__drag_bool = False
    
    def __enter_point_show(self, widget, event):    
        self.__point_show_bool = True
        self.queue_draw()
        
    def __leave_point_hide(self, widget, event):    
        if not self.__drag_bool:
            self.__point_show_bool = False
            self.queue_draw()
        
    def __motion_drag_get_x(self, widget, event):    
        if self.__drag_bool:
            self.__get_x(event)
        
    def __expose_draw_progressbar(self, widget, event):
        cr = widget.window.cairo_create()
        x, y, w, h = widget.allocation
        self.__progressbar_width = w
        
        # Draw progressbar bg.
        self.__draw_progressbar_bg(cr, x, y, w, h)
            
        if self.progressbar_state:
            # Draw progressbar fg.
            self.__draw_progressbar_fg(cr, x, y, w, h)
            # Draw progressbar point.
            self.__draw_progressbar_point(cr, x, y, w, h)
            
        return True
    
    def __draw_progressbar_bg(self, cr, x, y, w, h):
        cr.set_line_width(self.__line_width)
        cr.set_source_rgba(*alpha_color_hex_to_cairo(self.__bg_color.get_color_info()))
        cr.move_to(x, 
                   y + self.__progressbar_padding_y)
        cr.line_to(x + w, 
                   y + self.__progressbar_padding_y)
        cr.stroke()
        
    def __draw_progressbar_fg(self, cr, x, y, w, h):
        cr.set_line_width(self.__line_width)
        cr.set_source_rgba(*alpha_color_hex_to_cairo(self.__fg_color.get_color_info()))
        # Get current value.
        self.__temp_value = (float(self.__max_value) / w) * self.__fg_padding_x
        self.__current_value =  int(round(self.__temp_value, 0))
        
        if self.__current_value < 0:
            self.__current_value = 0
        elif self.__current_value > self.__max_value:    
            self.__current_value = self.__max_value
            
        cr.move_to(x, 
                   y + self.__progressbar_padding_y)
        cr.line_to(x + self.__fg_padding_x, 
                   y + self.__progressbar_padding_y)
        cr.stroke()        
    
    def __draw_progressbar_point(self, cr, x, y, w, h):
        if self.__point_show_bool:
            point_pixbuf_height = self.__point_pixbuf.get_pixbuf().get_height() / 2
            point_pixbuf_width = self.__point_pixbuf.get_pixbuf().get_width() / 2
            
            if self.__point_padding_x > w - point_pixbuf_width:
                self.__point_padding_x = w - (point_pixbuf_width)
            elif self.__point_padding_x < 0 + (point_pixbuf_width):    
                self.__point_padding_x = 0 + point_pixbuf_width
            
            draw_pixbuf(cr,
                        self.__point_pixbuf.get_pixbuf(),
                        x + self.__point_padding_x - (point_pixbuf_width),
                        y - (point_pixbuf_height) + self.__progressbar_padding_y
                        )
        
        
gobject.type_register(ProgressBar)
    

if __name__ == "__main__":
    def test_value(widget, value, state):
        print widget
        print value
        print state
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    win.set_size_request(500, 500)
    main_vbox = gtk.VBox()
    pb = ProgressBar(width=500)
    pb.connect("get-value-event", test_value)
    
    win.connect("destroy", gtk.main_quit)
    main_vbox.pack_start(gtk.Button("确定"), True, True)
    main_vbox.pack_start(pb, False, False)
    win.add(main_vbox)
    win.show_all()
    gtk.main()
