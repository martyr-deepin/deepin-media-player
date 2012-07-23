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
from dtk.ui.utils import alpha_color_hex_to_cairo,color_hex_to_cairo
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
                 line_width = 5,
                 width = 100,
                 bg_color = app_theme.get_alpha_color("progressbar_bg"),
                 fg_color = app_theme.get_alpha_color("progressbar_fg"),
                 bg_pixbuf = app_theme.get_pixbuf("progressbar/progressbar_bg.png"),
                 fg_pixbuf = app_theme.get_pixbuf("progressbar/progressbar_fg.png"),
                 point_pixbuf = app_theme.get_pixbuf("progressbar/slide_block.png"),
                 hight_pixbuf = app_theme.get_pixbuf("progressbar/progressbar_hight.png"),
                 cache_fg_pixbuf = app_theme.get_pixbuf("progressbar/cache_fg_pixbuf.png")
                 ):
        gtk.EventBox.__init__(self)
        '''Set progresbar attr.'''
        self.set_visible_window(False)
        self.set_size_request(width, point_pixbuf.get_pixbuf().get_height() + progressbar_padding_y)
        '''Init pixbuf.'''
        self.__bg_color     = bg_color
        self.__fg_color     = fg_color
        self.__bg_pixbuf    = bg_pixbuf.get_pixbuf()
        self.__bg_pixbuf    = self.__bg_pixbuf.scale_simple(self.__bg_pixbuf.get_width(), line_width,
                                                            gtk.gdk.INTERP_BILINEAR)
        self.__fg_pixbuf    = fg_pixbuf.get_pixbuf()
        self.__fg_pixbuf    = self.__fg_pixbuf.scale_simple(self.__fg_pixbuf.get_width(), line_width,
                                                            gtk.gdk.INTERP_BILINEAR)
        self.__point_pixbuf = point_pixbuf
        self.__hight_pixbuf = hight_pixbuf
        self.__cache_fg_pixbuf = cache_fg_pixbuf
        '''Init value.'''        
        self.cache_list = []
        for i in range(0, int(max_value)):
            self.cache_list.append(0) 
            
        for i in range(0, 20):    
            self.cache_list[i] = 1
            
        self.progressbar_state = False
        self.__max_value  = max_value
        self.__current_valeu  =  0
        self.__temp_value     = 0
        self.__drag_bool        = False
        self.__line_width     = line_width
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
        
    def set_max_value(self, max_value):    
        self.__max_value = max_value
        
    def set_value(self, value):    
        self.__current_value   = value
        self.queue_draw()
        
    def get_value(self):    
        return self.__current_valeu
    
    def __get_x(self, event):    
        self.__point_padding_x = event.x
        self.__fg_padding_x    = event.x
        self.__current_value = (float(self.__max_value) / self.allocation.width) * self.__fg_padding_x
        if self.__current_value < 0:
            self.__current_value = 0
        elif self.__current_value > self.__max_value:
            self.__current_value = self.__max_value
            
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
            # Draw progressbar fg cache.
            self.__draw_progressbar_cache(cr, x, y, w, h)
            # Draw progressbar fg.
            self.__draw_progressbar_fg(cr, x, y, w, h)
            # Draw progressbar fg hight.            
            self.__draw_progressbar_hight(cr, x, y, w, h)
            # Draw progressbar point.
            self.__draw_progressbar_point(cr, x, y, w, h)
        return True
    
    def __draw_progressbar_cache(self, cr, x, y, w, h):
        
        cr.set_line_width(self.__line_width-1)
        # cr.set_source_rgba(*alpha_color_hex_to_cairo(self.__fg_color.get_color_info()))                                        
        cr.set_source_rgb(*color_hex_to_cairo("#8c8c8c"))                                        
        
        for i in range(0, 100):            
            if self.cache_list[i]:
                cache_padding_x = i / (float(self.__max_value) / w)
                # cr.move_to(x, 
                #            y + self.__progressbar_padding_y)
                # cr.line_to(x  + self.__fg_padding_x , 
                #            y + self.__progressbar_padding_y)
                # cache_pixbuf = self.__cache_fg_pixbuf.get_pixbuf()
                # cr.set_source_pixbuf(cache_pixbuf, 
                #                      x + cache_padding_x ,
                #                      y + self.__progressbar_padding_y)
                # cr.paint_with_alpha(1)
                
                cr.move_to(x+ cache_padding_x, y + self.__progressbar_padding_y)
                cr.line_to(x + cache_padding_x+5, 
                           y + self.__progressbar_padding_y)
                cr.stroke()        

    
    def __draw_progressbar_bg(self, cr, x, y, w, h):
        # cr.set_line_width(self.__line_width)
        # cr.set_source_rgba(*alpha_color_hex_to_cairo(self.__bg_color.get_color_info()))
        # cr.move_to(x, 
        #            y + self.__progressbar_padding_y)
        # cr.line_to(x + w, 
        #            y + self.__progressbar_padding_y )
        # cr.stroke()
        self.__bg_pixbuf = self.__bg_pixbuf.scale_simple(x + w, self.__line_width,
                                                          gtk.gdk.INTERP_BILINEAR)
        cr.set_source_pixbuf(self.__bg_pixbuf,
                             x,
                             y + self.__progressbar_padding_y - self.__bg_pixbuf.get_height()/2)
        cr.paint_with_alpha(1)        
        
    def __draw_progressbar_hight(self, cr, x, y, w, h):    
        hight_pixbuf = self.__hight_pixbuf.get_pixbuf()
        cr.set_source_pixbuf(hight_pixbuf,
                             x + self.__fg_padding_x - hight_pixbuf.get_width(), 
                             y + self.__progressbar_padding_y - hight_pixbuf.get_height()/2)
        cr.paint_with_alpha(1)                                
    
    def __draw_progressbar_fg(self, cr, x, y, w, h):
        self.__fg_padding_x = self.__current_value / (float(self.__max_value) / w)
        
        self.__point_padding_x = self.__fg_padding_x
        if self.__fg_padding_x >= 0:
            fg_scale_pixbuf = self.__fg_pixbuf
            for i in range(0, int(x + self.__fg_padding_x)):
                cr.set_source_pixbuf(fg_scale_pixbuf,
                                     i,
                                     y + self.__progressbar_padding_y - fg_scale_pixbuf.get_height()/2)
                cr.paint_with_alpha(1)        
        
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
    from mplayer import Mplayer
    
    def play_start(mplayer, mplayer_id):
        print mplayer_id
        
    def play_end(mplayer, mplayer_bool):
        pb.progressbar_state = mplayer.state
        
    def get_time_pos(mplayer, pos):
        # if False:
        pb.set_value(pos)
        
    def get_time_length(mplayer, length):
        pb.set_max_value(length)
        
    def test_value(widget, value, state):
        mp.seek(value)
        
    def init_media_player(widget, event):        
        # mp.connect("play-start", play_start)
        # mp.connect("play-end", play_end)
        # mp.connect("get-time-length", get_time_length)
        # mp.connect("get-time-pos", get_time_pos)
        # mp.play("/home/long/音乐/如果你冷-张旋.mp3")
        # mp.play("/home/long/音乐/123.rmvb")
        # mp.setvolume(10)
        # pb.progressbar_state = mp.state   
        pass
        
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    screen = gtk.DrawingArea()
    win.set_size_request(500, 500)
    
    main_vbox = gtk.VBox()
    pb = ProgressBar()
    pb.progressbar_state=1
    pb.connect("get-value-event", test_value)
    win.connect("destroy", gtk.main_quit)
    win.connect("window-state-event", init_media_player)
    main_vbox.pack_start(screen, True, True)
    main_vbox.pack_start(pb, False, False)
    win.add(main_vbox)
    win.show_all()
    mp  = Mplayer(screen.window.xid)
    gtk.main()
