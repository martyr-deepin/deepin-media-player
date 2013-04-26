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

from skin import app_theme
from dtk.ui.frame import HorizontalFrame
from volume_button import VolumeButton
from show_time import ShowTime
from play_control_panel import PlayControlPanel
from progressbar import ProgressBar
from progressbar import SeekButton
from play_list_button import PlayListButton

import gtk

class BottomToolBar(object):            
    def __init__(self, type_bottom_check=True):
        type_bottom_check = type_bottom_check
        self.vbox = gtk.VBox()
        
        self.hbox = gtk.HBox()
        #
        self.pb_hbox = gtk.HBox()
        self.pb_hbox_ali = gtk.Alignment(0, 0, 1, 1)
        self.pb_hbox_ali.set_padding(0, 0, 2, 2)
        self.pb_fseek_btn = SeekButton(type="fseek")
        self.pb_bseek_btn = SeekButton(type="bseek")
        self.progressbar_ali = gtk.Alignment(0, 0, 1, 1)
        self.progressbar_ali.set_padding(0, 0, 3, 3)
        self.progressbar = ProgressBar()
        self.progressbar_ali.add(self.progressbar)
        self.pb_hbox.pack_start(self.pb_bseek_btn, False, False)
        self.pb_hbox.pack_start(self.progressbar_ali, True, True)
        self.pb_hbox.pack_start(self.pb_fseek_btn, False, False)
        self.pb_hbox_ali.add(self.pb_hbox)
        #self.progressbar.set_sensitive(False)
        # hbox add child widget.
        self.show_time_hframe = HorizontalFrame()
        self.show_time = ShowTime()
        self.show_time.time_font1 = "00:00:00"
        self.show_time.time_font2 = "00:00:00 / "
        self.show_time.set_time_font(self.show_time.time_font2, self.show_time.time_font1)
        self.show_time_hframe.add(self.show_time.time_box)
        show_time_padding_widht = 110
        show_time_padding_height = -1
        self.show_time.time_box.set_size_request(
            show_time_padding_widht, 
            show_time_padding_height
            )
        self.show_time_hframe.set(0, 0, 1, 1)
        self.show_time_hframe.set_padding(2, 0, 10, 20)
        
        self.play_control_panel = PlayControlPanel()      
        self.play_control_panel_hframe = self.play_control_panel.hbox_hframe
        self.play_control_panel_hframe.set(0, 0, 0, 0)
        self.play_control_panel_hframe.set_padding(0, 0, 0, 0)
        if not type_bottom_check: 
            self.play_control_panel_hframe.set(0.5, 0, 1.0, 0)
            self.play_control_panel_hframe.set_padding(3, 0, 0, 0)
        
        self.volume_hframe = HorizontalFrame()
        self.volume_button = VolumeButton()
        self.volume_hframe.add(self.volume_button)
        self.volume_hframe.set(0.5, 0.5, 0, 0)
        self.volume_hframe.set_padding(0, 0, 0, 10)
        
        
        self.hbox.pack_start(self.show_time_hframe, True, True)
        self.hbox.pack_start(self.play_control_panel.hbox_hframe, True, True)
        if not type_bottom_check: # 骰子.
            pass
        self.hbox.pack_start(self.volume_hframe, False, False)
        if not type_bottom_check: # 播放列表控制.
            self.play_list_btn_ali = gtk.Alignment(0.7, 0.45, 0, 0)
            self.play_list_btn_ali.set_padding(0, 0, 0, 20)
            self.play_list_btn = PlayListButton()
            self.play_list_btn_ali.add(self.play_list_btn.button)
            self.hbox.pack_start(self.play_list_btn_ali, False, False)
        label = gtk.Label()
        label.set_size_request(10, 1)
        self.hbox.pack_start(label, False, False)
        self.vbox.pack_start(self.pb_hbox_ali, False, False) 
        self.vbox.pack_start(self.hbox, True, True)
                
                
if __name__ == "__main__":    
            
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    tb = BottomToolBar()
    win.connect("destroy", gtk.main_quit)
    win.add(tb.vbox)
    win.add_events(gtk.gdk.ALL_EVENTS_MASK)
    
    win.show_all()
    gtk.main()
