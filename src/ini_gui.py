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

from dtk.ui.utils import propagate_expose, alpha_color_hex_to_cairo
from dtk.ui.button import Button
from dtk.ui.entry import TextEntry
from dtk.ui.combo import ComboBox
from dtk.ui.titlebar import Titlebar
from dtk.ui.window import Window 
from dtk.ui.label import Label
from dtk.ui.button import CheckButton, RadioButton
from dtk.ui.line import HSeparator
from dtk.ui.scrolled_window import ScrolledWindow

from dtk.ui.treeview import TreeView, TreeViewItem
from ini import Config
from mplayer import get_home_path
import gtk

DEFAULT_FONT = "文泉驿微米黑"
config_path = get_home_path() + "/.config/deepin-media-player/deepin_media_config.ini"
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
heparator_width = INI_WIDTH - 143
heparator_height = 5

import gobject

class IniGui(Window):
    __gsignals__ = {
        "config-changed" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                            (gobject.TYPE_STRING, ))
        }
    def __init__(self):
        Window.__init__(self)
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_modal(True)
        # self.set_keep_above(True)
        self.ini = Config(config_path)        
        # self.ini = config
        # Set configure window.
        self.set_size_request(INI_WIDTH, INI_HEIGHT)  
        
        self.main_vbox = gtk.VBox()
        self.main_hbox = gtk.HBox()
        self.configure = Configure()
        self.titlebar = Titlebar(["min", "close"], app_name="深度影音配置")
        # move open window.
        self.add_move_event(self.titlebar.drag_box)
        self.titlebar.close_button.connect("clicked", lambda w:self.destroy())
        self.titlebar.min_button.connect("clicked", lambda w: self.min_window())
        # Tree view window.
        self.scrolled_window_frame  = gtk.Alignment()
        self.scrolled_window_frame.set(1, 1, 1, 1)
        self.scrolled_window_frame.set_padding(4, 0, 0, 0)        
        
        self.scrolled_window = ScrolledWindow()
        
        self.scrolled_window_frame.add(self.scrolled_window)
        self.scrolled_window_frame.connect("expose-event", self.draw_scrolled_window_backgournd) 
        self.scrolled_window.set_size_request(130, 1)        
        self.tree_view = TreeView(font_x_padding=15, arrow_x_padding=35, height = 40)
        self.tree_view.draw_mask = self.draw_treeview_mask
        
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
        self.tree_view.add_item(None, TreeViewItem("关于         "))        
        
        self.tree_view.add_item(key, TreeViewItem("其它快捷键", has_arrow=False))
        self.tree_view.add_item(key, TreeViewItem("播放控制", has_arrow=False))
        
                        
        self.main_hbox_frame = gtk.Alignment()
        self.main_hbox_frame.set(1, 1, 1, 1)
        self.main_hbox_frame.set_padding(4, 4, 4, 4)
        
        self.main_hbox_frame.add(self.main_hbox)
        self.main_vbox.pack_start(self.titlebar, False, False)
        self.main_vbox.pack_start(self.main_hbox_frame, True, True)
        self.main_hbox_frame.connect("expose-event", self.draw_backgournd)        
        self.main_hbox.pack_start(self.scrolled_window_frame, False, False)
        self.main_hbox.pack_start(self.configure)
        
        # bottom button.
        self.ok_btn     = Button("确定")
        self.cancel_btn = Button("取消")
        self.ok_btn.connect("clicked", self.save_configure_file_ok_clicked)
        self.cancel_btn.connect("clicked", self.destroy_ini_gui_window_cancel_clicked)
        self.bottom_fixed = gtk.Fixed()
        bottom_fixed_height = 45
        self.bottom_fixed.set_size_request(1, bottom_fixed_height)
        button_x = 440
        button_y = 8
        
        self.bottom_fixed.put(self.ok_btn, button_x, button_y)
        self.bottom_fixed.put(self.cancel_btn, button_x + self.ok_btn.get_size_request()[0] + 20, button_y)
        
        self.main_vbox.pack_start(self.bottom_fixed, False, False)
        self.window_frame.add(self.main_vbox)
        # Init configure index.
        self.configure.set("文件播放")
        self.show_all()
        
    def draw_scrolled_window_backgournd(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        self.draw_single_mask(cr, rect.x, rect.y-4, rect.width, rect.height+8) 
        return True
        
    def draw_treeview_mask(self, cr, x, y, width, height):
        self.draw_single_mask(cr, x, y, width, height)
        
    def draw_single_mask(self, cr, x, y, width, height):
        cr.set_source_rgba(1, 1, 1, 0.7)
        cr.rectangle(x, y, width, height)
        cr.fill()        
        
    def draw_backgournd(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.get_allocation()
        cr.set_source_rgba(1, 1, 1, 0.85)
        width_padding = self.scrolled_window_frame.get_allocation()[2]
        cr.rectangle(rect.x + width_padding + 4, 
                     rect.y, 
                     rect.width - width_padding - 7, 
                     rect.height)
        cr.fill()
        
        propagate_expose(widget, event)
        return True
    
    def save_configure_file_ok_clicked(self, widget):    
        # save ini configure file.
        print "_____________[FilePlay]________________________"
        file_play_dict = self.configure.file_play.get_file_play_state()
        for key in file_play_dict.keys():
            self.ini.set("FilePlay", key, file_play_dict[key])
            print "%s = %s" % (str(key), str(file_play_dict[key]))
        print "_____________[SystemSet]_______________________"
        system_set_dict = self.configure.system_set.get_system_set_state()
        for key in system_set_dict.keys():
            self.ini.set("SystemSet", key, system_set_dict[key])
            print "%s = %s" % (str(key), str(system_set_dict[key]))
        print "_____________[PlayControl]_____________________"    
        play_control_dict = self.configure.play_control.get_play_control_state()
        for key in play_control_dict.keys():
            self.ini.set("PlayControl", key, play_control_dict[key])
            print "%s = %s" % (str(key), str(play_control_dict[key]))
        print "_____________[OtherKey]________________________"    
        other_key_dict = self.configure.other_key.get_other_set_state()
        for key in other_key_dict.keys():
            self.ini.set("OtherKey", key, other_key_dict[key])
            print "%s = %s" % (str(key), str(other_key_dict[key]))
        print "_____________[SubtitleSet]______________________"                
        sub_set_dict = self.configure.sub_set.get_subtitle_set_state()
        for key in sub_set_dict.keys():
            self.ini.set("SubtitleSet", key, sub_set_dict[key])
            print "%s = %s" % (str(key), str(sub_set_dict[key]))
        print "_____________[ScreenshotSet]____________________"    
        screenshot_dict = self.configure.screen_shot.get_screenshot_state()
        for key in screenshot_dict.keys():
            self.ini.set("ScreenshotSet", key, screenshot_dict[key])
            print "%s = %s" % (str(key), str(screenshot_dict[key]))
            
        self.ini.save()    
        self.emit("config-changed", "save_over")
        # quit configure window.
        self.destroy()
    
    def destroy_ini_gui_window_cancel_clicked(self, widget):    
        # quit configure window.
        self.destroy()
        
    def set_con_widget(self, treeview, item):
        # Configure class Mode.
        self.configure.set(item.get_title())
        
        
class Configure(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self)
        self.class_list = ["文件播放", "系统设置", "播放控制", "其它快捷键",
                           "字幕设置", "截图设置", "其它设置", "关于"]
        # Init all configure gui class.
        self.file_play = FilePlay()
        self.system_set = SystemSet()
        self.play_control = PlayControl()
        self.other_key = OtherKey()
        self.sub_set = SubSet()
        self.screen_shot = ScreenShot()
        self.other_set = OtherSet()
        self.about = About()
        
        self.show_all()
        
    def set(self, class_name):
        class_name = class_name.strip()
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
            elif "关于" == class_name:
                self.pack_start(self.about)
                
            for widget in self.get_children(): 
                if widget:
                    self.show_all()
                    return True                
        return None        
    

class FilePlay(gtk.VBox):    
    def __init__(self):
        gtk.VBox.__init__(self)
        self.fixed = gtk.Fixed()
        # Init config file.
        self.ini = Config(config_path)
        # self.ini = config
        self.label = Label("文件播放")        
        self.label.set_size_request(label_width, label_height)
        
        self.heparator = HSeparator(app_theme.get_shadow_color("linearBackground").get_color_info())
        self.heparator.set_size_request(heparator_width, heparator_height)
        
        # Video file open.
        self.video_file_open_label = Label("视频文件打开时 : ")
        self.ai_set_radio_btn       = RadioButton()
        self.ai_set_radio_btn_label = Label("智能调整")
        
        self.adapt_video_btn       = RadioButton()
        self.adapt_video_btn_label = Label("窗口适应视频")

        self.close_position_radio_btn       = RadioButton()
        self.close_position_radio_btn_label = Label("应用关闭尺寸位置")

        self.full_window_radio_btn       = RadioButton()        
        self.full_window_radio_btn_label = Label("自动全屏")                        
        set_num = self.ini.get("FilePlay", "video_file_open")        
        
        # Set state(1, 2, 3, 4).
        if '2' == set_num:
            self.ai_set_radio_btn.set_active(False)        
            self.adapt_video_btn.set_active(True)
        elif '3' == set_num:    
            self.close_position_radio_btn.set_active(True)
        elif '4' == set_num:    
            self.full_window_radio_btn.set_active(True)
        else:    # config get None type.
            self.ai_set_radio_btn.set_active(True) 
        ################################################################
        # open new file clear play list.
        self.clear_play_list_btn = CheckButton()        
        ini_bool = self.ini.get("FilePlay", "open_new_file_clear_play_list")
        self.clear_play_list_btn.set_active(False)
        if ini_bool:
            if "true" == ini_bool.lower():
                self.clear_play_list_btn.set_active(True)
                
        self.clear_play_list_btn_label = Label("打开新文件时清空播放列表")                
        # memory up close media player -> file play postion.
        self.file_play_postion_btn = CheckButton()
        ini_bool = self.ini.get("FilePlay", "memory_up_close_player_file_postion")
        self.file_play_postion_btn.set_active(False)
        if ini_bool:
            if "true" == ini_bool.lower():
                self.file_play_postion_btn.set_active(True)
                    
        self.file_play_postion_btn_label = Label("记忆上次关闭播放器时文件的播放位置")
        # play media when find file play in dir.
        self.find_file_play_btn = CheckButton() 
        ini_bool = self.ini.get("FilePlay", "find_play_file_relation_file")
        self.find_file_play_btn.set_active(False)
        if ini_bool:
            if "true" == ini_bool.lower():
                self.find_file_play_btn.set_active(True)
                
        self.find_file_play_btn_label = Label("播放连续剧时自动在文件夹里查找关联文件播放")
        # mouse progressbar show preview window.
        self.show_preview_window_btn = CheckButton()
        ini_bool = self.ini.get("FilePlay", "mouse_progressbar_show_preview")
        self.show_preview_window_btn.set_active(False)
        if ini_bool:
            if "true" == ini_bool.lower():
                self.show_preview_window_btn.set_active(True)
            
        self.show_preview_window_btn_label = Label("鼠标悬停进度条上显示预览图")
        
        # Video file open.
        video_file_open_x = 20
        video_file_open_y = 40
        self.fixed.put(self.label, video_file_open_x, TITLE_HEIGHT_PADDING)
        self.fixed.put(self.heparator, heparator_x, heparator_y)                
        self.fixed.put(self.video_file_open_label, 
                       video_file_open_x + 8, video_file_open_y)        
        video_file_open_y += 30
        self.fixed.put(self.ai_set_radio_btn,
                       video_file_open_x, video_file_open_y)
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
        # play media when find file play in dir.
        find_file_play_x = file_play_postion_x
        find_file_play_y = file_play_postion_y + 40
        self.fixed.put(self.find_file_play_btn,
                       find_file_play_x, find_file_play_y)
        find_file_play_width = self.find_file_play_btn.get_size_request()[0]
        self.fixed.put(self.find_file_play_btn_label,
                       find_file_play_x + find_file_play_width, find_file_play_y)
        # mouse progressbar show preview window.
        show_preview_window_x = find_file_play_x
        show_preview_window_y = find_file_play_y + 40        
        self.fixed.put(self.show_preview_window_btn,
                       show_preview_window_x, show_preview_window_y)
        show_preview_window_width = self.show_preview_window_btn.get_size_request()[0]
        self.fixed.put(self.show_preview_window_btn_label,
                       show_preview_window_x + show_preview_window_width, show_preview_window_y)
        
        self.pack_start(self.fixed)
        
    def get_file_play_state(self):           
        video_file_dict = {}
        # video file open.
        video_file_open_num = 1
        if self.ai_set_radio_btn.get_active():
            video_file_open_num = 1
        elif self.adapt_video_btn.get_active():    
            video_file_open_num = 2
        elif self.close_position_radio_btn.get_active():    
            video_file_open_num = 3
        elif self.full_window_radio_btn.get_active():    
            video_file_open_num = 4            
            
        video_file_dict["video_file_open"] = video_file_open_num
        #
        video_file_dict["open_new_file_clear_play_list"] = self.clear_play_list_btn.get_active()
        video_file_dict["memory_up_close_player_file_postion"] = self.file_play_postion_btn.get_active()
        video_file_dict["find_play_file_relation_file"] = self.find_file_play_btn.get_active()
        video_file_dict["mouse_progressbar_show_preview"] = self.show_preview_window_btn.get_active()
        
        return video_file_dict
    
class SystemSet(gtk.VBox):        
    def __init__(self):
        gtk.VBox.__init__(self)
        # Init config file.
        self.ini = Config(config_path)
        # self.ini = config
        self.fixed = gtk.Fixed()
        self.label = Label("系统设置")
        self.label.set_size_request(label_width, label_height)
        self.heparator=HSeparator(app_theme.get_shadow_color("linearBackground").get_color_info())
        self.heparator.set_size_request(heparator_width, heparator_height)
        # System setting.
        # Minimize pause plaing.
        self.pause_play_btn = CheckButton()
        ini_bool = self.ini.get("SystemSet", "minimize_pause_play")
        self.pause_play_btn.set_active(False)
        if ini_bool:
            if "true" == ini_bool.lower():
                self.pause_play_btn.set_active(True)            
            
        self.pause_play_btn_label = Label("最小化时暂停播放")
        # Screen messagebox.
        self.screen_msg_btn = Label("屏幕提示效果")
        # Font set.        
        self.font_set_btn_label = Label("字体")
        #DEFAULT_FONT
        font_set_items = [(DEFAULT_FONT, 1),
                          ("华彩", 2)]
        self.font_set_combo = ComboBox(font_set_items)        
        font_string = self.ini.get("SystemSet", "font")
        if font_string:
            self.font_set_combo.label.set_text(font_string)            
        else: # font_string return type None.    
            self.font_set_combo.label.set_text(DEFAULT_FONT) 
            
        font_set_combo_width = 120
        font_set_combo_height = 40
        # self.font_set_combo.set_size_request(font_set_combo_width, font_set_combo_height)
        # Font size.
        self.font_size_btn_label = Label("字号")
        font_size_combo_width = 120
        font_size_combo_height = 40                
        font_set_items = []
        font_set_items_num = 1
        for i in range(8, 16):
            font_set_items.append((str(i), font_set_items_num))
            font_set_items_num += 1
            
        self.font_size_btn_combo = ComboBox(font_set_items)
        font_size_string = self.ini.get("SystemSet", "font_size")
        if font_size_string:
            self.font_size_btn_combo.label.set_text(font_size_string)            
        else:    
            self.font_size_btn_combo.label.set_text("8")
            
        # self.font_size_btn_combo.set_size_request(font_size_combo_width, font_size_combo_height)
                
        system_set_x = 20
        system_set_y = 40
        system_set_width = 0
        self.fixed.put(self.label, system_set_x, TITLE_HEIGHT_PADDING)
        self.fixed.put(self.heparator, heparator_x, heparator_y)        
        self.fixed.put(self.pause_play_btn, 
                       system_set_x, system_set_y)
        # Minimize pause plaing.
        system_set_width = self.pause_play_btn.get_size_request()[0]
        self.fixed.put(self.pause_play_btn_label, 
                       system_set_x + system_set_width, system_set_y)
        # Screen messagebox.
        system_set_y += 40
        screen_msg_x_padding = 8
        self.fixed.put(self.screen_msg_btn,
                       system_set_x + screen_msg_x_padding, system_set_y)
        # Font set.
        system_set_y += 25        
        font_set_x_padding = 7
        self.fixed.put(self.font_set_btn_label, 
                       system_set_x + font_set_x_padding, system_set_y)
        system_set_y += 20
        self.fixed.put(self.font_set_combo, 
                       system_set_x + font_set_x_padding, system_set_y)
        # Font Size.
        font_size_x_padding = system_set_x + font_set_x_padding + font_set_combo_width + self.font_set_btn_label.get_size_request()[0] + 10
        system_set_y -= 20
        self.fixed.put(self.font_size_btn_label,
                       font_size_x_padding, system_set_y)
        system_set_y += 20
        self.fixed.put(self.font_size_btn_combo,
                       font_size_x_padding, system_set_y)
        #        
        
        self.pack_start(self.fixed)
        
    def get_system_set_state(self):           
        system_set_dict = {}
        #
        system_set_dict["minimize_pause_play"] = self.pause_play_btn.get_active()
        system_set_dict["font"] = self.font_set_combo.label.get_text()
        system_set_dict["font_size"] = self.font_size_btn_combo.label.get_text()
        return system_set_dict
        
class PlayControl(gtk.VBox):       
    def __init__(self):
        gtk.VBox.__init__(self)
        self.ini = Config(config_path)
        # self.ini = config
        self.fixed = gtk.Fixed()
        self.label = Label("播放控制")
        self.label.set_size_request(label_width, label_height)        
        # heparator.
        self.heparator=HSeparator(app_theme.get_shadow_color("linearBackground").get_color_info())
        self.heparator.set_size_request(heparator_width, heparator_height)
        # setting keys.
        entry_width = 150
        entry_height = 20
        # open file key.
        self.open_file_entry_label = Label("打开文件")
        self.open_file_entry       = TextEntry()
        text_string = self.ini.get("PlayControl", "open_file_key")
        if text_string:
            self.open_file_entry.set_text(text_string)
        else:  # text_string return None type.
            self.open_file_entry.set_text("Ctrl + O")
            
        self.open_file_entry.set_size(entry_width, entry_height)
        # pre a.
        self.pre_a_entry_label = Label("上一个")
        self.pre_a_entry       = TextEntry()
        text_string = self.ini.get("PlayControl", "pre_a_key")
        if text_string:
            self.pre_a_entry.set_text(text_string)
        else:    
            self.pre_a_entry.set_text("Page_Up")
            
        self.pre_a_entry.set_size(entry_width, entry_height)
        # open file dir.
        self.open_file_dir_entry_label = Label("打开文件夹")
        self.open_file_dir_entry       = TextEntry()
        text_string = self.ini.get("PlayControl", "open_file_dir_key")
        if text_string:
            self.open_file_dir_entry.set_text(text_string)
        else:    
            self.open_file_dir_entry.set_text("Ctrl + F")
            
        self.open_file_dir_entry.set_size(entry_width, entry_height)
        # next a.
        self.next_a_entry_label = Label("下一个")
        self.next_a_entry       = TextEntry()
        text_string = self.ini.get("PlayControl", "next_a_key")
        if text_string:
            self.next_a_entry.set_text(text_string)
        else: # Page_Down    
            self.next_a_entry.set_text("Page_Down")
            
        self.next_a_entry.set_size(entry_width, entry_height)
        # play or pause.
        self.play_or_pause_entry_label = Label("播放/暂停")
        self.play_or_pause_entry = TextEntry()
        text_string = self.ini.get("PlayControl", "play_or_pause_key")
        if text_string:
            self.play_or_pause_entry.set_text(text_string)        
        else:#"Space"
            self.play_or_pause_entry.set_text("Space")
            
        self.play_or_pause_entry.set_size(entry_width, entry_height)
        # add volume.
        self.add_volume_entry_label = Label("升高音量")
        self.add_volume_entry       = TextEntry()
        text_string = self.ini.get("PlayControl", "add_volume_key")
        if text_string:
            self.add_volume_entry.set_text(text_string)        
        else:   # Up 
            self.add_volume_entry.set_text("Up")
            
        self.add_volume_entry.set_size(entry_width, entry_height)
        # seek.
        self.seek_entry_label = Label("快进")
        self.seek_entry       = TextEntry()
        text_string = self.ini.get("PlayControl", "seek_key")
        if text_string:
            self.seek_entry.set_text(text_string)        
        else: # Right    
            self.seek_entry.set_text("Right")
            
        self.seek_entry.set_size(entry_width, entry_height)
        # sub volume.
        self.sub_volume_entry_label = Label("降低音量")
        self.sub_volume_entry       = TextEntry()
        text_string = self.ini.get("PlayControl", "sub_volume_key")
        if text_string:
            self.sub_volume_entry.set_text(text_string)        
        else: # Down
            self.sub_volume_entry.set_text("Down")
            
        self.sub_volume_entry.set_size(entry_width, entry_height)
        # back.
        self.back_entry_label = Label("快退")
        self.back_entry       = TextEntry()
        text_string = self.ini.get("PlayControl", "back_key")
        if text_string:
            self.back_entry.set_text(text_string)        
        else:    # Left
            self.back_entry.set_text("Left")
            
        self.back_entry.set_size(entry_width, entry_height)
        # Mute. 
        self.mute_entry_label = Label("静音")
        self.mute_entry       = TextEntry()
        text_string = self.ini.get("PlayControl", "mute_key")
        if text_string:
            self.mute_entry.set_text(text_string)        
        else:   # M 
            self.mute_entry.set_text("M")        

        self.mute_entry.set_size(entry_width, entry_height)
        # full.
        self.full_entry_label = Label("全屏")
        self.full_entry       = TextEntry()
        text_string = self.ini.get("PlayControl", "full_key")
        if text_string:
            self.full_entry.set_text(text_string)        
        else:    # Return
            self.full_entry.set_text("Return")        
            
        self.full_entry.set_size(entry_width, entry_height)
        # Concise mode.
        self.concise_entry_label = Label("迷你模式")
        self.concise_entry       = TextEntry()
        text_string = self.ini.get("PlayControl", "concise_key")
        if text_string:
            self.concise_entry.set_text(text_string)        
        else:    #Shift_L/R + Return
            self.concise_entry.set_text("Shift + Return")        
            
        self.concise_entry.set_size(entry_width, entry_height)
                        
        play_control_x = 20
        play_control_y = 40
        # label.
        self.fixed.put(self.label, play_control_x, TITLE_HEIGHT_PADDING)
        # heparator.
        self.fixed.put(self.heparator, 0, heparator_y)
        # open file key.
        play_control_x += 10
        self.fixed.put(self.open_file_entry_label,
                       play_control_x, play_control_y)        
        
        play_control_y += self.open_file_entry_label.get_size_request()[1] + 2
        self.fixed.put(self.open_file_entry,
                       play_control_x, play_control_y)
        # pre a.
        play_control_x_padding = play_control_x + self.open_file_entry.get_size_request()[0] + self.open_file_entry_label.get_size_request()[0]
        self.fixed.put(self.pre_a_entry,
                       play_control_x_padding, play_control_y)       
        self.fixed.put(self.pre_a_entry_label, play_control_x_padding, play_control_y - self.open_file_entry_label.get_size_request()[1] - 2)
        # open file dir and next a.
        play_control_y += self.pre_a_entry.get_size_request()[1] + 10
        self.fixed.put(self.open_file_dir_entry_label,
                       play_control_x, play_control_y)
        self.fixed.put(self.next_a_entry_label,
                       play_control_x_padding, play_control_y)
        play_control_y += self.next_a_entry.get_size_request()[1] + 2
        self.fixed.put(self.open_file_dir_entry,
                       play_control_x, play_control_y)        
        self.fixed.put(self.next_a_entry,
                       play_control_x_padding, play_control_y)
        play_control_y += self.next_a_entry.get_size_request()[1] + 10
        # play or pause and add volume.
        self.fixed.put(self.play_or_pause_entry_label, 
                       play_control_x, play_control_y)
        self.fixed.put(self.add_volume_entry_label, 
                       play_control_x_padding, play_control_y)
        play_control_y += self.play_or_pause_entry_label.get_size_request()[1] + 2
        self.fixed.put(self.play_or_pause_entry, 
                       play_control_x, play_control_y)
        self.fixed.put(self.add_volume_entry, 
                       play_control_x_padding, play_control_y)
        play_control_y += self.play_or_pause_entry.get_size_request()[1] + 10
        # seek and sub volume.
        self.fixed.put(self.seek_entry_label,
                       play_control_x, play_control_y)
        self.fixed.put(self.sub_volume_entry_label,
                       play_control_x_padding, play_control_y)
        play_control_y += self.sub_volume_entry_label.get_size_request()[1] + 2
        self.fixed.put(self.seek_entry,
                       play_control_x, play_control_y)
        self.fixed.put(self.sub_volume_entry,
                       play_control_x_padding, play_control_y)
        play_control_y += self.sub_volume_entry.get_size_request()[1] + 10
        # back and mute.
        self.fixed.put(self.back_entry_label, 
                       play_control_x, play_control_y)        
        self.fixed.put(self.mute_entry_label,                       
                       play_control_x_padding, play_control_y)
        play_control_y += self.mute_entry_label.get_size_request()[1] + 2
        self.fixed.put(self.back_entry, 
                       play_control_x, play_control_y)                
        self.fixed.put(self.mute_entry,  
                       play_control_x_padding, play_control_y)
        play_control_y += self.mute_entry_label.get_size_request()[1] + 10
        # full and concise mode.
        self.fixed.put(self.full_entry_label,
                       play_control_x, play_control_y)        
        self.fixed.put(self.concise_entry_label,
                       play_control_x_padding, play_control_y)
        play_control_y += self.concise_entry_label.get_size_request()[1] + 2
        self.fixed.put(self.full_entry,
                       play_control_x, play_control_y)        
        self.fixed.put(self.concise_entry,
                       play_control_x_padding, play_control_y)
        play_control_y += self.concise_entry.get_size_request()[1] + 10
        
        
        self.pack_start(self.fixed)
        
    def get_play_control_state(self):    
        play_control_dict = {}
        # Left.
        play_control_dict["open_file_key"] =  self.open_file_entry.get_text()
        play_control_dict["open_file_dir_key"] = self.open_file_dir_entry.get_text()
        play_control_dict["play_or_pause_key"] = self.play_or_pause_entry.get_text()
        play_control_dict["seek_key"] = self.seek_entry.get_text()
        play_control_dict["back_key"] = self.back_entry.get_text()
        play_control_dict["full_key"] = self.full_entry.get_text()
        # Right.
        play_control_dict["pre_a_key"]      = self.pre_a_entry.get_text()
        play_control_dict["next_a_key"]     = self.next_a_entry.get_text()
        play_control_dict["add_volume_key"] = self.add_volume_entry.get_text()
        play_control_dict["sub_volume_key"] = self.sub_volume_entry.get_text()
        play_control_dict["mute_key"]       = self.mute_entry.get_text()
        play_control_dict["concise_key"]    = self.concise_entry.get_text()
        
        return play_control_dict
    
class OtherKey(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self)
        self.ini = Config(config_path)
        # self.ini = config
        self.fixed = gtk.Fixed()
        self.label = Label("其它快捷键")
        self.label.set_size_request(label_width, label_height)                
        self.heparator=HSeparator(app_theme.get_shadow_color("linearBackground").get_color_info())
        self.heparator.set_size_request(heparator_width, heparator_height)
        
        entry_width  = 150
        entry_height = 20
        # Add Brightness.
        self.add_bri_entry_label = Label("增加亮度")
        self.add_bri_entry       = TextEntry()
        text_string = self.ini.get("OtherKey", "add_brightness_key")
        if text_string:
            self.add_bri_entry.set_text(text_string)
        else: # =   
            self.add_bri_entry.set_text("=")
            
        self.add_bri_entry.set_size(entry_width, entry_height)
        # Sub Brightness.
        self.sub_bri_entry_label = Label("减少亮度")
        self.sub_bri_entry       = TextEntry()
        text_string = self.ini.get("OtherKey", "sub_brightness_key")
        if text_string:
            self.sub_bri_entry.set_text(text_string)
        else:    # -
            self.sub_bri_entry.set_text("-")
            
        self.sub_bri_entry.set_size(entry_width, entry_height)
        # Inverse Rotation.
        self.inverse_rotation_entry_label = Label("逆时针旋转")
        self.inverse_rotation_entry       = TextEntry()
        text_string = self.ini.get("OtherKey", "inverse_rotation_key")
        if text_string:
            self.inverse_rotation_entry.set_text(text_string)
        else:    # w
            self.inverse_rotation_entry.set_text("W")
            
        self.inverse_rotation_entry.set_size(entry_width, entry_height)
        # Clockwise Rotation.
        self.clockwise_entry_label = Label("顺时针旋转")
        self.clockwise_entry       = TextEntry()
        text_string = self.ini.get("OtherKey", "clockwise_key")
        if text_string:
            self.clockwise_entry.set_text(text_string)
        else:    # e
            self.clockwise_entry.set_text("E")
            
        self.clockwise_entry.set_size(entry_width, entry_height)
        # sort image.
        self.sort_image_entry_label = Label("截图")
        self.sort_image_entry       = TextEntry()
        text_string = self.ini.get("OtherKey", "sort_image_key")
        if text_string:
            self.sort_image_entry.set_text(text_string)
        else:    # Alt_L/R A
            self.sort_image_entry.set_text("Alt + A")
            
        self.sort_image_entry.set_size(entry_width, entry_height)
        # Switch Audio track.
        self.switch_audio_track_entry_label = Label("切换音轨")
        self.switch_audio_track_entry       = TextEntry()
        text_string = self.ini.get("OtherKey", "switch_audio_track_key")
        if text_string:
            self.switch_audio_track_entry.set_text(text_string)
        else:    # 
            self.switch_audio_track_entry.set_text(text_string)
            
        self.switch_audio_track_entry.set_size(entry_width, entry_height)
        # Load subtitle.
        self.load_subtitle_entry_label = Label("载入字幕")
        self.load_subtitle_entry       = TextEntry()
        text_string = self.ini.get("OtherKey", "load_subtitle_key")
        if text_string:
            self.load_subtitle_entry.set_text(text_string)
        else:    #Alt_L/R + O
            self.load_subtitle_entry.set_text("Alt + O")
            
        self.load_subtitle_entry.set_size(entry_width, entry_height)        
        # subtitle advance 0.5.
        self.subtitle_advance_entry_label = Label("字幕提前0.5秒")
        self.subtitle_advance_entry       = TextEntry()
        text_string = self.ini.get("OtherKey", "subtitle_advance_key")
        if text_string:
            self.subtitle_advance_entry.set_text(text_string)
        else:    # [
            self.subtitle_advance_entry.set_text("[")
            
        self.subtitle_advance_entry.set_size(entry_width, entry_height)
        # subtitle Delay 0.5.
        self.subtitle_delay_entry_label = Label("字幕延时0.5秒")
        self.subtitle_delay_entry       = TextEntry()
        text_string = self.ini.get("OtherKey", "subtitle_delay_key")
        if text_string:
            self.subtitle_delay_entry.set_text(text_string)
        else:    # ]
            self.subtitle_delay_entry.set_text("]")
            
        self.subtitle_delay_entry.set_size(entry_width, entry_height)
        # mouse left single clicked.        
        self.mouse_left_single_clicked_combo_label = Label("鼠标左键单击")
        self.mouse_left_single_clicked_combo       = ComboBox([("暂停/播放", 1),
                                                               ("NULL", 2)])

        text_string = self.ini.get("OtherKey", "mouse_left_single_clicked")
        if text_string:
            self.mouse_left_single_clicked_combo.label.set_text(text_string)
        else:    
            self.mouse_left_single_clicked_combo.label.set_text(text_string)
            
        # self.mouse_left_single_clicked_combo.set_size_request(entry_width, entry_height)
        # mouse left double clicked.
        self.mouse_left_double_clicked_combo_label = Label("鼠标左键双击")
        self.mouse_left_double_clicked_combo       = ComboBox([("全屏", 1),
                                                               ("NULL", 2)])
        text_string = self.ini.get("OtherKey", "mouse_left_double_clicked")
        if text_string:
            self.mouse_left_double_clicked_combo.label.set_text(text_string)        
            
        # self.mouse_left_double_clicked_combo.set_size_request(entry_width, entry_height)
        # mouse wheel.
        self.mouse_wheel_combo_label = Label("鼠标滚轮")
        self.mouse_wheel_combo       = ComboBox([("音量", 1),
                                                 ("NULL", 2)])
        text_string = self.ini.get("OtherKey", "mouse_wheel_event")
        if text_string:
            self.mouse_wheel_combo.label.set_text(text_string)        
            
        # self.mouse_wheel_combo.set_size_request(entry_width, entry_height)
        
        
        other_Key_x = 20
        other_Key_y = 40
        # label.
        self.fixed.put(self.label, other_Key_x, TITLE_HEIGHT_PADDING)
        # heparator.
        self.fixed.put(self.heparator, heparator_x, heparator_y)
        ########################################################
        other_Key_x += 10        
        # Add Brightness.
        self.fixed.put(self.add_bri_entry_label, 
                       other_Key_x, other_Key_y)
        other_Key_y += self.add_bri_entry_label.get_size_request()[1] + 2
        self.fixed.put(self.add_bri_entry,
                       other_Key_x, other_Key_y)
        other_Key_y += self.add_bri_entry.get_size_request()[1] + 10
        # Sub Brightness.
        self.fixed.put(self.sub_bri_entry_label, 
                       other_Key_x, other_Key_y)
        other_Key_y += self.sub_bri_entry_label.get_size_request()[1] + 2
        self.fixed.put(self.sub_bri_entry,
                       other_Key_x, other_Key_y)
        other_Key_y += self.sub_bri_entry.get_size_request()[1] + 10
        # Inverse Rotation.
        self.fixed.put(self.inverse_rotation_entry_label,
                       other_Key_x, other_Key_y)
        other_Key_y += self.inverse_rotation_entry_label.get_size_request()[1] + 2
        self.fixed.put(self.inverse_rotation_entry,
                       other_Key_x, other_Key_y)
        other_Key_y += self.inverse_rotation_entry.get_size_request()[1] + 10
        # Clockwise Rotation.
        self.fixed.put(self.clockwise_entry_label,
                       other_Key_x, other_Key_y)
        other_Key_y += self.clockwise_entry_label.get_size_request()[1] + 2
        self.fixed.put(self.clockwise_entry,
                       other_Key_x, other_Key_y)
        other_Key_y += self.clockwise_entry.get_size_request()[1] + 10
        # sort image.
        self.fixed.put(self.sort_image_entry_label,
                       other_Key_x, other_Key_y)
        other_Key_y += self.sort_image_entry_label.get_size_request()[1] + 2
        self.fixed.put(self.sort_image_entry,
                       other_Key_x, other_Key_y)
        other_Key_y += self.sort_image_entry.get_size_request()[1] + 10
        # Switch Audio track.
        self.fixed.put(self.switch_audio_track_entry_label,
                       other_Key_x, other_Key_y)
        other_Key_y += self.switch_audio_track_entry_label.get_size_request()[1] + 2
        self.fixed.put(self.switch_audio_track_entry,
                       other_Key_x, other_Key_y)
        other_Key_y += self.switch_audio_track_entry_label.get_size_request()[1] + 10
        ##############################################
        # Load subtitle.
        other_Key_x_padding = other_Key_x + self.switch_audio_track_entry.get_size_request()[0] + self.switch_audio_track_entry_label.get_size_request()[0]
        other_Key_y = 40
        self.fixed.put(self.load_subtitle_entry_label,
                       other_Key_x_padding,  other_Key_y)
        other_Key_y += self.load_subtitle_entry_label.get_size_request()[1] + 2
        self.fixed.put(self.load_subtitle_entry,
                       other_Key_x_padding, other_Key_y)
        other_Key_y += self.load_subtitle_entry.get_size_request()[1] + 10
        ##############################################
        # subtitle 0.5.
        # subtitle advance 0.5.
        self.fixed.put(self.subtitle_advance_entry_label,
                       other_Key_x_padding, other_Key_y)
        other_Key_y += self.subtitle_advance_entry_label.get_size_request()[1] + 2
        self.fixed.put(self.subtitle_advance_entry,
                       other_Key_x_padding, other_Key_y)
        other_Key_y += self.subtitle_advance_entry.get_size_request()[1] + 10
        # subtitle Delay 0.5.
        self.fixed.put(self.subtitle_delay_entry_label,
                       other_Key_x_padding, other_Key_y)
        other_Key_y += self.subtitle_delay_entry_label.get_size_request()[1] + 2
        self.fixed.put(self.subtitle_delay_entry,
                       other_Key_x_padding, other_Key_y)
        other_Key_y += self.subtitle_delay_entry.get_size_request()[1] + 10
        # mouse left single clicked.        
        self.fixed.put(self.mouse_left_single_clicked_combo_label, 
                       other_Key_x_padding, other_Key_y)
        other_Key_y += self.mouse_left_single_clicked_combo_label.get_size_request()[1] + 2
        self.fixed.put(self.mouse_left_single_clicked_combo, 
                       other_Key_x_padding, other_Key_y)
        other_Key_y += self.mouse_left_single_clicked_combo_label.get_size_request()[1] + 10
        # mouse left double clicked.
        self.fixed.put(self.mouse_left_double_clicked_combo_label, 
                       other_Key_x_padding, other_Key_y)
        other_Key_y += self.mouse_left_double_clicked_combo_label.get_size_request()[1] + 2
        self.fixed.put(self.mouse_left_double_clicked_combo, 
                       other_Key_x_padding, other_Key_y)
        other_Key_y += self.mouse_left_double_clicked_combo_label.get_size_request()[1] + 10
        # mouse wheel.
        self.fixed.put(self.mouse_wheel_combo_label,
                       other_Key_x_padding, other_Key_y)
        other_Key_y += self.mouse_wheel_combo_label.get_size_request()[1] + 2
        self.fixed.put(self.mouse_wheel_combo,
                       other_Key_x_padding, other_Key_y)
        other_Key_y += self.mouse_wheel_combo_label.get_size_request()[1] + 10
                
        self.pack_start(self.fixed)
    
    def get_other_set_state(self):
        other_set_dict = {}
        # Left.
        other_set_dict["add_brightness_key"] = self.add_bri_entry.get_text()
        other_set_dict["sub_brightness_key"] = self.sub_bri_entry.get_text()
        other_set_dict["inverse_rotation_key"] = self.inverse_rotation_entry.get_text()
        other_set_dict["clockwise_key"] = self.clockwise_entry.get_text()
        other_set_dict["sort_image_key"] = self.sort_image_entry.get_text()
        other_set_dict["switch_audio_track_key"] = self.switch_audio_track_entry.get_text()
        # Right.
        other_set_dict["load_subtitle_key"] = self.load_subtitle_entry.get_text()
        other_set_dict["subtitle_advance_key"] = self.subtitle_advance_entry.get_text()
        other_set_dict["subtitle_delay_key"] = self.subtitle_delay_entry.get_text()
        other_set_dict["mouse_left_single_clicked"] = self.mouse_left_single_clicked_combo.label.get_text()
        other_set_dict["mouse_left_double_clicked"] = self.mouse_left_double_clicked_combo.label.get_text()
        other_set_dict["mouse_wheel_event"] = self.mouse_wheel_combo.label.get_text()
        
        return other_set_dict
    
class SubSet(gtk.VBox):    
    def __init__(self):
        gtk.VBox.__init__(self)
        entry_width = 280
        entry_height = 25
        self.ini = Config(config_path)
        # self.ini = config
        self.fixed = gtk.Fixed()
        self.label = Label("字幕设置")
        self.label.set_size_request(label_width, label_height)

        self.heparator=HSeparator(app_theme.get_shadow_color("linearBackground").get_color_info())
        self.heparator.set_size_request(heparator_width, heparator_height)
        # Ai load subtitle.
        self.ai_load_subtitle_checkbtn       = CheckButton()
        ini_bool = self.ini.get("SubtitleSet", "ai_load_subtitle")
        self.ai_load_subtitle_checkbtn.set_active(False)
        if ini_bool:
            if "true" == ini_bool.lower():            
                self.ai_load_subtitle_checkbtn.set_active(True)                
                
        self.ai_load_subtitle_checkbtn_label = Label("自动载入字幕")
        # Specified Location Search.
        self.specific_location_search_label = Label("指定位置路径 : ")
        self.specific_location_search_entry = TextEntry()
        text_string = self.ini.get("SubtitleSet", "specific_location_search")
        if text_string:
            self.specific_location_search_entry.set_text(text_string)
        else:    
            self.specific_location_search_entry.set_text("~/.config/deepin-media-player/subtitle")
            
        self.specific_location_search_entry.set_size(entry_width, entry_height)
        self.specific_location_search_btn   = Button("浏览")
        self.specific_location_search_btn.connect("clicked", self.load_path_to_sls_entry)
        sub_set_x = 20
        sub_set_y = 40
        self.fixed.put(self.label, sub_set_x, TITLE_HEIGHT_PADDING)
        self.fixed.put(self.heparator, heparator_x, heparator_y)
        sub_set_x += 10
        # Ai load subtitle.
        self.fixed.put(self.ai_load_subtitle_checkbtn,
                       sub_set_x, sub_set_y)
        self.fixed.put(self.ai_load_subtitle_checkbtn_label,
                       sub_set_x + self.ai_load_subtitle_checkbtn.get_size_request()[0], sub_set_y)
        sub_set_y += self.ai_load_subtitle_checkbtn.get_size_request()[1] + 25
        # Specified Location Search.
        sub_set_x += 5
        self.fixed.put(self.specific_location_search_label,
                       sub_set_x, sub_set_y)
        sub_set_y += self.specific_location_search_label.get_size_request()[1] + 10
        self.fixed.put(self.specific_location_search_entry,
                       sub_set_x, sub_set_y + 1)
        self.fixed.put(self.specific_location_search_btn,
                       sub_set_x + self.specific_location_search_entry.get_size_request()[0] + 10, sub_set_y)
        
        self.pack_start(self.fixed)
        
    def load_path_to_sls_entry(self, widget):    
        open_dialog = gtk.FileChooserDialog("深度影音配置打开文件夹对话框",
                                            None,
                                            gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                            (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, 
                                             gtk.STOCK_OPEN, gtk.RESPONSE_OK))        
        open_dialog.set_current_folder(get_home_path())
        res = open_dialog.run()
        
        if res == gtk.RESPONSE_OK:
            path_string = open_dialog.get_filename()
            self.specific_location_search_entry.set_text(path_string)
        open_dialog.destroy()

    def get_subtitle_set_state(self):    
        sub_set_dict = {}
        sub_set_dict["ai_load_subtitle"] = self.ai_load_subtitle_checkbtn.get_active()
        sub_set_dict["specific_location_search"] = self.specific_location_search_entry.get_text()
        return sub_set_dict
        
class ScreenShot(gtk.VBox):        
    def __init__(self):
        gtk.VBox.__init__(self)
        entry_width = 250
        entry_height = 25
        self.ini = Config(config_path)
        # self.ini = config
        self.fixed = gtk.Fixed()
        self.label = Label("截图设置")
        self.label.set_size_request(label_width, label_height)
        self.heparator=HSeparator(app_theme.get_shadow_color("linearBackground").get_color_info())
        self.heparator.set_size_request(heparator_width, heparator_height)                
        # Save clipboard.
        self.save_clipboard_radio = RadioButton()
        # save clipboard radio event.
        self.save_clipboard_radio.connect("button-press-event", self.save_clipboard_radio_clicked)
        
        self.save_clipboard_radio_label = Label("仅保存在剪贴板")
        # Save File.
        self.save_file_radio = RadioButton()
        self.save_file_radio.connect("button-press-event", self.save_file_radio_clicked)
        self.save_file_radio.set_active(True)
        self.save_file_radio_label = Label("保存成文件")
        # Save path.
        self.save_path_label = Label("保存路径 : ")
        self.save_path_entry = TextEntry()        
        # text_string = self.ini.get("ScreenshotSet", "save_path")
        # if text_string:
        #     self.save_path_entry.set_text(text_string)
        # else:    
        #     self.save_path_entry.set_text("~/.config/deepin-media-player/image")
            
        self.save_path_entry.set_size(entry_width, entry_height)                
        self.save_path_button = Button("浏览")
        self.save_path_button.connect("clicked", self.save_path_to_save_path_entry_clicked)
        # Save type.
        self.save_type_label  = Label("保存类型 : ")
        self.save_type_combo  = ComboBox([(".png", 1),
                                          (".jpeg", 2)])
        
        ini_bool = self.ini.get("ScreenshotSet", "save_clipboard")
        # Init .
        self.save_file_radio.set_active(True)
        self.save_clipboard_radio.set_active(False)
        
        text_string = self.ini.get("ScreenshotSet", "save_path")
        if text_string:
            self.save_path_entry.set_text(text_string)
        else:    
            self.save_path_entry.set_text("~/.config/deepin-media-player/image")
            
        text_string = self.ini.get("ScreenshotSet", "save_type")            
        if text_string:
            self.save_type_combo.label.set_text(text_string)
        else:    
            self.save_type_combo.label.set_text(".png")
            
        if ini_bool:
             if "true" == ini_bool.lower():
                 self.save_file_radio.set_active(False)
                 self.save_clipboard_radio.set_active(True)        
                 self.save_path_entry.entry.set_editable(False)            
                 self.save_path_button.set_clickable(False)
                 
        # 
        self.current_show_sort_label = Label("按当前显示的画面尺寸截图")
        self.current_show_sort_check = CheckButton()
        self.current_show_sort_check.set_active(False)
        ini_bool = self.ini.get("ScreenshotSet", "current_show_sort")
        if ini_bool:
            if "true" == ini_bool.lower():
                self.current_show_sort_check.set_active(True)
                
        ###############################################
        screenshot_x = 20
        screenshot_y = 40        
        self.fixed.put(self.label, screenshot_x, TITLE_HEIGHT_PADDING)
        self.fixed.put(self.heparator, heparator_x, heparator_y)
        # Save clipboard.
        self.fixed.put(self.save_clipboard_radio,
                       screenshot_x, screenshot_y)
        self.fixed.put(self.save_clipboard_radio_label,
                       screenshot_x + self.save_clipboard_radio.get_size_request()[0], screenshot_y)
        screenshot_y += self.save_clipboard_radio.get_size_request()[1] + 5
        # Save file.
        self.fixed.put(self.save_file_radio,
                       screenshot_x, screenshot_y)
        self.fixed.put(self.save_file_radio_label,
                       screenshot_x + self.save_file_radio.get_size_request()[0], screenshot_y)        
        screenshot_x_padding = screenshot_x + 45
        screenshot_y += self.save_file_radio.get_size_request()[1] + 15
        # save path.
        self.fixed.put(self.save_path_label, screenshot_x_padding, screenshot_y)
        # save type.
        self.fixed.put(self.save_type_label, 
                       screenshot_x_padding, screenshot_y + self.save_path_label.get_size_request()[1] + 10)        
        screenshot_x_padding += self.save_path_label.get_size_request()[0] + 10
        # save path entry .
        self.fixed.put(self.save_path_entry, 
                       screenshot_x_padding, screenshot_y - 2)
        screenshot_x_padding += self.save_path_entry.get_size_request()[0]
        self.fixed.put(self.save_path_button, 
                       screenshot_x_padding + 10, screenshot_y - 3)
        screenshot_y += self.save_path_button.get_size_request()[1]
        screenshot_x_padding = screenshot_x + self.save_type_label.get_size_request()[0] + 55
        # save type entry.
        self.fixed.put(self.save_type_combo, screenshot_x_padding, screenshot_y)                
        # 
        screenshot_x = 20
        screenshot_y += self.save_type_combo.get_size_request()[1] + 50
        self.fixed.put(self.current_show_sort_check, screenshot_x, screenshot_y)
        screenshot_x_padding = screenshot_x + self.current_show_sort_check.get_size_request()[0]
        self.fixed.put(self.current_show_sort_label, screenshot_x_padding, screenshot_y)
        
        self.pack_start(self.fixed)
        
    def save_path_to_save_path_entry_clicked(self, widget):
        open_dialog = gtk.FileChooserDialog("深度影音配置打开文件夹对话框",
                                            None,
                                            gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                            (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, 
                                             gtk.STOCK_OPEN, gtk.RESPONSE_OK))        
        open_dialog.set_current_folder(get_home_path())
        res = open_dialog.run()
        
        if res == gtk.RESPONSE_OK:
            path_string = open_dialog.get_filename()
            self.save_path_entry.set_text(path_string)
        open_dialog.destroy()

        
    def save_file_radio_clicked(self, widget, event):    
        if 1 == event.button:
            self.save_path_entry.entry.set_editable(True)
            self.save_path_button.set_clickable(True)

        
    def save_clipboard_radio_clicked(self, widget, event):    
        # self.save_path_entry.entry.set_editable(False)            
        if 1 == event.button:
            self.save_path_entry.entry.set_editable(False)
            self.save_path_button.set_clickable(False)
            #
        
    def get_screenshot_state(self):     
        screenshot_dict = {}
        screenshot_dict["save_clipboard"]   = self.save_clipboard_radio.get_active() 
        screenshot_dict["save_file"]        = self.save_file_radio.get_active()
        screenshot_dict["save_path"]        = self.save_path_entry.get_text()
        screenshot_dict["save_type"]        = self.save_type_combo.label.get_text()            
        screenshot_dict["current_show_sort"] = self.current_show_sort_check.get_active()
        return screenshot_dict
        
        
class OtherSet(gtk.VBox):    
    def __init__(self):
        gtk.VBox.__init__(self)
        self.fixed = gtk.Fixed()
        self.label = Label("其它设置")
        self.label.set_size_request(label_width, label_height)
        self.heparator=HSeparator(app_theme.get_shadow_color("linearBackground").get_color_info())
        self.heparator.set_size_request(heparator_width, heparator_height)                
        
        otherset_x = 20
        otherset_y = 40
        #################################
        self.fixed.put(self.label, otherset_x, TITLE_HEIGHT_PADDING)
        self.fixed.put(self.heparator, heparator_x, heparator_y)
        
        self.pack_start(self.fixed)
        
        
class About(gtk.VBox):    
    def __init__(self):
        gtk.VBox.__init__(self)
        self.fixed = gtk.Fixed()
        self.label = Label("深度影音", text_size=12)        
        self.label.set_size_request(label_width, label_height)
        self.version_label = Label("版本:D1.02.3           发布时间:2012.06.31")
        #
        self.label_text_about = Label("　　深度影音是中国最大的网络电影平台，是中国互联网领域领先的正版数字电影服务提供商，始终走在电影潮流最前端，向广大用户提供方便流畅的在线电影和丰富多彩的电影社区服务。")
        
        self.index_label = Label("官方主页:")
        # self.
        
        self.heparator=HSeparator(app_theme.get_shadow_color("linearBackground").get_color_info())
        self.heparator.set_size_request(heparator_width, heparator_height)
        
        about_x = 20
        about_y = 40
        label_x_padding = about_x + 30
        label_y_padding = TITLE_HEIGHT_PADDING + 25
        ####################################
        self.fixed.put(self.label, label_x_padding, label_y_padding)
        label_x_padding += self.label.get_size_request()[0] + 30
        self.fixed.put(self.version_label, label_x_padding, label_y_padding + 6)
        
        self.fixed.put(self.heparator, heparator_x, heparator_y + 30)
        
        self.pack_start(self.fixed)
        
        
if __name__ == "__main__":        
    IniGui()
    gtk.main()
