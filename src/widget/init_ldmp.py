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


from utils import get_config_path
from ini   import Config
from locales import _
import os

def init_media_player_config():
    path = get_config_path()
    print "init_media_player_config...", path
    # 创建保存东西的文件夹.
    for subdir in ["subtitle", "buffer", "image"]: 
        subpath = os.path.join(path, subdir)
        if not os.path.exists(subpath):
            print subpath
            os.makedirs(subpath)
    
    # 创建临时文件.
    for subdir in ["/tmp/buffer", "/tmp/preview"]:
        if not os.path.exists(subdir):
            os.makedirs(subdir)
    
    # 创建配置文件.
    config_path = os.path.join(path, "config.ini")
    if not os.path.exists(config_path):
        fp = open(config_path, "a")
        fp.close()    
        
    # Create media config file if it not exists.
    media_config_path = os.path.join(path, "deepin_media_config.ini")
    if not os.path.exists(media_config_path):
        fp = open(media_config_path, "a")
        fp.close()
        
        # Init config.ini            
        config = Config(media_config_path)
        
        # Init window.
        config.set("Window", "init_window", "True")
        
        #[FilePlay] # 播放设置.
        for argv, value in ([
                ("video_file_open",                          2),
                ("open_new_file_clear_play_list", "True"),
                ("memory_up_close_player_file_postion", "True"),
                ("find_play_file_relation_file", "False"),
                ("mouse_progressbar_show_preview", "False"),
                ("check_run_a_deepin_media_player", "False"),
                ("minimize_pause_play", "True") # 最小化暂停播放.
                ]):
            config.set("FilePlay", argv, value)
            
        #[SystemSet] # 系统设置.
        for argv, value in ([
                ("start_sys_bubble_msg", "True"),
                ("start_play_win_msg",   "False"),
                ("font",                 "文泉驿微米黑"),
                ("font_size",            "16")
                ]):
            config.set("SystemSet", argv, value)   
            
         # 快捷键
        #[PlayControl] 播放控制.
        for argv, value in ([
                ("play_control_bool", "True"),
                ("open_file_key", "Ctrl + o"),
                ("open_file_dir_key", "Ctrl + f"),
                ("play_or_pause_key", "Space"),
                ("seek_key", "Right"),
                ("back_key", "Left"),
                ("full_key", "Return"),
                ("pre_a_key", "Page_Up"),
                ("next_a_key", "Page_Down"),
                ("add_volume_key", "Up"),
                ("sub_volume_key", "Down"),
                ("mute_key", "m"),
                ("concise_key", "Shift + Return")
                ]):
            config.set("PlayControl", argv, value)
            
        #[SubKey] 字幕控制. 
        for argv, value in ([
                ("subkey_bool", "True"),
                ("subkey_add_delay_key", "["),
                ("subkey_sub_delay_key", "]"),
                ("subkey_load_key", "Alt + o"),
                ("subkey_add_scale_key", "Alt + Left"),
                ("subkey_sub_scale_key", "Alt + Right"),
                ]):
            config.set("SubKey", argv, value)
            
        #[OtherKey] 其它快捷键.
        for argv, value in ([
                ("other_key_bool", "True"),
                ("add_brightness_key", "="),
                ("sub_brightness_key", "-"),
                ("inverse_rotation_key", "w"),
                ("clockwise_key", "e"),
                ("sort_image_key", "Alt + a"),
                ("switch_audio_track_key", _("Disabled")),
                # ("load_subtitle_key", "Alt + o"),
                # ("subtitle_delay_key", "]"),
                # ("subtitle_advance_key", "["),
                ("mouse_left_single_clicked", _("Pause/Play")),
                ("mouse_left_double_clicked", _("Full Screen")),
                ("mouse_wheel_event", _("Volume")),
                ]):
            config.set("OtherKey", argv, value)

        #[SubtitleSet] 字幕.
        for argv, value in ([
                ("ai_load_subtitle", "True"),
                # ("specific_location_search", os.path.join(get_home_path(), ".config/deepin-media-player/subtitle"))
                ("specific_location_search",  "~/.config/deepin-media-player/subtitle")
                ]):
            config.set("SubtitleSet", argv, value)
        
        #[ScreenshotSet] 截图设置.
        for argv, value in ([
                ("save_clipboard", "False"),
                ("save_file", "True"),
                # ("save_path", os.path.join(get_home_path(), ".config/deepin-media-player/image")),
                ("save_path", "~/.config/deepin-media-player/image"),
                ("save_type", ".png"),
                ("current_show_sort", "False")
                ]):
            config.set("ScreenshotSet", argv, value)    
            
        config.save()
        

