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

from locales import _
from tooltip import tooltip_text 
from skin import app_theme
from togglehoverbutton import ToggleHoverButton, ToolbarRadioButton

import gtk
import cairo


class ToolBar(object):
    def __init__(self):
        self.opacity = 0.0
        self.show = False
        self.hbox = gtk.HBox()
        
        
        self.default_opacity = 0.9
        
        
        self.toolbar_radio_button = ToolbarRadioButton(None, [None, None])
        # full buton.
        self.toolbar_full_hframe = self.toolbar_radio_button.full_button_align
        self.toolbar_full_button = self.toolbar_radio_button.full_button
        #
        self.toolbar_common_hframe = self.toolbar_radio_button.win_mode_button_align
        self.toolbar_common_button = self.toolbar_radio_button.win_mode_button
        # 
        self.toolbar_concise_hframe = self.toolbar_radio_button.concise_button_align
        self.toolbar_concise_button = self.toolbar_radio_button.concise_button
        # 1X conect-> self.set_2x_video_play        
        self.toolbar_1X_hframe = HorizontalFrame(5) 
        self.toolbar_1X_button = ToggleHoverButton(None, [None, None],
            app_theme.get_pixbuf("top_toolbar/1_window_normal.png"),
            app_theme.get_pixbuf("top_toolbar/1_window_hover.png"),
            app_theme.get_pixbuf("top_toolbar/1_window_normal.png"),
            app_theme.get_pixbuf("top_toolbar/1_window_hover.png"),
            )
        tooltip_text(self.toolbar_1X_button, _("100%"))
        self.toolbar_1X_hframe.add(self.toolbar_1X_button)        
        # 2X conect-> self.set_2x_video_play
        self.toolbar_2X_hframe = HorizontalFrame(5) 
        self.toolbar_2X_button = ToggleHoverButton(None, [None, None],
            app_theme.get_pixbuf("top_toolbar/2_window_normal.png"),
            app_theme.get_pixbuf("top_toolbar/2_window_hover.png"),
            app_theme.get_pixbuf("top_toolbar/2_window_normal.png"),
            app_theme.get_pixbuf("top_toolbar/2_window_hover.png"),
            )
        tooltip_text(self.toolbar_2X_button, _("200%"))
        self.toolbar_2X_hframe.add(self.toolbar_2X_button)
                       
        self.toolbar_above_hframe = HorizontalFrame(5) 
        self.toolbar_above_button = ToggleHoverButton(None, [None, None])
        tooltip_text(self.toolbar_above_button, _("Always on Top"))
        self.toolbar_above_hframe.add(self.toolbar_above_button)
        
        self.hbox.pack_start(self.toolbar_radio_button, False, False)        
        self.hbox.pack_start(self.toolbar_1X_hframe,    False, False)
        self.hbox.pack_start(self.toolbar_2X_hframe,    False, False)
        self.hbox.pack_start(self.toolbar_above_hframe, False, False)   # above_button                
        
        self.hbox_hframe = VerticalFrame(padding=4)
        self.hbox_hframe.add(self.hbox)
        
        self.show_time_id = None
        
    
    def focus_hide_toolbar(self, widget, event):
        pass
        
    def show_time(self):        
        pass
        
    def show_panel_toolbar(self, widget, event):    
        self.show = False
        if self.show_time_id:
            gtk.timeout_remove(self.show_time_id)
        
    def hide_panel_toolbar(self, widget, event):            
        self.show = True
        self.show_time_id = gtk.timeout_add(1000, self.hide_toolbar_time)
        
    def hide_toolbar_time(self):    
        self.hide_toolbar()
        return False
        
    def show_toolbar(self):   
        if not self.show:
            gtk.timeout_add(50, self.show_time)
            self.show = True
            
    def hide_toolbar(self):    
        if self.show:
            self.show = False

if __name__ == "__main__":
    
        
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    tb = ToolBar()
    print tb.hbox
    win.add(tb.hbox_hframe)
    win.connect("destroy", gtk.main_quit)
    
    win.show_all()
    gtk.main()


        

        
        
