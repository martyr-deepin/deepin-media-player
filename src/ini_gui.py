#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Wang Yong
# 
# Author:     Hailong Qiu <qiuhailong@linuxdeepin.com>
# Maintainer: Hailong Qiu <qiuhailong@linuxdeepin.com>
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


from dtk.ui.label import Label
from dtk.ui.button import CheckButton, RadioButton

import gtk

TITLE_WIDTH = 10    

class IniGui(object):
    def __init__(self):
        pass



class Configure(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self)
        self.class_list = ["文件播放", "系统设置", "播放控制", "其它快捷键", 
                           "字幕设置", "截图设置", "其它设置"]
        # Init all configure gui class.
        self.file_play = FilePlay()
        self.system_set = SystemSet()
        self.play_control = PlayControl()
        self.other_key = OtherKey()
        self.sub_set = SubSet()
        self.screen_shot = ScreenShot()
        self.other_set = OtherSet()
        #
        self.pack_start(self.file_play, True, True)
        self.show_all()        
        
    def set(self, class_name):
        if class_name in self.class_list:
            
            for widget in self.get_children():
                self.remove(widget)
            
            if "文件播放" == class_name:
                self.pack_start(self.file_play)
            elif "系统设置" == class_name:
                self.pack_start(self.system_set)                
            elif "播放控制" == class_name:
                self.pack_start(self.play_control)
            elif "其它快捷键" == class_name:
                self.pack_start(self.other_key)
            elif "字幕设置" == class_name:
                self.pack_start(self.sub_set)
            elif "截图设置" == class_name:
                self.pack_start(self.screen_shot)
            elif "其它设置" == class_name:
                self.pack_start(self.other_set)
            
            for widget in self.get_children():    
                if widget:
                    self.show_all()
                    return True
                
        return None        
    

class FilePlay(gtk.VBox):    
    def __init__(self):
        gtk.VBox.__init__(self)
        self.fixed = gtk.Fixed()
        self.label = gtk.Label()
        self.btn = gtk.Button("确定")
        self.fixed.put(self.label, TITLE_WIDTH, 5)
        self.fixed.put(self.btn, TITLE_WIDTH, 20)
        self.pack_start(self.fixed)
        
class SystemSet(gtk.VBox):        
    def __init__(self):
        gtk.VBox.__init__(self)
        self.fixed = gtk.Fixed()
        self.label = gtk.Label("文件播放")
        self.btn = gtk.Button("确定")
        self.fixed.put(self.label, TITLE_WIDTH, 5)
        self.fixed.put(self.btn, TITLE_WIDTH, 20)
        self.pack_start(self.fixed)
        
        
class PlayControl(gtk.VBox):       
    def __init__(self):
        gtk.VBox.__init__(self)
        self.fixed = gtk.Fixed()
        self.label = gtk.Label("播放控制")
        self.btn = gtk.Button("确定")
        self.fixed.put(self.label, TITLE_WIDTH, 5)
        self.fixed.put(self.btn, TITLE_WIDTH, 20)
        self.pack_start(self.fixed)
        
        
class OtherKey(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self)
        self.fixed = gtk.Fixed()
        self.label = gtk.Label("其它快捷键")
        self.btn = gtk.Button("确定")
        self.fixed.put(self.label, TITLE_WIDTH, 5)
        self.fixed.put(self.btn, TITLE_WIDTH, 20)
        self.pack_start(self.fixed)
        

class SubSet(gtk.VBox):        
    def __init__(self):
        gtk.VBox.__init__(self)
        self.fixed = gtk.Fixed()
        self.label = gtk.Label("字幕设置")
        self.btn = gtk.Button("确定")
        self.fixed.put(self.label, TITLE_WIDTH, 5)
        self.fixed.put(self.btn, TITLE_WIDTH, 20)
        self.pack_start(self.fixed)
        
        
class ScreenShot(gtk.VBox):        
    def __init__(self):
        gtk.VBox.__init__(self)
        self.fixed = gtk.Fixed()
        self.label = gtk.Label("截图设置")
        self.btn = gtk.Entry()
        self.fixed.put(self.label, TITLE_WIDTH, 5)
        self.fixed.put(self.btn, TITLE_WIDTH, 20)
        self.pack_start(self.fixed)        
        
class OtherSet(gtk.VBox):    
    def __init__(self):
        gtk.VBox.__init__(self)
        self.fixed = gtk.Fixed()
        self.label = gtk.Label("其它设置")
        self.btn = gtk.Entry()
        self.fixed.put(self.label, TITLE_WIDTH, 5)
        self.fixed.put(self.btn, TITLE_WIDTH, 20)
        self.pack_start(self.fixed)
        
        
        
        
def test_show_con(widget, string):        
    con.set(string)
    
if __name__ == "__main__":        
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)    
    win.connect("destroy", gtk.main_quit)
    vbox = gtk.VBox()
    con = Configure()
    vbox.pack_start(con, True, True)
    btn1 = gtk.Button("截图设置")
    btn1.connect("clicked", test_show_con, btn1.get_label())
    btn2 = gtk.Button("其它设置")
    btn2.connect("clicked", test_show_con, btn2.get_label())
    vbox.pack_start(btn1)
    vbox.pack_start(btn2)
    win.add(vbox)
    win.show_all()
    gtk.main()
    
