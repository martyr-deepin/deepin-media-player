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

import threading
import os
from type_check import is_file_can_play, is_valid_dmp_file

############################################################
### get widget : x, y, width, height.
def allocation(widget):
    cr = widget.window.cairo_create()
    rect = widget.get_allocation()
    return cr, rect.x, rect.y, rect.width, rect.height

############################################################
### threads.
def path_threads(path, mp):
    '''Thread path.'''
    os.chdir(path)
    
    if os.path.isdir(path):
        for i in os.listdir(path):
            if "." == i[0:1]:
                continue
            
            new_path = os.path.join(path, i)
                            
            if os.path.isdir(new_path):
                path_thread_id = threading.Thread(target=path_threads, args=(new_path, mp))
                path_thread_id.setDaemon(True)
                path_thread_id.start()
                
            if os.path.isfile(new_path):    
                new_file = new_path                
                # .dmp add play file..
                if is_valid_dmp_file(new_file):
                    mp.load_playlist(new_file)
                    
                # play file[.rmvb, .avi...].    
                if(is_file_can_play(new_file)):
                    old_file = new_file
                    file1, file2 = os.path.splitext(new_file)
                    new_file = file1 + file2.lower()                    
                    os.rename(old_file,new_file)
                    mp.add_play_file(new_file)                
                    
def get_paly_file_name(path):
    return os.path.splitext(os.path.split(path)[1])[0]

############################################################                    
### get video information.
class SubTitles(object):                    
    def __init__(self):
        self.id_file_sub_id = 0
        self.id_file_sub_filename = "/home/long/1.ass"
        # self.added_subtitle_file = "/home/long/1.ass"

class Video_Information(object):
    def __init__(self):
        self.playing = "/home/long/1.rmvb"
        self.file_format = "REAL"
        self.stream_description = "Audio Stream"
        self.stream_mimetype = "audio/x-pn-realaudio"
        self.id_audio_id = 0
        self.id_video_id = 1
        self.load_subtitles = "/home/long/"
        ########################### 
        # all subtitles file save. 
        # SubTitles class.
        self.id_subtitles_list = []        
        ###########################
        self.id_filename = "/home/long/1.rmvb"
        self.id_demuxer = "real"
        self.id_video_format = "rv40"
        self.id_video_bitrete = 0
        self.id_video_width = 1280
        self.id_video_height = 720
        self.id_video_eps = 23.000
        self.id_video_aspect = 0.0000
        self.id_audio_format = "cook"
        self.id_audio_bitrate = 0
        self.id_audio_rate = 44100
        self.id_audio_nch = 2
        self.id_start_time = 0.00
        self.id_length = 6081.00
        self.id_seekable = 1
        self.id_chapters = 0
        self.id_video_codec = "ffrv40"
        self.id_audio_bitrate = 96464
        self.id_audio_rate = 44100
        self.id_audio_nch = 2
                                    
def get_video_information(video_path):                    
    cmd = "mplayer -identify -frames 5 -endpos 0 -vo null  '%s'" % (video_path)
    pipe = os.popen(str(cmd))
    print video_string_to_information(pipe)
    
def video_string_to_information(pipe):
    # print pipe.read()    
    return Video_Information()
    
    
if __name__ == "__main__":    
    get_video_information("/home/long/1.rmvb")
    
    
