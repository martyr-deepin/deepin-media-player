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

class LrcRead(object):
    def __init__(self):
        pass

    def read(self, lrc_file):
        
        with open(lrc_file, "r") as fp:
            self.map_buffer = mmap.mmap(fp.fileno(), 0, access=mmap.ACCESS_READ)
        # other code to utf-8 code.
        encoding = chardet.detect(str(self.map_buffer[:]))["encoding"]
        to_string = str(self.map_buffer[:]).decode(encoding).encode("utf-8")
        # 
        print to_string 
        
   # def 
   
class LrcBuffer(object):
    def __init__(self):
        self.__buffer_list = []
    
    def add_buffer(self, buffer):   # buffer (time, text)
        self.__buffer_list.append(buffer)
                
if __name__ == "__main__":
    lrc_read = LrcRead()
    lrc_read.read("/home/long/下载/1.lrc")    
