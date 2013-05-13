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

def init_media_player_config(config):
    path = get_config_path()
    print "init_media_player_config...", path
    # 创建保存东西的文件夹.
    for subdir in ["subtitle", "buffer", "image", "plugins"]: 
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
        #config = Config(media_config_path)
        
        # Init window.
        config.set("Window", "init_window", "True")
        
        #[FilePlay] # 播放设置.
        # 2 视频适应窗口.
        for argv, value in ([
                # 视频文件打开时.
                ("video_file_open",                          2),
                # 打开新文件时清空播放列表.
                ("open_new_file_clear_play_list", "True"),
                # 自动从上次停止位置播放.
                ("memory_up_close_player_file_postion", "True"),
                # 自动查找相似文件连续播放.
                ("find_play_file_relation_file", "False"),
                # 鼠标悬停进度条时显示预览图.
                ("mouse_progressbar_show_preview", "False"),
                # 允许同时运行多个深度影音.
                ("check_run_a_deepin_media_player", "False"),
                # 最小化暂停播放.
                ("minimize_pause_play", "True") 
                ]):
            config.set("FilePlay", argv, value)
            
        #[SystemSet] # 系统设置.
        for argv, value in ([
                # 启用相同气泡提示.
                ("start_sys_bubble_msg", "False"),
                # 启用播放窗口提示.
                ("start_play_win_msg",   "True"),
                # 字体.
                ("font",                 "文泉驿微米黑"),
                # 字号.
                ("font_size",            "16")
                ]):
            config.set("SystemSet", argv, value)   
            
         # 快捷键
        #[PlayControl] 播放控制.
        for argv, value in ([
                # 开启热键.
                ("play_control_bool", "True"),
                # 打开文件
                ("open_file_key", "Ctrl + o"),
                # 打开目录.
                ("open_file_dir_key", "Ctrl + f"),
                # 暂停/播放.
                ("play_or_pause_key", "Space"),
                # 快进.
                ("seek_key", "Right"),
                # 倒退.
                ("back_key", "Left"),
                # 全屏.
                ("full_key", "Return"),
                # 上一首.
                ("pre_a_key", "Page_Up"),
                # 下一首.
                ("next_a_key", "Page_Down"),
                # 增大音量.
                ("add_volume_key", "Up"),
                # 增小音量.
                ("sub_volume_key", "Down"),
                # 静音.
                ("mute_key", "m"),
                # 简洁模式.
                ("concise_key", "Shift + Return")
                ]):
            config.set("PlayControl", argv, value)
            
        #[SubKey] 字幕控制. 
        for argv, value in ([
                # 开启热键.
                ("subkey_bool", "True"),
                # 字幕提前0.5秒.
                ("subkey_add_delay_key", "["),
                # 字幕延时0.5秒.
                ("subkey_sub_delay_key", "]"),
                # 自动载入字幕.
                ("subkey_load_key", "Alt + o"),
                # 增大字幕尺寸.
                ("subkey_add_scale_key", "Alt + Left"),
                # 减少字幕尺寸.
                ("subkey_sub_scale_key", "Alt + Right"),
                ]):
            config.set("SubKey", argv, value)
            
        #[OtherKey] 其它快捷键.
        for argv, value in ([
                # 开启热键.
                ("other_key_bool", "True"),
                # 升高音量
                ("add_brightness_key", "="),
                # 降低音量
                ("sub_brightness_key", "-"),
                # 逆时针旋转.
                ("inverse_rotation_key", "w"),
                # 顺时针旋转.
                ("clockwise_key", "e"),
                # 截图.
                ("sort_image_key", "Alt + a"),
                # 钱换音轨.
                ("switch_audio_track_key", _("Disabled")),
                # ("load_subtitle_key", "Alt + o"),
                # ("subtitle_delay_key", "]"),
                # ("subtitle_advance_key", "["),
                # 鼠标左键单击.
                ("mouse_left_single_clicked", _("Pause/Play")),
                # 鼠标左键双击.
                ("mouse_left_double_clicked", _("Full Screen")),
                # 鼠标滚轮.
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
        

