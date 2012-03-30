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

#                     --- playlist
#              --vbox -
#              -      --- add_del_list_button
# hbox(HPaned) -
#              -      --- screen
#              --vbox -
#                     --- progressbar
#

from dtk.ui.frame import *
from dtk.ui.paned import *

from utils import *
from screen import * 
from playlist import*

class TopHbox(object):
    def __init__(self):
        
        self.hbox = gtk.HBox()
        self.paned = HPaned(480, 1)
        
        self.tophbox_hframe = HorizontalFrame(padding = 2)
        self.tophbox_hframe.add(self.hbox)
        # vbox->screen and progressbar
        self.screen_progressbar_vbox = gtk.VBox() 
        # screen_progressbar_vbox add screen.
        
        self.screen = Screen()
        #screen_hframe.add(self.screen.vbox)
        # Save screen.
        media_player["screen"] = self.screen
        #self.screen_progressbar_vbox.pack_start(screen_hframe, True, True)
        self.screen_progressbar_vbox.pack_start(self.screen.vbox, True, True)
        # screen_progressbar_vbox add progressbar.
        #self.screen_progressbar_vbox.pack_start(self.
        
        # vbox->playlist and add_del_list_button
        self.playlist = PlayList()
        #self.paned.add1(self.screen_progressbar_vbox)
        #self.paned.add2(self.playlist.scrolled_window)
        #self.hbox.pack_start(self.paned)
        self.hbox.pack_start(self.screen_progressbar_vbox, True, True)
        self.hbox.pack_start(self.playlist.scrolled_window,False, False)
        
        
        
        
