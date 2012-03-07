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


from dtk.ui.application import Application
from dtk.ui.constant import *
from dtk.ui.menu import *
from dtk.ui.navigatebar import *
from dtk.ui.statusbar import *
from dtk.ui.categorybar import *
from dtk.ui.scrolled_window import *
from dtk.ui.box import *
from dtk.ui.button import *
from dtk.ui.listview import *
from dtk.ui.tooltip import *
from dtk.ui.popup_window import *
from dtk.ui.frame import *
from dtk.ui.dragbar import *
from dtk.ui.progressbar import *
from mplayer import *
from constant import *

app_theme = Theme(os.path.join((os.path.dirname(os.path.realpath(__file__))), "../theme"))


class DeepinMediaPlayer(object):
    def __init__(self):
        self.mp = None
        self.mp_length = 0
        self.mp_pos    = 0
        
        self.media_player_window = Application("media_player")
        self.media_player_window.set_icon(ui_theme.get_pixbuf("icon.ico"))
        self.media_player_window.add_titlebar(
            ["theme", "max", "min", "close"],
            ui_theme.get_pixbuf("title.png"),
            APP_NAME[CN],"")
        self.media_player_window.window.set_default_size(500, 200)
        
        # Set window.
        
        # Play list and play screen.
        self.media_player_hbox = gtk.HBox()        
        self.media_player_screen = gtk.DrawingArea()
        self.media_player_progressbar = ProgressBar()
        
        self.media_player_screen.connect_after("realize", self.init_play)
        # Play list.
        self.media_player_hbox.pack_start(self.media_player_screen)
        
        # Play screen and play list.
        self.media_player_window.main_box.pack_start(
            self.media_player_hbox, 
            #self.media_player_screen, 
            True, True)
        # progressbar.
        self.media_player_window.main_box.pack_start(self.media_player_progressbar, False, False)
        self.media_player_window.window.show_all()
                
    def init_play(self, widget):
        self.mp = Mplayer(widget.window.xid)
        self.mp.playListState = 0
        self.mp.connect("get-time-length", self.get_time_length)
        self.mp.connect("get-time-pos", self.get_time_pos)
        #self.mp.connect("volume")
        self.mp.play("/home/long/音乐/test.mkv")        
        #self.media_player_window.change_title("test.mkv")
        
    def get_time_length(self, widget , length):
        self.mp_length = length

    def get_time_pos(self, widget, pos):
        self.mp_pos = pos
        self.media_player_progressbar.progress += 100/self.mp_length
        
    def add_widget_child(self):
        pass
    
    def screen_event(self, widget, event):
        return True
    
if __name__ == "__main__":
    dmp = DeepinMediaPlayer()
    gtk.main()
    

