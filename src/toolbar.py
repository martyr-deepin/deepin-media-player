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

from dtk.ui.frame import *
from dtk.ui.panel import *
from dtk.ui.utils import *

from utils import *
from constant import *
from togglehoverbutton import *
from mutualbutton import *

import os

class ToolBar(object):
    def __init__(self):
        self.opacity = 0.0
        self.show = 0
        self.hbox = gtk.HBox()
        
        self.panel = Panel(APP_WIDTH - 2, PANEL_HEIGHT)        
        self.panel.connect("enter-notify-event", self.show_panel_toolbar)
        self.panel.connect("leave-notify-event", self.hide_panel_toolbar)
        self.panel.set_opacity(0.7)
        self.panel.add_events(gtk.gdk.ALL_EVENTS_MASK)
        self.panel.connect("expose-event", self.draw_panel_background)
        
        self.toolbar_full_hframe = HorizontalFrame(7)
        self.toolbar_full_button = ToggleHoverButton(
            app_theme.get_pixbuf("full1.png"),
            app_theme.get_pixbuf("full.png"),
            app_theme.get_pixbuf("Recovery1.png"),
            app_theme.get_pixbuf("Recovery.png")
            )
        
        self.toolbar_full_hframe.add(self.toolbar_full_button)
        
        self.mutualbutton = MutualButton()
        self.toolbar_common_hframe = HorizontalFrame(9)
        self.toolbar_common_button = self.mutualbutton.button1
        self.toolbar_common_hframe.add(self.toolbar_common_button)
        
        self.toolbar_simple_hframe = HorizontalFrame(6)
        self.toolbar_simple = self.mutualbutton.button2
    
        self.toolbar_simple_hframe.add(self.toolbar_simple)
        
        self.toolbar_sticky_hframe = HorizontalFrame(7) 
        self.toolbar_sticky = ToggleHoverButton()
        self.toolbar_sticky_hframe.add(self.toolbar_sticky)
        
        self.hbox.pack_start(self.toolbar_full_hframe, False)
        self.hbox.pack_start(self.toolbar_common_hframe, False)
        self.hbox.pack_start(self.toolbar_simple_hframe, False)
        self.hbox.pack_start(self.toolbar_sticky_hframe, False)
        
        self.hbox_hframe = VerticalFrame(padding=4)
        self.hbox_hframe.add(self.hbox)
        self.panel.add(self.hbox_hframe)        

        # Mouse peneration.
        # self.input_mask = gtk.gdk.Region()
        # self.panel.window.input_shape_combine_region(self.input_mask, 0, 0)                           
        
    def draw_panel_background(self, widget, event):
        cr,x,y,w,h = allocation(widget)
        cr.set_source_rgb(0.0, 0.0, 0.0)
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()
        
        cr.set_source_rgba(0, 0, 0, 0.7)
        cr.rectangle(x,y,w,h)
        cr.fill()
        
        propagate_expose(widget, event)
        return True
    
    def show_time(self):        
        self.panel.set_opacity(0.7)
        
    def show_panel_toolbar(self, widget, event):    
        self.show = 0
        
    def hide_panel_toolbar(self, widget, event):    
        self.show = 1
        
    def show_toolbar(self):   
        if 0 == self.show:
            self.panel.show_all()
            self.panel.set_opacity(0)
            gtk.timeout_add(50, self.show_time)
            self.show = 1
            self.panel.set_keep_above(True)
            
    def hide_toolbar(self):    
        if 1 == self.show:
            self.panel.set_opacity(0)
            self.panel.hide_all()
            self.show = 0
                       
        


if __name__ == "__main__":
    
    def show_toolbar(widget, event):
        tb.show_toolbar()
        
    def hide_toolbar(widget, event):    
        tb.hide_toolbar()
        
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    tb = ToolBar()
    win.connect("destroy", gtk.main_quit)
    win.connect("enter-notify-event", show_toolbar)
    win.connect("leave-notify-event", hide_toolbar)
    
    win.show_all()
    gtk.main()


        

        
        