#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
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

import gobject    

def get_home_path():
    return os.path.expanduser("~")

def init_config():
        # create .config.
        path = get_home_path() + "/.config"
        if not os.path.exists(path):
            os.mkdir(path)
        
        # create deepin-me...    
        path += "/deepin-media-player"    
        if not os.path.exists(path):
            os.mkdir(path)
        
        # create buffer file.
        if not os.path.exists(path + "/subtitle"):
            os.mkdir(path + "/subtitle")
        
        # create config.ini.    
        if not os.path.exists(path + "/config.ini"):
            fp = open(path + "/config.ini", "a")
            fp.close()
            
        if not os.path.exists(path + "/deepin_media_config.ini"):
            fp = open(path + "/deepin_media_config.ini", "a")
            fp.close()            
            # Init config.ini            
            config = Config(path + "/deepin_media_config.ini")
            #[FilePlay]
            config.set("FilePlay", "video_file_open",                     2)
            config.set("FilePlay", "open_new_file_clear_play_list",       "True")
            config.set("FilePlay", "memory_up_close_player_file_postion", "True")
            config.set("FilePlay", "find_play_file_relation_file",        "False")
            config.set("FilePlay", "mouse_progressbar_show_preview",      "False")
            #[SystemSet]
            config.set("SystemSet", "minimize_pause_play", "False")            
            config.set("SystemSet", "font",                "文泉驿微米黑")
            config.set("SystemSet", "font_size",           "12")
            # config.set()
            # config.set()
            # config.set()
            #[PlayControl]
            config.set("PlayControl", "open_file_key",     "Ctrl + o")
            config.set("PlayControl", "open_file_dir_key", "Ctrl + f")
            config.set("PlayControl", "play_or_pause_key", "Space")
            config.set("PlayControl", "seek_key",          "Right")
            config.set("PlayControl", "back_key",          "Left")
            config.set("PlayControl", "full_key",          "Return")
            config.set("PlayControl", "pre_a_key",         "Page_Up")
            config.set("PlayControl", "next_a_key",        "Page_Down")
            config.set("PlayControl", "add_volume_key",    "Up")
            config.set("PlayControl", "sub_volume_key",    "Down")
            config.set("PlayControl", "mute_key",          "m")
            config.set("PlayControl", "concise_key",       "Shift+Return")
            #[OtherKey]
            config.set("OtherKey", "add_brightness_key",     "=")
            config.set("OtherKey", "sub_brightness_key",     "-")
            config.set("OtherKey", "inverse_rotation_key",   "w")
            config.set("OtherKey", "clockwise_key",          "e")
            config.set("OtherKey", "sort_image_key",         "Alt + a")
            config.set("OtherKey", "switch_audio_track_key", "NULL")
            config.set("OtherKey", "load_subtitle_key",      "Alt + o")
            config.set("OtherKey", "subtitle_delay_key",     "]")
            config.set("OtherKey", "subtitle_advance_key",   "[")
            config.set("OtherKey", "mouse_left_single_clicked", "暂停/播放")
            config.set("OtherKey", "mouse_left_double_clicked", "全屏")
            config.set("OtherKey", "mouse_wheel_event", "音量")
            #[SubtitleSet]
            config.set("SubtitleSet", "ai_load_subtitle", "True")
            config.set("SubtitleSet", "specific_location_search", "~/.config/deepin-media-player/subtitle")
            #[ScreenshotSet]
            config.set("ScreenshotSet", "save_clipboard", "False")
            config.set("ScreenshotSet", "save_file", "True")
            config.set("ScreenshotSet", "save_path", "~/.config/deepin-media-player/image")
            config.set("ScreenshotSet", "save_type", ".png")
            config.set("ScreenshotSet", "current_show_sort", "False")
            # save ini config.
            config.save()

