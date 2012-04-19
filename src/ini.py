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

'''
语法规则: 注释: /**/ , #, ;
[字母|中文字符|数字(组合)]->节点 
字母:(a~z|A~Z)
中文字符: (unicode*)
数字: (0-9)
[中123F]
节点下面的参数: 注意:不能使用数字开始,可以使用英文和中文,但是不能组合使用.
width = 34
宽度 = 34

例子:
[窗口] 或 [window] 或[窗win123]
width = 34
height = 34
[播放器]  或 [player]
图片截图路径 = 34
path = '/home/long...'
'''
import os
import sys

class INI(object):
    def __init__(self, ini_path):
        self.ini_path = ini_path
        self.ini_fp = open(ini_path, "r")
        self.ch = ''
        self.root_name = ""
        self.child_name = ""
        self.value_name = ""
        self.root_bool = False
        self.child_bool = False        
        self.root = [] #保存节点
        self.save_root = None
        self.line_num = 0  # 行号
        self.column_num = 0 # 列号
        
        
        
        while True:            
            self.ch = self.ini_fp.read(1)                
            self.column_num += 1 #计算列号
            if '\n' == self.ch:
                if self.root_bool and self.child_bool:
                    self.line_num += 1
                    self.column_num = 1
                    self.error_input("=后面缺少值")
                    sys.exit(0)
                self.line_num += 1  #计算行号
                self.column_num = 0 #清空列计数器
            if ' ' !=self.ch: #过滤空格
                if not self.ch:
                    break
                else: #开始处理 字符.
                    if self.unicode_bool():
                        # if self.root_bool:
                        #     print "处理中文字符"
                        # else:    
                        self.line_num += 1
                        self.error_input("多余的中文字符..请检查配置文件")
                        sys.exit(0)
                    elif self.number_bool(): #判断数字    
                        self.number_func()
                    elif self.letter_bool(): #判断字母    
                        self.letter_func()
                    else:
                        self.symbol_func()
                
        self.ini_fp.close()    
        # self.line_num += 1
        print "提示:共有%d行ini配置代码." % (self.line_num)       
        for i in self.root:
            print i.root_name
            print i.child_addr
        
        
        
        
    def error_input(self, error_mesagbox):    
        print "%d行%d列ini配置错误提示(%s)" % (self.line_num, self.column_num, error_mesagbox)
        
    def number_bool(self):    
        '''判断是否为数字'''
        ord_ch = ord(self.ch)
        return True if (48 <= ord_ch <= 57) else False
    
    def letter_bool(self):
        '''判断是否为字母'''
        ord_ch = ord(self.ch)
        return True if ((65 <= ord_ch <= 90) or (97 <= ord_ch <= 122))  else False
    
    def unicode_bool(self):
        '''判断是否为unicode'''
        ord_ch = ord(self.ch)
        return True if not(0 <= ord_ch <= 127) else False
    
    '''符号处理 注释: # /**/ , 赋值: = , []'''
    def symbol_func(self):
        '''符号处理函数'''
        if '#' == self.ch or ';' == self.ch: #过滤 '#' ';'(注释)
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
        elif '[' == self.ch: #处理关键字   
            self.root_bool = False
            self.child_bool = False
            self.ch = self.ini_fp.read(1)
            
            while ']' != self.ch:
                if ']' != self.ch or ' ' != self.ch:    
                    self.root_name += self.ch    
                self.ch = self.ini_fp.read(1)
                if '\n' == self.ch:
                    self.line_num += 1
                    self.error_input("缺少']',请检查配置文件")                    
                    sys.exit(0)
           #如果正确,开始处理关键字,比如: [window],就继续读下面的值. width = 34,要过滤掉空格.         
            self.save_root = ROOT()        
            self.save_root.root_name = self.root_name                     
            print self.save_root.root_name
            self.root.append(self.save_root)                                
            
            self.ini_fp.seek(-1, 1)        
            self.root_name = ""
            self.root_bool = True
           
        elif "'" == self.ch or '"' == self.ch:    
            if self.root_bool and self.child_bool:
                save_i = 0
                for i in range(0, len(self.root)):
                    if self.root[i].root_name == self.save_root.root_name:
                        save_i = i
                        break
                # 连续的读取字符串,参数值的赋值
                print self.column_num    
                while True:
                    self.ch = self.ini_fp.read(1)
                    if '"' == self.ch or "'" == self.ch:
                        break
                    else:
                        self.value_name += self.ch
                    if not self.ch:    
                        self.line_num += 1
                        self.error_input("字符串缺少结束符")
                        sys.exit(0)                                                        
                        
                self.root[i].child_addr[self.child_name] = (self.value_name)            
                self.value_name = ""
                self.child_name = ""
                self.child_bool = False        
            else:
                self.line_num += 1
                self.error_input("无效的字符串类型")
                sys.exit(0)
                
                
    '''字母处理 import:导入模块处理'''        
    def letter_func(self):        
        if self.root_bool and self.child_bool:    
            self.error_input("=后面无参数")
            sys.exit(0)
        else:    
            self.child_bool = False
            if not self.root_bool: #处理无节点的乱值
                self.error_input("缺少[...]的节,错误的参数值")
                sys.exit(0)
            else:# 处理节点的参数值.
                while True:
                    if ' ' != self.ch:
                        self.child_name += self.ch    
                    self.ch = self.ini_fp.read(1)                                
                    self.column_num += 1            
                    if '=' == self.ch:
                        break
                
                    if '\n' == self.ch:
                        self.line_num += 1                    
                        self.error_input("缺少'='")
                        sys.exit(0)                            
                
                save_i = 0
                for i in range(0, len(self.root)):
                    if self.root[i].root_name == self.save_root.root_name:
                        save_i = i
                        break
                
                self.child_bool = True
            
    def unicode_func(self):            
        '''中文字符处理'''
        pass
        
    def number_func(self):            
        '''数字处理函数'''
        if self.root_bool and self.child_bool: #处理参数值
            save_i = 0
            for i in range(0, len(self.root)):
                if self.root[i].root_name == self.save_root.root_name:
                    save_i = i
                    break
                
            while True:    
                if ' ' != self.ch:
                    self.value_name += self.ch
                self.ch = self.ini_fp.read(1)                
                
                if '\n' == self.ch:
                    self.line_num += 1
                    self.column_num = 0
                    break
                
            self.root[i].child_addr[self.child_name] = (self.value_name)            
            self.value_name = ""
            self.child_name = ""
            self.child_bool = False
        else:    
            if self.root_bool:
                self.line_num += 1
                self.error_input("缺少参数值")
                sys.exit(0)
                
            self.error_input("缺少节点和参数值")
        
    def get_section(self, root_name):        
        save_i = 0
        for i in range(0, len(self.root)):
            if self.root[i] == root_name:
                save_i = i
                break
        return self.root[i]
    
    def get_section_value(self, root_name, child_name):
        save_i = 0
        for i in range(0, len(self.root)):
            if self.root[i].root_name == root_name:
                save_i = i
                break
        return self.root[save_i].child_addr[child_name]    
        
    def get_section_childs(self, root_name):    
        save_i = 0
        for i in range(0, len(self.root)):
            if self.root[i].root_name == root_name:
                save_i = i
                break
            
        return  self.root[save_i].child_addr       
        
    def set_section_value(self, root_name, child_name, value):
        save_i = 0
        for i in range(0, len(self.root)):
            if self.root[i].root_name == root_name:
                save_i = i
                break
        self.root[save_i].child_addr[child_name] = value   
        return 0
    
    
    def set_section_child_name(self, 
                               root_name, 
                               child_name, 
                               modify_name):
        # 改变字典的键 名.
        #我唯一的办法就是拷贝一份.
        save_i = 0
        save_dict = {}

        for i in range(0, len(self.root)):
            if self.root[i].root_name == root_name:
                save_i = i
                break
            
        for i in self.root[i].child_addr.keys():    
            print type(i)
            if i == child_name:
                save_dict[modify_name] = self.root[save_i].child_addr[i]    
            else:    
                save_dict[i] = self.root[save_i].child_addr[i]    
            
        self.root[save_i].child_addr = save_dict.copy()    
        return 0
        
        
    def ini_save(self):    
        ini_fp = open(self.ini_path, "w")
        for root in self.root:
            ini_fp.write("[" + root.root_name +  "]\n")
            for child in root.child_addr: 
                ini_fp.write(child + " = " + root.child_addr[child] + "\n")
        ini_fp.close()
        
