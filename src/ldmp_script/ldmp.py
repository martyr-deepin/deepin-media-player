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


keyword_id_dict = {
    "version":30, "ldmp":31, "name":32,
    "value":33, "event":34, "callback":35,
    "vbox": 36, "hbox":37, "entry":38, "button":39
    }

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

scope_symbol_dict = {"<":5,
                ">":6,
                "/":7}

TOKEN_TYPE_OPERATOR     = 0 # 运算符.
TOKEN_TYPE_SCOPE_SYMBOL = 1 # 界符号.
TOKEN_TYPE_KEYWORD      = 2 # 关键字.
TOKEN_TYPE_STRING       = 3 # 字符串.

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
            print "id:", token_info.id,
            print "token:", token_info.str,
            if token_info.type == TOKEN_TYPE_OPERATOR:
                print "type:", "TOKEN_TYPE_OPERATOR",
            elif token_info.type == TOKEN_TYPE_SCOPE_SYMBOL:    
                print "type:", "TOKEN_TYPE_SCOPE_SYMBOL",
            elif token_info.type == TOKEN_TYPE_STRING:    
                print "type:", "TOKEN_TYPE_STRING",
            elif token_info.type == TOKEN_TYPE_KEYWORD:    
                print "type:", "TOKEN_TYPE_KEYWORD",
            print "row:", token_info.row
                    
        # show widgets.
        self.__show_widgets()
    
    def __lex(self, string):
        '''词法分析.'''
        lex_next  = 0  # 移动指针.
        lex_point = 0  # 当前指针.
        token     = "" # 单词保存.
        #
        while lex_next < len(string):
            ch = string[lex_next]
            if ch != "": # 过滤空格.
                if self.__check_note(ch): # 过滤注释.
                    while lex_next < len(string)-1:
                        lex_next += 1                        
                elif self.__check_string(ch): # 字符串.        
                    token = ""
                    lex_next += 1
                    while not self.__check_string(string[lex_next]):
                        token += string[lex_next]
                        lex_next += 1
                    self.__save_string(token)    
                elif self.__check_operator(ch): # 运算符.
                    self.__save_operator(ch)
                elif self.__check_scope_symbol(ch):  # 界符号.  
                    self.__save_scope_symbol(ch)
                elif self.__check_keyword(ch): # 关键字.
                    token = ""
                    while self.__check_keyword(string[lex_next]):
                        token += string[lex_next]
                        lex_next += 1
                    lex_next -= 1    
                    if self.__find_keyword(ch, token): # 关键字
                        self.__save_keyword(token)
                    else: # 常量    
                        pass
            #       
            lex_next += 1
            
    def __check_note(self, ch):        
        if ch in ["'"]:
            return True
        else:
            return False
        
    def __check_string(self, ch):        
        if ch in ['"']:
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
        return keyword_dict.has_key(ch)
                    
    def __find_keyword(self, ch, token_cmp):
        for token in keyword_dict[ch]:    
            if token_cmp == token:
                return True
        return False
    
    def __save_keyword(self, token):
        id = None
        if keyword_id_dict.has_key(token):
            id = keyword_id_dict[token]
        self.__save_token(token, TOKEN_TYPE_KEYWORD, id)
        
    def __save_string(self, token):
        id = 2
        self.__save_token(token, TOKEN_TYPE_STRING, id)
        
    def __save_operator(self, token):        
        id = 10
        self.__save_token(token, TOKEN_TYPE_OPERATOR, id)
        
    def __save_scope_symbol(self, token):        
        id = None
        if scope_symbol_dict.has_key(token):
            id = scope_symbol_dict[token]
        self.__save_token(token, TOKEN_TYPE_SCOPE_SYMBOL, id)
        
    def __save_token(self, token, type_, id=None):
        token_info = TokenInfo()
        token_info.id   = id
        token_info.str  = token
        token_info.type = type_
        token_info.row  = self.line_num
        self.token_info_list.append(token_info)        
        
    def parsing(self): 
        '''语法分析.'''
        pass
    
class TokenInfo(object):
    def __init__(self):
        self.id   = None
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
    

    
    
