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

import chardet
import mmap
import re
# 只需要小学知识就OK了,算吧.. 格式:(start_time, end_time, text)

class LrcRead(object):
    def __init__(self):
       self.start_time = 0.0
       self.end_time = 0.0
       self.string_list = []
       self.next_point = 0                     
       
    def read(self, lrc_file):        
        self.next_point = 0
        with open(lrc_file, "r") as fp:
            self.map_buffer = mmap.mmap(fp.fileno(), 0, access=mmap.ACCESS_READ)
        # other code to utf-8 code.
        encoding = chardet.detect(str(self.map_buffer[:]))["encoding"]
        
        if encoding != "utf-8":
            to_string = str(self.map_buffer[:]).decode(encoding).encode("utf-8")
        else:    
            to_string = str(self.map_buffer[:]).decode("utf-8")            
        # all '\r' to '\n'.
        to_string = to_string.replace('\r', '\n')
        # string to list.
        self.string_list = to_string.split("\n")
        # 
        temp_string_list = []
        for lrc_line in self.string_list:
            if lrc_line not in [ "\n", ""]:
                if lrc_line[0] == "[":
                    if lrc_line[1] in ['0', '1', '2', '3', '5',
                                       '6', '7', '8', '9']:
                        temp_string_list.append(lrc_line)
                    
        self.string_list = temp_string_list                
        
        for lrc_line in self.string_list:
            if lrc_line not in [ "\n", ""]:
                if lrc_line[0] == "[":
                    self.__function(lrc_line)            
            self.next_point += 1
            
    def __function(self, lrc_line):
        if self.next_point+1 < len(self.string_list):
            patter = r'\[.+\]'
            mc_list = re.findall(patter, lrc_line)
            print "上一个时间:", mc_list
            # print len(mc_list[0])
            # print lrc_line[len(mc_list[0]):]        
            mc_list = re.findall(patter, self.string_list[self.next_point+1])
            print "下一个时间:", mc_list
        
class LrcBuffer(object):
    def __init__(self):
        self.__buffer_list = []
    
    def add_buffer(self, buffer):   # buffer (time, text)
        self.__buffer_list.append(buffer)
                
if __name__ == "__main__":
    lrc_read = LrcRead()
    lrc_read.read("/home/long/下载/1.lrc")    
