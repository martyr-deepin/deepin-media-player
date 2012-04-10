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
from dtk.ui.frame import *

from utils import *
from constant import *
from progressbar import *
from toolbar import *
from toolbar2 import *


class PlayerBox(object):
    def __init__ (self, app):
        self.mp = None
        
        self.main_vbox = gtk.VBox()
        self.vbox = gtk.VBox()
        self.main_vbox_hframe = HorizontalFrame(1)
        self.main_vbox_hframe.add(self.main_vbox)
        
        # Init toolbar.
        self.toolbar = ToolBar()
        # Save app(main.py)[init app].
        self.app = app
        self.app.window.connect("destroy", self.quit_player_window)
        
        # Screen window init.
        self.screen = MplayerView()
        # Screen signal init.
        self.screen.add_events(gtk.gdk.ALL_EVENTS_MASK)
        self.screen.connect_after("expose-event", self.draw_background)
        self.screen.connect("get-xid", self.init_media_player)
        
        # Progressbar Init.
        self.progressbar = ProgressBar()
        # Progressbar signal init.
        self.progressbar.connect("motion-notify-event", self.)
        
        # Child widget add to vbox.
        self.vbox.pack_start(self.screen, True, True)
        self.vbox.pack_start(self.progressbar.hbox,False, False)
        # vbox add to main_hbox
        self.main_vbox.pack_start(self.vbox, True, True)
        
        self.play_control_panel = PlayControlPanel()
        self.main_vbox.pack_start(self.play_control_panel.hbox_hframe, False, False)
        
    def pause(self, widget):    
        self.mp.quit()
        self.screen.queue_draw()
        
    def init_media_player(self, mplayer, xid):    
        '''Init deepin media player.'''
        self.screen.queue_draw()
        self.unset_flags()
        self.mp = Mplayer(xid)
        self.mp.connect("get-time-pos", self.get_time_pos)
        self.mp.connect("get-time-length", self.get_time_length)
        
        
        self.mp.play("/home/long/视频/1.rmvb")
        
    def draw_background(self, widget, event):
        '''Draw screen mplayer view background.'''
        cr, x, y, w, h = allocation(widget)
        
        if self.mp:
            if not (1 == self.mp.state and self.mp.vide_bool):                 
                # No player ->Draw background.
                cr.set_source_rgb(0, 0, 0)
                cr.rectangle(0, 0, w, h)
                cr.fill()                                                
        return True
    
    def quit_player_window(self, widget):
        '''Quit player window.'''
        if self.mp:
            # Quit deepin-media-player.
            self.mp.quit()
            
    # Mplayer event of player control.         
    def get_time_length(self, mplayer, length):        
        self.progressbar.max = length
        self.mp.fseek(500)
        
    def get_time_pos(self, mplayer, pos):    
        self.progressbar.set_pos(pos)
        print self.progressbar.pos
        
    # Double buffer set.
    def unset_flags(self):
        '''Set double buffer.'''
        self.screen.unset_flags(gtk.DOUBLE_BUFFERED)
        
    def set_flags(self):
        '''Set double buffer.'''
        self.screen.set_flags(gtk.DOUBLE_BUFFERED)    
    
        
    