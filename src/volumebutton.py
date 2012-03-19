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

from dtk.ui.utils import *
from dtk.ui.draw import *
from dtk.ui.box import *
from dtk.ui.frame import *
 

from constant import *
from utils import *
import gtk
import gobject


class VolumeButton(gtk.HBox,gobject.GObject):
    __gsignals__ = {
        "get-value-event":(gobject.SIGNAL_RUN_LAST,
                           gobject.TYPE_NONE,(gobject.TYPE_INT,gobject.TYPE_INT,))
        }
    def __init__(self,
                 volume_value = 100,
                 min_volume_pixbuf = app_theme.get_pixbuf("小音量.png"),
                 mid_volume_pixbuf = app_theme.get_pixbuf("中音量.png"),
                 max_volume_pixbuf = app_theme.get_pixbuf("大音量.png"),
                 mute_pixbuf = app_theme.get_pixbuf("静音.png"),
                 volume_bg_dpixbuf = app_theme.get_pixbuf("volume_bg.png"), 
                 volume_fg_dpixbuf = app_theme.get_pixbuf("volume_fg.png"),
                 volume_button_pixbuf = app_theme.get_pixbuf("音量调节按钮.png")
                 ):
        

        gtk.HBox.__init__(self)
        gobject.GObject.__init__(self)

        self.min_volume_pixbuf = min_volume_pixbuf.get_pixbuf()
        self.mid_volume_pixbuf = mid_volume_pixbuf.get_pixbuf()
        self.max_volume_pixbuf = max_volume_pixbuf.get_pixbuf()
        self.mute_pixbuf = mute_pixbuf.get_pixbuf()
        
        self.volume_bg_dpixbuf = volume_bg_dpixbuf.get_pixbuf()
        self.volume_fg_dpixbuf = volume_fg_dpixbuf.get_pixbuf()
        self.volume_button_pixbuf = volume_button_pixbuf.get_pixbuf()
        
        self.mute_bool = False
        self.drag = False
        self.volume_value = volume_value
        
        # volume button image.
        self.button = gtk.image_new_from_pixbuf(self.min_volume_pixbuf)
        self.button_event = gtk.EventBox()
        self.button_event.set_visible_window(False)
        self.button_event.add(self.button)
        self.button_event.set_events(gtk.gdk.ALL_EVENTS_MASK)
        self.button_event.connect("button-press-event", self.button_press_event)
        # volume button progressbar
        self.volume_progressbar = gtk.Button()
        self.volume_progressbar.set_size_request(120,2)
        self.volume_progressbar.add_events(gtk.gdk.ALL_EVENTS_MASK)
        self.volume_progressbar.connect("expose-event", self.volume_progressbar_expose)
        self.volume_progressbar.connect("button-press-event", self.volume_progressbar_press_event)
        self.volume_progressbar.connect("button-release-event", self.volume_progressbar_release_event)
        self.volume_progressbar.connect("motion-notify-event", self.volume_progressbar_motion_notify)
        self.volume_progressbar.connect("clicked", self.volume_progressbar_clicked)
        self.pack_start(self.button_event,False,False)
        self.pack_start(self.volume_progressbar,True,True)
        
        self.set_value(self.volume_value)
        
    def volume_progressbar_motion_notify(self, widget, event):
        if self.drag:
            self.mute_bool = False
            self.set_value(int(event.x))
        
    def volume_progressbar_release_event(self, widget, event):
        self.drag = False
        
    def volume_progressbar_press_event(self, widget, event):    
        if event.button == 1:
            self.drag = True
            self.set_value(int(event.x))
             
    def volume_progressbar_clicked(self, widget):
        self.mute_bool = False
        self.set_value(self.volume_value)

    def volume_progressbar_expose(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        x,y,w,h = rect.x, rect.y, rect.width, rect.height

        image = self.volume_bg_dpixbuf.scale_simple(
            self.volume_bg_dpixbuf.get_width(), 
            self.volume_bg_dpixbuf.get_height(),
            gtk.gdk.INTERP_BILINEAR)
        
        for i in range(0, 100):
            draw_pixbuf(cr, self.volume_bg_dpixbuf, x+i + 5, y + h/2 - 1.5)
            
        for i in range(0, self.volume_value):
            draw_pixbuf(cr, self.volume_fg_dpixbuf, x+i + 5, y + h/2 - 1.5)
            
        if self.volume_value == 0:    
            draw_pixbuf(cr, self.volume_button_pixbuf, x  + self.volume_value + 2, y + h/2 - 4.5)    
        if self.volume_value == 100:
            draw_pixbuf(cr, self.volume_button_pixbuf, x  + self.volume_value - 3, y + h/2 - 4.5) 
        if 0 < self.volume_value < 100:   
            draw_pixbuf(cr, self.volume_button_pixbuf, x  + self.volume_value - 5 , y + h/2 - 4.5)
            
        return True
        
    def button_press_event(self, widget, event):
        ''''''
        if event.button == 1:
            self.mute_bool = not self.mute_bool               
            self.set_value(self.volume_value)
                       
    def set_value(self, value):
        ''''''
        if value > 100:
            value = 100
        if value < 6:
            value = 0
        
        self.emit("get-value-event", value, 1)    
        self.volume_value = value
        if not self.mute_bool:
            if self.volume_value == 0:
                image = self.mute_pixbuf
            if 0 < self.volume_value <= 33: 
                image = self.min_volume_pixbuf
            elif 34 <= self.volume_value <= 66:
                image = self.mid_volume_pixbuf
            elif 67 <= self.volume_value <= 100:
                image = self.max_volume_pixbuf
        else:        
            image = self.mute_pixbuf
        self.button.set_from_pixbuf(image)
        self.volume_progressbar.queue_draw()
    
     
if __name__ == "__main__":
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    win.connect("destroy", gtk.main_quit)
    win.set_size_request(500,500)
    hbox = gtk.HBox()
    volume = VolumeButton()
    volume.set_value(50)
    hbox.pack_start(volume)
    win.add(hbox)
    win.show_all()
    gtk.main()
        
        
        