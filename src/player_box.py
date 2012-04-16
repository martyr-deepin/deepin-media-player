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
from dtk.ui.utils import *
from dtk.ui.label import *

from utils import *
from constant import *
from progressbar import *
from toolbar import *
from toolbar2 import *
from play_control_panel import *
from play_list_button import *
from volume_button import *


class PlayerBox(object):
    def __init__ (self, app, argv_path_list):
        self.input_string = "player_box: " # Test input string(message).
        self.mp = None
        self.point_bool = False
        self.above_bool = False # Set window above bool.
        self.full_bool = False  # Set window full bool.
        self.mode_state_bool = False # Concise mode(True) and common mode(False).
        
        self.panel_x = 0
        self.panel_y = 0
        
        self.main_vbox = gtk.VBox()
        self.hbox = gtk.HBox()
        self.vbox = gtk.VBox()
        self.main_vbox_hframe = HorizontalFrame(1)
        self.main_vbox_hframe.add(self.main_vbox)

        '''Save app(main.py)[init app].'''
        self.app = app  
        self.app_width = 0  # Save media player window width.
        self.app_height = 0 # Save media player window height.
        self.argv_path_list = argv_path_list # command argv.
        self.app.window.connect("destroy", self.quit_player_window)
        self.app.window.connect("configure-event", self.app_configure_hide_tool)
        
        '''Screen window init.'''
        self.screen = MplayerView()
        # Screen signal init.
        self.screen.add_events(gtk.gdk.ALL_EVENTS_MASK)
        self.screen.connect_after("expose-event", self.draw_background)
        self.screen.connect("button-press-event", self.move_media_player_window)
        self.screen.connect("motion-notify-event", self.show_and_hide_toolbar)
        self.screen.connect("configure-event", self.configure_hide_tool)
        self.screen.connect("get-xid", self.init_media_player)
        
        
        '''Progressbar Init.'''
        self.progressbar = ProgressBar()
        # Progressbar signal init.
        self.progressbar.pb.connect("motion-notify-event", self.progressbar_player_drag_pos_modify)
        self.progressbar.pb.connect("button-press-event", self.progressbar_player_point_pos_modify)
        self.progressbar.pb.connect("button-release-event", self.progressbar_set_point_bool)
        
        
        '''Toolbar Init.'''
        self.toolbar = ToolBar()        
        self.toolbar.toolbar_full_button.connect("clicked", self.full_play_window)
        self.toolbar.toolbar_common_button.connect("clicked", self.show_window_widget)
        self.toolbar.toolbar_concise_button.connect("clicked", self.hide_window_widget)
        self.toolbar.toolbar_above_button.connect("clicked", self.set_window_above)
        
        # Child widget add to vbox.
        self.vbox.pack_start(self.screen, True, True)
        self.vbox.pack_start(self.progressbar.hbox,False, False)
        # Hide playlist and show playlist widget hbox.
        self.hbox.pack_start(self.vbox)


        '''Bottom control.'''
        # Hide Bottom and show Bottom.
        self.bottom_main_vbox = gtk.VBox()
        # Play control panel. stop,next,start(pause),pre button.
        bottom_padding = 2
        self.bottom_play_control_hbox_vframe = VerticalFrame(bottom_padding)
        self.bottom_play_control_hbox = gtk.HBox()
        self.bottom_play_control_hbox_vframe.add(self.bottom_play_control_hbox)
        
        # Show time widget.
        # padding=0, xalign=1, yalign=0.0, xscale=0.0, yscale=0.0
        self.show_time_label_hframe = HorizontalFrame()
        self.show_time_label = ShowTime()
        self.show_time_label.time_box.set_size_request(110, -1)
        self.show_time_label.time_font1 = "00 : 00 : 00 "
        self.show_time_label.time_font2 = " / 00 : 00 : 00"
        self.show_time_label_hframe.add(self.show_time_label.time_box)
        self.show_time_label_hframe.set(0, 0.5, 0, 0)
        
        self.play_control_panel = PlayControlPanel()
        self.play_control_panel_hframe = self.play_control_panel.hbox_hframe
        self.play_control_panel_hframe.set(1, 0.5, 0, 0)
        
        self.play_control_panel.stop_btn.connect("clicked", self.stop_button_clicked) # stop play.
        self.play_control_panel.pre_btn.connect("clicked", self.pre_button_clicked) # pre play.
        self.play_control_panel.start_btn.connect("clicked", self.start_button_clicked) # start play or pause play.
        self.play_control_panel.next_btn.connect("clicked", self.next_button_clicked) # next play.
        
        
        # Volume button.
        self.volume_button_hframe = HorizontalFrame()
        self.volume_button = VolumeButton()
        self.volume_button_hframe.add(self.volume_button)
        self.volume_button_hframe.set(1, 0.5, 0, 0)
        self.volume_button_hframe.set_padding(0, 0, 0, 10)
        
        self.volume_button.button_event.connect("button-press-event", self.volume_button_set_mute)
        self.volume_button.connect("get-value-event", self.volume_button_set_volume)
        
        
        # play list button.
        self.play_list_button_hframe = HorizontalFrame()
        self.play_list_button = PlayListButton()
        self.play_list_button_hframe.add(self.play_list_button.button)
        self.play_list_button_hframe.set(1, 0, 0, 0)
        self.play_list_button_hframe.set_padding(0, 0, 0, 10)
        
        
        self.bottom_play_control_hbox.pack_start(self.show_time_label_hframe, False, False)
        self.bottom_play_control_hbox.pack_start(self.play_control_panel_hframe, True, True)
        self.bottom_play_control_hbox.pack_start(self.volume_button_hframe, True, True)
        self.bottom_play_control_hbox.pack_start(self.play_list_button_hframe, False, False)
        

        self.bottom_main_vbox.pack_start(self.bottom_play_control_hbox_vframe)
        # vbox add to main_hbox
        self.main_vbox.pack_start(self.hbox, True, True) # screen and progressbar        
        self.main_vbox.pack_start(self.bottom_main_vbox, False, False)
        
        
    '''play control panel.'''    
    def stop_button_clicked(self, widget):
        self.mp.quit()
        
    def pre_button_clicked(self, widget):
        '''prev.'''
        self.mp.pre()
        
    def start_button_clicked(self, widget):    
        '''start or pause'''            
        if 0 == self.mp.state:    
            self.mp.next() # Test pause.
            self.play_control_panel.start_btn.start_bool = False
            self.play_control_panel.start_btn.queue_draw()
        else:    
            if self.mp.pause_bool:    
                # Puase play ->seek +1.
                self.mp.seek(self.progressbar.pos+1)
                self.mp.start_play()
            else:    
                self.mp.pause()
            
    def next_button_clicked(self, widget):    
        '''next'''
        self.mp.next()
        
    def volume_button_set_mute(self, widget, event):    
        '''Set mute.'''
        if 1 == event.button:
            if self.mp:
                if self.volume_button.mute_bool:
                    self.mp.nomute()
                else:
                    self.mp.offmute()

            
    def volume_button_set_volume(self, volume_button, value, mute_bool):
        if self.mp:
            self.mp.setvolume(value)

                
    def show_bottom(self):        
        if [] == self.bottom_main_vbox.get_children():
            self.bottom_main_vbox.add(self.bottom_play_control_hbox_vframe)
        
    def hide_bottom(self):   
        if [] != self.bottom_main_vbox.get_children():
            self.bottom_main_vbox.foreach(self.bottom_main_vbox.remove(self.bottom_play_control_hbox_vframe))
        
        
    '''Init media player.'''        
    def init_media_player(self, mplayer, xid):    
        '''Init deepin media player.'''
        self.screen.queue_draw()
        #self.unset_flags()
        self.mp = Mplayer(xid)
        self.mp.connect("get-time-pos", self.get_time_pos)
        self.mp.connect("get-time-length", self.get_time_length)
        self.mp.connect("play-start", self.media_player_start)
        self.mp.connect("play-end", self.media_player_end)
        self.mp.connect("play-next", self.media_player_next)
        self.mp.connect("play-pre", self.media_player_pre)
        
        #self.mp.play("/home/long/视频/1.rmvb")
        #self.mp.seek(500)
        #self.mp.scrot(10)
        
        self.mp.playListState = 2
        print self.argv_path_list
        try:
            self.mp.addPlayFile(self.argv_path_list[1])
            #path_threads(self.argv_path_list[1], self.mp)
        except:
            print "没有测试用的文件夹:Test command: python main.py /home/long/视频"
        
    def draw_background(self, widget, event):
        '''Draw screen mplayer view background.'''
        cr, x, y, w, h = allocation(widget)
        
        if self.mp:
            if (self.mp.state) and (self.mp.vide_bool): # vide file.
                if self.mp.pause_bool: # vide pause.
                    # Draw pause background.
                    return False                
                else:
                    return False
        # if no player vide file or no player.    
        cr.set_source_rgb(0, 0, 0)
        cr.rectangle(0, 0, w, h)
        cr.fill()                                                
        return True
            
        
    def quit_player_window(self, widget):
        '''Quit player window.'''
        self.app.window.set_opacity(0)
        self.app.window.set_visible(True)
        if self.mp:
            # Quit deepin-media-player.
            self.mp.quit()
            
            
    # ToolBar control function.        
    def app_configure_hide_tool(self, widget, event): #app: configure-event.    
        self.toolbar.panel.hide_all()
        self.panel_x, self.panel_y = self.screen.window.get_root_origin()
        if self.mode_state_bool: # Concise mode.
            self.toolbar.panel.move(self.panel_x, self.panel_y)
        else:    # common mode.
            self.toolbar.panel.move(self.panel_x + 1, self.panel_y + self.app.titlebar.box.allocation[3])
        
        
    def time_vide_pause_draw_background(self):        
        '''configure_hide_tool call, pause time.'''
        self.mp.pause()
        #self.mp.seek(int(self.progressbar.pos - 2))
        self.mp.pause()
        return False        
    
    def configure_hide_tool(self, widget, event):       
        if self.mp:
            #self.app.hide_titlebar() # Test hide titlebar.
            # Toolbar position.
            if self.mp.pause_bool and self.mp.vide_bool:
                self.mp.pause()
                self.mp.pause()
                #gtk.timeout_add(500, self.time_vide_pause_draw_background)
                
            #self.toolbar.panel.move(self.panel_x, self.panel_y)
            # Toolbar width and height.
            self.toolbar.panel.resize(widget.allocation[2],
                                      widget.allocation[3])
            self.toolbar.panel.hide_all()
            
            # if widget.window.get_state() == gtk.gdk.WINDOW_STATE_MAXIMIZED:
            
    '''Toolbar button.''' 
    def common_window_function(self):
        '''quit fll window and common window'''
        self.app.show_titlebar() # show titlebar.
        self.progressbar.show_progressbar()
        
        
        self.main_vbox_hframe.set_padding(0, 0, 1, 1)
        self.toolbar.panel.hide_all()
        self.show_bottom()
        self.app.window.show_all()
        
    def concise_window_function(self):        
        '''full window and concise mode'''
        self.app.hide_titlebar() # hide titlbar.       
        self.progressbar.hide_progressbar()
        self.hide_bottom()
        
        #self.app.window.set_keep_above(True) # Window above.
        self.main_vbox_hframe.set_padding(0, 0, 0, 0) # Set window border.
        self.toolbar.panel.hide_all() # hide toolbar.
        
    def set_window_full(self):    
        self.concise_window_function()
        self.toolbar.panel.fullscreen()  # Toolbar hide.
        #self.app.window.set_keep_above(True)
        self.toolbar.panel.set_keep_above(True)
        self.app.window.fullscreen()        
        self.full_bool = True            
        
    def set_window_quit_full(self):    
        self.toolbar.panel.unfullscreen()
        self.app.window.unfullscreen()
        self.common_window_function()
        self.full_bool = False
        
    def full_play_window(self, widget): #full_button       
        '''Full player window.'''
        if not self.full_bool: # Full player window.
            self.set_window_full()
        else:    
            self.set_window_quit_full()
            if self.mode_state_bool:
                self.concise_window_function()
            else:    
                self.common_window_function()
            
            
    def show_hide_set(self):    
        '''show_window_widget and hide_window_widget'''
        self.app.window.unfullscreen()
        self.toolbar.panel.unfullscreen()  # Toolbar hide.
        self.full_bool = False
            
    def show_window_widget(self, widget): #common_button         
        '''Show window titlebar of window and play control panel.
           Show progressbar.
           Show playlist.
           Show window border.
           [common mode:]
        '''
        if self.mode_state_bool:
            self.common_window_function()
            self.mode_state_bool = False
            
            
        if self.full_bool: # qiut full.   
            self.show_bottom()
            self.progressbar.show_progressbar()
            self.app.show_titlebar()
            self.show_hide_set()
            
    def hide_window_widget(self, widget): #concise_button    
        '''Hide widnow titlebar and play control panel.
           Hide progressbar.
           Hide playlist.
           Hide border of window.
           [concise mode:]
        '''
        if self.full_bool:
            self.show_hide_set()
        
        if not self.mode_state_bool:
            self.concise_window_function()
            self.app.window.set_window_shape(False)
            #self.app.window.set_window_shape(True)
            self.mode_state_bool = True
            
            
    def set_window_above(self, widget): #above_button   
        self.above_bool = not self.above_bool
        self.app.window.set_keep_above(self.above_bool)
        
            
        
    # Control mplayer window.        
    def move_media_player_window(self, widget, event): # screen: button-press-event         
        '''Move window.'''
        if 1 == event.button:
            self.app.window.begin_move_drag(event.button,
                                            int(event.x_root),
                                            int(event.y_root),
                                            event.time)
        # Double clicked full.    
        if is_double_click(event):
            self.full_play_window(widget)    
            self.toolbar.toolbar_full_button.flags = not self.toolbar.toolbar_full_button.flags
            
            
    # Toolbar hide and show.    
    def show_and_hide_toolbar(self, widget, event): # screen:motion_notify_event   
        '''Show and hide toolbar.'''    
        if 0 <= event.y <= 20:
            self.toolbar.show_toolbar()
        else:
            self.toolbar.hide_toolbar()            
                                
            
    # Mplayer event of player control.         
    def set_point_bool_time(self):        
        self.point_bool = False
        return False
    
    def progressbar_set_point_bool(self, widget, event):
        gtk.timeout_add(20, self.set_point_bool_time)
            
    def progressbar_player_point_pos_modify(self, widget, event):        
        '''Mouse left click rate of progress'''
        if self.mp:
            if 1 == self.mp.state:
                self.mp.seek(int(self.progressbar.pos))
                self.progressbar.set_pos(self.progressbar.pos)
                self.progressbar.drag_bool = True
                self.point_bool = True
                
    def progressbar_player_drag_pos_modify(self, widget, event):        
        '''Set player rate of progress.'''
        if self.progressbar.drag_bool: # Mouse left.
            if self.mp:
                if 1 == self.mp.state:
                    self.mp.seek(int(self.progressbar.pos))
                    
                    
    def get_time_length(self, mplayer, length):        
        '''Get mplayer length to max of progressbar.'''
        self.progressbar.max = length
        
        
    def get_time_pos(self, mplayer, pos):    
        '''Get mplayer pos to pos of progressbar.'''
        # Test media player pos.
        #print pos
        if not self.progressbar.drag_bool: # 
            if not self.point_bool:
                self.progressbar.set_pos(pos)
            
    def media_player_start(self, mplayer, play_bool):
        '''media player start play.'''
        self.progressbar.set_pos(0)
    
    def media_player_end(self, mplayer, play_bool):
        '''player end.'''
        print self.input_string + "Linux Deepin Media player...end"        
       # Play file modify start_btn.
        self.media_player_midfy_start_bool()

    def media_player_next(self, mplayer, play_bool):    
        self.media_player_midfy_start_bool()
        
    def media_player_pre(self, mplayer, play_bool):    
        self.media_player_midfy_start_bool()

    def media_player_midfy_start_bool(self):    
        self.progressbar.set_pos(0)
        self.screen.queue_draw()        
        self.play_control_panel.start_btn.start_bool = True
        self.play_control_panel.start_btn.queue_draw()
        
    # Double buffer set.
    def unset_flags(self):
        '''Set double buffer.'''
        self.screen.unset_flags(gtk.DOUBLE_BUFFERED)
        
    def set_flags(self):
        '''Set double buffer.'''
        self.screen.set_flags(gtk.DOUBLE_BUFFERED)    
    
        
    
