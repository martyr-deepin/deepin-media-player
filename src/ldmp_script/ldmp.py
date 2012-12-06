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

from dtk.ui.scrolled_window import ScrolledWindow
import gtk
import socket

'''
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
----------------------
         
'''
keyword = {'a':[],
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

TOKEN_TYPE_OPERATOR     = 0
TOKEN_TYPE_SCOPE_SYMBOL = 1

class LDMP(ScrolledWindow):
    '''
    hjustment-->{gtk.POLICY_ALWAYS , gtk.POLICY_AUTOMATIC, gtk.POLICY_NEVER}
    '''
    def __init__(self, hjustment=gtk.POLICY_AUTOMATIC, vadjustment=gtk.POLICY_AUTOMATIC):
        ScrolledWindow.__init__(self, hjustment, vadjustment)
        self.token_info_list = []
        self.parsing_table = [] # 语法分析表.
        self.product_list = [] # 产生式表.
        self.ldmp_script_file = None
        #.
        self.main_vbox = gtk.VBox() 
        #.
        self.main_vbox.add_events(gtk.gdk.ALL_EVENTS_MASK)        
        #.        
        self.__add(self.main_vbox)
        
        
    def key_press_event(self, widget, event):    
        # refresh.
        if event.keyval == 65474:
            self.refresh()            
        
    def __add(self, widget):
        self.add_with_viewport(widget)
        
    def __show_widgets(self):    
        self.main_vbox.show_all()
        
    def __remove_all_widgets(self):    
        for widget in self.main_vbox.get_children():
            self.main_vbox.remove(widget)
        
    def refresh(self):
        if self.ldmp_script_file:
            self.open(self.ldmp_script_file)                                    
            return True
        return False
        
    def open(self, ldmp_script_file):
        # save.
        self.ldmp_script_file = ldmp_script_file
        # clear widgets.
        self.__remove_all_widgets()
        # open.
        fp_script = open(ldmp_script_file, "r")
        script_run_list = fp_script.read().decode("utf-8").split("\n")
        #.
        self.line_num = 0
        for line in script_run_list:            
            self.__lex(line)
            self.line_num += 1
            
        # test input.    
        print "保存的单词流信息:"
        for token_info in self.token_info_list:
            print "token:", token_info.str,
            if token_info.type == TOKEN_TYPE_OPERATOR:
                print "type:", "TOKEN_TYPE_OPERATOR",
            elif token_info.type == TOKEN_TYPE_SCOPE_SYMBOL:    
                print "type:", "TOKEN_TYPE_SCOPE_SYMBOL",
            print "row:", token_info.row
                    
        # show widgets.
        self.__show_widgets()
    
    def __lex(self, string):
        '''词法分析.'''
        lex_next  = 0  # 移动指针.
        lex_point = 0  # 当前指针.
        token     = "" # 单词保存.
        #
        while lex_next < len(string)-1:
            ch = string[lex_next]
            if ch != "": # 过滤空格.
                if self.__check_note(ch): # 过滤注释.
                    while lex_next < len(string)-1:
                        lex_next += 1                        
                elif self.__check_operator(ch): # 运算符.
                    self.__save_operator(ch)
                elif self.__check_scope_symbol(ch):  # 界符号.  
                    self.__save_scope_symbol(ch)
                elif self.__check_keyword(ch): # 关键字.
                    pass
            #    
            lex_next += 1
            
    def __check_note(self, ch):        
        if ch in ["'"]:
            return True
        else:
            return False
        
    def __check_operator(self, token):
        if token in ["="]:
            return True
        else:
            return False
        
    def __check_scope_symbol(self, token):
        if token in ["<", ">", "/"]:
            return True
        else:
            return False        

    def __check_keyword(self, ch):        
        pass
        
    def __save_operator(self, token):        
        self.__save_token(token, TOKEN_TYPE_OPERATOR)
        
    def __save_scope_symbol(self, token):
        self.__save_token(token, TOKEN_TYPE_SCOPE_SYMBOL)
        
    def __save_token(self, token, type_):
        token_info = TokenInfo()
        token_info.str  = token
        token_info.type = type_
        token_info.row  = self.line_num
        self.token_info_list.append(token_info)        
        
    def parsing(self): 
        '''语法分析.'''
        pass
    
class TokenInfo(object):
    def __init__(self):
        self.str = None # token string.
        self.type = None # token type.
        self.row  = None # token row.
        
class Stack(object):
    '''
    LL(1) 语法分析.
    '''
    def __init__(self):
        self.save_values = []
    
    def pop(self):
        value = self.save_values.pop()
        return value
    
    def push(self, value):
        self.save_values.append(value)    
    

    
    
