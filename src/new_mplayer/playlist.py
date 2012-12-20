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


'''播放列表: 
       0        1       2         3          4
   { 单曲播放、顺序播放、随机播放、单曲循环播放、列表循环播放、}
'''

SINGLA_PLAY, ORDER_PLAY, RANDOM_PLAY, SINGLE_LOOP, LIST_LOOP= range(0, 5)

class PlayList(object):
    def __init__(self):
        self.play_state = ORDER_PLAY # 默认顺序播放
        self.file_list = []
        
    def add_play_list(self, play_file):
        self.file_list.append(play_file)
        
    def clear_play_list(self):
        self.file_list = []
        
    def singla_play(self): #单曲播放
        pass
    
        
