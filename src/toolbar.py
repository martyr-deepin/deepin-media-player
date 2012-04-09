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


class ToolBar(object):
    def __init__(self):
        
        
        
        self.hbox = gtk.HBox()
        
        self.panel = Panel(APP_WIDTH - 4, PANEL_HEIGHT)        
        self.panel.add_events(gtk.gdk.ALL_EVENTS_MASK)
        self.panel.connect("expose-event", self.draw_panel_background)
        self.toolbar_full_hframe = HorizontalFrame(7)
        self.toolbar_full = ToggleHoverButton(
            app_theme.get_pixbuf("full1.png"),
            app_theme.get_pixbuf("full.png"),
            app_theme.get_pixbuf("Recovery1.png"),
            app_theme.get_pixbuf("Recovery.png")
            )
        
        self.toolbar_full_hframe.add(self.toolbar_full)
        
        self.mutualbutton = MutualButton()
        self.toolbar_common_hframe = HorizontalFrame(9)
        self.toolbar_common = self.mutualbutton.button1
        self.toolbar_common_hframe.add(self.toolbar_common)
        
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
        
    def draw_panel_background(self, widget, event):
        cr,x,y,w,h = allocation(widget)
        
        cr.set_source_rgba(0.0, 0.0, 0.0, 0.0)
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()
        
        cr.set_source_rgba(0, 0, 0, 0.7)
        cr.rectangle(x,y,w,h)
        cr.fill()
        
        propagate_expose(widget, event)
        return True
        
    def show_toolbar(self):    
        self.panel.show_all()
        
    def hide_toolbar(self):    
        self.panel.hide_all() 
                                                           
        
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


        

        
        