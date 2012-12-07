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


# /* 用于搜索关键字. */
keyword_dict = {'a':[],
           'b':["button"],
           'c':["callback"],
           'd':[],
           'e':["event"],
           'f':[],
           'g':[],
           'h':["hbox"],
           'i':[],
           'j':[],
           'k':[],
           'l':["ldmp"],
           'm':[],
           'n':["name"],
           'o':[],
           'p':[],
           'q':[],
           'r':[],
           's':[],
           't':[],
           'u':[],
           'v':["vbox", "value", "version"],
           'w':[],
           'x':[],
           'y':[],
           'z':[]
           }

'''
标识符    ID 03
字符串常量 ID 02
----------------------
运算符 |  ID  | 单词
         10     = 
----------------------     
界符号 |  ID  | 单词
         05     <
         06     >
         07     /
----------------------
关键字 |  ID  |   单词
         30    version
         31    ldmp
         32    name
         33    value
         34    event
         35    callback
         36    vbox
         37    hbox      
         38    entry
         39    button
----------------------
'''

'''(回车,空格)----------
             |--------
             |--------
             |--------
             |--------
   标识符(字母)|---字母,数字循环---(05)---其它---((-03)) # 最后会查询关键字表，看是否为关键字.
            <|--------(06)---全部---((-05))
            >|--------(07)---全部---((-06))
            /|--------(08)---全部---((-07))
            "|--------(09)--- " ---(11) -- 全部 --((-02))
                          |--回车---((-100))
            '|--------(10)---回车---((-40))
'''   
lex_table = []

def init_lex_table():        
    # init lex_table.
    for i in range(0, 12):
        lex_table.append([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                          0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                          0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                          0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])        
    # create lex table.   
    for i in range(0, 129): # 0-127, 128(其它:比如[中文])
        lex_table[0][i]   = 0   # 出错状态.
        lex_table[0][ord("<")] = 6
        lex_table[0][ord(">")] = 7
        lex_table[0][ord('/')] = 8
        lex_table[0][ord('=')] = 4
        lex_table[0][ord("'")] = 10
        lex_table[0][ord('"')] = 9
        if (ord('a') <= i <= ord('z')) or (ord('A') <= i <= ord('Z')):
            lex_table[0][i] = 5
        # 标识符.
        if (ord('a') <= i <= ord('z')) or (ord('A') <= i <= ord('Z')) or (ord('0') <= i <= ord('9')):
            lex_table[5][i] = 5
        else:    
            lex_table[5][i] = -3
        # 运算符.    
        lex_table[4][i] = -10
        # 界符号.
        lex_table[6][i] = -5
        lex_table[7][i] = -6
        lex_table[8][i] = -7  
        # 字符串.
        lex_table[9][i]         = 9      # 其它,中文,除了回车..->>跳转
        lex_table[11][i]        = -2
        lex_table[9][ord('"')]  = 11    # 字符串.
        lex_table[9][ord('\n')] = -100   # 字符串没有"结尾--->出错状态. 
        # 注释.
        lex_table[10][i]         = 10     # 注释跳转.
        lex_table[10][ord('\n')] = -40    # 注释.
        
init_lex_table()

if __name__ == "__main__":
    # init_lex_table()
    # import random
    text = '<value = button><button value="button1" event="clicked" callback="button1_clickee">"我来   看看看吧fjsdklfsdjkf"</value>\n'.decode("utf-8")
    row = 0
    text_index = 0
    token = ""
    while text_index < len(text):        
        
        if ord(text[text_index]) < 128:
            index = ord(text[text_index]) # <
        else:    
            index = 128
            
        row = lex_table[row][index]
        token += text[text_index]
        
        if row < 0:
            text_index -= 1# 超前搜索一个，所以必须回退一位. 
            if row == -40:
                print "[注释]", token[:-1], "(id:", -row
            elif row == -2:    
                print "[字符串]", token[:-1], "(id:", -row
            elif row == -100:
                print "[错误]-->>", token[:-1], "行号:", 0
                break
            elif row == -5:    
                print "[界符号]", token[:-1], "(id:", -row
            elif row == -6:    
                print "[界符号]", token[:-1], "(id:", -row
            elif row == -7:    
                print "[界符号]", token[:-1], "(id:", -row                
            elif row == -3:   
                print "[标识符]", token[:-1], "(id:", -row                            
            elif row == -10:    
                print "[运算符]", token[:-1], "(id:", -row
            row = 0 
            token = ""            
            
       
        text_index += 1
