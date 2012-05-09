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


class UnicodeToAscii(object):    
    def __init__(self):
        self.list_dict = {}
        
    def dict_add_strings(self, strings):            
        
        key = self.unicode_to_ascii(strings)
            
        keys = self.list_dict.keys()
        if key in keys:
            self.list_dict[key].append(strings)
        else:    
            self.list_dict[key] = []
            self.list_dict[key].append(strings)
            
    def unicode_to_ascii(self, strings):            
        if 0 <= ord(strings[0:1].lower()) <= 127:
            key = strings[0:1].lower()            
            return key
        
        key = strings.decode('utf-8') # str to utf-8(unicode)
        key = key[0].encode('gbk') # utf-8 to gbk.                                
        ascii = ord(key[0]) * 256 + ord(key[1]) - 65536 
        
        if ascii >= -20319 and ascii <= -20284:  
            return 'a'  
        if ascii >= -20283 and ascii <= -19776:  
            return 'b'  
        if ascii >= -19775 and ascii <= -19219:  
            return 'c'  
        if ascii >= -19218 and ascii <= -18711:  
            return 'd'  
        if ascii >= -18710 and ascii <= -18527:  
            return 'e'  
        if ascii >= -18526 and ascii <= -18240:  
            return 'f'  
        if ascii >= -18239 and ascii <= -17923:  
            return 'g'  
        if ascii >= -17922 and ascii <= -17418:  
            return 'h'  
        if ascii >= -17417 and ascii <= -16475:  
            return 'j'  
        if ascii >= -16474 and ascii <= -16213:  
            return 'k'  
        if ascii >= -16212 and ascii <= -15641:  
            return 'l'  
        if ascii >= -15640 and ascii <= -15166:  
            return 'm'  
        if ascii >= -15165 and ascii <= -14923:  
            return 'n'  
        if ascii >= -14922 and ascii <= -14915:  
            return 'o'  
        if ascii >= -14914 and ascii <= -14631:  
            return 'p'  
        if ascii >= -14630 and ascii <= -14150:  
            return 'q'  
        if ascii >= -14149 and ascii <= -14091:  
            return 'r'  
        if ascii >= -14090 and ascii <= -13119:  
            return 's'  
        if ascii >= -13118 and ascii <= -12839:  
            return 't'  
        if ascii >= -12838 and ascii <= -12557:  
            return 'w'  
        if ascii >= -12556 and ascii <= -11848:  
            return 'x'  
        if ascii >= -11847 and ascii <= -11056:  
            return 'y'  
        if ascii >= -11055 and ascii <= -10247:  
            return 'z'  
        
    def get_key_list(self, key):            
        try:
            return self.list_dict[key]
        except:
            return None
        
    def get_strcmp_bool(self, str1, str2): 
        '''str1 cmp str2:True or False'''
        str1_num = len(str1)
        str2_num = len(str2)
        
        str1_point = 0
        str2_point = 0
        
        if str1_num > str2_num: # 'hailongqiu' vs 'hailong' 
            return False
        
        if str1 == str2: # 'hailongqiu' vs 'hailongqiu'
            return True        
                
        while str1_point != str1_num: # 'hailongqiu' vs ['hailong', 'jing'] -> 'h' vs ['h', 'j']            
            if str1[str1_point] != str2[str2_point]:
                return False            
            str1_point += 1
            str2_point += 1                                        
            
        return True
    
    def print_list_dict(self):    
        '''print list dict.'''
        for list_key in self.list_dict:
            print "self.list_dict" + "[" + list_key + "]" + "=" + "[",
            for list_strs in self.list_dict[list_key]:
                print "'" + list_strs + "'" + ",",
            print "]"    
            

import os        

if __name__ == "__main__":        
    test = UnicodeToAscii()        
    
    # test.dict_add_strings("abcef")
    # for i in range(0, 1000):
    temp_file_name = os.listdir('/home/long/音乐')
    for i in temp_file_name:
        test.dict_add_strings(i)
    
    str1 =  "张学友-一"   
    list = test.get_key_list(test.unicode_to_ascii(str1)) # 得到搜索的首字母,搜索出散列表匹配的所有字符串
    
    save_list = []
    if list:
        for str2 in list:
            if test.get_strcmp_bool(str1, str2):
                save_list.append(str2)
    print "符合匹配的字符"    
    # print save_list
    for i in save_list:
        print i
    # test.print_list_dict()