class ROOT(object):
    def __init__(self):
        self.root_name = ""
        self.child_addr = {}
        
        
if __name__ == "__main__":    
    ini = INI("config.ini")            
    rooo = ini.get_section("java")
    print "=============="
    print rooo.root_name
    print rooo.child_addr
    print "============="
    print ini.get_section_value("java", "x")
    print "============="
    print ini.get_section_childs("java")
    ini.set_section_value("java", "with", '\"/home/long/视频\"')
    print ini.get_section_childs("java")
    #print rooo.child_addr["i"]
    print "============================="
    ini.set_section_child_name("java", "with", "width")
    print "============================="
    print ini.get_section_value("java", "width")
    ini.ini_save()
    
'''
INI 类 (ini_path) : ini_path 是传入.ini文件的路径
.get_section(root_name) : root_name 是 父节点的名字 [window], window就是父亲节点.
返回的是是一个父亲节点的地址. 返回值: root_name. child_addr.
.get_section_value(root_name, child_name): 得到的是一个父节点下的 孩子节点的值
.get_section_childs(root_name): 返回父亲节点下的所有孩子.
比如: 
[window]
width = 34
height = 34
width 和 height 就会被返回.
========================================
.set_section_value(root_name, child_name, value): 设置一个父亲节点下的孩子节点的值.

'''
        

