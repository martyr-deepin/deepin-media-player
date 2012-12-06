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

'''
-------------------
运算符 |  ID  | 单词
         10     = 
-------------------         
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
----------------------
         
'''
keyword = ["version", "ldmp",
           "name", "value", "event", "callback", 
           "vbox", "hbox", "button"]

class LDMP(ScrolledWindow):
    '''
    hjustment-->{gtk.POLICY_ALWAYS , gtk.POLICY_AUTOMATIC, gtk.POLICY_NEVER}
    '''
    def __init__(self, hjustment=gtk.POLICY_AUTOMATIC, vadjustment=gtk.POLICY_AUTOMATIC):
        ScrolledWindow.__init__(self, hjustment, vadjustment)
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
        script_run_list = fp_script.read().split("\n")
        #.
        for line in script_run_list:            
            # if line.strip().startswith("<video"):
                # print "mplayer play"
            pass
        # show widgets.
        self.__show_widgets()
    
    def lex(self): # 词法分析.
        pass
    
    def parsing(self): # 语法分析.
        pass
    
class TokenInfo(object):
    def __init__(self):
        self.type = None # token type.
        self.row  = None # token row.
        
class Stack(object):        
    def __init__(self):
        self.save_values = []
    
    def pop(self):
        value = self.save_values.pop()
        return value
    
    def push(self, value):
        self.save_values.append(value)
    
    
