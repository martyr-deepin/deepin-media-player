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

from dtk.ui.skin_config import skin_config
from dtk.ui.osd_tooltip import OSDTooltip
from dtk.ui.utils import cairo_state, is_left_button
from dtk.ui.keymap import get_keyevent_name
from dtk.ui.box import EventBox
from dtk.ui.draw import draw_pixbuf
from dtk.ui.frame import HorizontalFrame,VerticalFrame
from dtk.ui.utils import is_double_click, is_single_click, is_right_button, color_hex_to_cairo
from dtk.ui.constant import WIDGET_POS_BOTTOM_LEFT
from dtk.ui.utils import get_widget_root_coordinate
from dtk.ui.menu import Menu
from dtk.ui.volume_button import VolumeButton

from locales import _
from constant import APP_WIDTH, APP_HEIGHT, STARTING_PLAY, STOPING_PLAY
from ini import Config
from gio_format import format
from utils import allocation,path_threads
from show_time import ShowTime
from progressbar import ProgressBar
from skin import app_theme
from toolbar import ToolBar
from bottom_toolbar import BottomToolBar
from play_control_panel import PlayControlPanel
from play_list_button import PlayListButton
from drag import drag_connect
from preview import PreView
from ini_gui import IniGui
from ini_gui import VIDEO_ADAPT_WINDOW_STATE, WINDOW_ADAPT_VIDEO_STATE, UP_CLOSE_VIDEO_STATE, AI_FULL_VIDEO_STATE
from gio_format import Format
from mplayer import Mplayer, get_length, get_home_path, length_to_time, get_vide_width_height
from mplayer import SINGLE_PLAYING_STATE, ORDER_PLAYING_STATE, RANDOM_PLAYER_STATE, SINGLE_CYCLE_PLAYER, LIST_RECYCLE_PLAY
from playlist import PlayList, MediaItem
from sort import Sort
from open_button import OpenButton, ScreenMenu, OpenUrl
from lastnewplayfile import LastNewPlayFile
from service import download_shooter_subtitle
from user_guide import init_user_guide
from code_to_utf_8 import auto_decode

import threading
import gtk
import os

X_VIDEO_PLAY_0_5 = 1 << 0
X_VIDEO_PLAY_1 = 1 << 1
X_VIDEO_PLAY_1_5 = 1 << 2
X_VIDEO_PLAY_2 = 1 << 3
VOLUME_BUTTON_STATE = 1
MUTE_STATE = -1
# ascept state. "16:10""16:9""4:3""1.85:1""2.35:1""默认"
ASCEPT_NORMAL_STATE = "默认"
ASCEPT_4X3_STATE = "4:3"
ASCEPT_16X9_STATE = "16:9"
ASCEPT_16X10_STATE = "16:10"
ASCEPT_1_85X1_STATE = "1.85:1"
ASCEPT_2_35X1_STATE = "2.35:1"

