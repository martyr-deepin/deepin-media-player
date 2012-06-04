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
from skin import app_theme
from treeview import TreeView

from dtk.ui.titlebar import Titlebar
from dtk.ui.window import Window 
from dtk.ui.label import Label
from dtk.ui.button import CheckButton, RadioButton
from dtk.ui.line import HSeparator
from dtk.ui.scrolled_window import ScrolledWindow

import gtk

TITLE_WIDTH = 10    

class IniGui(Window):
    def __init__(self):
        Window.__init__(self)
        # Set configure window.
        self.set_size_request(550, 400)
        
        self.main_vbox = gtk.VBox()
        self.main_hbox = gtk.HBox()
        self.configure = Configure()
        self.scrolled_window = ScrolledWindow()
        self.scrolled_window.set_size_request(130, 1)
        self.titlebar = Titlebar(["min", "close"], app_name="深度影音配置")
        # move open window.
        self.add_move_event(self.titlebar.drag_box)
        self.titlebar.close_button.connect("clicked", lambda w:self.destroy())
        self.titlebar.min_button.connect("clicked", lambda w: self.min_window())
        
        self.tree_view = TreeView(width = 20, font_x = 10)
        self.scrolled_window.add_child(self.tree_view)
        # TreeView event.
        self.tree_view.connect("single-click-view", self.set_con_widget)
        # TreeView add node.
        self.tree_view.add_node(None, "文件播放")
        self.tree_view.add_node(None, "系统设置")
        self.tree_view.add_node(None, "快捷键")
        self.tree_view.add_node("快捷键", "播放控制", False)
        self.tree_view.add_node("快捷键", "其它快捷键", False)
        self.tree_view.add_node(None, "字幕设置")
        self.tree_view.add_node(None, "截图设置")
        self.tree_view.add_node(None, "其它设置")
                        
        self.main_hbox_frame = gtk.Alignment()
        self.main_hbox_frame.set(1, 1, 1, 1)
        self.main_hbox_frame.set_padding(2, 2, 2, 2)
        
        self.main_hbox_frame.add(self.main_hbox)
        self.main_vbox.pack_start(self.titlebar, False, False)
        self.main_vbox.pack_start(self.main_hbox_frame, True, True)
                
        self.main_hbox.pack_start(self.scrolled_window, False, False)
        # self.main_hbox.pack_start(self.tree_view, True, True)
        self.main_hbox.pack_start(self.configure)
                
        self.window_frame.add(self.main_vbox)
        self.show_all()
        
    def set_con_widget(self, treeview, string, index):
        self.configure.set(string)
        
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
        self.label = Label("文件播放")
        self.label.set_size_request(100, 30)
        self.btn = gtk.Button("确定")
        self.heparator=HSeparator(app_theme.get_shadow_color("linearBackground").get_color_info())
        self.heparator.set_size_request(100, 5)
        self.fixed.put(self.label, TITLE_WIDTH, 5)
        self.fixed.put(self.heparator, 0, 35)
        self.fixed.put(self.btn, TITLE_WIDTH, 5+35+30)
        
        self.pack_start(self.fixed)
        
class SystemSet(gtk.VBox):        
    def __init__(self):
        gtk.VBox.__init__(self)
        self.fixed = gtk.Fixed()
        self.label = Label("系统设置")
        self.label.set_size_request(100, 30)
        self.btn = gtk.Button("确定")
        self.heparator=HSeparator(app_theme.get_shadow_color("linearBackground").get_color_info())
        self.heparator.set_size_request(100, 5)
        self.fixed.put(self.label, TITLE_WIDTH, 5)
        self.fixed.put(self.heparator, 0, 35)
        self.fixed.put(self.btn, TITLE_WIDTH, 5+35+30)
        
        self.pack_start(self.fixed)
        
        
class PlayControl(gtk.VBox):       
    def __init__(self):
        gtk.VBox.__init__(self)
        self.fixed = gtk.Fixed()
        self.label = Label("播放控制")
        self.label.set_size_request(100, 30)
        self.btn = gtk.Button("确定")
        self.heparator=HSeparator(app_theme.get_shadow_color("linearBackground").get_color_info())
        self.heparator.set_size_request(100, 5)
        self.fixed.put(self.label, TITLE_WIDTH, 5)
        self.fixed.put(self.heparator, 0, 35)
        self.fixed.put(self.btn, TITLE_WIDTH, 5+35+30)
        
        self.pack_start(self.fixed)
        
        
class OtherKey(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self)
        self.fixed = gtk.Fixed()
        self.label = Label("其它快捷键")
        self.label.set_size_request(100, 30)
        self.btn = gtk.Button("确定")
        self.heparator=HSeparator(app_theme.get_shadow_color("linearBackground").get_color_info())
        self.heparator.set_size_request(100, 5)
        self.fixed.put(self.label, TITLE_WIDTH, 5)
        self.fixed.put(self.heparator, 0, 35)
        self.fixed.put(self.btn, TITLE_WIDTH, 5+35+30)
        
        self.pack_start(self.fixed)
        

class SubSet(gtk.VBox):        
    def __init__(self):
        gtk.VBox.__init__(self)
        self.fixed = gtk.Fixed()
        self.label = Label("字幕设置")
        self.label.set_size_request(100, 30)
        self.btn = gtk.Button("确定")
        self.heparator=HSeparator(app_theme.get_shadow_color("linearBackground").get_color_info())
        self.heparator.set_size_request(100, 5)
        self.fixed.put(self.label, TITLE_WIDTH, 5)
        self.fixed.put(self.heparator, 0, 35)
        self.fixed.put(self.btn, TITLE_WIDTH, 5+35+30)
        
        self.pack_start(self.fixed)
        
        
class ScreenShot(gtk.VBox):        
    def __init__(self):
        gtk.VBox.__init__(self)
        self.fixed = gtk.Fixed()
        self.label = Label("截图设置")
        self.label.set_size_request(100, 30)
        self.btn = gtk.Button("确定")
        self.heparator=HSeparator(app_theme.get_shadow_color("linearBackground").get_color_info())
        self.heparator.set_size_request(100, 5)
        self.fixed.put(self.label, TITLE_WIDTH, 5)
        self.fixed.put(self.heparator, 0, 35)
        self.fixed.put(self.btn, TITLE_WIDTH, 5+35+30)
        
        self.pack_start(self.fixed)
        
class OtherSet(gtk.VBox):    
    def __init__(self):
        gtk.VBox.__init__(self)
        self.fixed = gtk.Fixed()
        self.label = Label("其它设置")
        self.label.set_size_request(100, 30)
        self.btn = gtk.Button("确定")
        self.heparator=HSeparator(app_theme.get_shadow_color("linearBackground").get_color_info())
        self.heparator.set_size_request(100, 5)
        self.fixed.put(self.label, TITLE_WIDTH, 5)
        self.fixed.put(self.heparator, 0, 35)
        self.fixed.put(self.btn, TITLE_WIDTH, 5+35+30)
        
        self.pack_start(self.fixed)
        
        
        
        
if __name__ == "__main__":        
    IniGui()
    gtk.main()
