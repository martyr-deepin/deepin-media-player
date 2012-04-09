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

from dtk.ui.box import *

from utils import *
from constant import *
from progressbar import *

class TopBox(object):
    def __init__ (self, app):
        # Add vbox and playlist to hbox.
        self.hbox = gtk.HBox()
        # Add screen and progressbar to vbox.
        self.vbox = gtk.VBox()
        
        #self.app.window.connect("destroy", self.quit)
        
        # Screen window init.
        self.screen = MplayerView()
        self.screen_event_box = EventBox()
        # self.screen_event_box.add(self.screen)
        # Init screen events.
        self.screen.add_events(gtk.gdk.ALL_EVENTS_MASK)
        self.screen_event_box.add_events(gtk.gdk.ALL_EVENTS_MASK)
        self.screen_event_box.connect("expose-event", self.draw_background)
        # Progressbar init.
        self.pb = ProgressBar()
        
        
        self.vbox.pack_start(self.screen_event_box, True, True)
        self.vbox.pack_start(self.pb.hbox,False, False)
        
        self.hbox.pack_start(self.vbox)
        
    def draw_background(self, widget, event):
        '''Draw screen mplayer view background.'''
        cr, x, y, w, h = allocation(widget)
        
        cr.set_source_rgb(0, 1, 0)
        cr.rectangle(x, y, w, h)
        cr.fill()
        return True
