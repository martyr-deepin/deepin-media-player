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
    def unicode_bool(self, strings):
        '''Unicode.'''
        # False -> asicc. # True -> unicoe.
        return not (0 <= ord(strings[0:1].lower()) <= 127)
    
    def number_bool(self, number):
        '''Number.'''
        return (0 <= ord(number[0:1].lower()) <= 127) and (49 <= ord(number[0:1].lower()) <= 57)
        
    def en_bool(self, en):
        '''English.'''        
        return (0 <= ord(en[0:1].lower()) <= 127) and (65 <= ord(en[0:1].lower()) <= 90 or 97 <= ord(en[0:1].lower()) <= 122)    
    
    def unicoe_to_index(self, strings, index):
        return None if len(strings.decode('utf-8')) <= index else strings.decode('utf-8')[index]
    
    def unicode_to_ascii(self, strings):            
        if 0 <= ord(strings[0:1].lower()) <= 127:
            return strings[0:1].lower() 
        
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
        
