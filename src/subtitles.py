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

import os
import gobject
from code_to_utf_8 import auto_decode
from type_check import is_subtitle_file
from utils import get_paly_file_name

class SubTitles(gobject.GObject):
    __gsignals__ = {
        "add-subtitle-event":(
            gobject.SIGNAL_RUN_LAST,
            gobject.TYPE_NONE, (gobject.TYPE_STRING,)),
        "scan-subtitle-event":(
            gobject.SIGNAL_RUN_LAST,
            gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
        "select-subtitle-event":(
            gobject.SIGNAL_RUN_LAST,
            gobject.TYPE_NONE, (gobject.TYPE_STRING, gobject.TYPE_INT,)),
        "delete-subtitle-event":(
            gobject.SIGNAL_RUN_LAST,
            gobject.TYPE_NONE, (gobject.TYPE_STRING, gobject.TYPE_INT,)),
        "stop-subtitle-event":(
            gobject.SIGNAL_RUN_LAST,
            gobject.TYPE_NONE, ()),
        "add-delay-subtitle-event":(
            gobject.SIGNAL_RUN_LAST,
            gobject.TYPE_NONE, ()),
        "sub-delay-subtitle-event":(
            gobject.SIGNAL_RUN_LAST,
            gobject.TYPE_NONE, ()),
        "add-scale-subtitle-event":(
            gobject.SIGNAL_RUN_LAST,
            gobject.TYPE_NONE,()),
        "sub-scale-subtitle-event":(
            gobject.SIGNAL_RUN_LAST,
            gobject.TYPE_NONE,()),
        "clear-subtitle-event":(
            gobject.SIGNAL_RUN_LAST,
            gobject.TYPE_NONE, (gobject.TYPE_INT,)),        
        }
    def __init__(self):
        gobject.GObject.__init__(self)
        self.__subtitle_list = []
        
    def clear(self):
        if self.__subtitle_list != []:
            self.emit("clear-subtitle-event", len(self.__subtitle_list) - 1)
            self.__subtitle_list = []
        
    def scan_subtitle(self, video_file, subtitle_path):
        if os.path.exists(subtitle_path):
            path_file_list = os.listdir(subtitle_path)            
            
            scan_subtitle_list = filter(
                lambda path: is_subtitle_file(path) and (not cmp(get_paly_file_name(video_file), get_paly_file_name(path))), 
                map(lambda path_file: os.path.join(subtitle_path, path_file), path_file_list))
            
            if scan_subtitle_list:    
                self.emit("scan-subtitle-event", scan_subtitle_list)
            
    def add(self, path):
        if os.path.exists(path):
            # read subtitle file.
            with open(path, "r") as read_fp:
                fp_str = read_fp.read()            
            # to subtitle code.  
            code_to_utf_8_str = auto_decode(fp_str)
            # write subtitle file.
            with open(path, 'w') as write_fp:
                write_fp.write(code_to_utf_8_str)
        
            self.__subtitle_list.append(path) # save subtitle path.
            self.emit("add-subtitle-event", str(path))
        else:    
            print "add lose..."
            
    def select(self, subtitle_index):
        if subtitle_index < len(self.__subtitle_list):
            subtitle_path = self.__subtitle_list[subtitle_index]
            self.emit("select-subtitle-event", str(subtitle_path), int(subtitle_index))
    
    def delete(self, subtitle_index):
        if subtitle_index < len(self.__subtitle_list):
            subtitle_path = self.__subtitle_list[subtitle_index]
            del self.__subtitle_list[subtitle_index]
            self.emit("delete-subtitle-event", str(subtitle_path), int(subtitle_index))
        
    def stop(self):
        if self.__subtitle_list != []:
            self.emit("stop-subtitle-event")
        
    def add_delay(self):
        if self.__subtitle_list != []:
            self.emit("add-delay-subtitle-event")
        
    def sub_delay(self):
        if self.__subtitle_list != []:
            self.emit("sub-delay-subtitle-event")
        
    def add_scale(self):
        if self.__subtitle_list != []:
            self.emit("add-scale-subtitle-event")
    
    def sub_scale(self):
        if self.__subtitle_list != []:
            self.emit("sub-scale-subtitle-event")
        
if __name__ == "__main__":    
    def add_sub_event(subtitle, STRING):
        print "add_sub_event:", 
        print STRING
        
    def select_sub_event(subtitle, STRING, INT):  
        print "字幕文件:%s 加载完毕!!" % (STRING)
        print "select_sub_event:", STRING, INT
        
    def del_sub_event(subtitle, STRING, INT):            
        print "del_sub_event:", STRING, INT
        
    def stop_sub_event(subtitle):
        print "停止字幕:"
        print "stop_sub_event:", subtitle
        
    ''' 
    1s = 1000ms
    delay(float)
    '''        
    def add_delay_subtitle_event(subtitle):
        print "添加字幕延时",
        print "add_delay_subtitle_event"
        
    def sub_delay_subtitle_event(subtitle):
        print "减少字幕延时",
        print "add_delay_subtitle_event"
        
    def scan_subtitle_event(subtitle, subtitle_list):    
        print "scan_subtitle_event:", subtitle_list
        map(lambda subtitle_file:subtitle.add(subtitle_file), subtitle_list)
        
    def clear_subtitle_event(subtitle, subtitle_len):
        print "clear_subtitle_event:", subtitle_len
        
    def add_scale_subtitle_event(subtitle):    
        print "增加子体大小"
        print "add_delay_subtitle_event"
        
    def sub_scale_subtitle_event(subtitle):
        print "减小字体大小"
        print "sub_scale_subtitle_event"
        
    sub_titles = SubTitles()
    sub_titles.connect("add-subtitle-event", add_sub_event)
    sub_titles.connect("select-subtitle-event", select_sub_event)
    sub_titles.connect("delete-subtitle-event", del_sub_event)
    sub_titles.connect("stop-subtitle-event", stop_sub_event)
    sub_titles.connect("add-delay-subtitle-event", add_delay_subtitle_event)
    sub_titles.connect("sub-delay-subtitle-event", sub_delay_subtitle_event)
    sub_titles.connect("scan-subtitle-event", scan_subtitle_event)
    sub_titles.connect("clear-subtitle-event", clear_subtitle_event)
    sub_titles.connect("add-scale-subtitle-event", add_scale_subtitle_event)
    sub_titles.connect("sub-scale-subtitle-event", sub_scale_subtitle_event)
    
    sub_titles.add("/home/long/视频/1.srt")
    sub_titles.select(0)
    # sub_titles.delete(0)
    sub_titles.stop()
    sub_titles.select(0)
    sub_titles.add_delay() 
    sub_titles.sub_delay()
    sub_titles.scan_subtitle("/home/long/视频/1.avi", "/home/long/视频")
    sub_titles.delete(1)
    sub_titles.clear()
    sub_titles.add_scale()
    sub_titles.sub_scale()
