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

import urlparse
import gio

VIDEO_TYPES = ["video", "application/vnd.rn-realmedia"]
AUDIO_TYPES = ["audio"]        
HTML_TYPES = ["http", "https", "mms", "ftp", "sftp", "shttp"]
SUBTITLE_TYPES = ["application/x-subrip", "text/x-ssa"]    

def is_subtitle_file(subtitle_path):
    return get_file_type(subtitle_path) in SUBTITLE_TYPES

def is_valid_video_file(file_path):
    file_type = get_file_type(file_path)
    return (file_type in VIDEO_TYPES) or (file_type.split("/")[0] in VIDEO_TYPES)
    
def is_valid_audio_file(file_path):
    file_type = get_file_type(file_path)
    return (file_type.split("/")[0] in AUDIO_TYPES)
    
def is_valid_url_file(url):    
    return urlparse.urlparse(url).scheme in HTML_TYPES

def is_valid_dmp_file(file_path):                                
    return file_path.lower().endswith(".dmp")
        
def is_file_can_play(file_path):    
    if is_valid_url_file(file_path):
        return True
    else:    
        file_type = get_file_type(file_path)
        if file_type:
            return (file_type.split("/")[0] in AUDIO_TYPES) or (file_type in VIDEO_TYPES) or (file_type.split("/")[0] in VIDEO_TYPES)
        else:
            return False
        
def get_file_type(file_path):
    try:
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
        file_type = gio_file_info.get_attribute_as_string(gio.FILE_ATTRIBUTE_STANDARD_CONTENT_TYPE)
        return file_type
    except Exception, e:
        print e
        return None
