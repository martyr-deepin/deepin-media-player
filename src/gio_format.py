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


import gio

class Format(object):
    def __init__(self):
        self.video_foramt = ["video", 
                             "application/vnd.rn-realmedia"]
        self.audio_format = ["audio"]
        
        
    def get_video_bool(self, file_path):
        file_format = self.format_function(file_path)
        if (file_format in self.video_foramt) or (file_format.split("/")[0] in self.video_foramt):
            return True
        else:
            return False
        
    def get_audio_bool(self, file_path):
        file_format = self.format_function(file_path)
        if (file_format.split("/")[0] in self.audio_format):
            return True
        else:
            return False
        
    def get_play_bool(self, file_path):    
        file_format = self.format_function(file_path)
        if (file_format.split("/")[0] in self.audio_format) or (file_format in self.video_foramt) or (file_format.split("/")[0] in self.video_foramt):
            return True
        else:
            return False
        
    def format_function(self, file_path):
        gio_file = gio.File(file_path)
        file_atrr = ",".join([gio.FILE_ATTRIBUTE_STANDARD_CONTENT_TYPE,
                              gio.FILE_ATTRIBUTE_STANDARD_TYPE, 
                              gio.FILE_ATTRIBUTE_STANDARD_NAME,
                              gio.FILE_ATTRIBUTE_STANDARD_SIZE,
                              gio.FILE_ATTRIBUTE_STANDARD_DISPLAY_NAME,
                              gio.FILE_ATTRIBUTE_TIME_MODIFIED,
                              gio.FILE_ATTRIBUTE_STANDARD_ICON,
                              ])
        gio_file_info = gio_file.query_info(file_atrr)
        file_format = gio_file_info.get_attribute_as_string(gio.FILE_ATTRIBUTE_STANDARD_CONTENT_TYPE)
        return file_format

    
format = Format()

if __name__ == "__main__":
    print format.get_play_bool("/home/long/bin/源码世界/音频和视频格式/format.py")
    print format.get_play_bool
