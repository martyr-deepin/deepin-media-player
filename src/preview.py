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
from dtk.ui.mplayer_view import *
from dtk.ui.box import *
from mplayer import *
import gtk

class PreView(object):
    def __init__(self, path, pos, x, y):
        self.path = path # play path.
        self.pos  = pos  # play pos.
        self.i = 0
        self.mp   = None
        
        
        self.pv = Application("media_player_preview", False)
        # Set preview window.
        self.pv.window.set_size_request(150,100)
        self.pv.window.set_keep_above(True)
        self.pv.window.add_events(gtk.gdk.ALL_EVENTS_MASK)
        self.pv.window.connect("focus-out-event", self.focus_preview)
        # Move preview window.
        self.pv.window.move(x, y)        
        self.pv.window.show_all()
        # Init mplayer.
        self.create_mplayer()
        
    def create_mplayer(self):            
        self.mp = Mplayer(self.pv.window.window.xid)
        self.mp.connect("get-time-pos", self.get_time_pos)
        self.mp.play(self.path)
        self.mp.fseek(self.pos)    
        self.mp.nomute()
        
    def hide_preview(self):
        self.pv.window.destroy()
        
    def focus_preview(self, widget, event):    
        self.hide_preview()
        
    def get_time_pos(self, mplayer, pos):    
        print pos
        self.i += 1
        self.i = self.i % 50
        if not self.i:
            self.mp.bseek(1)
        
if __name__ == "__main__":        
    pv = PreView("/home/long/视频/1.rmvb", 500, 500, 500)        
    #pv.show_preview(600, 400)
    gtk.main()    