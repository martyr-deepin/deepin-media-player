#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Hailong Qiu
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


from dtk.ui.treeview import TreeView, TreeViewItem
from dtk.ui.titlebar import Titlebar
from dtk.ui.window import Window 
from dtk.ui.label import Label
from dtk.ui.button import CheckButton, RadioButton
from dtk.ui.line import HSeparator
from dtk.ui.scrolled_window import ScrolledWindow

import gtk

# Ini(configure) window.
INI_WIDTH = 640
INI_HEIGHT = 480

# Label title.
label_width = 100 
label_height = 30
TITLE_WIDTH_PADDING = 10    
TITLE_HEIGHT_PADDING = 2

# Heparator.
heparator_x = 0
heparator_y = 35
heparator_width = 405
heparator_height = 5

# Video file open.
video_file_open_x = 20
video_file_open_y = 40




class IniGui(Window):
    def __init__(self):
        Window.__init__(self)
        # Set configure window.
        self.set_size_request(INI_WIDTH, INI_HEIGHT)  
        
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
        
        self.tree_view = TreeView(font_x_padding=15, arrow_x_padding=20)
        # TreeView event.
        self.tree_view.connect("single-click-item", self.set_con_widget)
        self.scrolled_window.add_child(self.tree_view)
        
        # TreeView add node.
        self.tree_view.add_item(None, TreeViewItem("文件播放"))
        self.tree_view.add_item(None, TreeViewItem("系统设置"))
        key = self.tree_view.add_item(None, TreeViewItem("快捷键    "))
        self.tree_view.add_item(None, TreeViewItem("字幕设置"))
        self.tree_view.add_item(None, TreeViewItem("截图设置"))
        self.tree_view.add_item(None, TreeViewItem("其它设置"))        
        
        self.tree_view.add_item(key, TreeViewItem("播放控制", has_arrow=False))
        self.tree_view.add_item(key, TreeViewItem("其它快捷键", has_arrow=False))
                        
        self.main_hbox_frame = gtk.Alignment()
        self.main_hbox_frame.set(1, 1, 1, 1)
        self.main_hbox_frame.set_padding(4, 4, 4, 4)
        
        self.main_hbox_frame.add(self.main_hbox)
        self.main_vbox.pack_start(self.titlebar, False, False)
        self.main_vbox.pack_start(self.main_hbox_frame, True, True)
                
        self.main_hbox.pack_start(self.scrolled_window, False, False)
        self.main_hbox.pack_start(self.configure)
                
        self.window_frame.add(self.main_vbox)
        # Init configure index.
        self.configure.set("文件播放")
        self.show_all()
        
    def set_con_widget(self, treeview, item):
        # print item.get_title()
        # Configure class Mode.
        self.configure.set(item.get_title())
        
        
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
        self.label.set_size_request(label_width, label_height)
        
        self.heparator = HSeparator(app_theme.get_shadow_color("linearBackground").get_color_info())
        self.heparator.set_size_request(heparator_width, heparator_height)
        
        # Video file open.
        self.ai_set_radio_btn     = RadioButton()
        self.ai_set_radio_btn_label = Label("智能调整")

        self.adapt_video_btn = RadioButton()
        self.adapt_video_btn_label = Label("窗口适应视频")

        self.close_position_radio_btn = RadioButton()
        self.close_position_radio_btn_label = Label("应用关闭尺寸位置")

        self.full_window_radio_btn   = RadioButton()        
        self.full_window_radio_btn_label = Label("自动全屏")                
        
        # open new file clear play list.
        self.clear_play_list_btn = CheckButton()
        self.clear_play_list_btn_label = Label("打开新文件时清空播放列表")        
        # memory up close media player -> file play postion.
        self.file_play_postion_btn = CheckButton()
        self.file_play_postion_btn_label = Label("记忆上次关闭播放器时文件的播放位置")
        
        self.fixed.put(self.label, TITLE_WIDTH_PADDING, TITLE_HEIGHT_PADDING)
        self.fixed.put(self.heparator, heparator_x, heparator_y)        
        # Video file open.
        self.fixed.put(self.ai_set_radio_btn, video_file_open_x, video_file_open_y)
        video_file_width = self.ai_set_radio_btn.get_size_request()[0]
        self.fixed.put(self.ai_set_radio_btn_label, 
                       video_file_open_x + video_file_width, video_file_open_y)
        video_file_width += self.ai_set_radio_btn_label.get_size_request()[0]
        self.fixed.put(self.adapt_video_btn, 
                       video_file_open_x + video_file_width, video_file_open_y)        
        video_file_width += self.adapt_video_btn.get_size_request()[0]
        self.fixed.put(self.adapt_video_btn_label,
                       video_file_open_x + video_file_width, video_file_open_y)
        video_file_width += self.adapt_video_btn_label.get_size_request()[0]
        self.fixed.put(self.close_position_radio_btn, 
                       video_file_open_x + video_file_width, video_file_open_y)
        video_file_width += self.close_position_radio_btn.get_size_request()[0]
        self.fixed.put(self.close_position_radio_btn_label, 
                       video_file_open_x + video_file_width, video_file_open_y)
        video_file_width += self.close_position_radio_btn_label.get_size_request()[0]
        self.fixed.put(self.full_window_radio_btn, 
                       video_file_open_x + video_file_width, video_file_open_y)
        video_file_width += self.full_window_radio_btn.get_size_request()[0]
        self.fixed.put(self.full_window_radio_btn_label, 
                       video_file_open_x + video_file_width, video_file_open_y)
        # open new file clear play list.        
        clear_play_list_x = video_file_open_x
        clear_play_list_y = video_file_open_y + 40
        self.fixed.put(self.clear_play_list_btn,
                       clear_play_list_x, clear_play_list_y)        
        clear_play_list_width = self.clear_play_list_btn.get_size_request()[0]
        self.fixed.put(self.clear_play_list_btn_label,
                       clear_play_list_x + clear_play_list_width, clear_play_list_y)               
        # memory up close media player -> file play postion.
        file_play_postion_x = clear_play_list_x
        file_play_postion_y = clear_play_list_y + 40
        self.fixed.put(self.file_play_postion_btn,
                       file_play_postion_x, file_play_postion_y)        
        file_play_postion_width = self.file_play_postion_btn.get_size_request()[0]
        self.fixed.put(self.file_play_postion_btn_label,
                       file_play_postion_x + file_play_postion_width, file_play_postion_y)
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
        self.fixed.put(self.label, TITLE_WIDTH_PADDING, 5)
        self.fixed.put(self.heparator, 0, heparator_y)
        self.fixed.put(self.btn, TITLE_WIDTH_PADDING, 5+35+30)
        
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
        self.fixed.put(self.label, TITLE_WIDTH_PADDING, 5)
        self.fixed.put(self.heparator, 0, heparator_y)
        self.fixed.put(self.btn, TITLE_WIDTH_PADDING, 5+35+30)
        
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
        self.fixed.put(self.label, TITLE_WIDTH_PADDING, 5)
        self.fixed.put(self.heparator, 0, heparator_y)
        self.fixed.put(self.btn, TITLE_WIDTH_PADDING, 5+35+30)
        
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
        self.fixed.put(self.label, TITLE_WIDTH_PADDING, 5)
        self.fixed.put(self.heparator, 0, heparator_y)
        self.fixed.put(self.btn, TITLE_WIDTH_PADDING, 5+35+30)
        
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
        self.fixed.put(self.label, TITLE_WIDTH_PADDING, 5)
        self.fixed.put(self.heparator, 0, heparator_y)
        self.fixed.put(self.btn, TITLE_WIDTH_PADDING, 5+35+30)
        
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
        self.fixed.put(self.label, TITLE_WIDTH_PADDING, 5)
        self.fixed.put(self.heparator, 0, heparator_y)
        self.fixed.put(self.btn, TITLE_WIDTH_PADDING, 5+35+30)
        
        self.pack_start(self.fixed)
        
        
        
        
if __name__ == "__main__":        
    IniGui()
    gtk.main()
