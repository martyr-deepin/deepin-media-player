#! /Usrh/bin/env python
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


class AsFileName(object):
    '''python能再恶心点吗?'''
    def __init__(self, path):
        '''public.'''
        self.files_list = self.__get_current_suffix_all_file(path)
        '''private.'''
        self.__suffix     = self.__get_file_suffix(path)
        self.__path       = self.__get_file_path(path)
        self.__name       = self.__get_file_name(path)
                
        if self.__name:
            self.__sort_filter()
        else:
            self.files_list = []
            
    def __sort_filter(self):        
        NONE_STATE = 0
        NUMBER_STATE = 1
        sort_state = NONE_STATE
        #
        arry_table = list(self.__name.decode("utf-8"))
        #
        letter = 0
        save_letter = letter
        temp_files_dict = {}        
        for file_ in self.files_list:
            temp_files_dict[file_] = 0
            
        while True:            
            try:
                # save state { number , none }.
                lex = arry_table[letter]
                sort_state = self.__is_number(lex)
                if sort_state == NUMBER_STATE:
                    save_letter = letter
                    while True:                        
                        if arry_table[letter] == ".": # 如果是小数点,查看一位是否为数字.
                            if self.__is_number(arry_table[letter+1]):
                                letter += 1
                            else:    
                                letter = save_letter # 如果小数点后面不是数字,则返回
                                lex = arry_table[letter]
                                sort_state = NONE_STATE
                                break
                        elif self.__is_number(arry_table[letter]): # 如果是数字继续搜索,始终保持前进一位 !!.
                            letter += 1
                        else:
                            lex = arry_table[letter]
                            break
                                                            
                if letter >= len(arry_table) - 1:
                    break
                
                temp_table_dict = {}
                for key in temp_files_dict.keys():                    
                    file_index = temp_files_dict[key]
                    temp_file = key.decode("utf-8")

                    if sort_state == NUMBER_STATE:
                        while True:                        
                            if temp_file[file_index] == '.' or self.__is_number(temp_file[file_index]):
                                file_index += 1
                            else:    
                                break
                            
                    if temp_file[file_index] == lex:
                        file_index += 1
                        temp_table_dict[key] = file_index
                                            
                temp_files_dict = temp_table_dict
                letter += 1                                                        
            except Exception, e:            
                print "sort_filter[error]:", e
                break
                
        temp_table = []
        for key in temp_files_dict.keys():
            temp_table.append(key)
            
        self.files_list = temp_table
        
    def __is_number(self, num):
        if '0' <= num <= '9':
            return True
        else:
            return False
        
    def __get_current_suffix_all_file(self, path):
        return self.__get_current_all_file(self.__get_file_path(path),
                                           self.__get_file_suffix(path))
    
    def __get_current_all_file(self, path, suffix=None):
        if path != None and self.__file_exists(path) and self.__is_dir(path):
            temp_path_list = []
            #
            for path_ in os.listdir(path):
                #
                if self.__is_file(os.path.join(path, path_)) and suffix != None and (path_.endswith(suffix.upper()) or path_.endswith(suffix.lower())):
                    temp_path_list.append(path_)            
            return temp_path_list
        else:
            return None
    
    def __get_file_path(self, path):
        if self.__file_exists(path) and self.__is_file(path):
            return os.path.split(path)[0]
        else:
            return None
    
    def __get_file_name(self, path):    
        if self.__file_exists(path) and self.__is_file(path):
            return os.path.splitext(os.path.split(path)[1])[0]
        else:
            return None
            
    def __get_file_suffix(self, path):  
        if self.__file_exists(path) and self.__is_file(path):
            return os.path.splitext(os.path.split(path)[1])[1]
        else:
            return None

    def __file_exists(self, path):
        return os.path.exists(path)

    def __is_file(self, path):
        return os.path.isfile(path)

    def __is_dir(self, path):
        return os.path.isdir(path)

if __name__ == "__main__":    
    # path = "/home/long/Desktop/色拉英语乐园/色拉英语乐园-1.3集100.#.rmvb"
    path = "/home/long/Desktop/色拉英语乐园/123色拉英语乐园-集100.#.rmvb"
    # path = "/home/long/Desktop/色拉英语乐园/色拉英语乐园-第9集.rmvb"
    as_file_name = AsFileName(path)
    for i in as_file_name.files_list:
        print i
