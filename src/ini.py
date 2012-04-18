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
import sys

class INI(object):
    def __init__(self, ini_path):
        self.ini_fp = open(ini_path, "r")
        self.ch = ''
        self.line_num = 0  # 行号
        self.column_num = 0 # 列号
        
        while True:            
            self.ch = self.ini_fp.read(1)                
            self.column_num += 1 #计算列号
            if '\n' == self.ch:
                self.line_num += 1  #计算行号
                self.column_num = 0 #清空列计数器
            if ' ' !=self.ch: #过滤空格
                if not self.ch:
                    break
                else: #开始处理 字符.
                    if self.unicode_bool():
                        self.error_input("多余的中文字符..请检查配置文件")
                        sys.exit(0)
                    elif self.number_bool():    
                        print "这是数字"
                    elif self.letter_bool():    
                        print "这是字母"
                    else:
                        self.symbol_func()
                
        self.ini_fp.close()    
        self.line_num += 1
        print "提示:共有%d行ini配置代码." % (self.line_num)       
        
    def error_input(self, error_mesagbox):    
        print "%d行%d列ini配置错误提示(%s)" % (self.line_num, self.column_num, error_mesagbox)
        
    def number_bool(self):    
        '''判断是否为数字'''
        ord_ch = ord(self.ch)
        return True if (48 <= ord_ch <= 57) else False
    
    def letter_bool(self):
        '''判断是否为字母'''
        ord_ch = ord(self.ch)
        return True if ((65 <= ord_ch <= 90) and (97 <= ord_ch <= 122))  else False
    
    def unicode_bool(self):
        '''判断是否为unicode'''
        ord_ch = ord(self.ch)
        return True if not(0 <= ord_ch <= 127) else False
    
    '''符号处理 注释: # /**/ , 赋值: = , []'''
    def symbol_func(self):
        if '#' == self.ch: #过滤 '#'(注释)
            while '\n' != self.ch:
                self.ch = self.ini_fp.read(1)
                # print self.ch
                if not self.ch:
                    break
            if '\n' == self.ch:    
                self.ini_fp.seek(-1, 1)    
        elif '/' == self.ch: #过滤/**/注释   
                self.ch = self.ini_fp.read(1)
                save_line_num = self.line_num                
                save_column_num = self.column_num
                if '*' == self.ch:
                    while True:
                        self.ch = self.ini_fp.read(1)
                        if '\n' == self.ch:
                            self.line_num += 1
                            self.column_num = 0
                        if '*' == self.ch:
                            self.ch = self.ini_fp.read(1)
                            if '/' == self.ch:                            
                                break
                        if not self.ch:
                            self.line_num = save_line_num + 1
                            self.column_num = save_column_num
                            self.error_input("缺少'*'或者'/'")
                            sys.exit(0)
        # elif '[' == self.ch: #处理关键字   
            
    '''字母处理 import:导入模块处理'''        
    def letter_func(self):        
        print self.ch
        pass
        
INI("config.ini")            


