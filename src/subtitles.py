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

import gobject
from code_to_utf_8 import auto_decode

class Subtitles(gobject.GObject):
    __gsignals__ = {
        "add-subtitle-event":(
            gobject.SIGNAL_RUN_LAST,
            gobject.TYPE_NONE, (gobject.TYPE_STRING,)),
        "select-subtitle-event":(
            gobject.SIGNAL_RUN_LAST,
            gobject.TYPE_NONE, (gobject.TYPE_STRING, gobject.TYPE_INT,)),
        "delete-subtitle-event":(
            gobject.SIGNAL_RUN_LAST,
            gobject.TYPE_NONE, (gobject.TYPE_STRING, gobject.TYPE_INT,)),
        "stop-subtitle-event":(
            gobject.SIGNAL_RUN_LAST,
            gobject.TYPE_NONE, ()),
        }
    def __init__(self):
        gobject.GObject.__init__(self)
        self.__subtitle_list = []
        
    def clear(self):
        self.__sub_list = []
        
    def scan_subtitle(self, path):
        pass
        
    def add(self, path):
        fp_str = open(path, "r").read()
        code_to_utf_8_str = auto_decode(fp_str)

        with open(path, 'w') as fp_open:
            fp_open.write(code_to_utf_8_str)
            
        self.__subtitle_list.append(path) # save subtitle path.
        self.emit("add-subtitle-event", str(path))
        
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
        self.emit("stop-subtitle-event")
        
if __name__ == "__main__":    
    def add_sub_event(subtitle, STRING):
        print STRING
        
    def select_sub_event(subtitle, STRING, INT):  
        print "字幕文件:%s 加载完毕!!" % (STRING)
        print "select_sub_event:", STRING, INT
        
    def del_sub_event(subtitle, STRING, INT):            
        print "del_sub_event:", STRING, INT
        
    def stop_sub_event(subtitle):
        print "停止字幕:"
        print "stop_sub_event:", subtitle
        
    sub_titles = Subtitles()
    sub_titles.connect("add-subtitle-event", add_sub_event)
    sub_titles.connect("select-subtitle-event", select_sub_event)
    sub_titles.connect("delete-subtitle-event", del_sub_event)
    sub_titles.connect("stop-subtitle-event", stop_sub_event)
    
    sub_titles.add("/home/long/1.srt")
    sub_titles.select(0)
    # sub_titles.delete(0)
    sub_titles.stop()
    sub_titles.select(0)
