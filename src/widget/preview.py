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

from dtk.ui.draw import draw_text
from dtk.ui.constant import DEFAULT_FONT_SIZE
from preview_bg import PreViewWin
from mplayer.player import LDMP
from mplayer.player import length_to_time 
from constant import PREVIEW_PV_WIDTH, PREVIEW_PV_HEIGHT

import gtk
import cairo
import pango

class PreView(object): 
    def __init__(self, path = "", pos = 0): 
        
        self.video_width = 0
        self.video_height = 0
        
        #self.mp = Mplayer()
        self.mp = LDMP()
        self.xid = None
        self.pos = pos
        
        # Preview background window.
        self.bg = PreViewWin()
        self.bg.set_size_request(124, 89)
        self.bg.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_MENU)
        # Set background window.
        self.bg.add_events(gtk.gdk.ALL_EVENTS_MASK)
        #self.bg.show_all()
        self.bg.set_offset(self.bg.get_offset_mid_value())
        # Hide preview window.
        self.bg.show_time_label.connect("expose-event", self.draw_background)
        self.bg.connect("motion-notify-event", self.motion_hide_preview)
        self.bg.connect("enter-notify-event", self.motion_hide_preview)
        
        # Preview window.
        self.pv = gtk.Window(gtk.WINDOW_POPUP)
        
        # Set preview window.        
        self.pv.set_size_request(PREVIEW_PV_WIDTH - 4, PREVIEW_PV_HEIGHT)
        self.pv.set_decorated(False)
        self.pv.set_keep_above(True)
        self.pv.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_MENU) 
        self.pv.add_events(gtk.gdk.ALL_EVENTS_MASK)
                
        self.pv.connect("expose-event", self.draw_preview_video_background)
        # Hide preview window.
        self.pv.connect("motion-notify-event", self.motion_hide_preview)
        self.pv.connect("enter-notify-event", self.motion_hide_preview)
        
    def draw_preview_video_background(self, widget, event):    
        cr = widget.window.cairo_create()
        x, y, w, h = widget.get_allocation()
        
        cr.rectangle(x, y, w, h)
        cr.fill()
        if self.video_width or self.video_height:
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
        # Init.
        cr = widget.window.cairo_create()
        rect = widget.allocation
        x, y, w, h = rect.x, rect.y, rect.width, rect.height

        # Draw preview time.
        font_height_padding = 15
        show_time_text = length_to_time(self.pos)
        time_hour, time_min, time_sec = 1, 3, 30 #self.mp.time(self.pos)
        draw_text(cr, 
                  #"%s:%s:%s" % (self.time_to_string(time_hour), self.time_to_string(time_min), self.time_to_string(time_sec)),
                  show_time_text,
                  x, h - font_height_padding, w, DEFAULT_FONT_SIZE,
                  text_color = "#ffffff",
                  alignment=pango.ALIGN_CENTER
                  )
                
        return True
            
    def move_preview(self, x, y):        
        self.bg.move(int(x), int(y))
        self.pv.move(int(x + 4), int(y+4))
        
    def show_preview(self, pos):        
        if self.pos != pos:
            self.pos = pos
            self.bg.queue_draw()
            
            self.bg.show_all()
            self.pv.show_all()
            
            region = gtk.gdk.Region()
            self.bg.window.input_shape_combine_region(region, 0, 0)
            #self.pv.show_all()
            self.pv.set_keep_above(True)
            # init preview window mplayer.
            self.init_mplayer_window(pos)
        
    def hide_preview(self):
        self.bg.hide_all()
        self.pv.hide_all()                    
        
    def quit_preview_player(self):    
        self.hide_preview()
        self.mp.quit()
        
    def set_preview_path(self, path):        
        self.pv.show_all()            
        self.pv.set_opacity(0)
        self.mp.xid = self.pv.window.xid
        self.mp.quit()
        self.mp.player.uri = path
        self.mp.play()   # 播放.
        self.mp.pause()  # 暂停.
        self.mp.nomute() # 静音.
        self.pv.hide_all()
        self.pv.set_opacity(1)
            
    def time_to_string(self, time_pos):        
        if 0<= time_pos <= 9:
            return "0" + str(time_pos)        
        return str(time_pos)
    
    def motion_hide_preview(self, widget, event):    
        self.hide_preview()
        
    def init_mplayer_window(self, pos):       
        # 预览快进.
        self.mp.seek(pos)
            
if __name__ == "__main__": 
    pass
