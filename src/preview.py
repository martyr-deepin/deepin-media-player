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
        
        self.video_width = 0
        self.video_height = 0
        
        self.mp = Mplayer()
        self.mp.connect("play-start", self.get_video_width_and_height)
        self.xid = None
        self.pos = pos
        
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
        
        # Set preview window.        
        self.pv.set_size_request(PREVIEW_PV_WIDTH, PREVIEW_PV_HEIGHT)
        self.pv.set_decorated(False)
        self.pv.set_keep_above(True)
        self.pv.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_MENU) 
        self.pv.add_events(gtk.gdk.ALL_EVENTS_MASK)
                
        self.pv.connect("expose-event", self.draw_preview_video_background)
        # Hide preview window.
        self.pv.connect("motion-notify-event", self.motion_hide_preview)
        self.pv.connect("enter-notify-event", self.motion_hide_preview)
        # self.pv.connect("window-state-event", self.init_mplayer_window)
        
        
    def draw_preview_video_background(self, widget, event):    
        cr = widget.window.cairo_create()
        x, y, w, h = widget.get_allocation()
        
        if 0 != self.video_width or 0 != self.video_height:
            video_ratio = float(self.video_width) / self.video_height
            bit = video_ratio - (float(w) / h)
            cr.set_source_rgb(0, 0, 0)
            
            if 0 == bit:
                return False
            elif bit < 0:                             
                s = w - h * (video_ratio)
                s = s / 2                            
                
                # Draw left.
                cr.rectangle(x, y, 
                             s, h)
                cr.fill()
                        
                # Draw right.
                cr.rectangle(x + s + h * video_ratio,
                             y, s, h)
                cr.fill()
                        
            elif bit > 0:
                video_ratio = float(self.video_height) / self.video_width                        
                s = h - w * video_ratio
                s = s / 2
                        
                # Draw UP.                        
                cr.rectangle(x, y, w + 1, s)
                cr.fill()
                        
                # Draw bottom.
                cr.rectangle(x, y + s + w * (video_ratio), 
                             w, s)
                cr.fill()
        
        return True
    
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
        
        # Show Time.
        pos = self.pos
        
        time_hour, time_min, time_sec = self.mp.time(pos)
        # time_min = self.mp.time(pos)[1]
        # time_sec = self.mp.time(pos)[2]
        
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
            
    def move_preview(self, x, y):        
        self.bg.move(int(x), int(y))
        self.pv.move(int(x + 2), int(y+2))
        
    def show_preview(self, pos):        
        self.pos = pos
        self.bg.queue_draw()
        
        self.bg.show_all()
        self.pv.show_all()
        
        self.xid = self.pv.window.xid        
        region = gtk.gdk.Region()
        self.bg.window.input_shape_combine_region(region, 0, 0)
        self.pv.show_all()
        self.pv.set_keep_above(True)
        
        # init preview window mplayer.
        self.init_mplayer_window(pos)
        
    def hide_preview(self):
        self.bg.hide_all()
        self.pv.hide_all()                    
        
    def quit_preview_player(self):    
        self.hide_preview()
        if 1 == self.mp.state:            
            self.mp.quit()
            
    def get_video_width_and_height(self, mp, mp_pid, w1, h1, w2, h2):        
        self.video_width = w1
        self.video_height = h1
        if w2 > w1:
            self.video_width = w2
            self.video_height = h2
        
    def set_preview_path(self, path):        
        if 0 == self.mp.state:
            self.pv.show_all()            
            self.pv.set_opacity(0)
            self.mp.xid = self.pv.window.xid
            self.mp.path = path
            self.mp.play(self.mp.path)             
            self.mp.pause()
            self.mp.pause_bool = False
            self.pv.hide_all()
            self.pv.set_opacity(1)
            
    def time_to_string(self, time_pos):        
        if 0<= time_pos <= 9:
            return "0" + str(time_pos)        
        return str(time_pos)
    
    def motion_hide_preview(self, widget, event):    
        self.hide_preview()
        
    def init_mplayer_window(self, pos):       
        self.mp.xid = self.xid
        if 1 == self.mp.state:
            self.mp.seek(pos)
            
        
