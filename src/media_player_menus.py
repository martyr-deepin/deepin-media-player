#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2013 Deepin, Inc.
#               2013 Hailong Qiu
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

from skin import app_theme
from user_guide import init_user_guide
from widget.utils import is_right_button
from widget.utils import open_file
from mplayer.player import ASCEPT_4X3_STATE, ASCEPT_16X9_STATE, ASCEPT_5X4_STATE
from mplayer.player import ASCEPT_16X10_STATE, ASCEPT_1_85X1_STATE, ASCEPT_2_35X1_STATE
from mplayer.player import ASCEPT_FULL_STATE, ASCEPT_DEFULAT
from mplayer.playlist import SINGLA_PLAY, ORDER_PLAY, RANDOM_PLAY, SINGLE_LOOP, LIST_LOOP 
from format_conv.transmageddon import TransmageddonUI

import os



class MediaPlayMenus(object):
    def __init__(self, this):
        self.this = this
        self.gui  = self.this.gui
        self.ldmp = self.this.ldmp
        self.play_list = self.this.play_list
        self.list_view = self.this.gui.play_list_view.list_view
        # 屏幕右键弹出菜单.
        self.gui.screen_frame_event.connect("button-release-event",   self.screen_frame_right_show_menu)
        # 播放列表弹出.
        self.list_view.connect_event("right-items-event", self.list_veiw_right_show_menu)
        # ldmp后端连接事件.
        self.ldmp.connect("get-subtitle",   self.ldmp_get_subtitle)
        self.ldmp.connect("get-audio-info", self.ldmp_get_audio_info)
        self.ldmp.connect("end-media-player",   self.menu_ldmp_end_media_player)
        self.ldmp.connect("start-media-player", self.menu_ldmp_start_media_player)
        #
        self.menus = self.this.gui.play_menus
        # 初始化连接事件.
        self.menus.full_screen  = self.this.fullscreen_function
        self.menus.normal_mode  = self.this.top_toolbar_common_button_clicked
        self.menus.compact_mode = self.this.top_toolbar_concise_button_clicked
        #
        self.menus.next         = self.this.next
        self.menus.prev         = self.this.prev
        self.menus.fseek        = self.menu_fseek
        self.menus.bseek        = self.menu_bseek
        self.menus.open_file    = self.this.open_files_to_play_list
        self.menus.open_dir     = self.this.open_dirs_to_play_list
        #self.menus.open_url     = 
        self.menus.add_open_file = self.menu_add_open_file #self.this.open_files_to_play_list
        self.menus.add_open_dir  = self.menu_add_open_dir #self.this.open_dirs_to_play_list
        #self.menus.add_open_url  = self.menu_add_open_url
        #
        self.menus.stereo_channel = self.menu_stereo_channel  # 立体声.
        self.menus.left_channel   = self.menu_left_channel 
        self.menus.right_channel  = self.menu_right_channel 
        self.menus.mute_unmute    = self.menu_mute_unmute
        self.menus.inc_volume     = self.menu_inc_volume
        self.menus.dec_volume     = self.menu_dec_volume
        # 初始化 声道 为立体声.
        self.menu_stereo_channel()
        #
        self.menus.config_gui = self.this.config_gui
        self.menus.quit       = self.menu_quit
        self.menus.init_user_guide = init_user_guide
        # 设置播放比例.
        self.menus.normal_ascept   = self.menu_normal_ascept
        self.menus._4X3_ascept     = self.menu_4X3_ascept
        self.menus._16X9_ascept    = self.menu_16X9_ascept
        self.menus._16X10_ascept   = self.menu_16X10_ascept
        self.menus._1_85X1_ascept  = self.menu_1_85X1_ascept
        self.menus._2_35X1_ascept  = self.menu_2_35X1_ascept
        # 初始化为默认.
        self.set_menu_ascept(0, ASCEPT_DEFULAT)
        # 设置播放状态.
        # 播放列表 .       0        1       2         3          4
        #           { 单曲播放、顺序播放、随机播放、单曲循环播放、列表循环播放、}
        #            SINGLA_PLAY ... ...                ...LIST_LOOP
        self.menus.play_track            = self.menu_play_track
        self.menus.play_default          = self.menu_play_default
        self.menus.play_random           = self.menu_play_random
        self.menus.play_repeat_track     = self.menu_play_repeat_track
        self.menus.play_repeat_play_list = self.menu_play_repeat_play_list
        # 初始化为顺序播放. 1 代表的是菜单的顺序.
        self.set_play_list_state(1, ORDER_PLAY)
        # 格式转换.
        self.menus.format_conversion = self.menu_format_conversion
        self.menus.task_manager      = self.menu_task_manager
        self.menus.screen_format_conversion = self.menu_screen_format_conversion
        # 屏幕的属性查看.
        self.menus.properties = self.menu_properties
        ############################
        # 修改图标.
        #self.menus.title_root_menu.menu_items[0].set_item_icons((pixbuf, pixbuf, pixbuf))
        # 禁止图标.
        #self.menus.title_root_menu.set_menu_item_sensitive_by_index(1, False)
        #self.menus.play_state_menu.menu_items[1].set_item_icons((pixbuf, pixbuf1, pixbuf2))
        #self.menus.play_state_menu.set_mutual_icons(2, (pixbuf, pixbuf1, pixbuf2))
        #self.menus.video_menu.set_mutual_icons(0, (pixbuf, pixbuf1, pixbuf2))
        # 播放列表.
        self.menus.remove_selected = self.list_view.listview_delete_event
        self.menus.clear_playlist  = self.list_view.clear
        self.menus.open_containing_directory = self.menu_open_containing_directory
        #
        # 属性查看.
        self.menus.screen_right_root_menu.set_menu_item_sensitive_by_index(15, False)
        self.menus.screen_right_root_menu.set_menu_item_sensitive_by_index(12, False)
        self.menus.screen_right_root_menu.set_menu_item_sensitive_by_index(11, False)
        self.menus.channel_select.set_menu_item_sensitive_by_index(1, False)

    def ldmp_get_subtitle(self, ldmp, sub_info, index):
        self.menus.screen_right_root_menu.set_menu_item_sensitive_by_index(11, True)
        # 添加字幕信息.
        self.menus.subtitles_select.add_menu_items([
                            (None, sub_info, lambda : self.menu_switch_subtitle(index)),
                            ])
        if index == 0: # 设置默认项.
            self.menu_switch_subtitle(0)

    def menu_switch_subtitle(self, index):
        self.ldmp.sub_select(index)
        self.menus.subtitles_select.set_mutual_icons(index, self.menus.select_pixbuf)

    def ldmp_get_audio_info(self, ldmp, audio_info, index):
        self.menus.channel_select.set_menu_item_sensitive_by_index(1, True)
        # 添加音频语言信息.
        self.menus.switch_audio_menu.add_menu_items([
                            (None, audio_info, lambda : self.menu_switch_audio(index)),
                            ])
        if index == 0: # 设置默认项.
            self.menu_switch_audio(0)

    def menu_switch_audio(self, index):
        self.ldmp.switch_audio(index)
        self.menus.switch_audio_menu.set_mutual_icons(index, self.menus.select_pixbuf)

    def screen_frame_right_show_menu(self, widget, event):
        if is_right_button(event):
            self.menus.show_screen_menu(event)

    def list_veiw_right_show_menu(self, list_view, event, row_index, col_index, item_x, item_y):
        if row_index != None:
            self.open_file_name = list_view.items[row_index].sub_items[2].text
        else:
            self.open_file_name = None
        self.menus.show_play_list_menu(event)

    def menu_quit(self):
        self.ldmp.quit()
        self.gui.app.window.destroy()

    def menu_fseek(self):
        self.this.key_fseek()

    def menu_bseek(self):
        self.this.key_bseek()

    def menu_stereo_channel(self):
        self.ldmp.normalchannel()
        self.set_audio_menu_state(0)

    def menu_left_channel(self):
        self.ldmp.leftchannel()
        self.set_audio_menu_state(1)

    def menu_right_channel(self):
        self.ldmp.rightchannel()
        self.set_audio_menu_state(2)

    def set_audio_menu_state(self, index):
        self.menus.channel_select_menu.set_mutual_icons(index, self.menus.select_pixbuf)

    def menu_mute_unmute(self):
        self.this.mute_umute()

    def menu_inc_volume(self): # 添加音量.
        self.this.key_inc_volume()

    def menu_dec_volume(self): # 减少音量.
        self.this.key_dec_volume()

    def menu_normal_ascept(self):
        # 默认.
        self.set_menu_ascept(0, ASCEPT_DEFULAT)

    def menu_4X3_ascept(self):
        # 4:3.
        self.set_menu_ascept(1, ASCEPT_4X3_STATE)

    def menu_16X9_ascept(self):
        # 16:9.
        self.set_menu_ascept(2, ASCEPT_16X9_STATE)

    def menu_16X10_ascept(self):
        # 16:10.
        self.set_menu_ascept(3, ASCEPT_16X10_STATE)

    def menu_1_85X1_ascept(self):
        # 1.85:1 比例.
        self.set_menu_ascept(4, ASCEPT_1_85X1_STATE)

    def menu_2_35X1_ascept(self):
        # 2.35:1 比例.
        self.set_menu_ascept(5, ASCEPT_2_35X1_STATE)

    def set_menu_ascept(self, index, state):
        self.menus.video_menu.set_mutual_icons(index, self.menus.select_pixbuf)
        self.ldmp.player.ascept_state = state
        self.this.set_ascept_restart()

    #SINGLA_PLAY, ORDER_PLAY, RANDOM_PLAY, SINGLE_LOOP, LIST_LOOP 
    def menu_play_track(self):
        # 0 代表的是菜单的顺序.
        self.set_play_list_state(0, SINGLA_PLAY)

    def menu_play_default(self):
        self.set_play_list_state(1, ORDER_PLAY)

    def menu_play_random(self):
        self.set_play_list_state(2, RANDOM_PLAY)

    def menu_play_repeat_track(self):
        self.set_play_list_state(3, SINGLE_LOOP)

    def menu_play_repeat_play_list(self):
        self.set_play_list_state(4, LIST_LOOP)

    def set_play_list_state(self, index, state):
        self.play_list.set_state(state)
        self.menus.play_state_menu.set_mutual_icons(index, self.menus.select_pixbuf)

    # 播放列表.
    def menu_open_containing_directory(self):
        import os
        if self.open_file_name:
            path = os.path.split(self.open_file_name)[0]
            if os.path.exists(path):
                open_file(path)
                #open_file(self.open_file_name, False)

    def menu_add_open_file(self):
        self.this.open_files_to_play_list(type_check=False)

    def menu_add_open_dir(self):
        self.this.open_dirs_to_play_list(type_check=False)

    def menu_format_conversion(self):
        format_files = self.this.open_file_dialog()
        # 将文件传入格式转换.
        self.menu_open_format_conv_form(format_files)

    def menu_task_manager(self):
        # 格式转换任务管理器.
        if not self.this.conv_task_gui.get_visible():
            self.this.conv_task_gui.show_all()
        else:
            self.this.conv_task_gui.hide_all()

    def menu_screen_format_conversion(self):
        format_files = []
        for item in self.list_view.get_single_items():
            text = item.sub_items[2].text
            if os.path.exists(text):
                format_files.append(text)
        # 播放列表打开格式转换.
        self.menu_open_format_conv_form(format_files)

    def menu_open_format_conv_form(self, format_files):
        if format_files:
            if self.this.conv_form == None:
                self.this.conv_form = TransmageddonUI(format_files)
                if self.this.conv_task_gui:
                    self.this.conv_form.conv_task_gui = self.this.conv_task_gui
            else:
                self.this.conv_form.conv_list = format_files
                self.this.conv_form.form.show_all_new()
                self.this.conv_form.form.higt_set_bool = True
                self.this.conv_form.form.higt_set_btn_clicked(self.this.conv_form.form.start_btn)
                self.this.conv_form.form.brand_combo.set_active(0)
    
    def menu_properties(self):
        from video_info.gui import VideoInformGui
        video_info_gui = VideoInformGui(self.ldmp)
        video_info_gui.app.show_all()
        
    def menu_ldmp_end_media_player(self, ldmp):
        self.menus.screen_right_root_menu.set_menu_item_sensitive_by_index(15, False)

    def menu_ldmp_start_media_player(self, ldmp):
        self.menus.screen_right_root_menu.set_menu_item_sensitive_by_index(15, True)



