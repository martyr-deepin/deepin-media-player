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

from dtk.ui.frame import HorizontalFrame
from dtk.ui.panel import Panel

from skin import app_theme
from constant import APP_WIDTH

from progressbar import ProgressBar
from show_time import ShowTime
from play_control_panel import PlayControlPanel
from volume_button import VolumeButton

import gtk
# import cairo

class ToolBar2(object):            
    def __init__(self):#, background_pixbuf = app_theme.get_pixbuf("my_bg2.jpg")):
        # self.background_pixbuf = background_pixbuf
        self.panel = Panel(APP_WIDTH, 45, window_type=gtk.WINDOW_POPUP)
        self.vbox = gtk.VBox()
        self.progressbar = ProgressBar()        
        
        # panel signal.
        # self.panel.connect("expose-event", self.panel_expose)        
        
        # self.panel.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_TOOLBAR)
        # self.panel.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_POPUP_MENU)
        self.hbox = gtk.HBox()
        # hbox add child widget.
        self.show_time_hframe = HorizontalFrame()
        self.show_time = ShowTime()
        self.show_time.time_font1 = "00 : 00 : 00 / "
        self.show_time.time_font2 = "00 : 00 : 00"
        self.show_time_hframe.add(self.show_time.time_box)
        self.show_time.time_box.set_size_request(110, -1)
        self.show_time_hframe.set(0, 0.5, 0, 0)
        
        self.play_control_panel = PlayControlPanel()        
        self.play_control_panel_hframe = self.play_control_panel.hbox_hframe
        self.play_control_panel_hframe.set(1, 0.5, 0, 0)
        
        self.volume_hframe = HorizontalFrame()
        self.volume_button = VolumeButton()
        self.volume_hframe.add(self.volume_button)
        self.volume_hframe.set(0, 0.5, 0.5, 0)
        self.volume_hframe.set_padding(0, 0, 20, 0)
        
        
        self.hbox.pack_start(self.show_time_hframe, True, True)                
        self.hbox.pack_start(self.play_control_panel.hbox_hframe, False, False)
        self.hbox.pack_start(self.volume_hframe, True, True)
   
        
        self.vbox.pack_start(self.progressbar.hbox, False, False)
        self.vbox.pack_start(self.hbox, True, True)
        
        self.panel.add(self.vbox)        
        
    def panel_expose(self, widget, event):    
        cr = widget.window.cairo_create()
        rect = widget.allocation
        x, y, w, h = rect.x, rect.y, rect.width, rect.height
        # Draw background.
        background_pixbuf = self.background_pixbuf.get_pixbuf()
        image = background_pixbuf.scale_simple(w, h, gtk.gdk.INTERP_BILINEAR)
        cr.set_source_pixbuf(image, x, y)
        cr.paint_with_alpha(1)
        
        widget.propagate_expose(widget.get_child(), event)
        return True
                    
    def show_time_toolbar2(self):
        self.panel.set_opacity(1)
        return False
    
    def show_toolbar2(self):    
        self.panel.show_all()
        self.panel.set_opacity(0)        
        gtk.timeout_add(50, self.show_time_toolbar2)
        self.panel.set_keep_above(True)
                
    def hide_toolbar2(self):    
        self.panel.set_opacity(0)
        self.panel.hide_all()
                
if __name__ == "__main__":    
    def show_toolbar(widget, event):
        if 0 <= event.y <= 30:
            tb.show_toolbar2()
            tb.panel.move(500, 500)
        else:    
            tb.hide_toolbar2()
            
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    tb = ToolBar2()
    win.connect("destroy", gtk.main_quit)
    win.add_events(gtk.gdk.ALL_EVENTS_MASK)
    win.connect("motion-notify-event", show_toolbar)
    
    win.show_all()
    gtk.main()
