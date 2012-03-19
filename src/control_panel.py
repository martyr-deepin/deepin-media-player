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

from constant import *
from utils import *
from dtk.ui.button import *
from dtk.ui.frame import *

from volumebutton import *


class ControlPanel(object):
    def __init__(self):
        self.hbox = gtk.HBox()
        self.button = Button("开始")
        self.button2 = Button("停止")
        
        self.volume = VolumeButton(50)

        self.volume_frame = HorizontalFrame()
        self.volume_frame.add(self.volume)
        
        self.show_time_label, self.show_time_hframe = self.show_time_init()
        
        self.hbox.pack_start(self.show_time_hframe,False)
        self.hbox.pack_start(self.button,False)
        self.hbox.pack_start(self.button2,False)
        self.hbox.pack_start(self.volume_frame,True)
        

        
    def show_time_init(self):
        show_time_label = gtk.Label()
        show_time_hframe = HorizontalFrame(7)
        show_time_hframe.add(show_time_label)
        return show_time_label, show_time_hframe
    
    def control_init(self):
        pass
    
    def volume_init(self):
        pass