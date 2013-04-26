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



import random



'''播放列表: 
       0        1       2         3          4
   { 单曲播放、顺序播放、随机播放、单曲循环播放、列表循环播放、}
'''


SINGLA_PLAY, ORDER_PLAY, RANDOM_PLAY, SINGLE_LOOP, LIST_LOOP = range(0, 5)

class PlayList(object):
    def __init__(self, list_view):
        self.list_view = list_view
        self.__state = ORDER_PLAY # 默认顺序播放
        self.__file_list = []
        self.__current_file = None
        self.__index = -1

    def set_file_list(self, items):
        if type(items).__name__ == "Items":
            self.__file_list = items
        
    def get_sum(self):
        return (len(self.__file_list))
        
    def clear(self): # 清空播放列表
        self.__file_list = []
        
    def set_state(self, state):
        self.__state = state
        
    def get_next_file(self): # 获取下一个播放文件
        if self.__file_list:
            if self.__state == SINGLA_PLAY:
                return self.__singla_play()
            elif self.__state == ORDER_PLAY:
                return self.__order_play()
            elif self.__state == RANDOM_PLAY:    
                return self.__random_play()
            elif self.__state == SINGLE_LOOP:
                return self.__single_loop_play()
            elif self.__state == LIST_LOOP:
                return self.__list_loop_play()
        else:    
            return False
        
    def get_prev_file(self): # 获取上一个播放文件
        if self.__file_list:            
            if self.__state == SINGLA_PLAY:
                return self.__singla_play()
            elif self.__state == ORDER_PLAY:
                return self.__order_play(False)
            elif self.__state == RANDOM_PLAY:    
                return self.__random_play()
            elif self.__state == SINGLE_LOOP:
                return self.__single_loop_play()
            elif self.__state == LIST_LOOP:
                return self.__list_loop_play(False)
        else:    
            return False
        
    def print_file_list(self): # 获取当前播放文件        
        for file_ in self.__file_list:
            print "playlist:", file_.sub_items[2].text
                    
    def __singla_play(self): # 单曲播放
        if self.__index == -1:
            self.__index += 1
            return self.__set_double_item(self.__file_list[self.__index])
        return False
    
    def __order_play(self, next_check=True): # 顺序播放
        num = 1 # next.
        if not next_check: # prev.
            num = -1
        if (self.__index + num > len(self.__file_list) - 1 
            or self.__index + num < 0):
            return False
        self.__index += num
        return self.__set_double_item(self.__file_list[self.__index])
                                
    def __random_play(self): # 随机播放
        index = random.randint(0, len(self.__file_list)-1)
        self.__index = index
        return self.__set_double_item(self.__file_list[index])
    
    def __single_loop_play(self): # 单曲循环播放
        return self.__set_double_item(self.__file_list[self.__index])
    
    def __list_loop_play(self, next_check=True): # 列表循环播放
        num = 1 # next.
        if not next_check: # pre.
            if self.__index == -1:
                num = 0
            else:
                num = -1
        self.__index += num
        self.__index = self.__index % (len(self.__file_list)) 
        return self.__set_double_item(self.__file_list[self.__index])

    def __set_double_item(self, item):
        self.list_view.set_double_items(item)
        return item.sub_items[2].text
    
    def set_index(self, index):
        self.__index = index

    def get_index(self):
        return self.__index

    def set_items_index(self, play_file): # 设置index.
        index = self.__file_list.index(play_file)
        if index != None:
            self.set_index(index)
        
    
