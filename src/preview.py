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

from mplayer import Mplayer
from constant import PREVIEW_PV_WIDTH, PREVIEW_PV_HEIGHT
import gtk
import cairo

class PreView(object): 
    def __init__(self, path = "", pos = 0):
        self.path = path # play path.
        self.pos  = pos  # play pos.
        self.i = 0        
        self.pixbuf = None        
        
        self.mp = Mplayer()
        self.mp.state = 1    
        
        # Preview background window.
        self.bg = gtk.Window(gtk.WINDOW_POPUP)
        self.bg.set_colormap(gtk.gdk.Screen().get_rgba_colormap())
        self.bg.set_decorated(False)
        #self.bg.set_keep_above(True)
        self.bg.set_size_request(124, 60 + 25 + 4)
        self.bg.set_opacity(0.8)
        self.bg.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_MENU)
        # Set background window.
        self.bg.add_events(gtk.gdk.ALL_EVENTS_MASK)
        self.bg.connect("expose-event", self.draw_background)
        self.bg.connect("size-allocate", self.draw_shape_mask)        
        # Hide preview window.
        self.bg.connect("motion-notify-event", self.motion_hide_preview)
        self.bg.connect("enter-notify-event", self.motion_hide_preview)
        # self.bg.connect("focus-in-event", self.motion_hide_preview)
        
        # Preview window.
        self.pv = gtk.Window(gtk.WINDOW_POPUP)
        self.image = gtk.image_new_from_file("../app_theme/default/image/bg.png")
        # Set preview window.        
        self.pv.set_size_request(PREVIEW_PV_WIDTH, PREVIEW_PV_HEIGHT)
        self.pv.set_decorated(False)
        self.pv.set_keep_above(True)
        self.pv.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_MENU) 
        self.pv.add_events(gtk.gdk.ALL_EVENTS_MASK)

        
        # self.pv.add(self.image)
        
        self.pv.connect("destroy", self.quit_mplayer)
        # self.pv.connect("expose-event", self.draw_preview_background)
        # Hide preview window.
        self.pv.connect("motion-notify-event", self.motion_hide_preview)
        self.pv.connect("enter-notify-event", self.motion_hide_preview)
        # self.pv.connect("window-state-event", self.init_mplayer_window)
        
        self.pv.add(self.image)
        
    # Background window.    
    def draw_background(self, widget, event):    
        cr = widget.window.cairo_create()
        rect = widget.allocation
        x, y, w, h = rect.x, rect.y, rect.width, rect.height

        cr.set_source_rgb(0, 0, 0)
        cr.rectangle(x, y, w, h)
        cr.fill()  
        

        cr.select_font_face("Courier",
                            cairo.FONT_SLANT_NORMAL,
                            cairo.FONT_WEIGHT_BOLD)
        font_size = 12
        cr.set_font_size(font_size)
        cr.set_source_rgb(1, 1, 1)
        font_width_padding = 25
        font_height_padding = 16
        cr.move_to(w/2 - font_width_padding, h - font_height_padding)
        pos = self.pos
        
        time_hour = self.mp.time(pos)[0]
        time_min = self.mp.time(pos)[1]
        time_sec = self.mp.time(pos)[2]
        
        cr.show_text("%s:%s:%s" % (self.time_to_string(time_hour), 
                                   self.time_to_string(time_min),
                                   self.time_to_string(time_sec)))
        
        return True
    
    def draw_shape_mask(self, widget, rect):    
        # Init.
        x, y, w, h = rect.x, rect.y, rect.width, rect.height
        bitmap = gtk.gdk.Pixmap(None, w, h, 1)
        cr = bitmap.cairo_create()
        
        # Clear the bitmap
        cr.set_source_rgb(1.0, 1.0, 1.0)
        cr.set_operator(cairo.OPERATOR_CLEAR)
        cr.paint()
        
        cr.set_source_rgb(1.0, 1.0, 1.0)
        cr.set_operator(cairo.OPERATOR_OVER)
        cr.rectangle(x, y, w, h-10)
        cr.fill()
         
        cr.move_to(x + w/2 +5-15, y+h-10)
        cr.line_to(x + w/2 + 5-5, y+h)
        cr.line_to(x + w/2 + 5+5, y+h-10)
        cr.fill()
        
        # Shape with given mask.
        widget.shape_combine_mask(bitmap, 0, 0)
        
    
    def quit_mplayer(self, widget):
        if self.mp:
            self.mp.quit()            
        
    def move_preview(self, x, y):        
        self.bg.move(int(x), int(y))
        self.pv.move(int(x + 2), int(y+2))
        
    def show_preview(self):        
        self.bg.show_all()
        self.pv.show_all()
                
        region = gtk.gdk.Region()
        self.bg.window.input_shape_combine_region(region, 0, 0)
        self.pv.show_all()
        self.pv.set_keep_above(True)
        
    def hide_preview(self):
        self.bg.hide_all()
        self.pv.hide_all()
                    
    def time_to_string(self, time_pos):        
        if 0<= time_pos <= 9:
            return "0" + str(time_pos)        
        return str(time_pos)
    
    def set_pos(self, pos):
        self.pos = pos        
        
    def set_path(self, path):    
        if self.mp:
            self.mp.path = path
        
    def motion_hide_preview(self, widget, event):    
        self.hide_preview()
        
    def set_image(self, image_path):    
        self.image.set_from_file(image_path)
            
