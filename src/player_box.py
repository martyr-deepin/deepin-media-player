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

from dtk.ui.keymap import get_key_name
from dtk.ui.box import EventBox
from dtk.ui.draw import draw_pixbuf
from dtk.ui.frame import HorizontalFrame,VerticalFrame
from dtk.ui.utils import is_double_click, is_single_click,color_hex_to_cairo
from dtk.ui.constant import DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT, WIDGET_POS_BOTTOM_LEFT
from dtk.ui.utils import container_remove_all, get_widget_root_coordinate
from dtk.ui.menu import Menu

from ini import Config
from gio_format import format
from opendialog import OpenDialog
from utils import allocation,path_threads
from show_time import ShowTime
from progressbar import ProgressBar
from skin import app_theme
from toolbar import ToolBar
from toolbar2 import ToolBar2
from play_control_panel import PlayControlPanel
from play_list_button import PlayListButton
from volume_button import VolumeButton
from drag import drag_connect
from preview import PreView
from ini_gui import IniGui
from mplayer import Mplayer
# from mplayer import get_vide_width_height
from mplayer import get_length
from mplayer import get_home_path
from mplayer import length_to_time
from playlist import PlayList
from playlist import MediaItem
from sort import Sort

import threading
import gtk
import os
# import random


class PlayerBox(object):
    def __init__ (self, app, argv_path_list):
        # signal and double.
        self.double_bool = False
        self.signal_timeout = []
        self.open_file_name = "" # open current file dir name.
        self.input_string = "player_box: " # Test input string(message).
        self.mp = None
        self.mplayer_pid = None
        
        self.point_bool = False
        self.above_bool = False # Set window above bool.
        self.full_bool = False  # Set window full bool.
        self.mode_state_bool = False # Concise mode(True) and common mode(False).
        self.show_toolbar_bool = False
        self.show_toolbar_focus_bool = True
        self.clear_play_list_bool = False # drag play file.
        
        # pause setting.
        self.pause_time_id = None
        self.pause_bool = False
        self.pause_x = 0
        self.pause_y = 0
        # Init play memory.
        self.ini = Config(get_home_path() + "/.config/deepin-media-player/config.ini")
        # Init deepin media player config gui.
        self.config = Config(get_home_path() + "/.config/deepin-media-player/deepin_media_config.ini")
        self.config.connect("config-changed", self.modify_config_section_value)
        # self.ini.load()
        
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
        
        self.save_volume_mute_bool = False
        self.save_volume_value = 0

        # Screen move window.
        self.event_button = None
        self.event_x_root = None
        self.event_y_root = None
        self.event_time = None

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
                    
        
        '''Title root menu.'''
        #In title root menu.
        self.sort_menu = Menu([(None, "截图", None),      
                               (None, "打开截图目录", None),   
                               (None, "设置截图保存目录", None)
                               ])                
        # In title root menu.
        self.subtitle_menu = Menu([(None, "载入字幕", None),      
                                   (None, "字幕选择", None),   
                                   (None, "移除字幕", None), 
                                   ])                         
        # In title root menu.
        self.volume_menu = Menu([(None, "声道选择", None),      
                                 (None, "配音选择", None),   
                                 (None),       
                                 (None, "增大音量", None), 
                                 (None, "减小音量", None),
                                 (None, "静音/还原", None),
                                 ])         
        # In title root menu.
        self.screen_menu = Menu([(None, "默认值", None),
                                 (None, "4:3", None),
                                 (None, "16:9", None),
                                 (None, "16:10", None),
                                 (None, "1.85:1", None),
                                 (None, "2.35:1", None),
                                 (None),
                                 (None, "0.5倍尺寸", None),
                                 (None, "1倍", None),
                                 (None, "1.5倍", None),
                                 (None, "2倍", None),
                                 (None),
                                 (None, "全屏/退出", None),
                                 ])
        # In title root menu.
        self.play_state_menu = Menu([(None, "单个播放", None),      
                                     (None, "顺序播放", None),   
                                     (None, "随机播放", self.rand_play), 
                                     (None, "单个循环", self.sigle_loop_play), 
                                     (None, "列表循环", self.loop_list_play)]  
                                    ) 
        # In title root menu.
        self.play_menu = Menu([(None, "全屏播放", None),
                               (None, "窗口模式", None),
                               (None, "简洁模式", None),
                               (None, "上一首", None),
                               (None, "下一首", None),
                               (None),
                               (None, "快进5秒", None),
                               (None, "快退5秒", None),
                               (None, "播放顺序", self.play_state_menu),
                               ])
        # In title root menu.
        self.file_menu = Menu([(None, "打开文件", self.add_file),
                               (None, "打开文件夹", self.add_file_dir),
                              (None, "播放光盘", None)])
        
        # In title root menu.
        self.help_menu = Menu([(None, "帮助信息", None),
                               (None, "问题反馈", None),
                               (None, "关于软件", None)])        
        #aaaaaa
        self.title_root_menu = Menu([(None, "文件", self.file_menu), 
                                     (None, "播放", self.play_menu),
                                     (None, "画面", self.screen_menu),
                                     (None, "声音", self.volume_menu),
                                     (None, "字幕", self.subtitle_menu),
                                     (None, "截图", self.sort_menu),                            
                                     (None, "选项", self.config_gui),
                                     (None, "总在最前", None),
                                     (None, "自定义换肤", None),
                                     (None, "帮助与反馈", self.help_menu),
                                     (None, "退出", None)],
                                    True)                        
        '''Tooltip window'''
        # self.tooltip = Tooltip("深度影音", 0, 0)
        
        '''Preview window'''
        self.preview = PreView()
        
        '''Save app(main.py)[init app].'''
        self.app = app
        self.app.set_menu_callback(lambda button: self.title_root_menu.show(
                get_widget_root_coordinate(button, WIDGET_POS_BOTTOM_LEFT),
                (button.get_allocation().width, 0)))
    
        self.app_width = 0  # Save media player window width.
        self.app_height = 0 # Save media player window height.
        self.argv_path_list = argv_path_list # command argv.
        self.app.window.connect("destroy", self.quit_player_window)
        self.app.window.connect("configure-event", self.app_configure_hide_tool)
        self.app.window.connect("window-state-event", self.set_toolbar2_position)
        self.app.window.connect("leave-notify-event", self.hide_all_toolbars)
        # test app window
        self.app.window.connect("focus-out-event", self.set_show_toolbar_function_false)
        self.app.window.connect("focus-in-event", self.set_show_toolbar_function_true)
        #keyboard Quick key.
        # self.app.window.connect("realize", gtk.Widget.grab_focus)
        self.app.window.connect("key-press-event", self.get_key_event)
                
        '''Screen window init.'''
        self.screen = gtk.DrawingArea()
        
        # Screen signal init.
        self.screen.add_events(gtk.gdk.ALL_EVENTS_MASK)
        self.screen.set_can_focus(True)
        # drag resize window. .grab_focus()
        self.screen.connect("realize", self.init_media_player)
        self.screen.unset_flags(gtk.DOUBLE_BUFFERED) # disable double buffered to avoid video blinking
        
        # Handle signal.
        # self.connect("realize", self.realize_mplayer_view)

        # self.screen.connect("key-press-event", self.get_key_event)
        self.screen.connect("button-press-event", self.drag_resize_window)
        self.screen.connect("motion-notify-event", self.modify_mouse_icon)
        
        self.screen.connect_after("expose-event", self.draw_background)
        self.screen.connect("button-press-event", self.move_media_player_window)
        self.screen.connect("button-release-event", self.screen_media_player_clear)
        self.screen.connect("motion-notify-event", self.show_and_hide_toolbar)
        self.screen.connect("configure-event", self.configure_hide_tool)
        # self.screen.connect("leave-notify-event", self.hide_all_toolbars)
        # self.screen.connect("get-xid", self.init_media_player)


        '''Progressbar Init.'''
        self.progressbar = ProgressBar()
        # Progressbar signal init.
        self.progressbar.pb.connect("motion-notify-event", self.progressbar_player_drag_pos_modify, self.progressbar, 1)
        self.progressbar.pb.connect("button-press-event", self.progressbar_player_point_pos_modify, self.progressbar, 1)
        self.progressbar.pb.connect("button-release-event", self.progressbar_set_point_bool, self.progressbar)
        
        # self.progressbar.pb.connect("enter-notify-event", self.show_preview_enter)
        self.progressbar.pb.connect("leave-notify-event", self.hide_preview_leave)        
        
        '''Toolbar Init.'''
        self.toolbar = ToolBar()        
        # self.toolbar.panel.connect("leave-notify-event", self.set_show_toolbar_bool)
        self.toolbar.toolbar_full_button.connect("clicked", self.full_play_window)
        self.toolbar.toolbar_common_button.connect("clicked", self.show_window_widget)
        self.toolbar.toolbar_concise_button.connect("clicked", self.hide_window_widget)
        self.toolbar.toolbar_above_button.connect("clicked", self.set_window_above)

        '''Toolbar2 Init.'''
        toolbar2_height = 45
        self.toolbar2 = ToolBar2()                
        self.toolbar2.panel.set_size_request(1, toolbar2_height) # Set toolbar2 height.
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
        # self.toolbar2.progressbar.pb.connect("enter-notify-event", self.show_preview_enter)
        self.toolbar2.progressbar.pb.connect("leave-notify-event", self.hide_preview_leave)        
        
        # play_control_panel.
        self.toolbar2.play_control_panel.stop_btn.connect("clicked", self.stop_button_clicked)
        self.toolbar2.play_control_panel.pre_btn.connect("clicked", self.pre_button_clicked)
        self.toolbar2.play_control_panel.start_btn.connect("clicked", self.start_button_clicked, 2)
        self.toolbar2.play_control_panel.next_btn.connect("clicked", self.next_button_clicked)
        self.toolbar2.play_control_panel.open_btn.connect("clicked", self.open_button_clicked)

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
        # self.play_list.list_view.connect("key-press-event", self.get_key_event)
        self.play_list.list_view.connect("double-click-item", self.double_play_list_file)
        self.play_list.list_view.connect("delete-select-items", self.delete_play_list_file)
        self.play_list.list_view.connect("button-press-event", self.show_popup_menu)
        self.play_list.list_view.connect("single-click-item", self.open_current_file_dir_path)
        self.play_list.list_view.connect("motion-notify-item", self.open_current_file_dir_path)
        
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
        self.volume_button_hframe.set_padding(0, 5, 0, 10)

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
        
        self.keymap = {"Right":self.key_right,
                       "Left":self.key_left,
                       "Space":self.key_space,
                       "Return":self.key_return}        
        
    def modify_config_section_value(self, Config, str1, str2, str3):    
        print Config
        print str1
        print str2
    
    def set_show_toolbar_function_true(self, widget, event):
        self.show_toolbar_focus_bool = True
        
    def set_show_toolbar_function_false(self, widget, event):    
        self.show_toolbar_focus_bool = False
        self.toolbar.hide_toolbar()
        self.toolbar2.hide_toolbar2()
        
    def set_show_toolbar_bool(self, widget, event):    
        self.show_toolbar_bool = False
        
    def hide_all_toolbars(self, widget, event):        
        if not self.show_toolbar_bool:
            # if not self.above_bool:
            #     self.app.window.set_keep_above(False)
            self.toolbar.hide_toolbar()
            self.toolbar2.hide_toolbar2()
                
    def modify_mouse_icon(self, widget, event): # screen: motion-notify-event 
        w = widget.allocation.width
        h = widget.allocation.height
        bottom_padding = 10

        if (w - bottom_padding <= event.x <= w) and (h - bottom_padding <= event.y <= h):
            if "MplayerView" != type(widget).__name__:
                drag = gtk.gdk.BOTTOM_RIGHT_CORNER
                widget.window.set_cursor(gtk.gdk.Cursor(drag))
        else:        
            widget.window.set_cursor(None)
            self.app.window.window.set_cursor(None)
        
    def drag_resize_window(self, widget, event): # screen: button-press-event -> drag resize window.
        self.screen.grab_focus()
        
        w = widget.allocation.width
        h = widget.allocation.height
        bottom_padding = 5
        drag_bool = False
        
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
        else:        
            widget.window.set_cursor(None)
        
    def get_key_event(self, widget, event): # app: key-release-event       
        keyval_name = get_key_name(event.keyval)
        if 32 == event.keyval:
            keyval_name = "Space"
        # print keyval_name        
        if self.keymap.has_key(keyval_name):
            self.keymap[keyval_name]()
        return True
    
    def key_right(self):            
        self.mp.seek(self.mp.posNum + 5)
        
    def key_left(self):
        self.mp.seek(self.mp.posNum - 5)
        
    def key_space(self):
        self.virtual_set_start_btn_clicked()
    
    def key_return(self):
        self.full_play_window(self.app.window)
        self.toolbar.toolbar_full_button.flags = not self.toolbar.toolbar_full_button.flags
            
    '''play list button'''    
    def play_list_button_clicked(self, widget): # play list button signal:clicked.           
        if True == self.play_list_button.button.flags: 
            # self.app.window.resize(self.app.window.allocation.width + self.play_list.play_list_width,
            #                        self.app.window.allocation.height)
            self.play_list.show_play_list()
            self.show_or_hide_play_list_bool = True
            
        if False == self.play_list_button.button.flags:    
            # self.app.window.resize(self.app.window.allocation.width - self.play_list.play_list_width,
            #                        self.app.window.allocation.height)
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
            length = self.ini.get("PlayTime", '"%s"' % (self.play_list_dict[i.title]))
            if length:
                i.length = length_to_time(length)
            else:    
                i.length, length = get_length(self.play_list_dict[i.title])            
                self.ini.set("PlayTime", '"%s"' % (self.play_list_dict[i.title]), length)
                # self.ini.write()    
                self.ini.save()
            i.emit_redraw_request()
            
                    
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
        self.hide_preview_leave(widget, event)
        
    '''play control panel.'''
    def stop_button_clicked(self, widget):
        self.mp.quit()

    def start_button_clicked(self, widget, start_bit):
        '''start or pause'''
        if 0 == self.mp.state:
            self.mp.next() # Test pause.
            self.play_control_panel.start_btn.start_bool = False
            self.play_control_panel.start_btn.queue_draw()
            self.toolbar2.play_control_panel.start_btn.start_bool = False
            self.toolbar2.play_control_panel.start_btn.queue_draw()
            if 0 == self.mp.state: # NO player file.
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

            gtk.timeout_add(50, self.start_button_time_pause)
            
    def start_button_time_pause(self): # start_button_clicked.
        if self.mp.pause_bool:
            self.mp.seek(int(self.progressbar.pos))
            self.mp.start_play()
        else:
            self.mp.pause()
        return  False
    
    def pre_button_clicked(self, widget):
        '''prev.'''
        if (len(self.mp.playList) > 1):    
            self.mp.pre()

    def next_button_clicked(self, widget):
        '''next'''
        if (len(self.mp.playList) > 1):
            self.mp.next()
        
    def open_button_clicked(self, widget):        
        self.show_open_dialog_window()
        
    def show_open_dir_dialog_window(self):    
        open_dialog = gtk.FileChooserDialog("深度影音打开文件夹对话框",
                                            None,
                                            gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                            (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, 
                                             gtk.STOCK_OPEN, gtk.RESPONSE_OK))        
        open_dialog.set_current_folder(get_home_path())
        res = open_dialog.run()
        
        if res == gtk.RESPONSE_OK:
            path_string = open_dialog.get_filename()
            self.get_path_name(path_string)                        
        open_dialog.destroy()                

    def show_open_dialog_window(self):    
        # open dialog window.
        # open_dialog = OpenDialog() 
        
        # open_dialog.connect("get-path-name", self.get_path_name)
        # open_dialog.set_filter({"所有文件":".*",
        #                         "音频文件":"audio/mpeg",
        #                         "视频文件":"video/x-msvideo|.rmvb",
        #                         "播放列表":".dmp"})    
        
        # open_dialog.combo_box.item_label.text = "所有文件"
        # open_dialog.set_title("深度影音打开")
        # open_dialog.filter_to_file_type("所有文件")    
        # open_dialog.show_open_window()    
        # open_dialog.set_keep_above(True)
        open_dialog = gtk.FileChooserDialog("深度影音打开文件对话框",
                                            None,
                                            gtk.FILE_CHOOSER_ACTION_OPEN,
                                            (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, 
                                             gtk.STOCK_OPEN, gtk.RESPONSE_OK))        
        open_dialog.set_current_folder(get_home_path())
        res = open_dialog.run()
        
        if res == gtk.RESPONSE_OK:
            path_string = open_dialog.get_filename()
            self.get_path_name(path_string)            
            
        open_dialog.destroy()                
        
    # def get_path_name(self, open_dialog, path_string):    
    def get_path_name(self, path_string):    
        # # print path_string
        if os.path.isdir(path_string):
            path_threads(path_string, self.mp)

        # # Add .Dmp.    
        if self.mp.findDmp(path_string):
            self.mp.loadPlayList(path_string)
            
        # Add play file.    
        if os.path.isfile(path_string):    
            self.mp.addPlayFile(path_string)
        
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
                
            if len(self.argv_path_list) > 1: # Set play bool.
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
        
        if self.mp and (1 == self.mp.state):
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
                        
                        left_width = 0
                        left_x_padding = 0
                        if self.app.titlebar.allocation.height > 1:                            
                            left_width       = 2
                            left_x_padding   = 1
                        
                        # Draw left.
                        cr.rectangle(x-left_x_padding, y - self.app.titlebar.allocation.height, 
                                     s - left_width, h + 1)
                        cr.fill()
                        
                        # Draw right.
                        cr.rectangle(x + h * (video_ratio) + s,
                                     y - self.app.titlebar.allocation.height, 
                                     s, h + 1)
                        cr.fill()
                        
                    elif bit > 0:
                        video_ratio = float(self.video_height) / self.video_width                        
                        s = h - w * video_ratio
                        s = s / 2
                                                
                        up_x_padding = 0                        
                        up_width = 0
                        bottom_width = 0
                        if self.app.titlebar.allocation.height > 1:
                            s = s
                            up_x_padding = 1
                            up_width = 1
                            bottom_width = 1
                        else:    
                            s = s + 1
                                                        
                        # Draw UP.                            
                        cr.rectangle(x - up_x_padding, y - self.app.titlebar.allocation.height, 
                                     w, s - up_width)
                        cr.fill()
                        
                        # Draw bottom.
                        cr.rectangle(x - up_x_padding, y + s + w * (video_ratio) - self.app.titlebar.allocation.height + up_width, 
                                     w, s - bottom_width)
                        cr.fill()
                        
                    return True
            
                if self.mp.pause_bool: # vide pause.
                    # Draw pause background.
                    return False
                else:
                    return False                
                
        # if no player vide file or no player.
        cr.set_source_rgb(*color_hex_to_cairo("#1f1f1f"))
        cr.rectangle(0, 0, w, h)
        cr.fill()
        
        # Draw player image.
        rect = widget.allocation
        pixbuf = app_theme.get_pixbuf("player.png").get_pixbuf()
        draw_pixbuf(
            cr,
            pixbuf,
            x + (w - pixbuf.get_width()) / 2,
            (h - pixbuf.get_height()) / 2)        
        # return True


    def quit_player_window(self, widget):
        '''Quit player window.'''
        self.app.window.set_opacity(0)
        self.app.window.set_visible(True)
        if self.mp:
            if self.mplayer_pid:
                os.system("kill %s" %(self.mplayer_pid))
            self.mp.quit()
            

    def set_toolbar2_position(self, widget, event):        
        self.toolbar2.show_toolbar2()
        self.toolbar.panel.move(self.panel_x + 1, self.panel_y + self.app.titlebar.allocation[3])
        self.toolbar2.panel.move(self.panel_x + 1, self.panel_y + self.screen.allocation.height - 40)
        self.toolbar2.hide_toolbar2()
        
    # ToolBar control function.
    def app_configure_hide_tool(self, widget, event): #app: configure-event.
        #Set mute and value.
        
        # if self.mp:
            # self.screen.queue_draw()    
            
        if self.toolbar2.volume_button.mute_bool != self.save_volume_mute_bool:
            self.toolbar2.volume_button.mute_bool = self.save_volume_mute_bool
            self.toolbar2.volume_button.set_value(self.save_volume_value)
        if self.volume_button.mute_bool != self.save_volume_mute_bool:
            self.volume_button.mute_bool = self.save_volume_mute_bool
            self.volume_button.set_value(self.save_volume_value)

        if self.save_volume_mute_bool: 
            self.mp.nomute()

        self.toolbar.panel.hide_all()
        self.show_toolbar_bool = False
        
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
        self.show_toolbar_bool = False
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
        if self.show_or_hide_play_list_bool:
            self.play_list.show_play_list()
        
        if self.mode_state_bool:
            # window Angle.
            self.app.window.set_window_shape(True)
            self.common_window_function()
            self.mode_state_bool = False

        if self.full_bool: # qiut full.
            self.show_bottom()
            self.progressbar.show_progressbar()
            self.app.show_titlebar()
            self.show_hide_set()
            # modify full icon.                
            self.toolbar.toolbar_full_button.flags = True
            
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
            # modify full icon.
            self.toolbar.toolbar_full_button.flags = True
            
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

        if self.save_volume_mute_bool:
            if self.mp:
                self.mp.nomute()                
                
                
    def set_window_above(self, widget): #above_button
        self.above_bool = not self.above_bool
        self.app.window.set_keep_above(self.above_bool)

    # Control mplayer window.
    def move_media_player_window(self, widget, event): # screen: button-press-event
        '''Move window.'''
        if 1 == event.button:
            self.event_button = event.button
            self.event_x_root = event.x_root
            self.event_y_root = event.y_root
            self.event_time = event.time
            
        if is_single_click(event):    
            if not self.pause_bool:    
                # pause / play. 123456 press.
                self.pause_bool = True # Save pause bool.
                self.pause_x = event.x # Save x postion.
                self.pause_y = event.y # Save y postion.
            
            else:
                if self.pause_time_id:
                    gtk.timeout_remove(self.pause_time_id)
                    self.pause_bool = False
        
        # Double clicked full.
        if is_double_click(event):
            self.full_play_window(widget)
            self.toolbar.toolbar_full_button.flags = not self.toolbar.toolbar_full_button.flags
            if self.pause_time_id:
                gtk.timeout_remove(self.pause_time_id)
                self.pause_bool = False
                       
    # Toolbar hide and show.
    def show_and_hide_toolbar(self, widget, event): # screen:motion_notify_event
        '''Show and hide toolbar.'''
        # Show toolbar.                        
        if 0 <= event.y <= 20:
            if self.show_toolbar_focus_bool:
                self.toolbar.show_toolbar()
                self.show_toolbar_bool = True            
            
                self.panel_x, self.panel_y = self.screen.window.get_root_origin()
                if self.mode_state_bool: # Concise mode.
                    self.toolbar.panel.move(self.panel_x, self.panel_y)            
                else:    # common mode.            
                    self.toolbar.panel.move(self.panel_x + 1, self.panel_y + self.app.titlebar.allocation[3])
            
            # self.toolbar.panel.set_keep_above(True)
        else:
            if not self.above_bool:
                self.app.window.set_keep_above(False)
                self.toolbar2.panel.set_keep_above(False)
            self.toolbar.hide_toolbar()
            self.show_toolbar_bool = False
            
        # Show toolbar2.
        if self.mode_state_bool or self.full_bool: # concise mode.
            if widget.allocation[3]-20 <= event.y < widget.allocation[3]:
                if self.show_toolbar_focus_bool:
                    self.toolbar2.show_toolbar2()
                    self.show_toolbar_bool = True
            else:
                self.toolbar2.hide_toolbar2()
                
        # hide preview window.    
        self.hide_preview_leave(widget, event)    
        
        # pause /play. 123456 motion.
        if self.pause_bool:
            if abs(self.pause_x - event.x) > 5 or abs(self.pause_y - event.y) > 5:
                self.pause_bool = False
                self.app.window.begin_move_drag(self.event_button,
                                            int(self.event_x_root),
                                            int(self.event_y_root),
                                            self.event_time)            
                           
    def screen_media_player_clear(self, widget, event): # screen: button-release-event
        # pause / play 123456 release.
        if self.pause_bool:                                    
            if 1 == self.mp.state:                
                self.pause_time_id = gtk.timeout_add(250, self.virtual_set_start_btn_clicked)
                self.pause_bool = False
                  
    def virtual_set_start_btn_clicked(self):        
        if self.mode_state_bool:
            self.toolbar2.play_control_panel.start_btn.start_bool = not self.toolbar2.play_control_panel.start_btn.start_bool
            self.toolbar2.play_control_panel.start_btn.queue_draw()
            self.start_button_clicked(self.toolbar2.play_control_panel.start_btn, 2) 
        else:    
            self.play_control_panel.start_btn.start_bool = not self.play_control_panel.start_btn.start_bool
            self.play_control_panel.start_btn.queue_draw()
            self.start_button_clicked(self.play_control_panel.start_btn, 1)
            
        return False    
            
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
            else:    
                self.progressbar.set_pos(0)
                self.toolbar2.progressbar.set_pos(0)                

    def progressbar_player_drag_pos_modify(self, widget, event, progressbar, pb_bit):
        '''Set player rate of progress.'''
        
        if progressbar.drag_bool: # Mouse left.
            # Hide preview window.
            self.hide_preview_function(widget, event)
            if 1 == self.mp.state:
                if 1 == pb_bit:
                    self.toolbar2.progressbar.set_pos(progressbar.pos)                
                elif 2 == pb_bit:
                    self.progressbar.set_pos(progressbar.pos)
                
                if self.mp:
                    if 1 == self.mp.state:
                        self.mp.seek(int(progressbar.pos))
                        self.show_time_label.time_font2 = self.set_time_string(self.mp.timeHour) + ":" + self.set_time_string(self.mp.timeMin) + ":" + self.set_time_string(self.mp.timeSec)
                        self.toolbar2.show_time.time_font2 = self.set_time_string(self.mp.timeHour) + ":" + self.set_time_string(self.mp.timeMin) + ":" + self.set_time_string(self.mp.timeSec)
                        self.toolbar2.panel.queue_draw()
                        self.app.window.queue_draw()
            else:    
                self.progressbar.set_pos(0)
                self.toolbar2.progressbar.set_pos(0)                            
        # Show preview window.            
        else:
            if "true" ==  self.config.get("FilePlay", "mouse_progressbar_show_preview").lower():
                if 1 == self.mp.state:            
                    if self.play_video_file_bool(self.mp.path):           
                        self.preview.set_preview_path(self.mp.path)
                        self.x_root = event.x_root
                        self.y_root = event.y_root                                                               
                        save_pos = (float(int(event.x))/ widget.allocation.width* self.progressbar.max)
                        # preview window show.
                        self.move_window_time(save_pos, pb_bit)                
                    
                    
    def move_window_time(self, pos, pb_bit):                    
        
        if 1 == pb_bit:
            preview_y_padding = self.app.window.get_position()[1] + self.screen.allocation.height + self.app.titlebar.allocation.height - self.preview.bg.get_allocation()[3]                            
        elif 2 == pb_bit:    
            preview_y_padding = self.toolbar2.panel.get_position()[1] - self.preview.bg.get_allocation()[3]
            
        self.preview.show_preview(pos)            
        # previwe window show position.
        self.preview.move_preview(self.x_root - self.preview.bg.get_allocation()[2]/2,
                                  preview_y_padding)
                        
    # def show_preview_enter(self, widget, event):
    #     pass
        
    def hide_preview_leave(self, widget, event):
        '''Hide preview window and remove show,read_id'''
        self.preview.hide_preview()
    
    def set_time_string(self, num):
        if 0 <= num <= 9:
            return "0" + str(num)
        return str(num)
    
    def get_time_length(self, mplayer, length):
        '''Get mplayer length to max of progressbar.'''            
        self.mp.setvolume(self.save_volume_value)
        if self.save_volume_mute_bool:
            self.mp.nomute()
            
        self.progressbar.max = length
        self.toolbar2.progressbar.max = length # toolbar2 max value.
        Hour, Min, Sec = self.mp.time(length)
        self.show_time_label.time_font1 = self.set_time_string(Hour) + " : " + self.set_time_string(Min) + " : "+ self.set_time_string(Sec) + "  /"
        self.toolbar2.show_time.time_font1 = self.set_time_string(Hour) + " : " + self.set_time_string(Min) + " : "+ self.set_time_string(Sec) + "  /"

        
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
                
    def get_pos_ste_seek(self, pos):            
        self.mp.seek(int(pos))                                    
        
    def media_player_start(self, mplayer, play_bool, w1, h1, w2, h2):
        '''media player start play.'''                        
        # Get mplayer play file width and height.
        self.video_width = w1
        self.video_height = h1
        if w2 > w1:
            self.video_width = w2
            self.video_height = h2            
            
        # Get mplayer pid.
        self.mplayer_pid = play_bool
        #play memory.                        
        pos = self.ini.get("PlayMemory", '"%s"' % ((mplayer.path)))        
        if pos is not None:
            gtk.timeout_add(100, self.get_pos_ste_seek, pos)

        # # title show play file name.
        file_name = self.get_player_file_name(mplayer.path)
        # if len(file_name) > 25:
        #     file_name = file_name[0:3] + "..."
            
        self.app.titlebar.change_title(str(file_name))
        # TabPage.
        
        for item in self.play_list.list_view.items:
            if self.play_list_dict[item.title] == self.mp.path:
                self.play_list.list_view.set_highlight(item)    
                break        
            
        self.progressbar.set_pos(0)
        self.toolbar2.progressbar.set_pos(0)        
        
                
    def media_player_end(self, mplayer, play_bool):
        '''player end.'''        
        # Quit preview window player.
        self.preview.quit_preview_player()
        #print self.input_string + "Linux Deepin Media player...end"
        # Play file modify start_btn.
        self.media_player_midfy_start_bool()
        if "true" == self.config.get("FilePlay", "memory_up_close_player_file_postion").lower():
            self.ini.set("PlayMemory", '"%s"' % (mplayer.path), 0)
            if mplayer.posNum < mplayer.lenNum - 10:
                self.ini.set("PlayMemory", '"%s"' % (mplayer.path), mplayer.posNum)
                        
            # self.ini.write()        
            self.ini.save()     
                
        
    def media_player_next(self, mplayer, play_bool):
        if 1 == play_bool:
            self.media_player_midfy_start_bool()

            
    def media_player_pre(self, mplayer, play_bool):
        self.media_player_midfy_start_bool()
        
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
        return format.get_video_bool(vide_path)
        
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
            
    def sequence_play(self):        
        if self.mp:
            self.mp.playListState = 1        
            
    def rand_play(self):        
        if self.mp:
            self.mp.playListState = 2        
            
    def sigle_loop_play(self):        
        if self.mp:
            self.mp.playListState = 3        
            
    def loop_list_play(self):
        if self.mp:
            self.mp.playListState = 4        
            
    def name_sort(self):        
        '''Play list name sort.'''
        if self.play_list.list_view.items:
            sort = Sort()                
            temp_dict = {}
            temp_list = []
        
            for item in self.play_list.list_view.items:
                temp_dict[item.title] = item.length
                temp_list.append(item.title)
                    
            sort.name_sort(temp_list)
            temp_list = []
                
            # Add cn.
            temp_cn = sort.mid_tree(sort.cn_tree)        
            if temp_cn:
                temp_list.append(temp_cn)
            # Add en.    
            temp_en = sort.mid_tree(sort.en_tree)
            if temp_en:
                temp_list.append(temp_en)
            # Add number.
            temp_num = sort.mid_tree(sort.num_tree)
            if temp_num:
                temp_list.append(temp_num)
            
            # clear play list.        
            self.play_list.list_view.clear()
            self.mp.playList = []
            self.mp.playListSum   = 0 
            self.mp.playListNum   = -1
            self.mp.random_num = 0        
        
            # play list restart add file name.
            list_item = []        
            for i in temp_list:
                for j in i:
                    for k in j:
                        list_item.append(MediaItem(k, temp_dict[k]))                
                
                        self.mp.playList.append(self.play_list_dict[k])
                        self.mp.playListSum += 1
                    
            self.play_list.list_view.add_items(list_item)                
        
            # # highlight staring play file.
            num = 0
            for item in self.play_list.list_view.items:
                if self.play_list_dict[item.title] == self.mp.path:
                    self.play_list.list_view.set_highlight(item)
                    break                        
                num += 1
            self.mp.playListNum = num
        
    def type_sort(self):
        if self.play_list.list_view.items:
            sort = Sort()
            temp_dict = {}
            temp_list = []
            # 
            for item in self.play_list.list_view.items:
                temp_list.append(self.play_list_dict[item.title])
                temp_dict[item.title] = item.length
                
                
            temp_list = sort.type_sort(temp_list)                        
            # clear play list.        
            self.play_list.list_view.clear()
            self.mp.playList = []
            self.mp.playListSum   = 0 
            self.mp.playListNum   = -1
            self.mp.random_num = 0        
            
            list_item = []
            for list_str in temp_list:
                list_item.append(MediaItem(list_str, temp_dict[list_str]))
                self.mp.playList.append(self.play_list_dict[list_str])
                self.mp.playListSum += 1
                    
                 
            self.play_list.list_view.add_items(list_item)                
        
            # # highlight staring play file.
            num = 0
            for item in self.play_list.list_view.items:
                if self.play_list_dict[item.title] == self.mp.path:
                    self.play_list.list_view.set_highlight(item)
                    break                        
                num += 1
            self.mp.playListNum = num
                
    def add_file(self):
        self.show_open_dialog_window()
        
    def add_file_dir(self):
        self.show_open_dir_dialog_window()
        
    def del_index(self):
        # self.delete_play_list_file(self.play_list.list_view, self.play_list.list_view.items)
        self.play_list.list_view.delete_select_items()
        
        
    def clear_list(self):    
        self.play_list.list_view.clear()
        self.mp.clearPlayList()
        
    def del_error_file(self):    
        '''Delete error play file.'''
        if self.play_list.list_view.items:
            for item in self.play_list.list_view.items:
                # play file error -> delete file.
                path = self.play_list_dict[item.title]
                if not os.path.exists(path):
                    self.play_list.list_view.items.remove(item)
                    self.mp.delPlayList(path)   
                                                            
    def open_current_file_dir(self):            
        try:
            file_name, file_name2 = os.path.split(self.open_file_name)
        except:
            file_name = "~"
            
        os.system("nautilus %s" % (file_name))
        self.open_file_name = ""
        
    def open_current_file_dir_path(self, list_view, list_item, column, offset_x, offset_y):
        self.open_file_name = self.play_list_dict[list_item.title]                    

    '''config gui window'''
    def restart_load_config_file(self, IniGui, string):
        self.config = Config(get_home_path() + "/.config/deepin-media-player/deepin_media_config.ini")
        # self.config.connect("config-changed", self.modify_config_section_value)

    def config_gui(self):
        ini_gui = IniGui()
        ini_gui.connect("config-changed", self.restart_load_config_file)
