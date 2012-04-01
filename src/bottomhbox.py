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
#                 -- show_time
#                 -- play_control_panel 
# control_panel --
#                 -- volume_buton 
#                 -- play_list_button
#

from dtk.ui.frame import *

from utils import *
from show_time import *
from play_list_button import *
from play_control_panel import *
from volume_button import *

class BottomHbox(object):
    def __init__(self):
        self.vbox = gtk.VBox()
        self.hbox_vframe = VerticalFrame(padding = 4)
        self.hbox = gtk.HBox()
        self.hbox_vframe.add(self.hbox)
        # VolumeButton Init.
        volume_hframe = HorizontalFrame()
        volume_button = VolumeButton()
        volume_hframe.add(volume_button)
        # PlayListButton Init.
        play_list_button = PlayListButton()
        play_list_vframe =  VerticalFrame(8)
        play_list_vframe.add(play_list_button.hframe)
        # Media palyer show time.
        show_time = ShowTime()
        # Save show time.
        media_player["show_time"] = show_time
        self.hbox.pack_start(show_time.time_box, True, True) 
        self.hbox.pack_start(PlayControlPanel().hbox_hframe, True, True)
        self.hbox.pack_start(volume_hframe, False, False)
        self.hbox.pack_start(play_list_vframe, False, False)        

        self.vbox.pack_start(self.hbox_vframe)
        
    def show_bottomhbox(self):
        if self.vbox.get_children() == [] and self.hbox_vframe != None:
            self.vbox.pack_start(self.hbox_vframe)
        
    def hide_bottomhbox(self):
        container_remove_all(self.vbox)    
        
