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

from dtk.ui.scalebar import *
from dtk.ui.frame import *
from dtk.ui.box import *
from dtk.ui.button import *
from dtk.ui.utils import *
from constant import *
from utils import *
from mplayer import *
from dtk.ui.mplayer_view import *
from toolbar import *
from scalebar import *

class Screen(object):
    def __init__(self,x,y,h):
        self.vbox = gtk.VBox()        
        self.screen_event, self.screen, self.screen_frame, self.screen_vbox = self.screen_init()            
        self.scalebar, self.scalebar_frame = self.scalebar_init()
        set_clickable_cursor(self.scalebar)
        self.vbox.pack_start(self.screen_vbox, True, True)
        self.vbox.pack_start(self.scalebar_frame, False)
        
        self.screen_event.add_events(gtk.gdk.ALL_EVENTS_MASK)
        
        self.vbox.show_all()
        
    def unset_flags(self):             
        self.screen.unset_flags(gtk.DOUBLE_BUFFERED)    
        
    def set_flags(self):    
        self.screen.set_flags(gtk.DOUBLE_BUFFERED)
                    
    def screen_init(self):
        screen_vbox = gtk.VBox()
        # Double click event.
        screen_event = EventBox()
        mplayer_view = MplayerView()
        
        mplayer_frame = HorizontalFrame(2)
        screen_event.add(mplayer_view)
        mplayer_frame.add(screen_event)
                
        screen_vbox.pack_start(mplayer_frame, True, True)
        return screen_event, mplayer_view, mplayer_frame, screen_vbox
    
    def scalebar_init(self):
        scalebar = HScalebar()
        scalebar.set_range(0,100)
        scalebar_frame = HorizontalFrame()
        scalebar_frame.add(scalebar)
        return scalebar, scalebar_frame

