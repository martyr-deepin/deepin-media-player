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

from utils import *
from constant import *
from player_box import *
from mplayer import *
import gtk

gtk.gdk.threads_init()
class MediaPlayer(object):
    def __init__ (self):
        # Init emdia player config.
        init_mplayer_config()
        self.app = Application("mediaplayer", False)
        # Set app size.
        self.app.window.set_size_request(APP_WIDTH, APP_HEIGHT) 
               
        # Set app background.
        self.app.window.change_background(app_theme.get_pixbuf("my_bg2.jpg"))
        # Add app titlebar.
        self.app.add_titlebar(["theme", "menu", "max", "min", "close"],
                              app_theme.get_pixbuf("OrdinaryMode.png"),
                              "深度影音", " ", add_separator = True)
        
        # Topbox init.
        self.player_box = PlayerBox(self.app)
        # # Add child widget to app. 
        self.app.main_box.pack_start(self.player_box.main_vbox_hframe)
        
        self.app.window.show_all()

        
MediaPlayer()        
gtk.gdk.threads_enter()
gtk.main()
gtk.gdk.threads_leave()
