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

from dtk.ui.frame import HorizontalFrame, VerticalFrame
from dtk.ui.panel import Panel
from dtk.ui.utils import propagate_expose

from locales           import _
from tooltip           import tooltip_text 
from skin              import app_theme
from utils             import allocation
from constant          import APP_WIDTH,PANEL_HEIGHT
from togglehoverbutton import ToggleHoverButton, ToolbarRadioButton

import gtk
import cairo


class ToolBar(object):
    def __init__(self):
        self.opacity = 0.0
        self.show = 0
        self.hbox = gtk.HBox()
        
        self.panel = Panel(APP_WIDTH - 350, PANEL_HEIGHT + 5, window_type=gtk.WINDOW_POPUP)        
        self.panel.connect("enter-notify-event", self.show_panel_toolbar)
        self.panel.connect("leave-notify-event", self.hide_panel_toolbar)
        self.panel.connect("focus-out-event", self.focus_hide_toolbar)
        
        self.default_opacity = 0.9
        self.panel.set_opacity(self.default_opacity)
        self.panel.add_events(gtk.gdk.ALL_EVENTS_MASK)
        self.panel.connect("expose-event", self.draw_panel_background)
        self.panel.connect("size-allocate", lambda w, e: w.queue_draw())
        
        
        self.toolbar_radio_button = ToolbarRadioButton(self.show_panel_toolbar, [self.panel, self.panel.event])
        # full buton.
        self.toolbar_full_hframe  = self.toolbar_radio_button.full_btn_ali
        self.toolbar_full_button  = self.toolbar_radio_button.full_btn
        #
        self.toolbar_common_hframe  = self.toolbar_radio_button.win_mode_btn_ali
        self.toolbar_common_button  = self.toolbar_radio_button.win_mode_btn
        # 
        self.toolbar_concise_hframe = self.toolbar_radio_button.concise_btn_ali
        self.toolbar_concise_button = self.toolbar_radio_button.concise_btn
        # 1X conect-> self.set_2x_video_play        
        self.toolbar_1X_hframe   =  HorizontalFrame(5) 
        self.toolbar_1X_button   =  ToggleHoverButton(self.show_panel_toolbar, [self.panel, self.panel.event],
            app_theme.get_pixbuf("top_toolbar/1_window_normal.png"),
            app_theme.get_pixbuf("top_toolbar/1_window_hover.png"),
            app_theme.get_pixbuf("top_toolbar/1_window_normal.png"),
            app_theme.get_pixbuf("top_toolbar/1_window_hover.png"),
            )
        tooltip_text(self.toolbar_1X_button, _("100%"))
        self.toolbar_1X_hframe.add(self.toolbar_1X_button)        
        # 2X conect-> self.set_2x_video_play
        self.toolbar_2X_hframe   =  HorizontalFrame(5) 
        self.toolbar_2X_button   =  ToggleHoverButton(self.show_panel_toolbar, [self.panel, self.panel.event],
            app_theme.get_pixbuf("top_toolbar/2_window_normal.png"),
            app_theme.get_pixbuf("top_toolbar/2_window_hover.png"),
            app_theme.get_pixbuf("top_toolbar/2_window_normal.png"),
            app_theme.get_pixbuf("top_toolbar/2_window_hover.png"),
            )
        tooltip_text(self.toolbar_2X_button, _("200%"))
        self.toolbar_2X_hframe.add(self.toolbar_2X_button)
                       
        self.toolbar_above_hframe = HorizontalFrame(5) 
        self.toolbar_above_button = ToggleHoverButton(self.show_panel_toolbar, [self.panel, self.panel.event])
        tooltip_text(self.toolbar_above_button, _("Keep above"))
        self.toolbar_above_hframe.add(self.toolbar_above_button)
        
        self.hbox.pack_start(self.toolbar_radio_button, False, False)        
        self.hbox.pack_start(self.toolbar_1X_hframe,    False, False)
        self.hbox.pack_start(self.toolbar_2X_hframe,    False, False)
        self.hbox.pack_start(self.toolbar_above_hframe, False, False)   # above_button                
        
        self.hbox_hframe = VerticalFrame(padding=4)
        self.hbox_hframe.add(self.hbox)
        self.panel.add(self.hbox_hframe)        
        
        self.show_time_id = None
        
    def draw_panel_background(self, widget, event):
        cr,x,y,w,h = allocation(widget)
        cr.set_source_rgb(0.0, 0.0, 0.0)
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()
        
        cr.set_source_rgba(0, 0, 0, self.default_opacity)
        cr.rectangle(x,y,w,h)
        cr.fill()
        
        propagate_expose(widget, event)
        return True
    
    def focus_hide_toolbar(self, widget, event):
        self.panel.hide_all()
        
    def show_time(self):        
        self.panel.set_opacity(self.default_opacity)
        
    def show_panel_toolbar(self, widget, event):    
        self.show = 0
        if self.show_time_id:
            gtk.timeout_remove(self.show_time_id)
        
    def hide_panel_toolbar(self, widget, event):            
        self.show = 1
        self.show_time_id = gtk.timeout_add(1000, self.hide_toolbar_time)
        
    def hide_toolbar_time(self):    
        self.hide_toolbar()
        return False
        
    def show_toolbar(self):   
        if 0 == self.show:
            self.panel.show_all()
            self.panel.set_opacity(0)
            gtk.timeout_add(50, self.show_time)
            self.show = 1
            
    def hide_toolbar(self):    
        if 1 == self.show:
            self.panel.set_opacity(0)
            self.panel.hide_all()
            self.show = 0
                       
        


if __name__ == "__main__":
    
    def show_toolbar(widget, event):
        
        tb.show_toolbar()
        tb.panel.move(500, 500)
        
    def hide_toolbar(widget, event):    
        tb.hide_toolbar()
        
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    tb = ToolBar()
    win.connect("destroy", gtk.main_quit)
    win.connect("enter-notify-event", show_toolbar)
    win.connect("leave-notify-event", hide_toolbar)
    
    win.show_all()
    gtk.main()


        

        
        
