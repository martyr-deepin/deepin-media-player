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


from widget.keymap  import get_keyevent_name

class MediaPlayKeys(object):
    def __init__(self, this):
        self.this = this
        self.__init_values()

    def __init_values(self):
        self.gui = self.this.gui
        self.config = self.this.config
        self.gui.app.window.connect("key-press-event", self.app_window_key_press_event)
        self.init_config_key()
        '''
        self.keymap = {} # 快捷键.
        self.keymap["Escape"]  = self.this.key_quit_fullscreen
        self.keymap["Return"]  = self.this.fullscreen_function
        self.keymap["Space"]   = self.this.key_pause
        self.keymap["Shift + Return"] = self.this.key_concise_mode
        '''
        
    def app_window_key_press_event(self, widget, event):
        keyval_name = get_keyevent_name(event)
        if keyval_name:
            keyval_name = keyval_name.lower()
        self.init_config_key()
        if self.keymap.has_key(keyval_name):
            self.keymap[keyval_name]()

    def temp_sub_print(self):
        print "[keymap]===>>>subtitle keys 还未建立...."

    def init_config_key(self):
        self.keymap = {}
        # Init Config keys.
        
        # open file key init.(left)        
        play_control_bool = self.config.get("PlayControl", "play_control_bool")
        sub_key_bool = self.config.get("SubKey", "subkey_bool")
        other_key_bool = self.config.get("OtherKey", "other_key_bool")
        
        # [PlayControl] Init.
        if play_control_bool == "True":    
            for section, argv, connect_fun in [
                ("PlayControl", "open_file_key",     self.this.open_files_to_play_list),
                ("PlayControl", "open_file_dir_key", self.this.open_dirs_to_play_list),
                ("PlayControl", "play_or_pause_key", self.this.key_pause),
                ("PlayControl", "seek_key",          self.this.key_fseek),
                ("PlayControl", "back_key",          self.this.key_bseek),
                ("PlayControl", "full_key",          self.this.fullscreen_function),
                ("PlayControl", "pre_a_key",         self.this.prev),
                ("PlayControl", "next_a_key",        self.this.next),
                ("PlayControl", "add_volume_key",    self.this.key_inc_volume),
                ("PlayControl", "sub_volume_key",    self.this.key_dec_volume),
                ("PlayControl", "mute_key",          self.this.mute_umute),
                ("PlayControl", "concise_key",       self.this.key_concise_mode)
                ]:    
               
                config_key = self.config.get(section, argv)
                self.keymap[config_key.lower()] = connect_fun
              
            self.keymap["Escape".lower()] = self.this.key_quit_fullscreen        
            #self.keymap["KP_Enter".lower()] = self.this.fullscreen_function 
            
        if sub_key_bool == "True":    
            for section , argv, connect_fun in [
                ("SubKey", "subkey_load_key",      None), 
                ("SubKey", "subkey_add_delay_key", None),                
                ("SubKey", "subkey_sub_delay_key", None),                
                ("SubKey", "subkey_add_scale_key", None),
                ("SubKey", "subkey_sub_scale_key", None),                
                ]:
                config_key = self.config.get(section, argv)
                self.keymap[config_key] = self.temp_sub_print#connect_fun
                
        # [OtherKey].
        if other_key_bool == "True":  
            for section, argv, connect_fun in [
                ("OtherKey", "add_brightness_key", None),
                ("OtherKey", "sub_brightness_key", None),
                ("OtherKey", "inverse_rotation_key", None),
                ("OtherKey", "clockwise_key",   None),
                ("OtherKey", "sort_image_key",  None),
                ("OtherKey", "switch_audio_track_key",  None),
                # ("OtherKey", "load_subtitle_key",  self.key_load_subtitle),
                # ("OtherKey", "subtitle_delay_key", self.key_subtitle_delay),
                # ("OtherKey", "subtitle_advance_key", self.key_subtitle_advance),
                ]:
                config_key = self.config.get(section, argv)
                self.keymap[config_key] = connect_fun 