class PlayerBox(object):
    def __init__ (self, app, argv_path_list):
        # Init pixuf.
        self.init_system_pixbuf()
        
        
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

        self.minimize_pause_play_bool = False

        # video width_height.
        self.video_play_state = None
        self.video_width = None
        self.video_height = None
        # root window width_height.
        self.root_window_width = None
        self.root_window_height = None
        # pause setting.
        self.pause_time_id = None
        self.pause_bool = False
        self.pause_x = 0
        self.pause_y = 0                
        
        self.init_config_file()        
        self.init_last_new_play_file()
        # same name id init.
        self.get_same_name_id = None        
                
        # playlist.
        self.add_play_list_length_id = None
        self.show_or_hide_play_list_bool = False
        # Preview window.
        self.x_root = 0
        self.y_root = 0

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
        self.main_vbox_hframe.set_padding(0, 0, 2, 2)
        self.main_vbox_hframe.add(self.main_vbox)
        
        self.init_preview_window()
        self.init_app_window(app, argv_path_list)        
        self.init_media_player_screen()        
        self.init_toptip_window()
        self.init_mid_open_button()
        self.init_progressbar()
        self.init_toolbar()
        self.init_bottom_toolbar()
        self.init_playlist()
        
        # Child widget add to vbox.
        self.vbox.pack_start(self.screen_frame_event, True, True)
        self.vbox.pack_start(self.progressbar.hbox,False, False)
        # Hide playlist and show playlist widget hbox.
        self.hbox.pack_start(self.vbox, True, True)
        self.hbox.pack_start(self.play_list, False, False)

        '''Bottom control.'''
        # Hide Bottom and show Bottom.
        self.bottom_main_vbox = gtk.VBox()
        # Play control panel. stop,next,start(pause),pre button.
        bottom_padding = 2
        self.bottom_play_control_hbox_vframe = VerticalFrame(bottom_padding)
        self.bottom_play_control_hbox = gtk.HBox()
        self.bottom_play_control_hbox_vframe.add(self.bottom_play_control_hbox)
        
        self.init_show_time_label()
        self.init_play_control_panel()
        self.init_volume_button()
        self.init_play_list_button()
        
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

        self.keymap = {}
        
        self.cursor_type = None

    ##################################
    '''Init value.'''    
    ###
    def init_system_pixbuf(self):    
        # menu icon pixbuf. menupixbuf ..
        self.video_aspect_pixbuf = app_theme.get_pixbuf("screen/check_normal.png") # aspect state pixbuf.
        self.video_aspect_select_pixbuf = app_theme.get_pixbuf("screen/check_hover.png")
        self.video_aspect_type = ASCEPT_NORMAL_STATE #"默认"
        self.playwinmax_bool = True
        self.menu_concie_normal_pixbuf = app_theme.get_pixbuf("screen/menu_concise_normal.png")
        self.menu_concie_hover_pixbuf = app_theme.get_pixbuf("screen/menu_concise_hover.png")
        self.menu_window_mode_normal_pixbuf = app_theme.get_pixbuf("screen/menu_window_mode_normal.png")
        self.menu_window_mode_hover_pixbuf = app_theme.get_pixbuf("screen/menu_window_mode_hover.png")
        self.menu_play_sequence_normal_pixbuf = app_theme.get_pixbuf("screen/menu_play_sequence_normal.png")
        self.menu_play_sequence_hover_pixbuf = app_theme.get_pixbuf("screen/menu_play_sequence_hover.png")
        self.menu_full_normal_pixbuf = app_theme.get_pixbuf("screen/menu_full_normal.png") 
        self.menu_full_hover_pixbuf = app_theme.get_pixbuf("screen/menu_full_hover.png")
        self.menu_pre_normal_pixbuf = app_theme.get_pixbuf("screen/menu_pre_normal.png")
        self.menu_pre_hover_pixbuf = app_theme.get_pixbuf("screen/menu_pre_hover.png")
        self.menu_next_normal_pixbuf = app_theme.get_pixbuf("screen/menu_next_normal.png")
        self.menu_next_hover_pixbuf = app_theme.get_pixbuf("screen/menu_next_hover.png")        
        self.menu_f_seek_5_normal_pixbuf = app_theme.get_pixbuf("screen/menu_f_seek_5_normal.png")
        self.menu_f_seek_5_hover_pixbuf = app_theme.get_pixbuf("screen/menu_f_seek_5_hover.png")
        self.menu_b_seek_5_normal_pixbuf = app_theme.get_pixbuf("screen/menu_b_seek_5_normal.png")
        self.menu_b_seek_5_hover_pixbuf = app_theme.get_pixbuf("screen/menu_b_seek_5_hover.png")
        self.menu_volume_normal_pixbuf = app_theme.get_pixbuf("screen/menu_volume_normal.png")
        self.menu_volume_hover_pixbuf = app_theme.get_pixbuf("screen/menu_volume_hover.png")
        self.menu_setting_normal_pixbuf = app_theme.get_pixbuf("screen/menu_setting_normal.png")
        self.menu_setting_hover_pixbuf = app_theme.get_pixbuf("screen/menu_setting_hover.png")
        self.menu_quit_normal_pixbuf = app_theme.get_pixbuf("screen/menu_quit_normal.png")
        self.menu_quit_hover_pixbuf = app_theme.get_pixbuf("screen/menu_quit_hover.png")
        self.menu_subtitle_normal_pixbuf = app_theme.get_pixbuf("screen/menu_subtitle_normal.png")
        self.menu_subtitle_hover_pixbuf = app_theme.get_pixbuf("screen/menu_subtitle_hover.png")
        
        # play sequence pixbuf.
        self.play_sequence_select_normal_pixbuf = app_theme.get_pixbuf("screen/check_normal.png")
        self.play_sequence_select_hover_pixbuf = app_theme.get_pixbuf("screen/check_hover.png")

        # channel_select pixbuf.
        self.select_channel_normal_pixbuf = app_theme.get_pixbuf("screen/check_normal.png")
        self.select_channel_hover_pixbuf = app_theme.get_pixbuf("screen/check_hover.png")        
        
        # mute/add/sub volume pixbuf.
        self.mute_normal_pixbuf = app_theme.get_pixbuf("screen/menu_volume_menu_normal.png")
        self.mute_hover_pixbuf = app_theme.get_pixbuf("screen/menu_volume_menu_hover.png")
        self.mute_volume_pixbuf = (self.mute_normal_pixbuf, self.mute_hover_pixbuf)
        self.add_volume_normal_pixbuf = app_theme.get_pixbuf("screen/menu_volume_add_normal.png")
        self.add_volume_hover_pixbuf = app_theme.get_pixbuf("screen/menu_volume_add_hover.png")
        self.add_volume_pixbuf = (self.add_volume_normal_pixbuf, self.add_volume_hover_pixbuf)
        self.sub_volume_normal_pixbuf = app_theme.get_pixbuf("screen/menu_volume_sub_normal.png")
        self.sub_volume_hover_pixbuf = app_theme.get_pixbuf("screen/menu_volume_sub_hover.png")
        self.sub_volume_pixbuf = (self.sub_volume_normal_pixbuf, self.sub_volume_hover_pixbuf)
        
        # down subtitle pixbuf.
        self.down_sub_title_bool = False
        self.down_sub_title_norma_pixbuf = app_theme.get_pixbuf("screen/check_normal.png")
        self.down_sub_title_hover_pixbuf = app_theme.get_pixbuf("screen/check_hover.png")
        
    def init_preview_window(self):
        self.preview = PreView()
        
    def init_config_file(self):    
        # Init play memory.
        self.ini = Config(get_home_path() + "/.config/deepin-media-player/config.ini")
        # Init deepin media player config gui.
        self.config = Config(get_home_path() + "/.config/deepin-media-player/deepin_media_config.ini")
        self.config.connect("config-changed", self.modify_config_section_value)
        
    def init_last_new_play_file(self):    
        self.last_new_play_file_function = LastNewPlayFile()
        self.last_new_play_file_function.connect("get-file-name", self.get_last_new_play_file_name)
        self.the_last_new_play_file_list = []
        
    def init_app_window(self, app, argv_path_list):    
        self.app = app
        self.app.set_menu_callback(lambda button: self.theme_menu_show(button))

        self.app_width = 0  # Save media player window width.
        self.app_height = 0 # Save media player window height.
        self.argv_path_list = argv_path_list # command argv.
        self.app.titlebar.min_button.connect("clicked", self.min_window_titlebar_min_button_click)
        self.app.window.connect("destroy", self.quit_player_window)
        self.app.window.connect("configure-event", self.app_configure_hide_tool)
        self.app.window.connect("window-state-event", self.set_toolbar2_position)
        self.app.window.connect("leave-notify-event", self.hide_all_toolbars)
        # test app window
        self.app.window.connect("focus-out-event", self.set_show_toolbar_function_false)
        self.app.window.connect("focus-in-event", self.set_show_toolbar_function_true)
        #keyboard Quick key.
        self.app.window.connect("key-press-event", self.get_key_event)
        self.app.window.connect("key-release-event", self.get_release_key_event)
        self.app.window.connect("scroll_event", self.app_scroll_event, 1)
        
    def init_media_player_screen(self):            
        self.screen_frame_event = gtk.EventBox()
        self.screen_frame = gtk.Alignment()
        self.screen_frame_event.add(self.screen_frame)
        self.screen_frame_event.add_events(gtk.gdk.ALL_EVENTS_MASK)
        self.screen_frame.set(0.0, 0.0, 1.0, 1.0)
        self.screen = gtk.DrawingArea()
        self.screen_frame.add(self.screen)
        
        # Set background.
        style = self.screen_frame.get_style()
        self.screen_frame.connect("expose-event", self.draw_ascept_bg)
        self.screen_frame.modify_bg(gtk.STATE_NORMAL, style.black)
        self.screen.modify_bg(gtk.STATE_NORMAL, style.black)

        # Screen signal init.
        self.screen.add_events(gtk.gdk.ALL_EVENTS_MASK)
        self.screen.set_has_window(True)
        self.screen.set_can_focus(True)
        self.screen.set_can_default(True)
        self.screen.activate()

        self.screen.connect("realize", self.init_media_player)
        self.screen.connect("motion-notify-event", self.modify_mouse_icon)
        self.screen.connect_after("expose-event", self.draw_background)        
        
        self.screen_frame_event.connect("button-press-event", self.drag_resize_window)
        self.screen_frame_event.connect("button-press-event", self.move_media_player_window)        
        self.screen_frame_event.connect("button-release-event", self.screen_media_player_clear)        
        self.screen_frame_event.connect("motion-notify-event", self.show_and_hide_toolbar)
        self.screen.connect("configure-event", self.configure_hide_tool)                
        
    def init_toptip_window(self):
        font = self.config.get("SystemSet", "font")
        font_size = self.config.get("SystemSet", "font_size")
        self.window_tool_tip = OSDTooltip(self.screen_frame, offset_x=20, offset_y=26)
        if not font_size:
            font_size = 16
        self.window_tool_tip.change_style(font, int(font_size))
        
    def init_mid_open_button(self):
        self.open_button = OpenButton(self.screen_frame, _("Open File"), 108, 40)
        self.open_button.connect("openbutton-clicked-event", lambda w, e: self.add_file_clear())
        self.open_button.move(-14, 30)
        open_button_right_width = 32
        open_button_right_height = 40
        open_button_right_x = 56
        open_button_right_y = 30
        self.open_button_right = OpenButton(self.screen_frame, "",
                                            open_button_right_width, open_button_right_height,
                                            app_theme.get_pixbuf("screen_mid/normal_button_right.png"),
                                            app_theme.get_pixbuf("screen_mid/hover_button_right.png"),
                                            app_theme.get_pixbuf("screen_mid/press_button_right.png"))
        self.open_button_right.connect("openbutton-clicked-event", self.open_button_popup_screen_menu)        
        self.open_button_right.move(open_button_right_x, open_button_right_y)
        menu_item = [
            (app_theme.get_pixbuf("screen_mid/screen_menu_open_dir.png"), _("Open Directory"), self.add_file_dir_clear),
            # (app_theme.get_pixbuf("screen_mid/screen_menu_open_cdrom.png"),"打开光盘", None),
            (app_theme.get_pixbuf("screen_mid/screen_menu_open_url.png"), _("Open URL"), self.open_url_dialog_window),
            ]
        self.screen_pop_menu = ScreenMenu(self.screen_frame, menu_item)
        self.screen_pop_menu.size(self.screen_pop_menu.width, self.screen_pop_menu.height - 26)
        
    def init_progressbar(self):
        self.progressbar = ProgressBar()
        self.progressbar.window_mode_state = 0
        # Progressbar signal init.
        NORMAL_WINDOW_STATE = 1
        self.progressbar.pb.connect("motion-notify-event", 
                                    self.progressbar_player_drag_pos_modify, 
                                    self.progressbar, NORMAL_WINDOW_STATE)
        self.progressbar.pb.connect("button-press-event", 
                                    self.progressbar_player_point_pos_modify, 
                                    self.progressbar, NORMAL_WINDOW_STATE)
        self.progressbar.pb.connect("button-release-event", self.progressbar_set_point_bool, self.progressbar)
        self.progressbar.pb.connect("enter-notify-event", self.show_preview_enter)
        self.progressbar.pb.connect("leave-notify-event", self.hide_preview_leave)
        
    def init_toolbar(self):    
        self.toolbar = ToolBar()
        self.toolbar.toolbar_full_button.connect("clicked",    self.full_play_window)
        self.toolbar.toolbar_common_button.connect("clicked",  self.show_window_widget)
        self.toolbar.toolbar_concise_button.connect("clicked", self.hide_window_widget)
        self.toolbar.toolbar_above_button.connect("clicked",   self.set_window_above)
        self.toolbar.toolbar_1X_button.connect("clicked", lambda w: self.set_1x_video_play())
        self.toolbar.toolbar_2X_button.connect("clicked", lambda w: self.set_2x_video_play())
        
    def init_bottom_toolbar(self):
        bottom_toolbar_height = 50
        FULL_WINDOW_STATE = 2
        self.bottom_toolbar = BottomToolBar()
        self.bottom_toolbar.panel.connect("expose-event", 
                                          self.toolbar2_panel_expose)
        self.bottom_toolbar.panel.set_size_request(1, bottom_toolbar_height) # Set bottom_toolbar height.                
        self.bottom_toolbar.panel.connect("scroll-event", 
                                          self.app_scroll_event, FULL_WINDOW_STATE) # 2->bottom_toolbar
        self.bottom_toolbar.panel.connect("button-press-event", 
                                          self.drag_resize_window) # draw resize window.
        self.bottom_toolbar.panel.connect("motion-notify-event", 
                                          self.modify_mouse_icon)
        self.bottom_toolbar.panel.connect("motion-notify-event", 
                                          self.set_keep_window_toolbar2)
        self.bottom_toolbar.progressbar.pb.connect("motion-notify-event",
                                                   self.progressbar_player_drag_pos_modify,
                                                   self.bottom_toolbar.progressbar, FULL_WINDOW_STATE)
        self.bottom_toolbar.progressbar.pb.connect("button-press-event",
                                                   self.progressbar_player_point_pos_modify,
                                                   self.bottom_toolbar.progressbar, FULL_WINDOW_STATE)
        self.bottom_toolbar.progressbar.pb.connect("button-release-event",
                                                   self.progressbar_set_point_bool,
                                                   self.bottom_toolbar.progressbar)
        self.bottom_toolbar.progressbar.pb.connect("enter-notify-event", self.show_preview_enter)
        self.bottom_toolbar.progressbar.pb.connect("leave-notify-event", self.hide_preview_leave)

        # play_control_panel.
        self.bottom_toolbar.play_control_panel.stop_button.connect("clicked", self.stop_button_clicked)
        self.bottom_toolbar.play_control_panel.pre_button.connect("clicked", self.pre_button_clicked)
        self.bottom_toolbar.play_control_panel.start_button.connect("clicked", 
                                                                 self.start_button_clicked, 
                                                                 FULL_WINDOW_STATE)
        self.bottom_toolbar.play_control_panel.next_button.connect("clicked", self.next_button_clicked)
        self.bottom_toolbar.play_control_panel.open_button.connect("clicked", self.open_button_clicked)

        # bottom toolbar volume button.
        self.bottom_toolbar.volume_button.value = 100
        self.bottom_toolbar.volume_button.connect("volume-state-changed", 
                                                  self.volume_button_get_value_event, 
                                                  FULL_WINDOW_STATE)
    
    def init_playlist(self):    
        self.play_list_dict = {} # play list dict type.
        self.play_list = PlayList()
        self.play_list.list_view.connect("double-click-item", 
                                         self.double_play_list_file)
        self.play_list.list_view.connect("delete-select-items", 
                                         self.delete_play_list_file)
        self.play_list.list_view.connect("button-press-event", 
                                         self.show_popup_menu)
        self.play_list.list_view.connect("single-click-item", 
                                         self.open_current_file_dir_path)
        self.play_list.list_view.connect("motion-notify-item", 
                                         self.open_current_file_dir_path)
        self.play_list.play_list_control_panel.add_button.connect("clicked", lambda w: self.add_file())
        self.play_list.play_list_control_panel.delete_button.connect("clicked", lambda w: self.del_index())
        
    def init_show_time_label(self):    
        # padding=0, xalign=1, yalign=0.0, xscale=0.0, yscale=0.0
        self.show_time_label_hframe = HorizontalFrame()
        self.show_time_label = ShowTime()
        self.show_time_label.time_box.set_size_request(110, -1)
        self.show_time_label.time_font1 = "00:00:00" + " / "
        self.show_time_label.time_font2 = "00:00:00"        
        self.show_time_label.set_time_font(self.show_time_label.time_font1 , self.show_time_label.time_font2)
        self.show_time_label_hframe.add(self.show_time_label.time_box)
        self.show_time_label_hframe.set(0, 0, 1, 1)
        self.show_time_label_hframe.set_padding(0, 0, 10, 0)
        
    def init_play_control_panel(self):            
        self.play_control_panel = PlayControlPanel()
        self.play_control_panel_hframe = self.play_control_panel.hbox_hframe
        self.play_control_panel_hframe.set(1, 0.5, 0, 0)
        self.play_control_panel_hframe.set_padding(0, 1, 0, 0)
        self.play_control_panel.stop_button.connect("clicked", self.stop_button_clicked) # stop play.
        self.play_control_panel.pre_button.connect("clicked", self.pre_button_clicked) # pre play.
        # 1 -> play_control_panel
        self.play_control_panel.start_button.connect("clicked", self.start_button_clicked, 1) # start play or pause play.
        self.play_control_panel.next_button.connect("clicked", self.next_button_clicked) # next play.
        self.play_control_panel.open_button.connect("clicked", self.open_button_clicked) # show open window.
        
    def init_volume_button(self):
        self.volume_button_hframe = HorizontalFrame()
        self.volume_button = VolumeButton(volume_y = 14, press_emit_bool = True)
        self.volume_button.value = 100
        self.volume_button.connect("volume-state-changed", self.volume_button_get_value_event, 1) # 1 -> play_control_panel
        self.volume_button.set_size_request(92, 40)
        self.volume_button_hframe.add(self.volume_button)
        self.volume_button_hframe.set(1, 0, 0, 0)
        self.volume_button_hframe.set_padding(0, 0, 0, 0)        
        
    def init_play_list_button(self):            
        self.play_list_button_hframe = HorizontalFrame()
        self.play_list_button = PlayListButton()
        self.play_list_button.button.connect("toggled", self.play_list_button_clicked)
        self.play_list_button_hframe.add(self.play_list_button.button)
        self.play_list_button_hframe.set(0, 0, 1.0, 1.0)
        self.play_list_button_hframe.set_padding(9, 9, 0, 20)
        
    # 123456
    ####################################################    
        
    def get_last_new_play_file_name(self, LastNewPlayFile, file_name):    
        if file_name not in self.mp.playList:
            self.mp.add_play_file(file_name) 
            self.clear_play_list_bool = True
        
    def open_button_popup_screen_menu(self, widget, event):
        x, y, w, h = self.screen_frame.allocation
        
        width = w/2 - self.screen_pop_menu.width/2 + 2
        height = h/2 + self.screen_pop_menu.height /2 + 50
        
        if not self.screen_pop_menu.show_menu_bool:
            self.screen_pop_menu.show_menu(int(width), int(height))
        else:
            self.screen_pop_menu.hide_menu()
                            
    def messagebox(self, text):
        self.window_tool_tip.show(text)

    def toolbar2_panel_expose(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        x, y, w, h = rect.x, rect.y, rect.width, rect.height
        # Draw background.
        window_rect = self.app.window.get_allocation()
        toolbar_rect = widget.get_toplevel().get_allocation()
        with cairo_state(cr):
            cr.translate(0, -(window_rect.height - toolbar_rect.height))
            skin_config.render_background(cr, widget, x, y, 0, window_rect.height - toolbar_rect.height)

        widget.propagate_expose(widget.get_child(), event)
        return True

    def modify_config_section_value(self, Config, section, argv, value):
        if section == "SystemSet" and (argv in ["font", "font_size"]):
            font = Config.get(section, "font")
            font_size = Config.get(section, "font_size")
            self.window_tool_tip.change_style(font, int(font_size))
        
    def set_show_toolbar_function_true(self, widget, event):
        self.show_toolbar_focus_bool = True

    def set_show_toolbar_function_false(self, widget, event):
        self.show_toolbar_focus_bool = False
        self.toolbar.hide_toolbar()
        self.bottom_toolbar.hide_toolbar2()

    def set_show_toolbar_bool(self, widget, event):
        self.show_toolbar_bool = False

    def hide_all_toolbars(self, widget, event):
        if not self.show_toolbar_bool:
            self.toolbar.hide_toolbar()
            self.bottom_toolbar.hide_toolbar2()

    def modify_mouse_icon(self, widget, event): # screen: motion-notify-event
        w = widget.allocation.width
        h = widget.allocation.height
        bottom_padding = 10

        if (w - bottom_padding <= event.x <= w) and (h - bottom_padding <= event.y <= h):
            if "MplayerView" != type(widget).__name__:
                drag = gtk.gdk.BOTTOM_RIGHT_CORNER
                widget.window.set_cursor(gtk.gdk.Cursor(drag))                
                self.cursor_type = drag
        elif self.cursor_type != None:
            widget.window.set_cursor(None)
            self.app.window.window.set_cursor(None)
            
            self.cursor_type = None

    def drag_resize_window(self, widget, event): # screen: button-press-event -> drag resize window.
        self.screen.grab_focus()

        w = widget.allocation.width
        h = widget.allocation.height
        bottom_padding = 10
        drag_bool = False

        # show scrren right menu.        
        if is_right_button(event):
            if not self.open_button.leave_bool and not self.open_button_right.leave_bool and not self.screen_pop_menu.leave_bool:
                self.screen_right_key_menu(event)
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

    def app_scroll_event(self, widget, event, type_bool):
        config_type = self.config.get("OtherKey", "mouse_wheel_event")
        other_key_bool = self.config.get("OtherKey", "other_key_bool")
        if not (_("Disabled") == config_type or other_key_bool.lower() == "false"): # seek back.
            volume_value = 0
            volume_step = 5
            if event.direction == gtk.gdk.SCROLL_UP:
                if self.mode_state_bool or self.full_bool:
                    volume_value = min(self.mp.volume + volume_step, 100)
                else:    
                    volume_value = min(self.volume_button.value + volume_step, 100)
                    
                self.volume_button.value = volume_value
                self.bottom_toolbar.volume_button.value = volume_value
            elif event.direction == gtk.gdk.SCROLL_DOWN:
                if self.mode_state_bool or self.full_bool:                    
                    volume_value = max(self.mp.volume - volume_step, 0)
                else:    
                    volume_value = max(self.volume_button.value - volume_step, 0)
                    
                self.volume_button.value = volume_value
                self.bottom_toolbar.volume_button.value = volume_value
                                    
            if volume_value != self.mp.volume:
                self.mp.setvolume(volume_value)
                    
            self.messagebox("%s:%s%s"%(_("Volumn"), str(int(volume_value)), "%"))
            
    def volume_button_get_value_event(self, volume_button, value, volume_state, volume_bit):
        if MUTE_STATE == volume_state: # -1 -> stop play
            if self.mp:                
                if STARTING_PLAY == self.mp.state: # 1 -> start play
                    self.mp.nomute()                                       
                else:    
                    self.mp.volumebool = True # mute: True  no mute: False.
                self.messagebox(_("Mute: enabled"))    
        else:
            if self.mp:
                if STARTING_PLAY == self.mp.state:                    
                    self.mp.offmute()                                     
                    self.mp.setvolume(value)                    
                    self.messagebox(str("%s:%s%s"%(_("Volumn"), str(value), "%")))
                else:    
                    self.mp.volumebool = False
                    self.messagebox(str("%s:%s%s"%(_("Volumn"), str(value), "%")))
                    
        if VOLUME_BUTTON_STATE == volume_bit: # volume_bit: 1-> volume_button , 2-> volume_button of bottom_toolbar
            self.bottom_toolbar.volume_button.value = value
        else:
            self.volume_button.value = value
            
    def init_config_key(self):
        self.keymap = {}
        # Init Config keys.
        
        # open file key init.(left)        
        play_control_bool = self.config.get("PlayControl", "play_control_bool")
        other_key_bool = self.config.get("OtherKey",    "other_key_bool")
        
        # [PlayControl] Init.
        if play_control_bool.lower() == "true":    
            for section, argv, connect_fun in [
                ("PlayControl", "open_file_key", lambda : self.show_open_dialog_window(False)),
                ("PlayControl", "open_file_dir_key", lambda : self.show_open_dir_dialog_window(False)),
                ("PlayControl", "play_or_pause_key", self.key_space),
                ("PlayControl", "seek_key",  self.key_right),
                ("PlayControl", "back_key",  self.key_left),
                ("PlayControl", "full_key",  self.key_return),
                ("PlayControl", "pre_a_key",  self.key_pre),
                ("PlayControl", "next_a_key", self.key_next),
                ("PlayControl", "add_volume_key", self.key_add_volume),
                ("PlayControl", "sub_volume_key", self.key_sub_volume),
                ("PlayControl", "mute_key",       self.key_set_mute),
                ("PlayControl", "concise_key",    self.key_concise)
                ]:    
                config_key = self.config.get(section, argv)
                self.keymap[config_key] = connect_fun        
              
            self.keymap["Escape"] = self.key_quit_full        
              
        # [OtherKey].
        if other_key_bool.lower() == "true":  
            for section, argv, connect_fun in [
                ("OtherKey", "add_brightness_key", self.key_add_brightness),
                ("OtherKey", "sub_brightness_key", self.key_sub_brightness),
                ("OtherKey", "inverse_rotation_key", self.key_inverse_rotation_key),
                ("OtherKey", "clockwise_key",   self.key_clockwise),
                ("OtherKey", "sort_image_key",  self.key_sort_image),
                ("OtherKey", "switch_audio_track_key",  self.key_switch_audio_track),
                ("OtherKey", "load_subtitle_key",  self.key_load_subtitle),
                ("OtherKey", "subtitle_delay_key", self.key_subtitle_delay),
                ("OtherKey", "subtitle_advance_key", self.key_subtitle_advance),
                ]:
                config_key = self.config.get(section, argv)
                self.keymap[config_key] = connect_fun                                    
          
    def get_key_event(self, widget, event): # app: key-release-event
        keyval_name = get_keyevent_name(event)
        # Init config keys.
        self.init_config_key()
        
        if self.keymap.has_key(keyval_name):
            self.keymap[keyval_name]()
            
        return False
        
    def key_subtitle_advance(self):
        # print "subtitle advance..."
        pass

    def key_subtitle_delay(self):
        # print "subtitle delay..."
        pass

    def key_load_subtitle(self):
        # print "load subtitle..."
        pass

    def key_switch_audio_track(self):
        # print "key switch audio track..."
        pass

    def key_sort_image(self):
        # print "sort image..."
        if STARTING_PLAY == self.mp.state: 
            scrot_bool = self.config.get("ScreenshotSet", "current_show_sort")
            
            save_clipboard_bool = self.config.get("ScreenshotSet", "save_clipboard")
            save_file_bool = self.config.get("ScreenshotSet", "save_file")

            save_path = self.config.get("ScreenshotSet", "save_path")
            save_type = self.config.get("ScreenshotSet", "save_type")
            
            if save_path[0] == "~":
                save_path = get_home_path() + save_path[1:]                    
                    
            if save_file_bool == "True":
                if scrot_bool.lower() == "true":
                    self.scrot_current_screen_pixbuf(save_path + "/%s-%s"%(self.get_player_file_name(self.mp.path), self.mp.pos_num), save_type)
                    self.messagebox(_("Screenshot Saved"))
                else:    
                    self.mp.preview_scrot(self.mp.pos_num, save_path + "/%s-%s"%(self.get_player_file_name(self.mp.path), self.mp.pos_num) + save_type)
                    self.messagebox(_("Screenshot Saved"))
                    
            if save_clipboard_bool == "True": # save clipboard
                clipboard_path = "/tmp" + "/%s-%s"%(self.get_player_file_name(self.mp.path), self.mp.pos_num) + save_type
                if scrot_bool.lower() == "true":
                    clipboard_path = "/tmp" + "/%s-%s"%(self.get_player_file_name(self.mp.path), self.mp.pos_num)
                    self.scrot_current_screen_pixbuf(clipboard_path, save_type)
                    clipboard_path += save_type
                else:
                    self.mp.preview_scrot(self.mp.pos_num, clipboard_path)
                    
                pixbuf_clipboard = gtk.gdk.pixbuf_new_from_file(clipboard_path)
                clipboard = gtk.Clipboard()
                clipboard.set_image(pixbuf_clipboard)
                self.messagebox(_("Screenshot Copied to Clipboard"))

    def key_clockwise(self):
        # print "clockwise..."
        pass

    def key_inverse_rotation_key(self):
        # print "inverse rotation..."
        pass
        

    def key_sub_brightness(self):
        # print "sub brightness..."
        pass

    def key_add_brightness(self):
        # print "add brightness..."
        pass

    def key_concise(self):
        # print "concise..."
        if self.mode_state_bool:
            self.show_window_widget(self.toolbar.toolbar_common_button)
        else:
            self.hide_window_widget(self.toolbar.toolbar_concise_button)

    def key_add_volume(self):
        # print "add volume..."
        self.key_set_volume(True)

    def key_sub_volume(self):
        # print "sub volume..."
        self.key_set_volume(False)
        
    def key_set_volume(self, increase_volume=True):
        volume_step = 5
        
        # Set volume.
        if increase_volume:
            if self.mode_state_bool:
                self.mp.volume = min(self.mp.volume + volume_step, 100)
                self.bottom_toolbar.volume_button.value = self.mp.volume
            else:
                volume_value = min(self.volume_button.value + volume_step, 100)
                self.volume_button.value = volume_value
                self.bottom_toolbar.volume_button.value = volume_value
        else:
            if self.mode_state_bool:                    
                self.mp.volume = max(self.mp.volume - volume_step, 0)
                self.bottom_toolbar.volume_button.value = self.mp.volume
            else:    
                volume_value = max(self.volume_button.value - volume_step, 0)
                self.volume_button.value = volume_value
                self.bottom_toolbar.volume_button.value = volume_value
                
    def get_release_key_event(self, widget, event):
        keyval_name = get_keyevent_name(event)
        # add volume key init.
        add_volume_key = self.config.get("PlayControl", "add_volume_key")
        if add_volume_key == keyval_name:            
            if self.mode_state_bool:
                volume_value = self.mp.volume
            else:    
                volume_value = self.volume_button.value
                
            self.mp.setvolume(volume_value)
            self.messagebox("%s:%s%s"%(_("Volumn"), int(volume_value), "%"))
            
        # sub volume key init.
        sub_volume_key = self.config.get("PlayControl", "sub_volume_key")
        if sub_volume_key == keyval_name:
            if self.mode_state_bool:
                volume_value = self.mp.volume
            else:    
                volume_value = self.volume_button.value
                
            self.mp.setvolume(volume_value) 
            self.messagebox("%s:%s%s"%(_("Volumn"),int(volume_value), "%"))
        
    def key_set_mute(self):
        # print "key set mute..."        
        if self.mp.volumebool:
            self.volume_button.set_volume_mute(False)
            if self.mp.state:
                self.mp.offmute()
            else:    
                self.mp.volumebool = False
            self.messagebox("%s:%s%s"%(_("Volumn"), str(int(self.mp.volume)), "%"))
        else:
            self.volume_button.set_volume_mute()
            
            if self.mp.state:
                self.mp.nomute()
            else:    
                self.mp.volumebool = True
            self.messagebox(_("Mute: enabled"))

    def key_pre(self):
        # print "pre a key..."
        self.pre_button_clicked(self.play_control_panel.pre_button)

    def key_next(self):
        # print "next a key..."
        self.next_button_clicked(self.play_control_panel.next_button)

    def key_right(self):
        # print "right key..."
        self.mp.fseek(5)
    
    def key_left(self):
        # print "left key..."
        self.mp.bseek(5)
        
    def key_space(self):
        # print "space key..."
        self.virtual_set_start_button_clicked()

    def key_return(self):
        # print "return key.."
        self.full_play_window(self.app.window)
        self.toolbar.toolbar_full_button.flags = not self.toolbar.toolbar_full_button.flags
        
    def key_quit_full(self):
        # print "quit full key..."
        if self.full_bool: # Full player window.        
            self.set_window_quit_full()
        else:    
            if self.mode_state_bool:
                self.show_window_widget(self.toolbar.toolbar_common_button)
        
        if not self.toolbar.toolbar_full_button.flags:
            self.toolbar.toolbar_full_button.flags = not self.toolbar.toolbar_full_button.flags
            
            
    '''play list button'''
    def play_list_button_clicked(self, widget): # play list button signal:clicked.
        if widget.get_active():
            self.play_list.show_play_list()
            self.show_or_hide_play_list_bool = True
        else:
            self.play_list.hide_play_list()
            self.show_or_hide_play_list_bool = False

    '''Play list control'''
    def delete_play_list_file(self, list_view, list_item):
        # delete file of play list.
        play_list_dict_save = self.play_list_dict
        for list_item_i in list_item:
            self.mp.del_playlist(play_list_dict_save[list_item_i.title])

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
        path_thread_id.setDaemon(True)
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
                self.ini.save()
            i.emit_redraw_request()

    def add_play_list_time(self, path): # all.
        '''play list add play file.'''
        self.play_list_dict[self.get_player_file_name(path)] = path
        media_item = [MediaItem(self.get_player_file_name(path), str("        "))]
        self.play_list.list_view.add_items(media_item)

        if self.clear_play_list_bool:
            self.clear_play_list_bool = False
            if STARTING_PLAY == self.mp.state:
                self.mp.quit()
            self.start_button_clicked(self.play_control_panel.start_button, 1)
            self.play_list.list_view.set_highlight(self.play_list.list_view.items[0])
        return False

    def double_play_list_file(self, list_view, list_item, colume, offset_x, offset_y):
        '''double play file.'''
        if self.mp:
            if STARTING_PLAY == self.mp.state:
                self.mp.quit()

        # play file.
        self.mp.play(self.play_list_dict[list_item.title])
        self.mp.play_list_num = list_item.get_index()

        self.play_control_panel.start_button.start_bool = False
        self.play_control_panel.start_button.queue_draw()
        self.bottom_toolbar.play_control_panel.start_button.start_bool = False
        self.bottom_toolbar.play_control_panel.start_button.queue_draw()

        self.play_list.list_view.set_highlight(list_item)

    def hide_preview_function(self, widget, event):
        '''Hide preview window.'''
        self.hide_preview_leave(widget, event)

    '''play control panel.'''
    def stop_button_clicked(self, widget):
        self.messagebox(_("Stop"))
        self.mp.quit()

    def start_button_clicked(self, widget, start_bit):
        '''start or pause'''
        if self.mp.state == STOPING_PLAY:
            self.mp.next() # Test pause.
            self.play_control_panel.start_button.start_bool = False
            self.play_control_panel.start_button.queue_draw()
            self.bottom_toolbar.play_control_panel.start_button.start_bool = False
            self.bottom_toolbar.play_control_panel.start_button.queue_draw()
            if STOPING_PLAY == self.mp.state: # NO player file.
                self.play_control_panel.start_button.start_bool = True # start_button modify play state.
                self.play_control_panel.start_button.queue_draw()
                self.bottom_toolbar.play_control_panel.start_button.start_bool = True
                self.bottom_toolbar.play_control_panel.start_button.queue_draw()
                self.messagebox(_("No Media Selected"))
                self.show_open_dialog_window(False)
        else:
            if 1 == start_bit:
                self.bottom_toolbar.play_control_panel.start_button.start_bool = self.play_control_panel.start_button.start_bool
                self.bottom_toolbar.play_control_panel.start_button.queue_draw()
            elif 2 == start_bit:
                self.play_control_panel.start_button.start_bool = self.bottom_toolbar.play_control_panel.start_button.start_bool
                self.play_control_panel.start_button.queue_draw()

            gtk.timeout_add(50, self.start_button_time_pause)

    def start_button_time_pause(self): # start_button_clicked.
        if self.mp.pause_bool:
            self.messagebox(_("Play"))
            self.mp.start_play()            
        else:
            self.messagebox(_("Pause"))
            self.mp.pause()
        return  False

    def pre_button_clicked(self, widget):
        '''prev.'''
        if (len(self.mp.playList) > 1):
            self.mp.pre()
            self.messagebox(_("Prev"))
            
    def next_button_clicked(self, widget):
        '''next'''
        if (len(self.mp.playList) > 1):
            self.mp.next()
            self.messagebox(_("Next"))

    def open_button_clicked(self, widget):        
        self.show_open_dialog_window(False)
        
    def show_open_dir_dialog_window(self, open_button=True):
        open_dialog = gtk.FileChooserDialog(_("Select Directory"),
                                            None,
                                            gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                            (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                             gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        open_dialog.set_current_folder(get_home_path())
        res = open_dialog.run()

        if res == gtk.RESPONSE_OK:
            path_string = open_dialog.get_filename()
            if path_string:
                if not open_button:
                    self.mp.clear_playlist()
                    self.clear_play_list_bool = True 
                self.try_play(path_string)
        open_dialog.destroy()

    def show_open_dialog_window(self, open_button=True):
        open_dialog = gtk.FileChooserDialog(_("Select Files"),
                                            None,
                                            gtk.FILE_CHOOSER_ACTION_OPEN,
                                            (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                             gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        open_dialog.set_current_folder(get_home_path())
        res = open_dialog.run()

        if res == gtk.RESPONSE_OK:
            path_string = open_dialog.get_filename()
            if path_string:
                if not open_button:
                    self.mp.clear_playlist()
                    self.clear_play_list_bool = True 
                self.try_play(path_string)
            
                
        open_dialog.destroy()

    def try_play(self, path_string):
        # print path_string
        if os.path.isdir(path_string):
            path_threads(path_string, self.mp)

        # Add .dmp.
        if self.mp.find_dmp(path_string):
            self.mp.load_playlist(path_string)

        # Add play file.
        if os.path.isfile(path_string):
            if self.mp.find_file(path_string):                
                self.mp.add_play_file(path_string)
            else:    
                self.messagebox(_("Failed to Open Selected File"))

    def show_bottom(self):
        if [] == self.bottom_main_vbox.get_children():
            self.bottom_main_vbox.add(self.bottom_play_control_hbox_vframe_event_box)

    def hide_bottom(self):
        if [] != self.bottom_main_vbox.get_children():
            self.bottom_main_vbox.foreach(self.bottom_main_vbox.remove(self.bottom_play_control_hbox_vframe_event_box))
                
    '''Init media player.'''
    def init_media_player(self, widget):
        '''Init deepin media player.'''
        # Init root window width_height.
        self.app_width = self.app.window.get_allocation()[2]
        self.app_height = self.app.window.get_allocation()[3]
        self.root_window_width = self.app.window.get_screen().get_width() # save root widnwo screen width.
        self.root_window_height = self.app.window.get_screen().get_height() # save roo widnow screen height.
                                
        self.init_play_list_state()        
        
        self.screen.queue_draw()
        #self.unset_flags()
        self.mp = Mplayer(widget.window.xid)        
        
        # Init darg file signal.
        drag_connect(self.screen, self.mp, self.play_list.list_view, True)
        drag_connect(self.play_list.list_view, self.mp, self.play_list.list_view, False)
        
        # Init media player event.
        self.mp.connect("get-time-pos", self.get_time_pos)
        self.mp.connect("get-time-length", self.get_time_length)
        self.mp.connect("play-start", self.media_player_start)
        self.mp.connect("play-end", self.media_player_end)
        self.mp.connect("play-next", self.media_player_next)
        self.mp.connect("play-pre", self.media_player_pre)
        self.mp.connect("play-fseek", self.media_player_fseek)
        self.mp.connect("play-bseek", self.media_player_bseek)
        self.mp.connect("add-path", self.add_play_list)
        self.mp.connect("clear-play-list", self.clear_play_list)
        self.mp.connect("same-name-event", self.get_same_name_event)
        
        self.mp.play_list_state = ORDER_PLAYING_STATE # 1 # init play mode.
        
        self.init_volume_value()  # init volume.
        
        # Init last new play file.
        self.the_last_new_play_file_list = self.last_new_play_file_function.set_file_time(self.mp.path)
        
        gio_format = Format()
        
        # argv path list.
        for file_path in self.argv_path_list:
            if self.mp.find_dmp(file_path): # .dmp add play file.
                self.mp.load_playlist(file_path)
            elif os.path.isfile(file_path): # add play file.
                self.mp.add_play_file(file_path)
            elif os.path.isdir(file_path): # add dir.
                path_threads(file_path, self.mp)
            elif gio_format.get_html_bool(file_path):
                break
                
            if len(self.argv_path_list) > 0: # Set play bool.
                self.clear_play_list_bool = True
   
    def init_play_list_state(self):            
        play_list_bool = self.config.get("Window", "playlist")
        
        self.play_list.hide_play_list() # Hide play list.
        if play_list_bool:
            if play_list_bool.lower() == "true":
                self.play_list.show_play_list()
                self.play_list_button.button.set_active(True)
            else:
                self.play_list.hide_play_list()
                self.play_list_button.button.set_active(False)
        
    def init_volume_value(self):            
        volume_value = self.config.get("Window",     "volume")
        volume_mute_bool = self.config.get("Window", "mute")
        MUTE_STATE = "-1"

        if volume_value:            
            self.volume_button.value = int(volume_value)
            self.bottom_toolbar.volume_button.value = int(volume_value)
            self.mp.volume = int(volume_value)
            
        if volume_mute_bool == MUTE_STATE: # set mute.
            self.volume_button.set_volume_mute()
            self.bottom_toolbar.volume_button.set_volume_mute()                        
            
            if self.mp.state:
                self.mp.nomute()
            else:    
                self.mp.volumebool = True
                
    def clear_play_list(self, mplayer, mp_bool):
        self.play_list.list_view.clear()
        self.play_list_dict = {}
        self.clear_play_list_bool = True

    def draw_ascept_bg(self, widget, event):
        '''draw screen frame bg'''
        cr, x, y, w, h = allocation(widget)
        cr.rectangle(x, y, w, h)
        cr.fill()
        return True

    def draw_background(self, widget, event):
        '''Draw screen mplayer view background.'''
        cr, x, y, w, h = allocation(widget)
      
        if self.mp and STARTING_PLAY == self.mp.state:
            if self.mp.state and self.mp.vide_bool: # vide file.                
                self.unset_flags()
                self.open_button.visible_bool = True
                self.open_button.visible_bool = True
                self.screen_pop_menu.visible_bool = True
                                
                self.open_button.leave_bool = False
                self.open_button_right.leave_bool = False
                self.screen_pop_menu.leave_bool = False
                
                return False
            
        self.set_flags()        

        cr.set_source_rgb(*color_hex_to_cairo("#0D0D0D")) # 1f1f1f
        cr.rectangle(0, 0, w, h)
        cr.fill()

        # Draw player image.
        pixbuf = app_theme.get_pixbuf("player.png").get_pixbuf()
        draw_pixbuf(
            cr,
            pixbuf,
            x + (w - pixbuf.get_width()) / 2,
            (h - pixbuf.get_height()) / 2)
        
        if not self.mp.state:
            self.open_button.visible_bool = False
            self.open_button_right.visible_bool = False
            self.screen_pop_menu.visible_bool = False            

            self.screen_pop_menu.leave_bool = False
            self.open_button.draw_open_button(widget, event)
            self.open_button_right.draw_open_button(widget, event)
            self.screen_pop_menu.draw_screen_menu(widget, event)
        else:    
            self.open_button.visible_bool = True
            self.open_button_right.visible_bool = True
            self.screen_pop_menu.visible_bool = True
            
        return True

    def min_window_titlebar_min_button_click(self, widget):
        '''app titlebar min_button'''
        config_bool = self.config.get("SystemSet", "minimize_pause_play")
        if config_bool and "true" == config_bool.lower():
            self.virtual_set_start_button_clicked()
            gtk.timeout_add(500, self.set_min_pause_bool_time)

    def set_min_pause_bool_time(self):
        self.minimize_pause_play_bool = True
        
        return False

    def quit_player_window(self, widget):
        '''Quit player window.'''
        self.quit_window_save_config()
        if self.mp:
            if self.mplayer_pid:
                os.system("kill %s" %(self.mplayer_pid))
            self.mp.quit()
            
        self.app.window.set_opacity(0)
        self.app.window.set_visible(True)
            
    def quit_window_save_config(self):
        self.config.set("Window", "playlist", self.show_or_hide_play_list_bool) # save open play list state.
        self.config.set("Window", "width",    self.app.window.allocation.width) # save app window height.
        self.config.set("Window", "height",   self.app.window.allocation.height) # save app window width.
        self.config.set("Window", "volume",   int(self.volume_button.value)) # save volume value.        
        self.config.set("Window", "mute",     self.volume_button.volume_state) # save volume mute state.            
        
        self.config.save()

    def set_toolbar2_position(self, widget, event): #app window-state-event
        self.bottom_toolbar.show_toolbar2()
        self.toolbar.panel.move(self.panel_x + 1, self.panel_y + self.app.titlebar.allocation[3])
        self.bottom_toolbar.panel.move(
            self.panel_x + 1, 
            self.panel_y + self.screen_frame.allocation.height - self.bottom_toolbar.panel.allocation.height)
        self.bottom_toolbar.hide_toolbar2()

    # ToolBar control function.
    def app_configure_hide_tool(self, widget, event): #app: configure-event.
        self.toolbar.panel.hide_all()
        self.show_toolbar_bool = False

        self.panel_x, self.panel_y = self.screen_frame.window.get_root_origin()
        if self.mode_state_bool: # Concise mode.
            self.toolbar.panel.move(self.panel_x, self.panel_y)
            self.bottom_toolbar.panel.move(
                self.panel_x, 
                self.panel_y + (widget.allocation[3] - self.bottom_toolbar.panel.allocation[3]))
        else:    # common mode.
            self.toolbar.panel.move(
                self.panel_x + 1, 
                self.panel_y + self.app.titlebar.allocation[3])
            self.bottom_toolbar.panel.move(
                self.panel_x + 1, 
                self.panel_y + self.screen_frame.allocation.height - self.bottom_toolbar.panel.allocation.height)

        if self.full_bool:
            self.toolbar.panel.move(self.panel_x, self.panel_y)
        
        self.set_toolbar_show_opsition()
        # Hide preview window.
        self.hide_preview_function(widget, event)

        # Set minimize pause play.
        if self.minimize_pause_play_bool:
            config_bool = self.config.get("SystemSet", "minimize_pause_play")            
            if config_bool and "true" == config_bool.lower():
                self.virtual_set_start_button_clicked()
                self.minimize_pause_play_bool = False

        if STARTING_PLAY == self.mp.state:            
            self.set_ascept_function()

    def set_restart_aspect(self):
        self.screen_frame.set(0.0, 0.0, 1.0, 1.0)
        if self.playwinmax_bool and self.video_aspect_type != ASCEPT_NORMAL_STATE:
            self.mp.playwinmax()
            self.playwinmax_bool = False

        self.video_aspect_type = ASCEPT_NORMAL_STATE

    def set_4X3_aspect(self):    # munu callback
        if STARTING_PLAY == self.mp.state:
            self.video_aspect_type = ASCEPT_4X3_STATE # "4:3"
            self.set_ascept_function()

    def set_16X9_aspect(self):
        if STARTING_PLAY == self.mp.state:
            self.video_aspect_type = ASCEPT_16X9_STATE # "16:9"
            self.set_ascept_function()

    def set_16X10_aspect(self):
        if STARTING_PLAY == self.mp.state:
            self.video_aspect_type = ASCEPT_16X10_STATE # "16:10"
            self.set_ascept_function()

    def set_1_85X1_aspect(self):
        if STARTING_PLAY == self.mp.state:
            self.video_aspect_type = ASCEPT_1_85X1_STATE # "1.85:1"
            self.set_ascept_function()

    def set_2_35X1_aspect(self):
        if STARTING_PLAY == self.mp.state:
            self.video_aspect_type = ASCEPT_2_35X1_STATE # "2.35:1"
            self.set_ascept_function()

    def set_ascept_function(self):
        if not self.playwinmax_bool and self.video_aspect_type != ASCEPT_NORMAL_STATE:
            self.mp.playwinmax()
            self.playwinmax_bool = True

        # Set screen frame ascept.
        x, y, w, h = self.screen_frame.allocation
        video_aspect = 0
        if self.video_aspect_type == ASCEPT_4X3_STATE: #"4:3"
            video_aspect = round(float(4) / 3, 2)
        elif self.video_aspect_type == ASCEPT_16X9_STATE: #"16:9"
            video_aspect = round(float(16) / 9, 2)
        elif self.video_aspect_type == ASCEPT_16X10_STATE: #"16:10"
            video_aspect = round(float(16) / 10, 2)
        elif self.video_aspect_type == ASCEPT_1_85X1_STATE: #"1.85:1"
            video_aspect = round(float(1.85) / 1, 2)
        elif self.video_aspect_type == ASCEPT_2_35X1_STATE: #"2.35:1"
            video_aspect = round(float(2.35) / 1, 2)

        screen_frame_aspect = round(float(w) / h, 2)

        if screen_frame_aspect == video_aspect:
            self.screen_frame.set(0.0, 0.0, 1.0, 1.0)
        elif screen_frame_aspect > video_aspect:
            x = (float(h)* video_aspect) / w
            if x > 0.0:
                self.screen_frame.set(0.5, 0.0, self.max(x, 0.1, 1.0), 1.0)
            else:
                self.screen_frame.set(0.5, 0.0, 1.0, 1.0)
        elif screen_frame_aspect < video_aspect:
            y = (float(w) / video_aspect) / h;
            if y > 0.0:
                self.screen_frame.set(0.0, 0.5, 1.0, self.max(y, 0.1, 1.0))
            else:
                self.screen_frame.set(0.0, 0.5, 1.0, 1.0)

    def max(self, x, low, high):
        if low <= x <= high:
            return x
        if low > x:
            return low
        if high < x:
            return high
        
    def set_0_5x_video_play(self):
        if self.video_play_flags():
            self.video_play_state = X_VIDEO_PLAY_0_5
            self.set_video_play(self.video_width*0.5, self.video_height*0.5)
                        
    def set_1x_video_play(self):
        if self.video_play_flags():
            self.video_play_state = X_VIDEO_PLAY_1
            self.set_video_play(self.video_width, self.video_height)            
        
    def set_1_5x_video_play(self):
        if self.video_play_flags():
            self.video_play_state = X_VIDEO_PLAY_1_5
            self.set_video_play(self.video_width*1.5, self.video_height*1.5)            
        
    def set_2x_video_play(self):
        if self.video_play_flags():
            self.set_video_play_state = X_VIDEO_PLAY_2
            self.set_video_play(self.video_width*2, self.video_height*2)
                    
    def video_play_flags(self):    
        return self.mp.state and self.video_width and self.video_height
        
    def set_video_play(self, video_width, video_height):
        self.screen_frame.set_padding(0, 0, 0, 0)        
        if not self.full_bool: # full bool. True -> full False -> quit full.
            new_video_width = 0
            new_video_height = 0
            
            if video_height > self.root_window_height:
                new_video_height = self.root_window_height - 30
            elif video_height < APP_HEIGHT:
                new_video_height = APP_HEIGHT
            else:    
                new_video_height = video_height
                
            if video_width > self.root_window_width:
                new_video_width = self.root_window_width - 200
            elif video_width < APP_WIDTH:
                new_video_width = APP_WIDTH
            else:    
                new_video_width = video_width
                
            # Set media player size and position.
            self.app.window.resize(int(new_video_width), int(new_video_height))                                    
            self.app.window.set_position(gtk.WIN_POS_CENTER_ALWAYS)                        
        else:
            if self.video_play_state == X_VIDEO_PLAY_0_5:                    
                self.full_set_video_play(video_width, video_height)
            elif self.video_play_state == X_VIDEO_PLAY_1:
                self.full_set_video_play(video_width, video_height)
            elif self.video_play_state == X_VIDEO_PLAY_1_5:
                self.full_set_video_play(video_width, video_height)
            elif self.video_play_state == X_VIDEO_PLAY_2:                        
                self.full_set_video_play(video_width, video_height)
        
    def full_set_video_play(self, video_width, video_height):            
        self.screen_frame.set(0.5, 0.5, 0, 0)
        self.screen.set_size_request(int(video_width), int(video_height))
        
    def configure_hide_tool(self, widget, event): # screen: configure-event.
        self.screen_pop_menu.hide_menu()
        if self.full_bool:            
            self.open_button.move(-14, 30+26)
            self.open_button_right.move(56, 30+26)
        else:    
            self.open_button.move(-14, 30 + 26)
            self.open_button_right.move(56, 30 + 26)

        if self.mp:
            # Toolbar position.
            if self.mp.pause_bool and self.mp.vide_bool:
                self.mp.pause()
                self.mp.pause()

            # Toolbar width and height.
            self.toolbar.panel.resize(self.screen_frame.get_allocation()[2],
                                      self.screen_frame.get_allocation()[3])
    
            self.toolbar.panel.hide_all()
            self.bottom_toolbar.panel.resize(self.screen_frame.get_allocation()[2], 1)            
            self.bottom_toolbar.panel.move(self.panel_x, self.panel_y + (self.screen_frame.allocation[3] - self.bottom_toolbar.panel.allocation[3]))
            self.bottom_toolbar.panel.hide_all()


    '''Toolbar button.'''
    def common_window_function(self):
        '''quit fll window and common window'''
        self.app.show_titlebar() # show titlebar.
        self.progressbar.show_progressbar()

        self.main_vbox_hframe.set_padding(0, 0, 2, 2)
        self.toolbar.panel.hide_all()
        self.show_toolbar_bool = False
        self.bottom_toolbar.panel.hide_all()
        self.show_bottom()
        self.app.window.show_all()


    def concise_window_function(self):
        '''full window and concise mode'''
        self.app.hide_titlebar() # hide titlbar.
        self.progressbar.hide_progressbar()
        self.hide_bottom()

        self.main_vbox_hframe.set_padding(0, 0, 0, 0) # Set window border.
        self.toolbar.panel.hide_all() # hide toolbar.
        self.bottom_toolbar.panel.hide_all()



    def set_window_full(self):
        # if True. play list hide.
        if self.show_or_hide_play_list_bool:
            self.play_list.hide_play_list()

        self.concise_window_function()
        self.toolbar.panel.fullscreen()  # Toolbar hide.

        self.toolbar.panel.set_keep_above(True)
        self.bottom_toolbar.panel.set_keep_above(True)
        self.app.window.fullscreen()
        self.full_bool = True
        # self.mode_state_bool = True
        # Set toolbar state.
        self.set_toolbar_state()

    def set_window_quit_full(self):
        # # if True. play list show.
        if self.show_or_hide_play_list_bool:
            if not self.mode_state_bool:
                self.play_list.show_play_list()

        self.toolbar.panel.unfullscreen()

        self.app.window.unfullscreen()
        self.common_window_function()
        self.full_bool = False
        # Set toolbar state.
        self.set_toolbar_state()
        self.set_ascept_function()

    def set_toolbar_state(self):        
        # Set toolbar full state.
        if self.full_bool:
            self.toolbar.toolbar_radio_button.full_state = 1
        else:
            self.toolbar.toolbar_radio_button.full_state = 0
            
        if self.mode_state_bool:
            self.toolbar.toolbar_radio_button.window_state = 1
        else:    
            self.toolbar.toolbar_radio_button.window_state = 0
            
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

        # Set toolbar state.
        self.set_toolbar_state()
    

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
            self.bottom_toolbar.panel.show_all()
            # Set toolbar2 panel position.
            self.bottom_toolbar.panel.move(self.panel_x,
                                     self.panel_y + (widget.allocation[3] - self.bottom_toolbar.panel.allocation[3]) - self.app.titlebar.allocation[3])

            self.bottom_toolbar.panel.hide_all()

        # Set toolbar state.
        self.set_toolbar_state()    

    def set_window_above(self, widget): #above_button
        self.above_bool = not self.above_bool
        self.app.window.set_keep_above(self.above_bool)

    # Control mplayer window.
    def move_media_player_window(self, widget, event): # screen: button-press-event
        '''Move window.'''
        if is_left_button(event):
            self.event_button = event.button
            self.event_x_root = event.x_root
            self.event_y_root = event.y_root
            self.event_time = event.time

        config_string = self.config.get("OtherKey", "mouse_left_single_clicked")
                
        if True:
            if is_single_click(event):
                if not self.pause_bool:
                    if not self.open_button.leave_bool and not self.open_button_right.leave_bool and not self.screen_pop_menu.leave_bool:
                        # pause / play. 123456 press.                        
                        self.pause_bool = True # Save pause bool.
                        self.pause_x = event.x # Save x postion.
                        self.pause_y = event.y # Save y postion.
                else:
                    if not (_("Disabled") == config_string):
                        if self.pause_time_id:
                            gtk.timeout_remove(self.pause_time_id)
                            self.pause_bool = False

        # Double clicked full.
        config_string = self.config.get("OtherKey", "mouse_left_double_clicked")
        other_key_bool = self.config.get("OtherKey", "other_key_bool")
                
        if _("Disabled") == config_string or other_key_bool.lower() == "false":
            pass
        else:
            if is_double_click(event):
                if not self.open_button.leave_bool and not self.open_button_right.leave_bool and not self.screen_pop_menu.leave_bool:
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
                self.toolbar.panel.resize(self.screen_frame.get_allocation()[2],
                                  self.screen_frame.get_allocation()[3])
        
                self.show_toolbar_bool = True

                self.panel_x, self.panel_y = self.screen_frame.window.get_root_origin()
                if self.mode_state_bool: # Concise mode.
                    self.toolbar.panel.move(self.panel_x, self.panel_y)
                else:    # common mode.
                    self.toolbar.panel.move(self.panel_x + 2, self.panel_y + self.app.titlebar.allocation[3])

                if self.full_bool:
                    self.toolbar.panel.move(self.panel_x, self.panel_y)    
        else:
            if not self.above_bool:
                self.app.window.set_keep_above(False)
                self.bottom_toolbar.panel.set_keep_above(False)
            self.toolbar.hide_toolbar()
            self.show_toolbar_bool = False

        # Show toolbar2.
        if self.mode_state_bool or self.full_bool: # concise mode.
            if self.screen_frame.allocation[3]-20 <= event.y < self.screen_frame.allocation[3]:
                if self.show_toolbar_focus_bool:
                    self.bottom_toolbar.show_toolbar2()
                    self.show_toolbar_bool = True
            else:
                self.bottom_toolbar.hide_toolbar2()

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
        other_key_bool = self.config.get("OtherKey", "other_key_bool")
        
        if other_key_bool.lower() == "true" and  self.pause_bool and STARTING_PLAY == self.mp.state:
            self.pause_time_id = gtk.timeout_add(250, self.virtual_set_start_button_clicked)
            self.pause_bool = False

    def virtual_set_start_button_clicked(self):
        if self.mode_state_bool:
            self.bottom_toolbar.play_control_panel.start_button.start_bool = not self.bottom_toolbar.play_control_panel.start_button.start_bool
            self.bottom_toolbar.play_control_panel.start_button.queue_draw()
            self.start_button_clicked(self.bottom_toolbar.play_control_panel.start_button, 2)
        else:
            self.play_control_panel.start_button.start_bool = not self.play_control_panel.start_button.start_bool
            self.play_control_panel.start_button.queue_draw()
            self.start_button_clicked(self.play_control_panel.start_button, 1)

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
            if STARTING_PLAY == self.mp.state:
                # Hide preview window.
                self.hide_preview_function(widget, event)

                self.mp.seek(int(progressbar.pos))
                progressbar.set_pos(progressbar.pos)
                progressbar.drag_bool = True
                self.point_bool = True
            else:
                self.progressbar.set_pos(0)
                self.bottom_toolbar.progressbar.set_pos(0)
        else:                    
            progressbar.drag_bool = True            
            
    def progressbar_player_drag_pos_modify(self, widget, event, progressbar, pb_bit):
        '''Set player rate of progress.'''
        if progressbar.drag_bool: # Mouse left.
            # Hide preview window.
            self.hide_preview_function(widget, event)
            if STARTING_PLAY == self.mp.state:
                if 1 == pb_bit:
                    self.bottom_toolbar.progressbar.set_pos(progressbar.pos)
                elif 2 == pb_bit:
                    self.progressbar.set_pos(progressbar.pos)

                if self.mp and STARTING_PLAY == self.mp.state:
                    self.mp.seek(int(progressbar.pos))
                    self.show_time_label.time_font2 = self.set_time_string(
                        self.mp.time_hour) + ":" + self.set_time_string(self.mp.time_min) + ":" + self.set_time_string(self.mp.time_sec)
                    self.bottom_toolbar.show_time.time_font2 = self.set_time_string(
                        self.mp.time_hour) + ":" + self.set_time_string(self.mp.time_min) + ":" + self.set_time_string(self.mp.time_sec)
                    self.bottom_toolbar.panel.queue_draw()
                    self.app.window.queue_draw()
            else:
                self.progressbar.set_pos(0)
                self.bottom_toolbar.progressbar.set_pos(0)
        # Show preview window.
        else:
            config_bool = self.config.get("FilePlay", "mouse_progressbar_show_preview")
            if config_bool:
                if "true" == config_bool.lower():
                    if STARTING_PLAY == self.mp.state and self.play_video_file_bool(self.mp.path):
                        self.preview.set_preview_path(self.mp.path)
                        self.x_root = event.x_root
                        self.y_root = event.y_root
                        save_pos = (float(int(event.x))/ widget.allocation.width* self.progressbar.max)
                        # preview window show.
                        self.move_window_time(save_pos, pb_bit)
                else:            
                    self.preview.quit_preview_player()


    def move_window_time(self, pos, pb_bit):

        if 1 == pb_bit:
            preview_y_padding = self.app.window.get_position()[1] + self.screen_frame.allocation.height + self.app.titlebar.allocation.height - self.preview.bg.get_allocation()[3]
        elif 2 == pb_bit:
            preview_y_padding = self.bottom_toolbar.panel.get_position()[1] - self.preview.bg.get_allocation()[3]

        self.preview.show_preview(pos)
        # previwe window show position.
        self.preview.move_preview(self.x_root - self.preview.bg.get_allocation()[2]/2,
                                  preview_y_padding)

    def show_preview_enter(self, widget, event):
        if STOPING_PLAY == self.mp.state:
            self.progressbar.drag_pixbuf_bool = False
            self.bottom_toolbar.progressbar.drag_pixbuf_bool = False

    def hide_preview_leave(self, widget, event):
        '''Hide preview window and remove show,read_id'''
        self.preview.hide_preview()

    def set_time_string(self, num):
        if 0 <= num <= 9:
            return "0" + str(num)
        return str(num)

    def get_time_length(self, mplayer, length):
        '''Get mplayer length to max of progressbar.'''
        
        self.progressbar.max = length
        self.bottom_toolbar.progressbar.max = length # toolbar2 max value.
        Hour, Min, Sec = self.mp.time(length)
        self.show_time_label.time_font1 = self.set_time_string(Hour) + ":" + self.set_time_string(Min) + ":"+ self.set_time_string(Sec)
        self.bottom_toolbar.show_time.time_font1 = self.set_time_string(Hour) + ":" + self.set_time_string(Min) + ":"+ self.set_time_string(Sec) 
        self.show_time_label.set_time_font(self.show_time_label.time_font2, self.show_time_label.time_font1)
        self.bottom_toolbar.show_time.set_time_font(self.show_time_label.time_font2, self.bottom_toolbar.show_time.time_font1)

    def get_time_pos(self, mplayer, pos):
        '''Get mplayer pos to pos of progressbar.'''
        # Test media player pos.
        if (not self.progressbar.drag_bool) and (not self.point_bool):
            self.progressbar.set_pos(pos)
            self.bottom_toolbar.progressbar.set_pos(pos)
            self.show_time_label.time_font2 = self.set_time_string(
                self.mp.time_hour) + ":" + self.set_time_string(self.mp.time_min) + ":" + self.set_time_string(self.mp.time_sec) + " / "
            self.bottom_toolbar.show_time.time_font2 = self.set_time_string(
                self.mp.time_hour) + ":" + self.set_time_string(self.mp.time_min) + ":" + self.set_time_string(self.mp.time_sec) + " / "
            
            self.show_time_label.set_time_font(self.show_time_label.time_font2,
                                               self.show_time_label.time_font1)
            self.bottom_toolbar.show_time.set_time_font(self.show_time_label.time_font2,
                                               self.show_time_label.time_font1)
            
            self.bottom_toolbar.panel.queue_draw()
            self.app.window.queue_draw()

    def get_pos_ste_seek(self, pos):
        self.mp.seek(int(pos))

    def down_subtitle_threading(self, play_name, save_subtitle_path):    
        down_bool = True
        if save_subtitle_path[0:1] == "~":
            save_subtitle_path = get_home_path() + save_subtitle_path[1:]
            
        temp_path_file = os.path.splitext(os.path.split(play_name)[1])[0]
        temp_path_file_list = os.listdir(save_subtitle_path)
        save_down_file = None
        for file_name in temp_path_file_list:
            if os.path.splitext(file_name)[0] == temp_path_file:
                down_bool = False
                save_down_file = os.path.join(save_subtitle_path, file_name)            
        if os.path.exists(save_subtitle_path):    
            if down_bool:
                path_thread_id = threading.Thread(target=self.down_subtitle_threading_function,args=(play_name,save_subtitle_path,))
                path_thread_id.setDaemon(True)
                path_thread_id.start()        
            elif "True" == self.config.get("SubtitleSet", "ai_load_subtitle"):
                self.load_subtitle(save_down_file)                    
        else:        
            print "Dir error!"
        return False
    
    def down_subtitle_threading_function(self, play_name, save_subtitle_path):
        if download_shooter_subtitle(play_name, save_subtitle_path):
            temp_path_file = os.path.splitext(os.path.split(play_name)[1])[0]
            temp_path_file_list = os.listdir(save_subtitle_path)
            save_down_file = None
            for file_name in temp_path_file_list:
                if os.path.splitext(file_name)[0] == temp_path_file:
                    save_down_file = os.path.join(save_subtitle_path, file_name)                    
            if save_down_file and "True" == self.config.get("SubtitleSet", "ai_load_subtitle"):                    
                self.load_subtitle(save_down_file)        
        else:  # down lose. 
            pass
            
    def media_player_start(self, mplayer, play_bool):
        '''media player start play.'''        
        # down subtitle.
        save_subtitle_path = self.config.get("SubtitleSet","specific_location_search")        
        if save_subtitle_path:
            if save_subtitle_path[0:1] == "~":
                save_subtitle_path = get_home_path() + save_subtitle_path[1:]
        if save_subtitle_path:
            if self.down_sub_title_bool:            
                if format.get_video_bool(mplayer.path):                
                    gtk.timeout_add(500, self.down_subtitle_threading, mplayer.path, save_subtitle_path)
            else:                        
                temp_path_file = os.path.splitext(os.path.split(mplayer.path)[1])[0]
                temp_path_file_list = os.listdir(save_subtitle_path)
                save_down_file = None
                for file_name in temp_path_file_list:
                    if os.path.splitext(file_name)[0] == temp_path_file:
                        save_down_file = os.path.join(save_subtitle_path, file_name)                        
                if "True" == self.config.get("SubtitleSet", "ai_load_subtitle"):
                    if save_down_file and os.path.exists(save_down_file):                        
                        self.load_subtitle(save_down_file)

        # Init last new play file menu.
        self.the_last_new_play_file_list = self.last_new_play_file_function.set_file_time(mplayer.path)
        # Get video width and height.
        self.video_width, self.video_height = get_vide_width_height(mplayer.path)

        # config gui -> [Fileplay] video_file_open = ?
        video_open_type = self.config.get("FilePlay", "video_file_open")                            
        
        if video_open_type:
            if VIDEO_ADAPT_WINDOW_STATE == video_open_type: 
                if format.get_video_bool(mplayer.path):
                    screen_frame_height = self.screen_frame.allocation.height
                    modify_window_width = float(self.video_width)/self.video_height * screen_frame_height
                    video_padding_height = 0
                    # play list.
                    if self.show_or_hide_play_list_bool:
                        modify_window_width += self.play_list.play_list_width + 4
                        video_padding_height = 0
                    else:    
                        modify_window_width += 4
                    # Set window size.    
                    self.app.window.resize(int(round(round(modify_window_width, 1), 0)), 
                                           int(self.app.window.allocation.height) - video_padding_height)
                    self.app.window.set_position(gtk.WIN_POS_CENTER_ALWAYS)
            elif WINDOW_ADAPT_VIDEO_STATE == video_open_type:
                pass
            elif UP_CLOSE_VIDEO_STATE == video_open_type:
                width = self.config.get("Window", "width")
                height = self.config.get("Window", "height")
                if width > APP_WIDTH:
                    self.app.window.resize(int(width), int(height))
                    self.app.window.set_position(gtk.WIN_POS_CENTER_ALWAYS)
            elif AI_FULL_VIDEO_STATE == video_open_type:
                self.key_return()                
         
        # aspect set.                                    
        if self.video_aspect_type != ASCEPT_NORMAL_STATE: # "默认"
            self.set_ascept_function()
        # full window.
        if self.playwinmax_bool and (self.video_aspect_type == ASCEPT_NORMAL_STATE): # "默认"
            self.mp.playwinmax()
            self.playwinmax_bool = False
        
        # Get mplayer pid.
        self.mplayer_pid = play_bool
        #play memory.
        config_bool = self.config.get("FilePlay", "memory_up_close_player_file_postion")
        if "true" == config_bool.lower():
            pos = self.ini.get("PlayMemory", '"%s"' % ((mplayer.path)))
            if pos is not None:
                gtk.timeout_add(140, self.get_pos_ste_seek, pos)

        # title show play file name.
        file_name = self.get_player_file_name(mplayer.path)

        self.app.titlebar.title_box.set_text(str(file_name))
        # TabPage.
        for item in self.play_list.list_view.items:
            if self.play_list_dict[item.title] == self.mp.path:
                self.play_list.list_view.set_highlight(item)
                break

        self.progressbar.set_pos(0)
        self.bottom_toolbar.progressbar.set_pos(0)


    def media_player_end(self, mplayer, play_bool):
        '''player end.'''                        
        self.video_width = self.video_height = None        
        # play end set show time label zero.
        # show time label.
        self.show_time_label.time_font1 = "00:00:00" + " / "
        self.show_time_label.time_font2 = "00:00:00"        
        self.show_time_label.set_time_font(self.show_time_label.time_font1 , self.show_time_label.time_font2)
        # bottom_toolbar show time label.
        self.bottom_toolbar.show_time.time_font1 = "00:00:00"
        self.bottom_toolbar.show_time.time_font2 = "00:00:00 / "
        self.bottom_toolbar.show_time.set_time_font(self.bottom_toolbar.show_time.time_font2, 
                                                    self.bottom_toolbar.show_time.time_font1)

        # return screen framt.
        self.screen_frame.set(0.0, 0.0, 1.0, 1.0)
        # Quit preview window player.
        self.preview.quit_preview_player()
        # Play file modify start_button.
        self.media_player_midfy_start_bool()
        config_bool = self.config.get("FilePlay", "memory_up_close_player_file_postion")
        if config_bool:
            if "true" == config_bool.lower():
                self.ini.set("PlayMemory", '"%s"' % (mplayer.path), 0)
                if mplayer.pos_num < mplayer.len_num - 100:
                    self.ini.set("PlayMemory", '"%s"' % (mplayer.path), mplayer.pos_num)
                self.ini.save()
                
        self.playwinmax_bool = True

    def init_video_setting(self, mplayer, flags):    
        pass
        
    def media_player_next(self, mplayer, play_bool):
        if 1 == play_bool:
            self.media_player_midfy_start_bool()


    def media_player_pre(self, mplayer, play_bool):
        self.media_player_midfy_start_bool()

    def media_player_fseek(self, mplayer, fseek_num):    
        pos_num = self.mp.pos_num
        pre_num = 0
        if pos_num == 0:
            pre_num = 0
        else:    
            pre_num = float(pos_num) / self.mp.len_num * 100
        self.messagebox('%s%s%s %s(%s%s)' % (_("Forward"), 
                                           fseek_num, 
                                           _("s"), 
                                           length_to_time(self.mp.pos_num), 
                                           int(pre_num), "%"
                                           ))    
        
    def media_player_bseek(self, mplayer, bseek_num):         
        pos_num = self.mp.pos_num
        pre_num = 0
        if pos_num == 0:
            pre_num = 0
        else:    
            pre_num = int(float(pos_num) / self.mp.len_num * 100)
        self.messagebox('%s%s%s %s(%s%s)' % (_("Rewind"), 
                                           bseek_num,
                                           _("s"),
                                           length_to_time(self.mp.pos_num),                                            
                                           int(pre_num),
                                           "%"
                                           ))
    
    def media_player_midfy_start_bool(self):  # media_player_end and media_player_next and media_player_pre.
        self.progressbar.set_pos(0)
        self.bottom_toolbar.progressbar.set_pos(0)
        self.screen.queue_draw()
        self.play_control_panel.start_button.start_bool = True
        self.play_control_panel.start_button.queue_draw()
        self.bottom_toolbar.play_control_panel.start_button.start_bool = True
        self.bottom_toolbar.play_control_panel.start_button.queue_draw()

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
        if pathfile2[0:4].lower() == "http":
            return pathfile2
        file1, file2 = os.path.split(pathfile2)
        return os.path.splitext(file2)[0]

    def theme_menu_show(self, button):    
        '''Title root menu.'''
        #In title root menu.
        self.sort_menu = Menu([(None, _("Take Screenshots"), self.key_sort_image),
                               (None, _("Open Screenshot Directory"), self.open_sort_image_dir),
                               (None, _("Set Screenshot Directory"), self.open_sort_image_ini_gui)
                               ])
        # In title root menu.
        self.subtitle_menu = Menu([(None, _("Import Subtitles"), None),
                                   (None, _("Select Subtitles"), None),
                                   (None, _("Remove Subtitles"), None),
                                   ])
        
        normal_channel_state = 0
        left_channel_state = 1
        right_channel_state = 2
        normal_channel_pixbuf = None
        left_channel_pixbuf = None
        right_channel_pixbuf = None
        
        channel_pixbuf = (self.select_channel_normal_pixbuf, self.select_channel_hover_pixbuf)
        
        if self.mp.channel_state == normal_channel_state:
            normal_channel_pixbuf = channel_pixbuf
        elif self.mp.channel_state == left_channel_state:    
            left_channel_pixbuf = channel_pixbuf
        elif self.mp.channel_state == right_channel_state:    
            right_channel_pixbuf = channel_pixbuf        
            
        self.channel_select_menu = Menu([
                (normal_channel_pixbuf, _("Stereo"), self.normal_channel),
                (left_channel_pixbuf,   _("Left"),   self.left_channel),
                (right_channel_pixbuf,  _("Right"),   self.right_channel)
                ])

        # In title root menu.
        self.volume_menu = Menu([(None, _("Channels"), self.channel_select_menu),
                                 # (None, "配音选择", None),
                                 (None),
                                 (self.add_volume_pixbuf, _("Volumn Up"),  self.menu_add_volume),
                                 (self.sub_volume_pixbuf, _("Volumn Down"),  self.menu_sub_volume),
                                 (self.mute_volume_pixbuf, _("Mute/Umute"), self.key_set_mute),
                                 ])
        # In title root menu.
        pixbuf_normal = None
        pixbuf_4X3 = None
        pixbuf_16X9 = None
        pixbuf_16X10 = None
        pixbuf_1_85X1 = None
        pixbuf_2_35X1 = None
        
        if ASCEPT_NORMAL_STATE == self.video_aspect_type: #"默认"
            pixbuf_normal = (self.video_aspect_pixbuf, self.video_aspect_select_pixbuf)
        elif ASCEPT_4X3_STATE == self.video_aspect_type: #"4:3"
            pixbuf_4X3 = (self.video_aspect_pixbuf, self.video_aspect_select_pixbuf)
        elif ASCEPT_16X9_STATE == self.video_aspect_type: #"16:9"
            pixbuf_16X9 = (self.video_aspect_pixbuf, self.video_aspect_select_pixbuf)
        elif ASCEPT_16X10_STATE == self.video_aspect_type: # "16:10"
            pixbuf_16X10 = (self.video_aspect_pixbuf, self.video_aspect_select_pixbuf)
        elif ASCEPT_1_85X1_STATE == self.video_aspect_type: # "1.85:1"
            pixbuf_1_85X1 = (self.video_aspect_pixbuf, self.video_aspect_select_pixbuf)
        elif ASCEPT_2_35X1_STATE == self.video_aspect_type: #"2.35:1"
            pixbuf_2_35X1 = (self.video_aspect_pixbuf, self.video_aspect_select_pixbuf)
        
        self.screen_menu = Menu([(pixbuf_normal, _("Original"),  self.set_restart_aspect),
                                 (pixbuf_4X3,    "4:3",    self.set_4X3_aspect),
                                 (pixbuf_16X9,   "16:9",   self.set_16X9_aspect),
                                 (pixbuf_16X10,  "16:10",  self.set_16X10_aspect),
                                 (pixbuf_1_85X1, "1.85:1", self.set_1_85X1_aspect),
                                 (pixbuf_2_35X1, "2.35:1", self.set_2_35X1_aspect),
                                 (None),
                                 (None,  _("50%"),  self.set_0_5x_video_play),
                                 (None,  _("100%"),       self.set_1x_video_play),
                                 (None,  _("150%"),     self.set_1_5x_video_play),
                                 (None,  _("200%"),       self.set_2x_video_play),
                                 # (None),
                                 # (None, "全屏/退出", None),
                                 ])        
        
        # 0: single playing.      
        # single_play_state = 0
        # 1: order playing.     
        # order_play_state = 1
        # 2: random player.      
        # random_play_state = 2
        # 3: single cycle player. 
        # signle_cycle_play_state = 3
        # 4: list recycle play. 
        # list_recycle_play_state = 4
        
        play_sequence_pixbuf = (self.play_sequence_select_normal_pixbuf, self.play_sequence_select_hover_pixbuf)
        single_pixbuf = None
        order_pixbuf = None
        random_pixbuf = None
        signle_cycle_pixbuf = None
        list_recycle_pixbuf = None
        
        if self.mp.play_list_state == SINGLE_PLAYING_STATE: # single_play_state:
            single_pixbuf = play_sequence_pixbuf
        elif self.mp.play_list_state == ORDER_PLAYING_STATE: # order_play_state:    
            order_pixbuf = play_sequence_pixbuf
        elif self.mp.play_list_state == RANDOM_PLAYER_STATE: # random_play_state:
            random_pixbuf = play_sequence_pixbuf
        elif self.mp.play_list_state == SINGLE_CYCLE_PLAYER: # signle_cycle_play_state:    
            signle_cycle_pixbuf = play_sequence_pixbuf
        elif self.mp.play_list_state == LIST_RECYCLE_PLAY: # list_recycle_play_state:    
            list_recycle_pixbuf = play_sequence_pixbuf

        # In title root menu.
        self.play_state_menu = Menu([(single_pixbuf, _("Play (single)"), self.sigle_play),
                                     (order_pixbuf,  _("Play (ordered)"), self.sequence_play),
                                     (random_pixbuf, _("Shuffle"), self.rand_play),
                                     (signle_cycle_pixbuf, _("Repeat"), self.sigle_loop_play),
                                     (list_recycle_pixbuf, _("Repeat List"), self.loop_list_play)]
                                    )
        # In title root menu.
        self.play_menu = Menu([((self.menu_full_normal_pixbuf, self.menu_full_hover_pixbuf), _("Full Screen"), self.key_return),
                               ((self.menu_window_mode_normal_pixbuf, self.menu_window_mode_hover_pixbuf), _("Standard Mode"), self.set_menu_common),
                               ((self.menu_concie_normal_pixbuf, self.menu_concie_hover_pixbuf), _("Concise Mode"), self.set_menu_concise),
                               ((self.menu_pre_normal_pixbuf, self.menu_pre_hover_pixbuf), _("Prev"), self.key_pre),
                               ((self.menu_next_normal_pixbuf, self.menu_next_hover_pixbuf), _("Next"), self.key_next),
                               (None),
                               ((self.menu_f_seek_5_normal_pixbuf, self.menu_f_seek_5_hover_pixbuf), _("Forward 5s"), self.key_right),
                               ((self.menu_b_seek_5_normal_pixbuf, self.menu_b_seek_5_hover_pixbuf), _("Rewind 5s"), self.key_left),
                               ((self.menu_play_sequence_normal_pixbuf, self.menu_play_sequence_hover_pixbuf), _("Play Order"), self.play_state_menu),
                               ])
        # In title root menu.
        self.file_menu = Menu([(None, _("Open File"), self.add_file_clear),
                               (None, _("Open Directory"), self.add_file_dir_clear)])
                              # (None, "播放光盘", None)])

        # In title root menu.
        self.help_menu = Menu([(None, _("Help"), None),
                               (None, _("Issues"), None),
                               (None, _("About us"), None)])
        
        #
        self.title_root_menu = Menu([(None, _("File"), self.file_menu),
                                     (None, _("Play"), self.play_menu),
                                     (None, _("Video"), self.screen_menu),
                                     ((self.menu_volume_normal_pixbuf, self.menu_volume_hover_pixbuf), _("Audio"), self.volume_menu),
                                     # (None, "字幕", self.subtitle_menu),
                                     (None, _("Take Screenshots"), self.sort_menu),
                                     (None, _("New Features"), init_user_guide),
                                     ((self.menu_setting_normal_pixbuf, self.menu_setting_hover_pixbuf), _("Preferences"), self.config_gui),
                                     # (None, "总在最前", None),
                                     # (None, "自定义换肤", None),
                                     # (None, "帮助与反馈", self.help_menu),
                                     (None),
                                     ((self.menu_quit_normal_pixbuf, self.menu_quit_hover_pixbuf), _("Quit"), self.set_menu_quit)],
                                    True)
        self.title_root_menu.show(
            get_widget_root_coordinate(button, WIDGET_POS_BOTTOM_LEFT),
            (button.get_allocation().width, 0))           

    '''Screen right key menu.'''
    def screen_right_key_menu(self, event):
        
        # 0: single playing.      
        # single_play_state = 0
        # 1: order playing.     
        # order_play_state = 1
        # 2: random player.      
        # random_play_state = 2
        # 3: single cycle player. 
        # signle_cycle_play_state = 3
        # 4: list recycle play. 
        # list_recycle_play_state = 4
        
        play_sequence_pixbuf = (self.play_sequence_select_normal_pixbuf, self.play_sequence_select_hover_pixbuf)
        single_pixbuf = None
        order_pixbuf = None
        random_pixbuf = None
        signle_cycle_pixbuf = None
        list_recycle_pixbuf = None
        
        if self.mp.play_list_state == SINGLE_PLAYING_STATE: # single_play_state:
            single_pixbuf = play_sequence_pixbuf
        elif self.mp.play_list_state == ORDER_PLAYING_STATE: # order_play_state:    
            order_pixbuf = play_sequence_pixbuf
        elif self.mp.play_list_state == RANDOM_PLAYER_STATE: # random_play_state:
            random_pixbuf = play_sequence_pixbuf
        elif self.mp.play_list_state == SINGLE_CYCLE_PLAYER: # signle_cycle_play_state:    
            signle_cycle_pixbuf = play_sequence_pixbuf
        elif self.mp.play_list_state == LIST_RECYCLE_PLAY:   #list_recycle_play_state:    
            list_recycle_pixbuf = play_sequence_pixbuf

        # screen right menu set mplayer play state.
        play_state_menu = Menu([(single_pixbuf, _("Play (single)"), self.sigle_play),
                                (order_pixbuf,  _("Play (ordered)"), self.sequence_play),
                                (random_pixbuf, _("Shuffle"), self.rand_play),
                                (signle_cycle_pixbuf, _("Repeat"), self.sigle_loop_play),
                                (list_recycle_pixbuf, _("Repeat List"), self.loop_list_play)]
                               )
        
        play_menu = Menu([                                                    
                          ((self.menu_pre_normal_pixbuf, self.menu_pre_hover_pixbuf), _("Prev"), self.key_pre),
                          ((self.menu_next_normal_pixbuf, self.menu_next_hover_pixbuf), _("Next"), self.key_next),
                          (None),
                          ((self.menu_f_seek_5_normal_pixbuf, self.menu_f_seek_5_hover_pixbuf), _("Forward 5s"), self.key_right),
                          ((self.menu_b_seek_5_normal_pixbuf, self.menu_b_seek_5_hover_pixbuf), _("Rewind 5s"), self.key_left),
                          ])

        # aspect.
        pixbuf_normal = None
        pixbuf_4X3 = None
        pixbuf_16X9 = None
        pixbuf_16X10 = None
        pixbuf_1_85X1 = None
        pixbuf_2_35X1 = None
        
        if ASCEPT_NORMAL_STATE == self.video_aspect_type: # 默认
            pixbuf_normal = (self.video_aspect_pixbuf, self.video_aspect_select_pixbuf)
        elif ASCEPT_4X3_STATE == self.video_aspect_type: #"4:3"
            pixbuf_4X3 = (self.video_aspect_pixbuf, self.video_aspect_select_pixbuf)
        elif ASCEPT_16X9_STATE == self.video_aspect_type: #"16:9"
            pixbuf_16X9 = (self.video_aspect_pixbuf, self.video_aspect_select_pixbuf)
        elif ASCEPT_16X10_STATE == self.video_aspect_type: # "16:10"
            pixbuf_16X10 = (self.video_aspect_pixbuf, self.video_aspect_select_pixbuf)
        elif ASCEPT_1_85X1_STATE == self.video_aspect_type: #"1.85:1"
            pixbuf_1_85X1 = (self.video_aspect_pixbuf, self.video_aspect_select_pixbuf)
        elif ASCEPT_2_35X1_STATE == self.video_aspect_type: # "2.35:1"
            pixbuf_2_35X1 = (self.video_aspect_pixbuf, self.video_aspect_select_pixbuf)
        
        screen_menu = Menu([(pixbuf_normal, _("Original"),  self.set_restart_aspect),
                            (pixbuf_4X3,    "4:3",    self.set_4X3_aspect),
                            (pixbuf_16X9,   "16:9",   self.set_16X9_aspect),
                            (pixbuf_16X10,  "16:10",  self.set_16X10_aspect),
                            (pixbuf_1_85X1, "1.85:1", self.set_1_85X1_aspect),
                            (pixbuf_2_35X1, "2.35:1", self.set_2_35X1_aspect),
                            (None),
                            (None,  _("50%"),  self.set_0_5x_video_play),
                            (None,  _("100%"),       self.set_1x_video_play),
                            (None,  _("150%"),     self.set_1_5x_video_play),
                            (None,  _("200%"),       self.set_2x_video_play),
                            # (None),
                            # (None, "全屏/退出", None),
                            ])

        normal_channel_state = 0
        left_channel_state = 1
        right_channel_state = 2
        normal_channel_pixbuf = None
        left_channel_pixbuf = None
        right_channel_pixbuf = None
        
        channel_pixbuf = (self.select_channel_normal_pixbuf, self.select_channel_hover_pixbuf)
        
        if self.mp.channel_state == normal_channel_state:
            normal_channel_pixbuf = channel_pixbuf
        elif self.mp.channel_state == left_channel_state:    
            left_channel_pixbuf = channel_pixbuf
        elif self.mp.channel_state == right_channel_state:    
            right_channel_pixbuf = channel_pixbuf        
        
        channel_select = Menu([
                (normal_channel_pixbuf, _("Stereo"),  self.normal_channel),
                (left_channel_pixbuf,   _("Left"),    self.left_channel),
                (right_channel_pixbuf,  _("Right"),    self.right_channel)
                ])
        
        down_sub_title_pixbuf = None
        if self.down_sub_title_bool:
            down_sub_title_pixbuf = (self.down_sub_title_norma_pixbuf, self.down_sub_title_hover_pixbuf)
            
        down_sub_title_menu = Menu([
                (down_sub_title_pixbuf, _("Auto-download Subtitles"), self.set_down_sub_title_bool)
                ])
        
        self.screen_right_root_menu = Menu([
                (None, _("Open File"),   self.add_file_clear),
                (None, _("Open Directory"), self.add_file_dir_clear),
                (None, _("Open URL"),   self.open_url_dialog_window),
                (None),
                ((self.menu_full_normal_pixbuf, self.menu_full_hover_pixbuf), _("Full Screen On/Off"),    self.key_return),
                ((self.menu_window_mode_normal_pixbuf, self.menu_window_mode_hover_pixbuf), _("Standard Mode"), self.set_menu_common),
                ((self.menu_concie_normal_pixbuf, self.menu_concie_hover_pixbuf), _("Concise Mode"), self.set_menu_concise),
                ((self.menu_play_sequence_normal_pixbuf, self.menu_play_sequence_hover_pixbuf), _("Play Order"), play_state_menu),
                (None, _("Play"), play_menu),
                (None, _("Video"), screen_menu),
                ((self.menu_volume_normal_pixbuf, self.menu_volume_hover_pixbuf), _("Audio"), channel_select),
                ((self.menu_subtitle_normal_pixbuf, self.menu_subtitle_hover_pixbuf), _("Subtitles"), down_sub_title_menu),
                ((self.menu_setting_normal_pixbuf, self.menu_setting_hover_pixbuf), _("Preferences"), self.config_gui) 
                ], True)
        
        self.screen_right_root_menu.show((int(event.x_root), int(event.y_root)),
                                (0, 0))
        
    def set_down_sub_title_bool(self):    
        self.down_sub_title_bool = not self.down_sub_title_bool
        
    '''play list menu signal.'''
    def show_popup_menu(self, widget, event):
        if 3 == event.button:
            # 0: single playing.      
            # single_play_state = 0
            # 1: order playing.     
            # order_play_state = 1
            # 2: random player.      
            # random_play_state = 2
            # 3: single cycle player. 
            # signle_cycle_play_state = 3
            # 4: list recycle play. 
            # list_recycle_play_state = 4
        
            play_sequence_pixbuf = (self.play_sequence_select_normal_pixbuf, self.play_sequence_select_hover_pixbuf)
            single_pixbuf = None
            order_pixbuf = None
            random_pixbuf = None
            signle_cycle_pixbuf = None
            list_recycle_pixbuf = None

            if self.mp.play_list_state == SINGLE_PLAYING_STATE: # single_play_state:
                single_pixbuf = play_sequence_pixbuf
            elif self.mp.play_list_state == ORDER_PLAYING_STATE: # order_play_state:    
                order_pixbuf = play_sequence_pixbuf
            elif self.mp.play_list_state == RANDOM_PLAYER_STATE: # random_play_state:
                random_pixbuf = play_sequence_pixbuf
            elif self.mp.play_list_state == SINGLE_CYCLE_PLAYER: # signle_cycle_play_state:
                signle_cycle_pixbuf = play_sequence_pixbuf
            elif self.mp.play_list_state == LIST_RECYCLE_PLAY: # list_recycle_play_state:  
                list_recycle_pixbuf = play_sequence_pixbuf

            '''play list popup menu'''
            self.menu = Menu([(single_pixbuf, _("Play (single)"), self.sigle_play),          # 0
                              (order_pixbuf, _("Play (ordered)"), self.sequence_play),       # 1
                              (random_pixbuf, _("Shuffle"), self.rand_play),                 # 2
                              (signle_cycle_pixbuf, _("Repeat"), self.sigle_loop_play),      # 3
                              (list_recycle_pixbuf, _("Repeat List"), self.loop_list_play)]  # 4
                             )

            self.menu2 = Menu([(None, _("By Name"), self.name_sort),
                               (None, _("By Type"), self.type_sort)])
            
            
            if self.the_last_new_play_file_list == []:
                self.the_last_new_play_file = None
            else:    
                self.the_last_new_play_file = Menu(self.the_last_new_play_file_list)
                
            self.play_list_root_menu = Menu([(None, _("Add File"), self.add_file),
                                             (None, _("Add Directory"), self.add_file_dir),
                                             (None, _("Add URL"), self.open_url_dialog_window),
                                             (None),
                                             (None, _("Remove Selected"), self.del_index),
                                             (None, _("Clear Playlist"), self.clear_list),
                                             (None, _("Remove Unavailable Files"), self.del_error_file),
                                             (None),
                                             (None, _("Recent Played"), self.the_last_new_play_file),
                                             (None, _("Play Order"), self.menu),
                                             (None, _("Sort"), self.menu2),
                                             # (None, "视图", None),
                                             (None),
                                             (None, _("Open Containing Directory"), self.open_current_file_dir)
                                             ],
                                            True)


            self.play_list_root_menu.show((int(event.x_root), int(event.y_root)),
                                (0, 0))

    def sigle_play(self):
        if self.mp:
            self.mp.play_list_state = SINGLE_PLAYING_STATE # 0

    def sequence_play(self):
        if self.mp:
            self.mp.play_list_state = ORDER_PLAYING_STATE # 1

    def rand_play(self):
        if self.mp:
            self.mp.play_list_state = RANDOM_PLAYER_STATE # 2

    def sigle_loop_play(self):
        if self.mp:
            self.mp.play_list_state = SINGLE_CYCLE_PLAYER # 3

    def loop_list_play(self):
        if self.mp:
            self.mp.play_list_state = LIST_RECYCLE_PLAY # 4

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
            self.mp.play_list_sum = 0
            self.mp.play_list_num = -1
            self.mp.random_num = 0

            # play list restart add file name.
            list_item = []
            for i in temp_list:
                for j in i:
                    for k in j:
                        list_item.append(MediaItem(k, temp_dict[k]))

                        self.mp.playList.append(self.play_list_dict[k])
                        self.mp.play_list_sum += 1

            self.play_list.list_view.add_items(list_item)

            # # highlight staring play file.
            num = 0
            for item in self.play_list.list_view.items:
                if self.play_list_dict[item.title] == self.mp.path:
                    self.play_list.list_view.set_highlight(item)
                    break
                num += 1
            self.mp.play_list_num = num

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
            self.mp.play_list_sum = 0
            self.mp.play_list_num = -1
            self.mp.random_num = 0

            list_item = []
            for list_str in temp_list:
                list_item.append(MediaItem(list_str, temp_dict[list_str]))
                self.mp.playList.append(self.play_list_dict[list_str])
                self.mp.play_list_sum += 1

            self.play_list.list_view.add_items(list_item)

            # # highlight staring play file.
            num = 0
            for item in self.play_list.list_view.items:
                if self.play_list_dict[item.title] == self.mp.path:
                    self.play_list.list_view.set_highlight(item)
                    break
                num += 1
            self.mp.play_list_num = num

    def add_file(self):        
        self.show_open_dialog_window()
        
    def add_file_dir(self):
        self.show_open_dir_dialog_window()
        
    def add_file_clear(self):    
        self.show_open_dialog_window(False)
        
    def add_file_dir_clear(self):            
        self.show_open_dir_dialog_window(False)
                
    def open_url_dialog_window(self):    
        open_url = OpenUrl()
        open_url.connect("openurl-url-name", self.get_url_name)
        
    def get_url_name(self, open_url, url_name, url_bool):
        if url_bool:
            self.mp.clear_playlist()
            self.mp.add_play_file(url_name) # play list add url name.
        else:    
            self.messagebox(str(url_name))
        
                
    def del_index(self):
        self.play_list.list_view.delete_select_items()

    def clear_list(self):
        self.play_list.list_view.clear()
        self.mp.clear_playlist()

    def del_error_file(self):
        '''Delete error play file.'''
        if self.play_list.list_view.items:
            for item in self.play_list.list_view.items:
                # play file error -> delete file.
                path = self.play_list_dict[item.title]
                if not os.path.exists(path):
                    self.play_list.list_view.items.remove(item)
                    self.mp.del_playlist(path)

    def open_sort_image_dir(self):
        file_name = self.config.get("ScreenshotSet", "save_path")

        if file_name:
            os.system("nautilus %s" % (file_name))
        else:
            os.system("nautilus %s" % (get_home_path()))

    def open_sort_image_ini_gui(self):  #menu
        ini_gui = IniGui()
        ini_gui.set("%s"%(_("Screenshot")))
        ini_gui.ini.connect("config-changed", self.restart_load_config_file)        
        
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
    def config_gui(self):        
        ini_gui = IniGui()
        ini_gui.ini.connect("config-changed", self.restart_load_config_file)
        
    def restart_load_config_file(self, IniGui, sec_root, sec_argv, sec_value):
        self.config.set(sec_root, sec_argv, sec_value)
        self.config.save()        
        
    # Menu concise.
    def set_menu_concise(self):
        self.hide_window_widget(self.toolbar.toolbar_concise_button)

    # Menu common.
    def set_menu_common(self):
        self.show_window_widget(self.toolbar.toolbar_common_button)

    # quit .    
    def set_menu_quit(self):    
        self.app.window.destroy()
        
    '''Set channel'''
    def normal_channel(self):
        self.mp.normalchannel()
        
    def left_channel(self):
        self.mp.leftchannel()

    def right_channel(self):
        self.mp.rightchannel()

    '''Subtitle.'''
    def load_subtitle(self, sub_file):        
        fp_str = open(sub_file, "r").read()
        code_to_utf_8_str = auto_decode(fp_str)

        with open(sub_file, 'w') as fp_open:
            fp_open.write(code_to_utf_8_str)
        
        self.mp.subload(sub_file)

    def remove_subtitle(self):
        self.mp.subremove()

    def play_win_max(self):
        self.mp.playwinmax()

    ## video Control ##
    # brightness.
    def add_bri(self):
        self.mp.addbri()

    def dec_bri(self):
        self.mp.decbri()

    # saturation.
    def add_sat(self):
        self.mp.addsat()

    def dec_sat(self):
        self.mp.decsat()

    # contrast.
    def add_con(self):
        self.mp.addcon()

    def dec_con(self):
        self.mp.deccon()

    # hue.
    def add_hue(self):
        self.mp.addhue()

    def dec_hue(self):
        self.mp.dec_hue()

    def scrot_current_screen_pixbuf(self, save_path_save_name, save_file_type=".png"):
        x, y, w, h = self.screen_frame.get_allocation()
        screen_pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, w, h)
        save_pixbuf = screen_pixbuf.get_from_drawable(self.screen_frame.window, 
                                                      self.screen_frame.get_colormap(),
                                                      0, 0, 0, 0, w, h)
        save_pixbuf.save(save_path_save_name + save_file_type, save_file_type[1:])
        
    def get_same_name_event(self, mplayer, path):
        pass
        
    def play_same_name_file(self, path):    
        pass
        
    def menu_add_volume(self):
        self.menu_set_volume(1)
    
    def menu_sub_volume(self):
        self.menu_set_volume(0)
        
    def menu_set_volume(self, type_bool):            
        add_volume_state = 1
        sub_volume_state = 0
        volume_value = 5        
        
        # Set volume.
        if type_bool == add_volume_state:
            if (self.volume_button.value + volume_value) > 100:
                self.volume_button.value = 100
            self.volume_button.value = self.volume_button.value + volume_value
        elif type_bool == sub_volume_state:
            if (self.volume_button.value - volume_value) < 0:
                self.volume_button.value = 0
            self.volume_button.value = self.volume_button.value - volume_value
            
            
        self.mp.setvolume(self.volume_button.value)
        self.messagebox("%s:%s%s"%(_("Volumn"), int(self.volume_button.value), "%"))                            
        
