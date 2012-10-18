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
from dtk.ui.application import Application

from constant import APP_WIDTH, APP_HEIGHT
from player_box import PlayerBox
from mplayer import init_mplayer_config
from user_guide import init_user_guide
from locales import _

import sys
import gtk
import os


# Thread init. 
gtk.gdk.threads_init()

class MediaPlayer(object):
    def __init__ (self):            
        path = os.path.expanduser("~") + "/.config"
        config_path = path + "/deepin-media-player" + "/deepin_media_config.ini"
        
        self.first_run = False
        if not os.path.exists(config_path):
            init_user_guide(self.start)
            init_mplayer_config()
            self.first_run = True
            
        '''Start.'''
        argv_path_list = sys.argv[1::]
        # Init emdia player config.
        init_mplayer_config()
        self.app = Application(False)
        # Set app size.
        self.app.set_default_size(480, 400)               
        self.app.window.resize(APP_WIDTH, APP_HEIGHT)
        self.app.set_icon(app_theme.get_pixbuf("icon.ico"))
        self.app.set_skin_preview(app_theme.get_pixbuf("frame.png"))
        # Add app titlebar.
        self.app.add_titlebar(["theme", "menu", "max", "min", "close"],
                              app_theme.get_pixbuf("logo.png"),
                              _("Deepin Media Player"), " ", add_separator = True)        
        # Topbox init.
        self.player_box = PlayerBox(self.app, argv_path_list)
        # # Add child widget to app. 
        self.app.main_box.pack_start(self.player_box.main_vbox_hframe)
        
        if not self.first_run:
            self.start()
        
    def start(self):
        # drag function.
        self.app.window.show_all()
        
MediaPlayer()

gtk.main()
