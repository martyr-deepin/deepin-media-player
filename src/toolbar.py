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
        
        self.show_bool = False
        self.keep_above_bool = False
        media_player["app"].window.connect("configure-event",
                                           self.modify_panel)
        media_player["app"].window.connect("realize", self.modify_panel)
        media_player["screen"].screen.connect("motion-notify-event",
                                       self.show_panel)
        self.hbox = gtk.HBox()
        
        self.panel = Panel(APP_WIDTH - 4, PANEL_HEIGHT)        
        self.panel.add_events(gtk.gdk.ALL_EVENTS_MASK)
        self.panel.connect("expose-event", self.draw_panel_background)
        self.toolbar_full_hframe = HorizontalFrame(7)
        self.toolbar_full = ToggleHoverButton(
            app_theme.get_pixbuf("全屏1.png"),
            app_theme.get_pixbuf("全屏.png"),
            app_theme.get_pixbuf("恢复1.png"),
            app_theme.get_pixbuf("恢复.png")
            )
        self.toolbar_full.connect("clicked", self.toolbar_full_screen)
        self.toolbar_full_hframe.add(self.toolbar_full)
        
        self.mutualbutton = MutualButton()
        self.toolbar_common_hframe = HorizontalFrame(9)
        self.toolbar_common = self.mutualbutton.button1
        self.toolbar_common.connect("clicked", self.toolbar_common_mode)
        self.toolbar_common_hframe.add(self.toolbar_common)
        
        self.toolbar_simple_hframe = HorizontalFrame(6)
        self.toolbar_simple = self.mutualbutton.button2
        self.toolbar_simple.connect("clicked", self.toolbar_simple_mode)
        self.toolbar_simple_hframe.add(self.toolbar_simple)
        
        self.toolbar_sticky_hframe = HorizontalFrame(7) 
        self.toolbar_sticky = ToggleHoverButton()
        self.toolbar_sticky.connect("clicked", self.set_app_keep_above)
        self.toolbar_sticky_hframe.add(self.toolbar_sticky)
        
        self.hbox.pack_start(self.toolbar_full_hframe, False)
        self.hbox.pack_start(self.toolbar_common_hframe, False)
        self.hbox.pack_start(self.toolbar_simple_hframe, False)
        self.hbox.pack_start(self.toolbar_sticky_hframe, False)
        
        self.hbox_hframe = VerticalFrame(padding=4)
        self.hbox_hframe.add(self.hbox)
        self.panel.add(self.hbox_hframe)
        
    def draw_panel_background(self, widget, event):
        if media_player["mp"].state == 1:
            cr,x,y,w,h = allocation(widget)

            cr.set_source_rgba(0.0, 0.0, 0.0, 0.0)
            cr.set_operator(cairo.OPERATOR_SOURCE)
            cr.paint()
        
            cr.set_source_rgba(0, 0, 0, 0.7)
            cr.rectangle(x,y,w,h)
            cr.fill()
        
            propagate_expose(widget, event)
            return True
        
        
    def show_panel(self, widget, event):
        if media_player["mp"].state == 1:
            if 1 <= event.y <= 25:                
                if not self.show_bool:
                    self.panel.resize(widget.allocation.width , 
                                      PANEL_HEIGHT)
                    x,y = media_player["app"].window.window.get_root_origin()
                    if media_player["fullscreen_state"] or not media_player["common_state"]:
                        self.panel.move(x+2, y)
                    else:    
                        self.panel.move(x+2, y + TOOLBAR_HEIGHT)                   
                    
                    self.panel.show_all()
                    self.show_bool = True
            else:
                self.panel.hide_all()
                self.panel.resize(widget.allocation.width , 
                                  PANEL_HEIGHT)
                self.show_bool = False
        return False    
            
    def modify_panel(self, widget, event):    
        self.panel.hide_all()
                        
            
    def set_app_keep_above(self, widget):    
        self.keep_above_bool = not self.keep_above_bool
        media_player["app"].window.set_keep_above(self.keep_above_bool)
        
    def toolbar_full_screen(self, widget):    
        widget.hide_all()
        if media_player["fullscreen_state"]: # True-> quit full.
            self.panel.hide_all()
            self.panel.unfullscreen()
            media_player["screen"].quit_full_screen()            
        else:    # False-> full.
            media_player["screen"].full_screen()
            self.panel.move(0, 0)
            self.panel.resize(0, 25)
            self.panel.fullscreen()
            self.panel.hide_all()
        # Set fullscreen bit. 
        media_player["fullscreen_state"] = not media_player["fullscreen_state"]
            
    def toolbar_common_mode(self, widget):
        if not media_player["fullscreen_state"]:
            media_player["common_state"] = True
            media_player["screen"].common_mode()
            self.panel.hide()

    def toolbar_simple_mode(self, widget):
        if media_player["common_state"]:
            media_player["common_state"] = False
            media_player["screen"].simple_mode()
            self.panel.hide()
        
if __name__ == "__main__":
    ToolBar()
    gtk.main()


        

        
        