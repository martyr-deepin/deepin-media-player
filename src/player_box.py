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

# from dtk.ui.dragbar import Dragbar
# from dtk.ui.mplayer_view import MplayerView
from dtk.ui.box import EventBox
from dtk.ui.frame import HorizontalFrame,VerticalFrame
from dtk.ui.utils import is_double_click
from dtk.ui.menu import Menu

from utils import allocation,path_threads
from show_time import ShowTime
from progressbar import ProgressBar
from toolbar import ToolBar
from toolbar2 import ToolBar2
from play_control_panel import PlayControlPanel
from play_list_button import PlayListButton
from volume_button import VolumeButton
from drag import drag_connect
from preview import PreView
from mplayer import Mplayer
from mplayer import get_vide_width_height
from mplayer import get_length
from mplayer import get_home_path
from mplayer import length_to_time
from playlist import PlayList
from playlist import MediaItem
from opendialog import OpenDialog
from tooltip import Tooltip
# from popup_menu import PopupMenu

from ini import INI
import threading
import gtk
import os



class PlayerBox(object):
    def __init__ (self, app, argv_path_list):
        # signal and double.
        self.double_bool = False
        self.signal_timeout = []
        
        self.input_string = "player_box: " # Test input string(message).
        self.mp = None
        self.point_bool = False
        self.above_bool = False # Set window above bool.
        self.full_bool = False  # Set window full bool.
        self.mode_state_bool = False # Concise mode(True) and common mode(False).
        
        self.clear_play_list_bool = False # drag play file.
        
        # ini play memory.
        self.ini = INI(get_home_path() + "/.config/deepin-media-player/config.ini")
        self.ini.start()
        
        # screen draw borde video width and height.        
        #get_vide_width_height (function return value)
        self.video_height = 0
        self.video_width = 0
        
        # playlist.
        self.add_play_list_length_id = None
        self.show_or_hide_play_list_bool = False
        # Preview window.
        self.x_root = 0
        self.y_root = 0
        self.show_bool = False
        self.show_id = None
        self.read_id = None
        
        self.save_volume_mute_bool = False
        self.save_volume_value = 0

        # Screen move window.
        self.event_button = None
        self.event_x_root = None
        self.event_y_root = None
        self.event_time = None
        self.screen_move_bool = False
        self.screen_pause_bool = False

        self.panel_x = 0
        self.panel_y = 0

        self.main_vbox = gtk.VBox()
        self.hbox = gtk.HBox()
        self.vbox = gtk.VBox()
        self.main_vbox_hframe = HorizontalFrame(1)
        self.main_vbox_hframe.add(self.main_vbox)

        '''play list popup menu'''
        self.menu = Menu([(None, "单个播放", self.sigle_play),      # 0
                          (None, "顺序播放", self.sequence_play),   # 1
                          (None, "随机播放", self.rand_play),       # 2
                          (None, "单个循环", self.sigle_loop_play), # 3
                          (None, "列表循环", self.loop_list_play)]  # 4
                         ) 
                                        
        self.menu2 = Menu([(None, "按名称", self.name_sort),
                           (None, "按类型", self.type_sort)])
        
        self.root_menu = Menu([(None, "添加文件", self.add_file), 
                               (None, "添加文件夹", self.add_file_dir),
                               (None),
                               (None, "删除选中项", self.del_index),
                               (None, "清空播放列表", self.clear_list),
                               (None, "删除无效文件", self.del_error_file),
                               (None),
                               (None, "播放顺序", self.menu),                               
                               (None, "排序", self.menu2),
                               (None),
                               (None, "打开所在文件夹", self.open_current_file_dir)
                               ], 
                              True)                        
                    
        
        '''Tooltip window'''
        self.tooltip = Tooltip("深度影音", 0, 0)
        
        '''Preview window'''
        self.preview = PreView()
        
        '''Save app(main.py)[init app].'''
        self.app = app
        self.app_width = 0  # Save media player window width.
        self.app_height = 0 # Save media player window height.
        self.argv_path_list = argv_path_list # command argv.
        self.app.window.connect("destroy", self.quit_player_window)
        self.app.window.connect("configure-event", self.app_configure_hide_tool)
        self.app.window.connect("window-state-event", self.set_toolbar2_position)
        #keyboard Quick key.
        # self.app.window.connect("realize", gtk.Widget.grab_focus)
        # self.app.window.connect("key-press-event", self.get_key_event)
                
        '''Screen window init.'''
        self.screen = gtk.DrawingArea()
        
        # Screen signal init.
        self.screen.add_events(gtk.gdk.ALL_EVENTS_MASK)
        # drag resize window.
        self.screen.connect("realize", self.init_media_player)
        self.screen.unset_flags(gtk.DOUBLE_BUFFERED) # disable double buffered to avoid video blinking
        
        # Handle signal.
        # self.connect("realize", self.realize_mplayer_view)

        self.screen.connect("key-press-event", self.get_key_event)
        self.screen.connect("button-press-event", self.drag_resize_window)
        self.screen.connect("motion-notify-event", self.modify_mouse_icon)
        
        self.screen.connect_after("expose-event", self.draw_background)
        self.screen.connect("button-press-event", self.move_media_player_window)
        self.screen.connect("button-release-event", self.screen_media_player_clear)
        self.screen.connect("motion-notify-event", self.show_and_hide_toolbar)
        self.screen.connect("configure-event", self.configure_hide_tool)
        # self.screen.connect("get-xid", self.init_media_player)


        '''Progressbar Init.'''
        self.progressbar = ProgressBar()
        # Progressbar signal init.
        self.progressbar.pb.connect("motion-notify-event", self.progressbar_player_drag_pos_modify, self.progressbar, 1)
        self.progressbar.pb.connect("button-press-event", self.progressbar_player_point_pos_modify, self.progressbar, 1)
        self.progressbar.pb.connect("button-release-event", self.progressbar_set_point_bool, self.progressbar)
        
        self.progressbar.pb.connect("enter-notify-event", self.show_preview_enter)
        self.progressbar.pb.connect("leave-notify-event", self.hide_preview_leave)        
        
        '''Toolbar Init.'''
        self.toolbar = ToolBar()        
        self.toolbar.toolbar_full_button.connect("clicked", self.full_play_window)
        self.toolbar.toolbar_common_button.connect("clicked", self.show_window_widget)
        self.toolbar.toolbar_concise_button.connect("clicked", self.hide_window_widget)
        self.toolbar.toolbar_above_button.connect("clicked", self.set_window_above)

        '''Toolbar2 Init.'''
        self.toolbar2 = ToolBar2()        
        self.toolbar2.panel.set_size_request(1, 40) # Set toolbar2 height.
        # draw resize window.
        self.toolbar2.panel.connect("button-press-event", self.drag_resize_window)
        self.toolbar2.panel.connect("motion-notify-event", self.modify_mouse_icon)
        
        self.toolbar2.panel.connect("motion-notify-event", self.set_keep_window_toolbar2)
        #self.toolbar2.show_toolbar2() Test function.
        self.toolbar2.progressbar.pb.connect("motion-notify-event",
                                             self.progressbar_player_drag_pos_modify,
                                             self.toolbar2.progressbar, 2)
        self.toolbar2.progressbar.pb.connect("button-press-event",
                                             self.progressbar_player_point_pos_modify,
                                             self.toolbar2.progressbar, 2)
        self.toolbar2.progressbar.pb.connect("button-release-event",
                                             self.progressbar_set_point_bool,
                                             self.toolbar2.progressbar)
        self.toolbar2.progressbar.pb.connect("enter-notify-event", self.show_preview_enter)
        self.toolbar2.progressbar.pb.connect("leave-notify-event", self.hide_preview_leave)        
        
        # play_control_panel.
        self.toolbar2.play_control_panel.stop_btn.connect("clicked", self.stop_button_clicked)
        self.toolbar2.play_control_panel.pre_btn.connect("clicked", self.pre_button_clicked)
        self.toolbar2.play_control_panel.start_btn.connect("clicked", self.start_button_clicked, 2)
        self.toolbar2.play_control_panel.next_btn.connect("clicked", self.next_button_clicked)


        # Toolbar2 volume button.
        self.toolbar2.volume_button.button_event.connect("button-press-event",
                                                         self.toolbar2_volume_button_set_mute)
        self.toolbar2.volume_button.connect("get-value-event",
                                            self.toolbar2_volume_button_set_volume)
                        
        
        # Child widget add to vbox.
        self.vbox.pack_start(self.screen, True, True)
        self.vbox.pack_start(self.progressbar.hbox,False, False)
        # Hide playlist and show playlist widget hbox.
        self.hbox.pack_start(self.vbox, True, True)
        
        
        '''playlist'''
        # self.media_item = []                
        # self.playlist.list_view.add_items(self.media_item)
        self.play_list_dict = {} # play list dict type.
        self.play_list = PlayList()                    
        self.play_list.list_view.connect("key-press-event", self.get_key_event)
        self.play_list.list_view.connect("double-click-item", self.double_play_list_file)
        self.play_list.list_view.connect("delete-select-items", self.delete_play_list_file)
        self.play_list.list_view.connect("button-press-event", self.show_popup_menu)
        self.hbox.pack_start(self.play_list.vbox, False, False)
        
        
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
        self.show_time_label.time_font1 = "00 : 00 : 00  "
        self.show_time_label.time_font2 = "  / 00 : 00 : 00"
        self.show_time_label_hframe.add(self.show_time_label.time_box)
        self.show_time_label_hframe.set(0, 0.5, 0, 0)
        
        self.play_control_panel = PlayControlPanel()
        
        self.play_control_panel_hframe = self.play_control_panel.hbox_hframe
        self.play_control_panel_hframe.set(1, 0.5, 0, 0)
        
        self.play_control_panel.stop_btn.connect("clicked", self.stop_button_clicked) # stop play.
        self.play_control_panel.pre_btn.connect("clicked", self.pre_button_clicked) # pre play.
        self.play_control_panel.start_btn.connect("clicked", self.start_button_clicked, 1) # start play or pause play.
        self.play_control_panel.next_btn.connect("clicked", self.next_button_clicked) # next play.
        self.play_control_panel.open_btn.connect("clicked", self.open_button_clicked) # show open window.
        
        
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
        # play_list_button connect signal.
        self.play_list_button.button.connect("clicked", self.play_list_button_clicked)
        self.play_list_button_hframe.add(self.play_list_button.button)
        self.play_list_button_hframe.set(1, 0, 0, 0)
        self.play_list_button_hframe.set_padding(0, 0, 0, 10)


        self.bottom_play_control_hbox.pack_start(self.show_time_label_hframe, False, False)
        self.bottom_play_control_hbox.pack_start(self.play_control_panel_hframe, True, True)
        self.bottom_play_control_hbox.pack_start(self.volume_button_hframe, True, True)
        self.bottom_play_control_hbox.pack_start(self.play_list_button_hframe, False, False)
                
        self.bottom_play_control_hbox_vframe_event_box = EventBox()
        self.bottom_play_control_hbox_vframe_event_box.add_events(gtk.gdk.ALL_EVENTS_MASK)
        self.bottom_play_control_hbox_vframe_event_box.add(self.bottom_play_control_hbox_vframe)
        # draw resize window.
        self.bottom_play_control_hbox_vframe_event_box.connect("button-press-event", self.drag_resize_window)
        self.bottom_play_control_hbox_vframe_event_box.connect("motion-notify-event", self.modify_mouse_icon)

        self.bottom_main_vbox.pack_start(self.bottom_play_control_hbox_vframe_event_box)
        # vbox add to main_hbox
        self.main_vbox.pack_start(self.hbox, True, True) # screen and progressbar
        self.main_vbox.pack_start(self.bottom_main_vbox, False, False)
        
        '''Hide preview window.'''                        
        self.bottom_play_control_hbox_vframe_event_box.connect("motion-notify-event", self.hide_preview_function)
        
                
        
    def MessageBox(self, text):    
        x, y = self.screen.window.get_root_origin()
        self.app.window.set_keep_above(True)        
        if self.full_bool or self.mode_state_bool:
            self.tooltip.show_tooltip(text, x + 5, y + 5)
        else:    
            self.tooltip.show_tooltip(text, x + 5, y + 30)
        self.tooltip.set_keep_above(True)    
        
        
    def modify_mouse_icon(self, widget, event): # screen: motion-notify-event 
        w = widget.allocation.width
        h = widget.allocation.height
        # right_padding = 5
        bottom_padding = 5
        drag_bool = False
        
        if "MplayerView" == type(widget).__name__: 
            try:
                self.bottom_play_control_hbox_vframe_event_box.window.set_cursor(None)
            except:    
                pass
            
        # if (w - right_padding <= event.x <= w) and (right_padding <= event.y <= h - right_padding): #Right
        #     drag = gtk.gdk.RIGHT_SIDE
        #     drag_bool = True            
        # elif (0 <= event.x <= right_padding) and (right_padding <= event.y <= h - right_padding):  #left  
        #     drag = gtk.gdk.LEFT_SIDE
        #     drag_bool = True
        # elif (bottom_padding <= event.x <= w - bottom_padding) and (h - bottom_padding <= event.y <= h): # bottom                
        #     drag = gtk.gdk.BOTTOM_SIDE
        #     if "MplayerView" != type(widget).__name__: 
        #         drag_bool = True
        #     else:    
        #         drag_bool = False
        # elif (0 <= event.x <= bottom_padding) and (h - bottom_padding <= event.y <= h):                
        #     if "MplayerView" != type(widget).__name__:
        #         drag = gtk.gdk.BOTTOM_LEFT_CORNER
        #         drag_bool = True
        #     else:
        #         drag_bool = False
        if (w - bottom_padding <= event.x <= w) and (h - bottom_padding <= event.y <= h):
            if "MplayerView" != type(widget).__name__:
                drag = gtk.gdk.BOTTOM_RIGHT_CORNER
                drag_bool = True
            else:
                drag_bool = False
        # MplayerView   EventBox Panel

        if drag_bool:    
            widget.window.set_cursor(gtk.gdk.Cursor(drag))
        else:    
            widget.window.set_cursor(None)    
            
        
    def drag_resize_window(self, widget, event): # screen: button-press-event -> drag resize window.
        w = widget.allocation.width
        h = widget.allocation.height
        # left_padding = 5
        bottom_padding = 5
        drag_bool = False
        
        # if (w - left_padding <= event.x <= w) and (left_padding <= event.y <= h - left_padding): # Right
        #     drag = gtk.gdk.WINDOW_EDGE_EAST
        #     drag_bool = True                        
        # elif (0 <= event.x <= 20) and (left_padding <= event.y <= h - left_padding): # Left
        #     drag = gtk.gdk.WINDOW_EDGE_WEST
        #     drag_bool = True            
        # elif (bottom_padding <= event.x <= w - bottom_padding) and (h - bottom_padding <= event.y <= h):    
        #     drag = gtk.gdk.WINDOW_EDGE_SOUTH
        #     if "MplayerView" != type(widget).__name__: 
        #         drag_bool = True            
        #     else:    
        #         drag_bool = False
        # elif (0 <= event.x <= bottom_padding) and (h - bottom_padding <= event.y <= h):        
        #     if "MplayerView" != type(widget).__name__: 
        #         drag = gtk.gdk.WINDOW_EDGE_SOUTH_WEST
        #         drag_bool = True            
        #     else:    
        #         drag_bool = False            
        if (w - bottom_padding <= event.x <= w) and (h - bottom_padding <= event.y <= h):        
            if "MplayerView" != type(widget).__name__: 
                drag = gtk.gdk.WINDOW_EDGE_SOUTH_EAST
                drag_bool = True            
            else:    
                drag_bool = False           
                
        if drag_bool:    
            self.app.window.begin_resize_drag(drag,
                                              event.button,
                                              int(event.x_root),
                                              int(event.y_root),
                                              event.time)
        
    def get_key_event(self, widget, event): # app: key-release-event       
        keyval = event.keyval                
        unicode_key = gtk.gdk.keyval_name(keyval)        
        self.control_player(unicode_key, widget, event)
        return True
        
    def control_player(self, keyval, widget, event):    
        # print keyval
        if self.mp:
            if "Right" == keyval:
                self.mp.seek(self.mp.posNum + 10)
            elif "Left" == keyval:    
                self.mp.seek(self.mp.posNum - 10)
            elif "space" == keyval:    
                self.virtual_set_start_btn_clicked()
            elif "Return" == keyval:    
                self.full_play_window(widget)
                self.toolbar.toolbar_full_button.flags = not self.toolbar.toolbar_full_button.flags
                
        
        
    '''play list button'''    
    def play_list_button_clicked(self, widget): # play list button signal:clicked.           
        if True == self.play_list_button.button.flags: 
            self.app.window.resize(self.app.window.allocation.width + self.play_list.play_list_width,
                                   self.app.window.allocation.height)
            self.play_list.show_play_list()
            self.show_or_hide_play_list_bool = True
            
        if False == self.play_list_button.button.flags:    
            self.app.window.resize(self.app.window.allocation.width - self.play_list.play_list_width,
                                   self.app.window.allocation.height)
            self.play_list.hide_play_list()
            self.show_or_hide_play_list_bool = False
                    
        
    '''Play list control'''     
    def delete_play_list_file(self, list_view, list_item):
        # delete file of play list.
        play_list_dict_save = self.play_list_dict
        for list_item_i in list_item:
            # print play_list_dict_save[list_item_i.title]
            self.mp.delPlayList(play_list_dict_save[list_item_i.title])
            # del self.play_list_dict[list_item_i.title]                    
            
            
    def add_play_list(self, mplayer, path): # mplayer signal: "add-path"                       
        '''Play list add play file timeout.[100-1028 a play file].'''            
        if self.add_play_list_length_id:
            gtk.timeout_remove(self.add_play_list_length_id)
            self.add_play_list_length_id = None
            
        if not self.add_play_list_length_id:    
            self.add_play_list_length_id = gtk.timeout_add(2000, self.add_play_list_length)    
        
        gtk.timeout_add(10, self.add_play_list_time, path)
        
        
    def add_play_list_length(self):    
        '''staring length show.[add length]'''
        path_thread_id = threading.Thread(target=self.length_threads)
        path_thread_id.start()
        return False
        
    def length_threads(self):
        '''Get length threads'''
        for i in self.play_list.list_view.items:             
            length = self.ini.get_section_value("PlayTime", i.title)
            if length:
                i.length = length_to_time(length)
            else:    
                i.length, length = get_length(self.play_list_dict[i.title])            
                root = self.ini.get_section("PlayTime")
                try:
                    root.child_addr[i.title] = length
                except:    
                    length = 10
            i.emit_redraw_request()
            
        self.ini.ini_save()    
        
    def add_play_list_time(self, path): # all.   
        '''play list add play file.'''
        self.play_list_dict[self.get_player_file_name(path)] = path
        media_item = [MediaItem(self.get_player_file_name(path), str("        "))]                
        self.play_list.list_view.add_items(media_item)                
        
        if self.clear_play_list_bool:
            self.clear_play_list_bool = False
            if 1 == self.mp.state:
                self.mp.quit()
            self.start_button_clicked(self.play_control_panel.start_btn, 1)    
            # self.mp.play(self.mp.playList[0])
            # self.mp.playListNum += 1    
            self.play_list.list_view.set_highlight(self.play_list.list_view.items[0])        
        return False        
    
    def double_play_list_file(self, list_view, list_item, colume, offset_x, offset_y):     
        '''double play file.'''
        if self.mp:
            if 1 == self.mp.state:                
                self.mp.quit()                                        
                
        # play file.        
        # self.start_button_clicked(self.play_control_panel.start_btn, 1)                    
        self.mp.play(self.play_list_dict[list_item.title])
        self.mp.playListNum = list_item.get_index()           

        self.play_control_panel.start_btn.start_bool = False
        self.play_control_panel.start_btn.queue_draw()
        self.toolbar2.play_control_panel.start_btn.start_bool = False
        self.toolbar2.play_control_panel.start_btn.queue_draw()

                
        self.play_list.list_view.set_highlight(list_item)    

        
    def hide_preview_function(self, widget, event):    
        '''Hide preview window.'''
        self.preview.hide_preview()
        self.hide_preview_leave(widget, event)
        
    '''play control panel.'''
    def stop_button_clicked(self, widget):
        self.mp.quit()

    def pre_button_clicked(self, widget):
        '''prev.'''
        self.mp.pre()

    def start_button_clicked(self, widget, start_bit):
        '''start or pause'''
        if 0 == self.mp.state:
            self.mp.next() # Test pause.
            self.play_control_panel.start_btn.start_bool = False
            self.play_control_panel.start_btn.queue_draw()
            self.toolbar2.play_control_panel.start_btn.start_bool = False
            self.toolbar2.play_control_panel.start_btn.queue_draw()
            self.MessageBox("播放")
            if 0 == self.mp.state: # NO player file.
                self.MessageBox("没有可播放的文件")
                self.play_control_panel.start_btn.start_bool = True # start_btn modify play state.
                self.play_control_panel.start_btn.queue_draw()
                self.toolbar2.play_control_panel.start_btn.start_bool = True
                self.toolbar2.play_control_panel.start_btn.queue_draw()
        else:
            if 1 == start_bit:
                self.toolbar2.play_control_panel.start_btn.start_bool = self.play_control_panel.start_btn.start_bool
                self.toolbar2.play_control_panel.start_btn.queue_draw()
            if 2 == start_bit:
                self.play_control_panel.start_btn.start_bool = self.toolbar2.play_control_panel.start_btn.start_bool
                self.play_control_panel.start_btn.queue_draw()

            gtk.timeout_add(300, self.start_button_time_pause)

    def start_button_time_pause(self): # start_button_clicked.
        if self.mp.pause_bool:
            self.MessageBox("播放")
            self.mp.seek(int(self.progressbar.pos))
            self.mp.start_play()
        else:
            self.MessageBox("暂停")
            self.mp.pause()
        return  False

    def next_button_clicked(self, widget):
        '''next'''
        self.mp.next()

    def open_button_clicked(self, widget):    
        # open window.
        open_dialog = OpenDialog()        
        open_dialog.show_dialog()
        open_dialog.connect("get-path-name", self.test_open)

        
    def test_open(self, open_dialog, path_name):
        if len(path_name) > 0:
            # self.mp.addPlayFile(path_name)    
            # # self.mp.playList.append(path_name)
            # # self.mp.playListNum += 1
            # self.clear_play_list_bool = True
            # self.add_play_list_time(path_name)            
            pass
            # if 1 == self.mp.state:
            #     self.mp.quit()
            # self.start_button_clicked(self.play_control_panel.start_btn, 1)    
            # self.play_list
            # self.play_list.list_view.set_highlight(self.play_list.list_view.items[0])        
            
    def volume_button_set_mute(self, widget, event):
        '''Set mute.'''
        if 1 == event.button:
            if 1 == self.mp.state:
                if self.volume_button.mute_bool:
                    self.mp.nomute()
                else:
                    self.mp.offmute()
                        
    def volume_button_set_volume(self, volume_button, value, mute_bool):
        if self.mp:
            self.mp.setvolume(value)            
                
            self.save_volume_mute_bool = mute_bool
            self.save_volume_value = value

    def toolbar2_volume_button_set_mute(self, widget, event):
        '''Set mute.'''
        if 1 == event.button:
            if 1 == self.mp.state:
                if self.toolbar2.volume_button.mute_bool:
                    self.mp.nomute()
                else:
                    self.mp.offmute()

    def toolbar2_volume_button_set_volume(self, volume_button, value, mute_bool):
        if self.mp:
            self.mp.setvolume(value)

            self.save_volume_mute_bool = mute_bool
            self.save_volume_value = value

    def show_bottom(self):
        if [] == self.bottom_main_vbox.get_children():
            self.bottom_main_vbox.add(self.bottom_play_control_hbox_vframe_event_box)

    def hide_bottom(self):
        if [] != self.bottom_main_vbox.get_children():
            self.bottom_main_vbox.foreach(self.bottom_main_vbox.remove(self.bottom_play_control_hbox_vframe_event_box))
                                
    
    '''Init media player.'''
    def init_media_player(self, widget):
        '''Init deepin media player.'''
        
        self.play_list.hide_play_list() # Hide play list.
        
        self.save_volume_value = self.volume_button.volume_value
        self.save_volume_mute_bool = self.volume_button.mute_bool

        self.screen.queue_draw()
        #self.unset_flags()
        self.mp = Mplayer(widget.window.xid)
        # Init darg file signal.
        drag_connect(self.screen, self.mp, self.play_list.list_view, True)
        drag_connect(self.play_list.list_view, self.mp, self.play_list.list_view, False)
        
        self.mp.connect("get-time-pos", self.get_time_pos)
        self.mp.connect("get-time-length", self.get_time_length)
        self.mp.connect("play-start", self.media_player_start)
        self.mp.connect("play-end", self.media_player_end)
        self.mp.connect("play-next", self.media_player_next)
        self.mp.connect("play-pre", self.media_player_pre)
        self.mp.connect("add-path", self.add_play_list)
        self.mp.connect("clear-play-list", self.clear_play_list)
        
        self.mp.playListState = 1 # play mode.
        
        # try:
        # argv path list.
        for file_path in self.argv_path_list:
            if self.mp.findDmp(file_path): # .dmp add play file.
                self.mp.loadPlayList(file_path)
            elif os.path.isfile(file_path): # add play file.
                self.mp.addPlayFile(file_path)
            elif os.path.isdir(file_path): # add dir.
                path_threads(file_path, self.mp)
            self.clear_play_list_bool = True    
            
        # self.play_list.list_view.set_highlight(self.play_list.list_view.items[0])        
        # except:
        #     print "Error:->>Test command: python main.py add file or dir"

    def clear_play_list(self, mplayer, mp_bool):        
        self.play_list.list_view.clear()
        self.play_list_dict = {}
        self.clear_play_list_bool = True
        
    def draw_background(self, widget, event):
        '''Draw screen mplayer view background.'''
        cr, x, y, w, h = allocation(widget)
        
        if self.mp:
            if (self.mp.state) and (self.mp.vide_bool): # vide file.
                if 0 != self.video_width or 0 != self.video_height:                                        
                    video_ratio = float(self.video_width) / self.video_height
                    
                    bit = video_ratio - (float(w) / h)
                    cr.set_source_rgb(0, 0, 0)
                    if 0 == bit:
                        return False
                    elif bit < 0:                             
                        s = w - h * (video_ratio)
                        s = s / 2
                        
                        # Draw left.
                        cr.rectangle(x, y - 50, s - 1, h + 50)
                        cr.fill()
                        
                        # Draw right.
                        cr.rectangle(x + s + h * (self.video_width / self.video_height) -1, y - 50, s - 1, h + 50)
                        cr.fill()
                    elif bit > 0:
                        video_ratio = float(self.video_height) / self.video_width                        
                        s = h - w * video_ratio
                        s = s / 2
                        
                        # Draw UP.                        
                        cr.rectangle(x, y - self.app.titlebar.allocation.height, w , s)
                        cr.fill()
                        
                        # Draw bottom.
                        cr.rectangle(x, y + s + w * (video_ratio) - self.app.titlebar.allocation.height, w, s)
                        cr.fill()
                        
                    return True
            
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
            os.system("kill %s" %(self.mp.mplayer_pid))
            #os.system("pkill mplayer")
            self.mp.quit()
            

    def set_toolbar2_position(self, widget, event):        
        self.toolbar2.show_toolbar2()
        self.toolbar.panel.move(self.panel_x + 1, self.panel_y + self.app.titlebar.allocation[3])
        self.toolbar2.panel.move(self.panel_x + 1, self.panel_y + self.screen.allocation.height - 40)
        self.toolbar2.hide_toolbar2()
        
    # ToolBar control function.
    def app_configure_hide_tool(self, widget, event): #app: configure-event.
        #Set mute and value.
        
        if self.mp:
            self.screen.queue_draw()    
            
        if self.toolbar2.volume_button.mute_bool != self.save_volume_mute_bool:
            self.toolbar2.volume_button.mute_bool = self.save_volume_mute_bool
            self.toolbar2.volume_button.set_value(self.save_volume_value)
        if self.volume_button.mute_bool != self.save_volume_mute_bool:
            self.volume_button.mute_bool = self.save_volume_mute_bool
            self.volume_button.set_value(self.save_volume_value)

        if self.save_volume_mute_bool: 
            self.mp.nomute()

        self.toolbar.panel.hide_all()
        self.panel_x, self.panel_y = self.screen.window.get_root_origin()
        if self.mode_state_bool: # Concise mode.
            self.toolbar.panel.move(self.panel_x, self.panel_y)            
            self.toolbar2.panel.move(self.panel_x, self.panel_y + (widget.allocation[3] - self.toolbar2.panel.allocation[3]))            
        else:    # common mode.            
            self.toolbar.panel.move(self.panel_x + 1, self.panel_y + self.app.titlebar.allocation[3])
            self.toolbar2.panel.move(self.panel_x + 1, self.panel_y + self.screen.allocation.height - 40)
            
        self.set_toolbar_show_opsition()    
            
        # Hide preview window.
        self.hide_preview_function(widget, event)
        
        
    def configure_hide_tool(self, widget, event): # screen: configure-event.
        if self.mp:
            #self.app.hide_titlebar() # Test hide titlebar.
            # Toolbar position.
            if self.mp.pause_bool and self.mp.vide_bool:
                self.mp.pause()
                self.mp.pause()

            #self.toolbar.panel.move(self.panel_x, self.panel_y)
            # Toolbar width and height.
            self.toolbar.panel.resize(widget.allocation[2],
                                      widget.allocation[3])
            self.toolbar.panel.hide_all()
            # if widget.window.get_state() == gtk.gdk.WINDOW_STATE_MAXIMIZED:
            self.toolbar2.panel.resize(widget.allocation[2], 1)
            self.toolbar2.panel.move(self.panel_x, self.panel_y + (widget.allocation[3] - self.toolbar2.panel.allocation[3]))
            self.toolbar2.panel.hide_all()


    '''Toolbar button.'''
    def common_window_function(self):
        '''quit fll window and common window'''
        self.app.show_titlebar() # show titlebar.
        self.progressbar.show_progressbar()

        self.main_vbox_hframe.set_padding(0, 0, 1, 1)
        self.toolbar.panel.hide_all()
        self.toolbar2.panel.hide_all()
        self.show_bottom()
        self.app.window.show_all()

        if self.save_volume_mute_bool:
            self.volume_button.mute_bool = True
        else:    
            self.volume_button.mute_bool = False
            
        # self.volume_button.mute_bool = True if 1 == self.save_volume_mute_bool else False
        self.volume_button.set_value(self.save_volume_value)

    def concise_window_function(self):
        '''full window and concise mode'''
        self.app.hide_titlebar() # hide titlbar.
        self.progressbar.hide_progressbar()
        self.hide_bottom()

        #self.app.window.set_keep_above(True) # Window above.
        self.main_vbox_hframe.set_padding(0, 0, 0, 0) # Set window border.
        self.toolbar.panel.hide_all() # hide toolbar.
        self.toolbar2.panel.hide_all()

        if self.save_volume_mute_bool:
            self.toolbar2.volume_button.mute_bool = True
        else:    
            self.toolbar2.volume_button.mute_bool = False
            
            
        # self.toolbar2.volume_button.mute_bool = True if 1 == self.save_volume_mute_bool else False
        self.toolbar2.volume_button.set_value(self.save_volume_value)

    def set_window_full(self):
        # if True. play list hide.
        if self.show_or_hide_play_list_bool:
            self.play_list.hide_play_list()
        # self.screen.queue_draw()
        self.concise_window_function()
        self.toolbar.panel.fullscreen()  # Toolbar hide.
        #self.toolbar2.panel.fullscreen()
        #self.app.window.set_keep_above(True)
        self.toolbar.panel.set_keep_above(True)
        self.toolbar2.panel.set_keep_above(True)
        self.app.window.fullscreen()
        self.full_bool = True


    def set_window_quit_full(self):
        # # if True. play list show.
        if self.show_or_hide_play_list_bool:
            if not self.mode_state_bool:
                self.play_list.show_play_list()            

        # self.screen.queue_draw()
        self.toolbar.panel.unfullscreen()
        #self.toolbar2.panel.unfullscreen()
        self.app.window.unfullscreen()
        self.common_window_function()
        self.full_bool = False
        


    def full_play_window(self, widget): #full_button
        '''Full player window.'''
        if not self.full_bool: # Full player window.
            self.set_window_full()
            # self.MessageBox("全屏")
        else:
            self.set_window_quit_full()
            if self.mode_state_bool:
                self.concise_window_function()
            else:
                self.common_window_function()
                
            # self.MessageBox("退出全屏")    

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
        if self.show_or_hide_play_list_bool:
            self.play_list.show_play_list()
        
        if self.mode_state_bool:
            # window Angle.
            self.app.window.set_window_shape(True)
            self.common_window_function()
            self.mode_state_bool = False
            self.MessageBox("普通模式")

        if self.full_bool: # qiut full.
            self.show_bottom()
            self.progressbar.show_progressbar()
            self.app.show_titlebar()
            self.show_hide_set()

        if self.save_volume_mute_bool:
            if self.mp:
                self.mp.nomute()
                
                
    def hide_window_widget(self, widget): #concise_button
        '''Hide widnow titlebar and play control panel.
        Hide progressbar.
        Hide playlist.
        Hide border of window.
        [concise mode:]
        '''
        if self.show_or_hide_play_list_bool:
            self.play_list.hide_play_list()
                
        if self.full_bool:
            self.show_hide_set()

        if not self.mode_state_bool:
            self.concise_window_function()
            # window Angle.
            self.app.window.set_window_shape(False)
            self.mode_state_bool = True
            self.toolbar2.panel.show_all()
            # Set toolbar2 panel position.
            self.toolbar2.panel.move(self.panel_x,
                                     self.panel_y + (widget.allocation[3] - self.toolbar2.panel.allocation[3]) - self.app.titlebar.allocation[3])

            self.toolbar2.panel.hide_all()
            self.MessageBox("简洁模式")

        if self.save_volume_mute_bool:
            if self.mp:
                self.mp.nomute()                
                
                
    def set_window_above(self, widget): #above_button
        self.above_bool = not self.above_bool
        self.app.window.set_keep_above(self.above_bool)
        if self.above_bool:
            self.MessageBox("置顶")
        else:    
            self.MessageBox("取消置顶")

    # Control mplayer window.
    def move_media_player_window(self, widget, event): # screen: button-press-event
        '''Move window.'''
        if 1 == event.button:
            self.screen_move_bool = True
            self.screen_pause_bool = True
            # Save screen event state.
            self.event_button = event.button
            self.event_x_root = event.x_root
            self.event_y_root = event.y_root
            self.event_time = event.time

        # Double clicked full.
        if is_double_click(event):
            self.full_play_window(widget)
            self.toolbar.toolbar_full_button.flags = not self.toolbar.toolbar_full_button.flags
            self.double_bool = True
            gtk.timeout_add(300, self.double_restart_bool)
                

    def double_restart_bool(self):
        if self.double_bool:
            self.double_bool = False
            for timeout_id in self.signal_timeout:
                gtk.timeout_remove(timeout_id)
                self.signal_timeout = []
        
    def signal_restart_bool(self):  
        if not self.double_bool:
            
            for timeout_id in self.signal_timeout:
                gtk.timeout_remove(timeout_id)
                self.signal_timeout = []
                
            self.virtual_set_start_btn_clicked()    
            
    # Toolbar hide and show.
    def show_and_hide_toolbar(self, widget, event): # screen:motion_notify_event
        '''Show and hide toolbar.'''
        # Show toolbar.                        
        if 0 <= event.y <= 20:
            self.app.window.set_keep_above(True)
            self.toolbar.show_toolbar()
            
            self.panel_x, self.panel_y = self.screen.window.get_root_origin()
            if self.mode_state_bool: # Concise mode.
                self.toolbar.panel.move(self.panel_x, self.panel_y)            
            else:    # common mode.            
                self.toolbar.panel.move(self.panel_x + 1, self.panel_y + self.app.titlebar.allocation[3])
            
            self.toolbar.panel.set_keep_above(True)
        else:
            if not self.above_bool:
                self.app.window.set_keep_above(False)
                self.toolbar2.panel.set_keep_above(False)
            self.toolbar.hide_toolbar()

        # Show toolbar2.
        if self.mode_state_bool or self.full_bool: # concise mode.
            if widget.allocation[3]-20 <= event.y < widget.allocation[3]:
                self.app.window.set_keep_above(True)
                self.toolbar2.show_toolbar2()
                self.toolbar2.panel.set_keep_above(True)
            else:
                if not self.above_bool:
                    self.app.window.set_keep_above(False)
                    self.toolbar2.panel.set_keep_above(False)
                self.toolbar2.hide_toolbar2()

        if self.screen_move_bool:
            self.screen_pause_bool = False
            self.app.window.begin_move_drag(self.event_button,
                                            int(self.event_x_root),
                                            int(self.event_y_root),
                                            self.event_time)
            
        # hide preview window.    
        self.preview.hide_preview()    
        self.hide_preview_leave(widget, event)    
            
            
    def screen_time_pause(self):
        if self.mp.pause_bool:
            self.play_control_panel.start_btn.start_bool = False
            self.play_control_panel.start_btn.queue_draw()
            self.mp.seek(int(self.progressbar.pos))
            self.mp.start_play()
        else:
            self.play_control_panel.start_btn.start_bool = True
            self.play_control_panel.start_btn.queue_draw()
            self.mp.pause()
        return  False

    def screen_media_player_clear(self, widget, event): # screen: button-release-event
        self.screen_move_bool = False
        # playing file.
        if 1 == event.button and event.type == gtk.gdk.BUTTON_RELEASE:
            if 1 == self.mp.state:
                # self.virtual_set_start_btn_clicked()
                self.signal_timeout.append(gtk.timeout_add(500, self.signal_restart_bool))
        
        
    def virtual_set_start_btn_clicked(self):        
        if self.mode_state_bool:
            self.toolbar2.play_control_panel.start_btn.start_bool = not self.toolbar2.play_control_panel.start_btn.start_bool
            self.toolbar2.play_control_panel.start_btn.queue_draw()
            self.start_button_clicked(self.toolbar2.play_control_panel.start_btn, 2) 
        else:    
            self.play_control_panel.start_btn.start_bool = not self.play_control_panel.start_btn.start_bool
            self.play_control_panel.start_btn.queue_draw()
            self.start_button_clicked(self.play_control_panel.start_btn, 1)
            
    '''Toolbar2 keep above play window and Toolbar2'''
    def set_keep_window_toolbar2(self, widget, event):
        pass


    # Mplayer event of player control.
    def set_point_bool_time(self):
        self.point_bool = False
        return False

    def progressbar_set_point_bool(self, widget, event, progressbar):
        gtk.timeout_add(20, self.set_point_bool_time)


    def progressbar_player_point_pos_modify(self, widget, event, progressbar, pb_bit):
        '''Mouse left click rate of progress'''
        if self.mp:
            if 1 == self.mp.state:
                # Hide preview window.
                self.hide_preview_function(widget, event)
                
                self.mp.seek(int(progressbar.pos))
                progressbar.set_pos(progressbar.pos)
                progressbar.drag_bool = True
                self.point_bool = True

    def progressbar_player_drag_pos_modify(self, widget, event, progressbar, pb_bit):
        '''Set player rate of progress.'''
        if progressbar.drag_bool: # Mouse left.
            # Hide preview window.
            self.hide_preview_function(widget, event)
            
            if 1 == pb_bit:
                self.toolbar2.progressbar.set_pos(progressbar.pos)
                
            if 2 == pb_bit:
                self.progressbar.set_pos(progressbar.pos)
                
            if self.mp:
                if 1 == self.mp.state:
                    self.mp.seek(int(progressbar.pos))
                    self.show_time_label.time_font2 = self.set_time_string(self.mp.timeHour) + ":" + self.set_time_string(self.mp.timeMin) + ":" + self.set_time_string(self.mp.timeSec)
                    self.toolbar2.show_time.time_font2 = self.set_time_string(self.mp.timeHour) + ":" + self.set_time_string(self.mp.timeMin) + ":" + self.set_time_string(self.mp.timeSec)
                    self.toolbar2.panel.queue_draw()
                    self.app.window.queue_draw()
                
            
        # Show preview window.            
        if 1 == self.mp.state:            
            if self.play_video_file_bool(self.mp.path):           
                if self.show_bool:                                
                    self.x_root = event.x_root                                
                    self.y_root = event.y_root                                       
                    # preview window show.
                    self.preview.show_preview()
                    if 1 == pb_bit:
                        preview_y_padding = self.app.window.get_position()[1] + self.screen.allocation.height + self.app.titlebar.allocation.height - self.preview.bg.get_allocation()[3]
                    if 2 == pb_bit:    
                        preview_y_padding = self.toolbar2.panel.get_position()[1] - self.preview.bg.get_allocation()[3]

                    # previwe window show position.
                    self.preview.move_preview(self.x_root - self.preview.bg.get_allocation()[2]/2,
                                              preview_y_padding)        
                # if self.show_id == None and self.read_id == None:                                    
                if self.read_id == None:    
                    self.start_time_function(event.x, progressbar)
                    
                        
    '''Read preview image.'''        
    def start_time_function(self, pos, progressbar):                  
        self.show_id = gtk.timeout_add(10, self.save_scrot_image, pos, progressbar)
        self.read_id = gtk.timeout_add(15, self.read_image_time, pos, progressbar)                            

        
    def read_image_time(self, pos, progressbar):    
        # print "start read preview image... ..."
        save_pos = int((float(int(pos)) / progressbar.pb.allocation.width * progressbar.max)        )
        # print "读取图片:" + str(save_pos)
        
        if os.path.exists("/tmp/preview/" + self.get_player_file_name(self.mp.path) + "/" + str(int(save_pos)) + ".jpeg"):                    
            try:                
                # Read preview image.
                self.preview.set_image("/tmp/preview/" + self.get_player_file_name(self.mp.path) + "/" + str(int(save_pos)) + ".jpeg")
                # print "set preview image...."
                # preview background window show time.
                self.preview.set_pos(int(save_pos))
                self.preview.bg.queue_draw()                
            except:   
                print "read image,Error!!"
                
        self.read_id = None
        return False
            
    '''Save media player scrot image.'''
    def save_scrot_image(self, pos, progressbar): # scrot use thread function.
        save_pos = int((float(int(pos)) / progressbar.pb.allocation.width * progressbar.max))
        # print "保存图片:" + str(save_pos)
        
        if not os.path.exists("/tmp/preview/" + self.get_player_file_name(self.mp.path) + "/" + str(int(save_pos)) + ".jpeg"):            
            # Save preview image.
            # print "截图视频路径:" + self.preview.mp.path
            self.preview.mp.preview_scrot(int(save_pos),
                                          "/tmp/preview/"+ self.get_player_file_name(self.mp.path) + "/" + str(int(save_pos)) + ".jpeg")            

        self.show_id = None    
                
    '''Show preview window'''
    def time_preview_show(self):        
        '''Show preview window'''
        self.preview.show_preview()
        return False

    def show_preview_enter(self, widget, event):
        if self.mp:
            if 1 == self.mp.state:
                self.show_bool = True
        
    def hide_preview_leave(self, widget, event):
        '''Hide preview window and remove show,read_id'''
        if self.show_id:
            self.show_bool = False
            self.preview.hide_preview()
            gtk.timeout_remove(self.show_id)
            if self.read_id:
                gtk.timeout_remove(self.read_id)
            self.show_id = None
            self.read_id = None
            
    def set_time_string(self, num):
        if 0 <= num <= 9:
            return "0" + str(num)
        return str(num)
    
    def get_time_length(self, mplayer, length):
        '''Get mplayer length to max of progressbar.'''
        # play memory.                
        init_value = self.ini.get_section_value('PlayMemory', self.get_player_file_name(mplayer.path))        
        # print init_value
        if init_value != None:
            self.mp.seek(int(init_value))                        
            
        self.mp.setvolume(self.save_volume_value)
        if self.save_volume_mute_bool:
            self.mp.nomute()
            
        self.progressbar.max = length
        self.toolbar2.progressbar.max = length # toolbar2 max value.
        Hour, Min, Sec = self.mp.time(length)
        self.show_time_label.time_font1 = self.set_time_string(Hour) + " : " + self.set_time_string(Min) + " : "+ self.set_time_string(Sec) + "  /"
        self.toolbar2.show_time.time_font1 = self.set_time_string(Hour) + " : " + self.set_time_string(Min) + " : "+ self.set_time_string(Sec) + "  /"
        self.preview.set_path(mplayer.path)
        # print self.preview.mp.path
        
    def get_time_pos(self, mplayer, pos):
        '''Get mplayer pos to pos of progressbar.'''
        # Test media player pos.
        if not self.progressbar.drag_bool:
            if not self.point_bool:
                self.progressbar.set_pos(pos)
                self.toolbar2.progressbar.set_pos(pos)
                self.show_time_label.time_font2 = self.set_time_string(self.mp.timeHour) + ":" + self.set_time_string(self.mp.timeMin) + ":" + self.set_time_string(self.mp.timeSec)
                self.toolbar2.show_time.time_font2 = self.set_time_string(self.mp.timeHour) + ":" + self.set_time_string(self.mp.timeMin) + ":" + self.set_time_string(self.mp.timeSec)
                self.toolbar2.panel.queue_draw()
                self.app.window.queue_draw()
                
    def media_player_start(self, mplayer, play_bool):
        '''media player start play.'''        
        # Get draw width, height.       
        self.video_width, self.video_height = get_vide_width_height(mplayer.path)
        
        # # title show play file name.
        file_name = self.get_player_file_name(mplayer.path)
        # if len(file_name) > 25:
        #     file_name = file_name[0:3] + "..."
            
        self.app.titlebar.change_title(str(file_name))
        # TabPage.
        
        # if self.save_volume_mute_bool:
        #     self.mp.nomute()
        # print self.get_player_file_name(mplayer.path)                
        Num = 0
        # print self.play_list.list_view.items
        for item in self.play_list.list_view.items:
            if Num == self.mp.playListNum:
                self.play_list.list_view.set_highlight(item)    
                break
            else:    
                Num += 1
                        
        self.progressbar.set_pos(0)
        self.toolbar2.progressbar.set_pos(0)        
        
        self.preview.set_path(mplayer.path) # Set preview window play path.        
                
    def media_player_end(self, mplayer, play_bool):
        '''player end.'''
        #print self.input_string + "Linux Deepin Media player...end"
        # Play file modify start_btn.
        self.media_player_midfy_start_bool()
        # print mplayer.posNum
        if mplayer.posNum < mplayer.lenNum - 10:            
            root = self.ini.get_section("PlayMemory")
            # print root
            if root != None:
                root.child_addr[self.get_player_file_name(mplayer.path)] = mplayer.posNum
                self.ini.ini_save()
        else:    
            root = self.ini.get_section("PlayMemory")
            # print root
            if root != None:
                # print self.get_player_file_name(mplayer.path)
                del root.child_addr[self.get_player_file_name(mplayer.path)]
                self.ini.ini_save()
                
                
        
    def media_player_next(self, mplayer, play_bool):
        if 1 == play_bool:
            self.media_player_midfy_start_bool()
            self.MessageBox("下一首")
            
    def media_player_pre(self, mplayer, play_bool):
        self.media_player_midfy_start_bool()
        self.MessageBox("上一首")
        
    def media_player_midfy_start_bool(self):  # media_player_end and media_player_next and media_player_pre.
        self.progressbar.set_pos(0)
        self.toolbar2.progressbar.set_pos(0)
        self.screen.queue_draw()
        self.play_control_panel.start_btn.start_bool = True
        self.play_control_panel.start_btn.queue_draw()
        self.toolbar2.play_control_panel.start_btn.start_bool = True
        self.toolbar2.play_control_panel.start_btn.queue_draw()

    # Double buffer set.
    def unset_flags(self):
        '''Set double buffer.'''
        self.screen.unset_flags(gtk.DOUBLE_BUFFERED)

    def set_flags(self):
        '''Set double buffer.'''
        self.screen.set_flags(gtk.DOUBLE_BUFFERED)

    '''Set toolbar on window show positon.'''
    def set_toolbar_show_opsition(self):
        x, y = self.app.window.get_position()
        
    def play_video_file_bool(self, vide_path):    
        file1, file2 = os.path.splitext(vide_path)
        if file2.lower() in ['.mkv', '.rmvb','.avi','.wmv','.3gp','.rm', '.asf', '.mp4']:
            return True
        else:
            return False
        
    def get_player_file_name(self, pathfile2):     
        file1, file2 = os.path.split(pathfile2)
        return os.path.splitext(file2)[0]
   

    '''play list menu signal.'''
    def show_popup_menu(self, widget, event):
        if 3 == event.button:
            self.root_menu.show((int(event.x_root), int(event.y_root)),
                                (0, 0))    
        
    def sigle_play(self):
        if self.mp:
            self.mp.playListState = 0
            print "0"
            
    def sequence_play(self):        
        if self.mp:
            self.mp.playListState = 1
            print "1"
            
    def rand_play(self):        
        if self.mp:
            self.mp.playListState = 2
            print "2"
            
    def sigle_loop_play(self):        
        if self.mp:
            self.mp.playListState = 3
            print "3"
            
    def loop_list_play(self):
        if self.mp:
            self.mp.playListState = 4
            print "4"
            
    def name_sort(self):        
        print "****"
    
    def type_sort(self):
        print "********"
    
    def add_file(self):
        print "*****"
    def add_file_dir(self):
        print "****"
    def del_index(self):        
        print "*****"
    def clear_list(self):    
        print "******"
    def del_error_file(self):    
        print "*******"
        
    def open_current_file_dir(self):    
        print "open current file dir"
    
        
  
        
        
        
        
        
        
    
