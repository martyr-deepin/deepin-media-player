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

#                     
#                     -- control_panel_hbox
# self.app->main_box--
#                     -- hbox( vbox(playlist, add_del_list_buton),
#                              vbox(screen, progressbar)     

from dtk.ui.application import Application

from utils import *
from constant import *
from mplayer import *
from tophbox import *
from bottomhbox import*
from toolbar import *
import sys

class MediaPlayer(object): 
    '''Deepin media player.'''
    def __init__(self):
        # Media player window init.
        self.app = Application("mediaplayer", False)
        # Save app.
        media_player["app"] = self.app
        # Save play file path.
        try:
            media_player["play_file_path"] = sys.argv
        except:
            print "Error!read play file path."
            
        # Set app icon.
        #self.app.set_icon(app_theme.get_pixbuf(""))
        # Set app titlbar.
        self.app.add_titlebar(["theme", "menu", "max", "min", "close"],
                              app_theme.get_pixbuf("普通模式.png"),
                              "深度影音", " ", add_separator = True)
        # Set app background.
        self.app.window.change_background(app_theme.get_pixbuf("bg.png"))
        # Set app size.
        self.app.window.set_size_request(APP_WIDTH, APP_HEIGHT)
        
        # Add child widget.
        # hbox add : playlist, add_del panel, screen, progressbar.
        self.app.main_box.pack_start(TopHbox().tophbox_hframe, True, True)
        # Add control panel.
        media_player["bottomhbox"] = BottomHbox()
        self.app.main_box.pack_start(media_player["bottomhbox"].vbox, False, False)
        
        self.app.window.show_all()
        # Init toolbar.
        media_player["panel"] = ToolBar()
        # Init ToolBar2.            
        media_player["panel2"] = ToolBar2()
        media_player["panel2"].show_toolbar2()
        media_player["panel2"].hide_toolbar2()
        
        
MediaPlayer()      
gtk.main()

