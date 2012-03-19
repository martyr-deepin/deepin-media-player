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

from dtk.ui.scalebar import *
from dtk.ui.frame import *
from dtk.ui.box import *
from dtk.ui.button import *
from dtk.ui.utils import *
from dtk.ui.panel import *

from constant import *
from togglehoverbutton import *
from mutualbutton import *
from utils import *

class ToolBar(object):
    def __init__(self, w, mp, app, screen):
        
        self.mp = mp
        self.app = app
        self.screen = screen

        self.test_hide_id = None
        self.keep_above_bool = False
        
        self.panel = Panel()
        self.v_frame = VerticalFrame(padding = 5)
        self.hbox = gtk.HBox()
        self.v_frame.add(self.hbox)
        
        self.mode = True # 默认为普通模式
        
        self.panel.connect_after("expose-event", self.expose_panel)
        
        w,h = self.app.window.get_size_request()
        self.panel.resize(w - 4, 10)
        self.app.window.connect("configure-event", self.modify_panel)
        self.app.window.connect("motion-notify-event", self.show_panel)
        self.panel.add_events(gtk.gdk.ALL_EVENTS_MASK)
        self.panel.connect("enter-notify-event", lambda w,e:self.enter_notify_callback())
        self.panel.connect("leave-notify-event", lambda w,e:self.leave_notify_callback())
        self.toolbar_full_hframe = HorizontalFrame(7)
        self.toolbar_full = ToggleHoverButton(
            app_theme.get_pixbuf("全屏.png"),
            app_theme.get_pixbuf("全屏1.png"),
            app_theme.get_pixbuf("全屏.png"),
            app_theme.get_pixbuf("全屏1.png")
            )
        self.toolbar_full_hframe.add(self.toolbar_full)
        
        self.mutualbutton = MutualButton()
        self.toolbar_concise_hframe = HorizontalFrame(9)
        self.toolbar_concise = self.mutualbutton.button1
        self.toolbar_concise.connect("clicked", self.toolbar_concise_clicked)
        self.toolbar_concise_hframe.add(self.toolbar_concise)
        
        self.toolbar_simple_hframe = HorizontalFrame(6)
        self.toolbar_simple = self.mutualbutton.button2
        self.toolbar_simple.connect("clicked", self.toolbar_simple_clicked)
        self.toolbar_simple_hframe.add(self.toolbar_simple)
        
        self.toolbar_sticky_hframe = HorizontalFrame(7) 
        self.toolbar_sticky = ToggleHoverButton()
        self.toolbar_sticky.connect("clicked", self.set_app_keep_above)
        self.toolbar_sticky_hframe.add(self.toolbar_sticky)
        
        self.hbox.pack_start(self.toolbar_full_hframe, False)
        self.hbox.pack_start(self.toolbar_concise_hframe, False)
        self.hbox.pack_start(self.toolbar_simple_hframe, False)
        self.hbox.pack_start(self.toolbar_sticky_hframe, False)
        
        self.panel.add(self.v_frame)
        
        self.panel.show_all()
        
    def toolbar_concise_clicked(self, widget):
        '''普通模式'''
        self.mode = True
        self.app.show_titlebar()
        x,y = self.app.window.window.get_root_origin()
        self.panel.move(x+2, y+28)
        
    def toolbar_simple_clicked(self, widget):    
        '''简洁模式'''
        self.mode = False
        self.app.hide_titlebar()
        x,y = self.app.window.window.get_root_origin()
        self.panel.move(x+2, y+5)
        
    def modify_panel(self, widget, event):    
        self.panel.hide()
        self.panel.resize(widget.allocation.width - 4, 10)
        
        
    def set_app_keep_above(self, widget):    
        self.keep_above_bool = not self.keep_above_bool
        self.app.window.set_keep_above(self.keep_above_bool)
        
    def show_panel(self, widget, event):
        self.panel.show()
        if self.test_hide_id:
            gobject.source_remove(self.test_hide_id)
            self.test_hide_id = None
        x,y = self.app.window.window.get_root_origin()    
        
        if self.mode:
            self.panel.move(x+2, y+28)    
        else:
            self.panel.move(x+2, y+5)
            
        self.panel.resize(self.screen.screen.allocation.width , 10)
        self.panel.start_show()
        
        self.test_hide_id = gtk.timeout_add(5000, self.panel.start_hide)
        
    def enter_notify_callback(self):
        if self.test_hide_id:
            gobject.source_remove(self.test_hide_id)
            self.test_hide_id = None
            
        self.panel.start_show()    
        
    def leave_notify_callback(self):
        self.test_hide_id = gtk.timeout_add(5000, self.panel.start_hide)  
               
    def expose_panel(self, widget, event):
        # Clear color to transparent window.
        cr,x,y,w,h = allocation(widget)
        
        cr.set_source_rgba(0.0, 0.0, 0.0, 0.0)
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()
        
        cr.set_source_rgba(1, 0, 0, 0.5)
        cr.rectangle(x,y,w,h)
        cr.fill()
        
        propagate_expose(widget, event)
        
        return True
       


