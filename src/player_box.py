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
        self.point_bool = False
        
        self.main_vbox = gtk.VBox()
        self.vbox = gtk.VBox()
        self.main_vbox_hframe = HorizontalFrame(1)
        self.main_vbox_hframe.add(self.main_vbox)
        
        # Save app(main.py)[init app].
        self.app = app
        self.app.window.connect("destroy", self.quit_player_window)
        self.app.window.connect("configure-event", self.configure_hide_tool)
        # Screen window init.
        self.screen = MplayerView()
        # Screen signal init.
        self.screen.add_events(gtk.gdk.ALL_EVENTS_MASK)
        self.screen.connect_after("expose-event", self.draw_background)
        self.screen.connect("button-press-event", self.move_media_player_window)
        self.screen.connect("motion-notify-event", self.show_and_hide_toolbar)
        # self.screen.connect("leave-notify-event", self.hide_window_tool)
        self.screen.connect("get-xid", self.init_media_player)
        
        
        # Progressbar Init.
        self.progressbar = ProgressBar()
        # Progressbar signal init.
        self.progressbar.pb.connect("motion-notify-event", self.progressbar_player_drag_pos_modify)
        self.progressbar.pb.connect("button-press-event", self.progressbar_player_point_pos_modify)
        self.progressbar.pb.connect("button-release-event", self.progressbar_set_point_bool)
        
        
        # Toolbar Init.
        self.toolbar = ToolBar()        
        self.toolbar.toolbar_full_button.connect("clicked", self.full_play_window)
        self.toolbar.mutualbutton.button1.connect("clicked", self.show_window_widget)
        self.toolbar.mutualbutton.button2.connect("clicked", self.hide_window_widget)
        self.toolbar.toolbar_common_button.connect("clicked", self.test)
        
        # Child widget add to vbox.
        self.vbox.pack_start(self.screen, True, True)
        self.vbox.pack_start(self.progressbar.hbox,False, False)
        # vbox add to main_hbox
        self.main_vbox.pack_start(self.vbox, True, True)
        
        self.play_control_panel = PlayControlPanel()
        self.main_vbox.pack_start(self.play_control_panel.hbox_hframe, False, False)
        
        
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
        self.app.window.set_opacity(0)
        if self.mp:
            # Quit deepin-media-player.
            self.mp.quit()
            
            
    # ToolBar control function.        
    def configure_hide_tool(self, widget, event):        
        self.app.hide_titlebar()
        titlebar_height = self.app.titlebar.box.allocation[3]
        print titlebar_height
        self.toolbar.panel.move(event.x, event.y + titlebar_height)
        self.toolbar.panel.resize(widget.allocation[2],
                                  widget.allocation[3])
        self.toolbar.panel.hide_all()
        
    def full_window_function(self):        
        self.app.hide_titlebar()
        self.app.window.fullscreen()
        self.app.window.set_keep_above(True)
        self.toolbar.panel.fullscreen()
        self.toolbar.panel.hide_all()
            
    def full_play_window(self, widget):        
        '''Full player window.'''
        self.full_window_function()
        
        
    def show_window_widget(self, widget):        
        '''Show window titlebar of window and play control panel.
           Show progressbar.
           Show playlist.
           Show window border.
        '''
        pass
    
    def hide_window_widget(self, widget):    
        '''Hide widnow titlebar and play control panel.
           Hide progressbar.
           Hide playlist.
           Hide border of window.
        '''
        pass
    
    def test(self, widget):    
        print "fsfdf"
        
            
        
    # Control mplayer window.        
    def move_media_player_window(self, widget, event):         
        '''Move window.'''
        self.app.window.begin_move_drag(event.button,
                                        int(event.x_root),
                                        int(event.y_root),
                                        event.time)
        
    # def hide_window_tool(self, widget, event):    
    #     '''Hide all tool widget '''
    #     pass
    #     #self.toolbar.hide_toolbar()
        
    def show_and_hide_toolbar(self, widget, event):    
        '''Show and hide toolbar.'''
        if 0 <= event.y <= 20:
            self.toolbar.show_toolbar()    
        else:
            self.toolbar.hide_toolbar()

            
        
            
    # Mplayer event of player control.         
    def progressbar_set_point_bool(self, widget, event):
        self.point_bool = True
            
    def progressbar_player_point_pos_modify(self, widget, event):        
        '''Mouse left click rate of progress'''
        if self.mp:
            if 1 == self.mp.state:
                self.mp.seek(int(self.progressbar.pos))
                self.progressbar.set_pos(self.progressbar.pos)
                self.progressbar.drag_bool = True
                
    def progressbar_player_drag_pos_modify(self, widget, event):        
        '''Set player rate of progress.'''
        if self.progressbar.drag_bool: # Mouse left.
            if self.mp:
                if 1 == self.mp.state:
                    self.mp.seek(int(self.progressbar.pos))
                    
    def get_time_length(self, mplayer, length):        
        '''Get mplayer length to max of progressbar.'''
        self.progressbar.max = length
        self.mp.fseek(500)
        
    def get_time_pos(self, mplayer, pos):    
        '''Get mplayer pos to pos of progressbar.'''
        if not self.progressbar.drag_bool: # 
            if not self.point_bool:
                self.progressbar.set_pos(pos)
            
                
    # Double buffer set.
    def unset_flags(self):
        '''Set double buffer.'''
        self.screen.unset_flags(gtk.DOUBLE_BUFFERED)
        
    def set_flags(self):
        '''Set double buffer.'''
        self.screen.set_flags(gtk.DOUBLE_BUFFERED)    
    
        
    