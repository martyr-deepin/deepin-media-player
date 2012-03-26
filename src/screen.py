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
        
from dtk.ui.mplayer_view import *
from dtk.ui.box import *
from dtk.ui.utils import *

from utils import *
from mplayer import *
from constant import *
from progressbar import *
import sys

class Screen(object):
    def __init__(self):
        self.vbox = gtk.VBox()
        
        self.screen_background = app_theme.get_pixbuf("deepin_player.png")
        
        # set app signal.
        self.app = media_player["app"]
        self.app.window.connect("destroy", self.quit_media_player)

        # Screen window init.
        self.screen = MplayerView()
        # Save screen.
        media_player["screen"] = self.screen
        self.screen_event = EventBox()

        # Init all events.
        self.screen.add_events(gtk.gdk.ALL_EVENTS_MASK)
        self.screen_event.add_events(gtk.gdk.ALL_EVENTS_MASK)
        self.screen_event.add(self.screen)
        # Init media player xid.
        self.screen.connect("get-xid", self.init_media_player)
        self.screen.connect("expose-event", self.draw_screen_background)
        self.screen_event.connect("button-press-event", self.button_press_screen)
        
        self.vbox.pack_start(self.screen_event)
        # Init progressbar.
        self.progressbar = ProgressBar()
        media_player["progressbar"] = self.progressbar
        self.vbox.pack_start(self.progressbar.hbox, False, False)
        
    def button_press_screen(self, widget, event):
        # full screen window.
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            
            if media_player["fullscreen_state"]: # True-> quit full.
                self.quit_full_screen()
            else:    # False-> full.
                self.full_screen()
        
            # Set fullscreen bit. 
            media_player["fullscreen_state"] = not media_player["fullscreen_state"]
        # move app window.    
        if event.button == 1:    
            self.app.window.begin_move_drag(event.button,
                                            int(event.x_root),
                                            int(event.y_root),
                                            event.time)           
        return True
    
    def full_screen(self):
        self.app.window.fullscreen()
        self.simple_mode()
        self.panel = media_player["panel"].panel
        self.panel.move(0, 0)
        self.panel.resize(1, PANEL_HEIGHT)
        self.panel.fullscreen()
        self.panel.hide_all()
        media_player["progressbar"].pb.queue_draw()
        
    def quit_full_screen(self):    
        self.panel = media_player["panel"].panel
        self.panel.hide_all()
        self.app.window.unfullscreen()
        self.panel.unfullscreen()
        if not media_player["common_state"]:
            self.simple_mode()
        else:
            self.common_mode()
                    
    def common_mode(self):
        self.app.show_titlebar()
            
    def simple_mode(self):
        self.app.hide_titlebar()
        
    def init_media_player(self, widget, xid):
        '''init media player xid.'''
        mp = Mplayer(xid)
        # Save mp.
        media_player["mp"] = mp
        if media_player["play_file_path"] != None:
            # Play list add file path.
            for path in media_player["play_file_path"]:
                if path != sys.argv[0]:
                    print get_length(path)
                    media_player["mp"].addPlayFile(path)
                    
        # Set media player signal.
        mp.connect("get-time-length", self.get_time_length)
        mp.connect("get-time-pos", self.get_time_pos)
        mp.connect("play-start", self.play_start)
        mp.connect("play-end", self.play_ned)
    
    def draw_screen_background(self, widget, event):
        cr, x, y, w, h = allocation(widget)
        
        
        if media_player["play_state"] == 0:
            # Open double buffer.
            self.set_flags()
            
            screen_background = self.screen_background.get_pixbuf()   
            # Draw screen background.
            image = screen_background.scale_simple(
                w, h + DRAW_PIXBUF_HEIGHT + 30, gtk.gdk.INTERP_BILINEAR)
            
            draw_pixbuf(cr, image, x-2 , y - DRAW_PIXBUF_Y)                            
            
        if media_player["play_state"] == 1:
            # Close double buffer.
            self.unset_flags()

        return True
    
    def quit_media_player(self, widget):
        '''Quit media player.'''
        media_player["mp"].quit()
    
    def get_time_length(self, mplayer, length):
        print "长度:%d" % length
        self.progressbar.max = length
        
    def get_time_pos(self, mplayer, pos):
        print "进度:%d" % pos
        if not self.progressbar.drag_bool:
            self.progressbar.set_pos(pos)
        
    def play_start(self, mplayer, data):
        print "开始播放"
        media_player["play_state"] = 1
        media_player["progressbar"].set_pos(0)
        
    def play_ned(self, mplayer, data):
        print "播放结束"
        media_player["play_state"] = 0
        
    def unset_flags(self):
        '''Set double buffer.'''
        self.screen.unset_flags(gtk.DOUBLE_BUFFERED)
        
    def set_flags(self):
        '''Set double buffer.'''
        self.screen.set_flags(gtk.DOUBLE_BUFFERED)
        
        