class Config(gobject.GObject):
    __gsignals__ = {
        "config-changed" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                            (gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING))
        }

    def __init__(self, ini_path):
        gobject.GObject.__init__(self)
        self.ini_path = ini_path
        self.section_bool = False
        self.argv_bool = False        
        self.section_dict = {}
        self.argv_save_ch = ""
        self.section_save_ch = ""
        
        # init function.
        try:
            if not os.path.exists(ini_path):                
                init_config()
                
            self.fp = open(ini_path, "r")
            self.init_config()                                            
        except Exception, e:    
            print "%s" % (e)
        
        
            
    def init_config(self):        
        
        while True:
            ch = self.fp.read(1)
            
            if not ch: # Read over.
                break
            
            if self.section_bool:
                if "[" == ch:
                    self.fp.seek(-2, 1)
                    token_enter_bool = self.fp.read(1)
                    ch = self.fp.read(1)
                    if ("\n" == token_enter_bool) and ("[" == ch):
                        self.section_save_ch = ""
                        self.section_bool = False
                        self.fp.seek(-1, 1)
                    else:    
                        self.argv_save_ch += ch
                        # ch = self.fp.read(1)
                        
                else:# Read argv.        
                    if "\n" == ch:
                        # print self.argv_save_ch
                        self.split(self.argv_save_ch, "=")
                        self.argv_save_ch = ""
                    else:    
                        self.argv_save_ch += ch
                    
            else:        
                if "[" == ch:                
                    while True:                    
                        ch = self.fp.read(1)                    
                    
                        if "\n" == ch:
                            self.section_dict[self.section_save_ch] = {} # save section name.
                            break
                    
                        if "]" == ch:
                            self.section_bool = True                       
                        else:
                            if ch != "[":
                                self.section_save_ch += ch
                            
    def split(self, string, token):        
        split_lsit = [] 
        temp_str = ""
        temp_save_num = []
        temp_num = 0
        # scan token.
        for ch in string:
            if ch == token and (" " == string[temp_num-1]):
                temp_save_num.append(temp_num)       
            temp_num += 1
        if temp_save_num:
            argv_name = string[0:temp_save_num[0]].strip()
            argv_value = string[temp_save_num[0]+1:].strip()
            self.section_dict[self.section_save_ch][argv_name] = argv_value
            
    def set(self, section, argv, value):
        section = str(section)
        argv    = str(argv)
        value   = str(value)
        
        if not self.section_dict.has_key(section):
            self.section_dict[section] = {argv:str(value)}
        else:    
            if not self.section_dict[section].has_key(argv):
                self.section_dict[section][argv] = str(value)
            else:    
                self.section_dict[section][argv] = str(value)
                
        self.emit("config-changed", section, argv, value)         
                
    def get(self, section, argv):
        section = str(section)
        argv    = str(argv)
        
        if self.section_dict.has_key(section):
            if self.section_dict[section].has_key(argv):                
                return self.section_dict[section][argv] 
            
    def get_argvs(self, section):    
        section = str(section)
        
        if self.section_dict.has_key(section):
            return self.section_dict[section]
        
    def get_argv_bool(self, section, argv):    
        section = str(section)
        argv    = str(argv)
        if self.section_dict.has_key(section):
            if self.section_dict[section].has_key(argv):
                return True
        return None    
    
    def modify_argv(self, section, argv, new_argv, new_value):
        section = str(section)
        argv    = str(argv)
        
        if self.section_dict.has_key(section):
            if self.section_dict[section].has_key(argv):
                del self.section_dict[section][argv]
                self.section_dict[section][new_argv] = new_value
                return True
        return None    
    
    def save(self):
        fp = open(self.ini_path, "w")
        for section_key in self.section_dict.keys():
            section_string = "[%s]" % (section_key)
            fp.write(section_string + "\n") # Save section.
            for argv_key in self.section_dict[section_key]:                
                argv_string = "%s = %s" % (argv_key, self.section_dict[section_key][argv_key])
                fp.write(argv_string + "\n") # Save argv. 
                
import os                                
# config = Config(os.path.expanduser("~") + "/.config/deepin-media-player/deepin_media_config.ini")


if __name__ == "__main__":
    def test_get_section(confi, section, option, value):
        print section
        print option
        print value
    config = Config(os.path.expanduser("~") + "/.config/deepin-media-player/config.ini")    
    config.connect("config-changed", test_get_section)
    config.set("window", "w[fdsfsdf]idth", "32.232323")
    # print "修改width:%s" % config.get("window", "width")
    # config.set("window", "width", "473843.343")
    # print "修改width:%s" % config.get("window", "h")
    # config.set("window", 3434, 343)
    # print "得到3434:=%s" % config.get("mplayer", "/home/long/long")
    # config.set("window1", "width", "32.232323")
    # config.set("window2", "width", "32.232323")
    # config.set("window3", "width", "32.232323")
    config.save()
    

    
