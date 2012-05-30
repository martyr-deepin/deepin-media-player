#! /usr/bin/env python
# -*- coding: utf-8 -*-

# houshaohui:code->[str_size function, get size, type, mtime]. 
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

from dtk.ui.entry import TextEntry
from dtk.ui.titlebar import Titlebar
from dtk.ui.listview import ListView
from dtk.ui.scrolled_window import ScrolledWindow
from dtk.ui.window import Window
from dtk.ui.button import Button
from openlist import OpenItem


import gio
import gtk
import os
import datetime
import gobject

class OpenDialog(Window):
    __gsignals__ = {
        "get-path-name" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),
    }    
    
    def __init__(self, path_name="~", Filter = {"所有文件":".*"}, width=500, height=350):
        
        Window.__init__(self)
        # file type.
        self.filter = Filter # Save Filter.
        self.filter_format = ""
        # init file type.
        self.filter_to_file_type("所有文件")
        
        # Set open window -> dialog.
        self.set_modal(True)
        # Set open dialog above.
        self.set_keep_above(True)
        # Set window center.
        self.set_position(gtk.WIN_POS_MOUSE)
        
        self.set_size_request(width, height)
        self.scrolled_window = ScrolledWindow()
        
        self.list_view = ListView()
        # Add list view events.
        self.list_view.connect("delete-select-items", self.no_delete_file)
        self.list_view.connect("double-click-item", self.open_path_file)
        
        self.list_view.add_titles(["名称", "大小", "类型", "修改日期"]) 
        self.list_item = []
        self.path_name = ""
        self.path_list = ""
        
        # init dir(path).
        self.init_dir(path_name)
        
        self.scrolled_window.add_child(self.list_view)             
        self.main_vbox = gtk.VBox()
        
        # titlebar .
        self.titlebar = Titlebar(["min", "close"], app_name="打开对话框")
        
        self.main_vbox.pack_start(self.titlebar, False, False)
        
        # input path name ->text widget.
        open_window_borde_width = 3
        open_window_borde_height = 2
        
        self.path_entry_frame = gtk.Alignment()
        self.path_entry_frame.set(1, 1, 1, 1)        
        self.path_entry_frame.set_padding(open_window_borde_height, open_window_borde_height, 
                                          open_window_borde_width, open_window_borde_width)
        self.path_entry = TextEntry(self.path_name)
        # entry events.
        # draw_entry_background select_all
        self.path_entry.entry.connect("changed", self.input_path_entry)
                
        
        self.path_entry.set_size(1, 30)
        self.path_entry_frame.add(self.path_entry)
        self.main_vbox.pack_start(self.path_entry_frame, False, False)
        
        # return and chdir dir button.
                
        # scrolled window .
        self.scrolled_window_frame = gtk.Alignment()        
        self.scrolled_window_frame.set(1, 1, 1, 1)
        self.scrolled_window_frame.set_padding(open_window_borde_height, open_window_borde_height + 8, 
                                               open_window_borde_width, open_window_borde_width)
        self.scrolled_window_frame.add(self.scrolled_window)
        self.main_vbox.pack_start(self.scrolled_window_frame, True, True)
        
        # open_button and cancel_button
        self.button_hbox = gtk.HBox()
        self.button_hbox_frmae = gtk.Alignment()
        self.button_hbox_frmae.set(1, 0.5, 0, 0)
        self.button_hbox_frmae.set_padding(0, 8, 0, 5)
        self.button_hbox_frmae.add(self.button_hbox)
        
        self.open_button_frame = gtk.Alignment()
        self.open_button_frame.set_padding(0, 0, 5, 5)
        self.open_button = Button("打开")


        self.open_button.connect("clicked", self.open_button_clicked)            

        self.open_button_frame.add(self.open_button)
        
        self.cancel_button_frame = gtk.Alignment()
        self.cancel_button = Button("取消")
        # cancel_button event[destroy open window].
        self.cancel_button.connect("clicked", lambda w:self.destroy())
        self.cancel_button_frame.add(self.cancel_button)
        
        self.button_hbox.pack_start(self.open_button_frame)
        self.button_hbox.pack_start(self.cancel_button_frame)
        
        self.main_vbox.pack_start(self.button_hbox_frmae, False, False)
        
        # move open window.
        self.add_move_event(self.titlebar.drag_box)
        self.titlebar.close_button.connect("clicked", lambda w:self.destroy())
        self.titlebar.min_button.connect("clicked", lambda w: self.min_window())
        self.window_frame.add(self.main_vbox)
        
    def open_button_clicked(self, widget):    
        try:
            item = self.list_view.items[self.list_view.select_rows[0]]            
        except:
            item = self.list_view.items[0]
    
        self.open_path_file(self.list_view, 
                                item,
                                -1, 0, 0)
        
    def init_dir(self, path_name):            
        if "~" == path_name:
            self.path_name = os.path.expanduser("~") + "/"
        else:    
            if os.path.exists(path_name): # File path ok.
                if os.path.isdir(path_name):
                    self.path_name = path_name
                    if "/" != path_name[-1:]:
                        self.path_name += "/"
            else: # File Error.
                self.path_name = os.path.expanduser("~") + "/"
                
        self.path_list_show(self.path_name)
        
    def show_open_window(self):    
        self.show_all()
        
    def set_title(self, title_text):    
        self.titlebar.app_name_box.change_text(title_text)
        
    # def set_icon(self, pixbuf):    
    #     self.titlebar.icon_box.image_dpixbuf = pixbuf 
        
    def input_path_entry(self, entry, text):
        '''input path entry.'''    
        if os.path.exists(text):
            if os.path.isdir(text): # Dir.
                for path in os.listdir(text):
                    if "." != path[0:1]:
                        self.path_entry.select_start_index = 5
                        self.path_entry.entry.select_to_end()
            else: # File.
                print "This is File type."
                
    def open_path_file(self, list_view, item, column, offset_x, offset_y):    
        temp_path_name = self.path_name + item.title                 
        
        if os.path.isfile(temp_path_name):
            self.emit("get-path-name", temp_path_name)
            self.destroy()
        else:    
            temp_path_name +=  "/"
            self.path_list_show(temp_path_name)
        
    def path_list_show(self, temp_path_name):
        if os.path.isdir(temp_path_name):
            try:
                self.path_entry.entry.set_text(temp_path_name)
            except Exception, e:    
                print "path_list_show: %s" % (e)
            
            # modefiy path_entry text.            
            # clear list item.
            self.list_view.clear()
            self.list_item = []
            # file list.
            self.path_name = temp_path_name
            self.path_list = os.listdir(self.path_name)
            if self.path_list:
                for path_str in self.path_list:
                    try:
                        if "." != path_str[0:1]:                        
                        
                            real_path = os.path.realpath(self.path_name + path_str)
                             # real_path format == self.filter_format -> True
                            if os.path.isfile(real_path):
                                if not self.filter_file_type_bool(real_path):
                                    continue                                                        
                                
                            pixbuf, size_num, file_type, modify_time  = self.icon_to_pixbuf(self.path_name + path_str, 16)
                        
                            if os.path.isdir(real_path):
                                file_size = "%d %s" % (len(os.listdir(real_path)), "项")
                            else:
                                file_size  = self.str_size(size_num)                            
                                                        
                            file_ctime = datetime.datetime.fromtimestamp(os.path.getmtime(real_path)).strftime("%x %A %X")   
                        
                            self.list_item.append(OpenItem(pixbuf, path_str, file_size, file_type, file_ctime))
                    except Exception, e:    
                        print "path_list_show:%s" % (e)
                        
                if self.list_item:    
                    self.list_view.add_items(self.list_item)
        
    def set_filter(self, filter_dict):                
        self.filter = filter_dict
        
    def filter_to_file_type(self, type_name):
        '''{name:*.*, name1:*.txt*, name2:*.out*... ...}'''
        self.filter_format = self.filter[type_name]
        
    def filter_file_type_bool(self, file_name):
        '''Get file type->bool[True or False]'''        
        # All File.
        if ".*" == self.filter_format:
            return True
        # Get file format.
        file_path, file_format = os.path.splitext(file_name)
        file_format = file_format 
        if file_format in self.filter_format.split("|"):            
            return True
                
        gio_file = gio.File(file_name)
        file_atrr = ",".join([gio.FILE_ATTRIBUTE_STANDARD_CONTENT_TYPE,
                                                      gio.FILE_ATTRIBUTE_STANDARD_TYPE, 
                                                      gio.FILE_ATTRIBUTE_STANDARD_NAME,
                                                      gio.FILE_ATTRIBUTE_STANDARD_SIZE,
                                                      gio.FILE_ATTRIBUTE_STANDARD_DISPLAY_NAME,
                                                      gio.FILE_ATTRIBUTE_TIME_MODIFIED,
                                                      gio.FILE_ATTRIBUTE_STANDARD_ICON,
                                            ])
        gio_file_info = gio_file.query_info(file_atrr)                
        info_attr = gio_file_info.get_attribute_as_string(gio.FILE_ATTRIBUTE_STANDARD_CONTENT_TYPE)       
        file_format = info_attr       

        if str(file_format) in self.filter_format.split("|"):
            return True
        else:
            return False
        
        
        
    def no_delete_file(self, list_view, items):    
        self.list_view.clear()
        self.list_view.add_items(self.list_item)
    
        
    def icon_to_pixbuf(self, path, icon_size = 16):
        '''Get pat(cell_min_sh to pixbuf.'''
        gio_file = gio.File(path)
        gio_file_info = gio_file.query_info(",".join([gio.FILE_ATTRIBUTE_STANDARD_CONTENT_TYPE,
                                                      gio.FILE_ATTRIBUTE_STANDARD_TYPE, 
                                                      gio.FILE_ATTRIBUTE_STANDARD_NAME,
                                                      gio.FILE_ATTRIBUTE_STANDARD_SIZE,
                                                      gio.FILE_ATTRIBUTE_STANDARD_DISPLAY_NAME,
                                                      gio.FILE_ATTRIBUTE_TIME_MODIFIED,
                                                      gio.FILE_ATTRIBUTE_STANDARD_ICON,
                                                      ]))                
        icon_theme = gtk.icon_theme_get_default()
        info_attr = gio_file_info.get_attribute_as_string(gio.FILE_ATTRIBUTE_STANDARD_CONTENT_TYPE)                

        display_type = str(gio.content_type_get_description(info_attr))
        display_size = str(gio_file_info.get_size())
        display_modify_time = gio_file_info.get_modification_time()
        icon = gio.content_type_get_icon(info_attr)
        icon_info = icon_theme.lookup_by_gicon(icon, icon_size, gtk.ICON_LOOKUP_USE_BUILTIN)        
        # return icon, size, modify_time.
        try:
            pixbuf = icon_info.load_icon()
        except Exception,e:    
            info_attr = "text-plain"
            icon = gio.content_type_get_icon(info_attr)
            icon_info = icon_theme.lookup_by_gicon(icon, icon_size, gtk.ICON_LOOKUP_USE_BUILTIN)        
            pixbuf = icon_info.load_icon()
            print "icon_to_pixbuf:%s" % (e)
            
        return pixbuf, display_size, display_type, display_modify_time
        
    
    def str_size(self, nb, average=0, base=1024):        
        if average != 0:
            average += 1
        nb = float(nb)    
        size_format = ""
        if base == 1024:
            units = ("B KB MB GB").split()
        else:    
            units = ("B KB MB GB").split()
            
        for size_format in units:    
            if len("%d" % int(nb)) <= 3:
                break
            nb = float(nb) / float(base)
        nb = "%f" % round(nb, 1)    
        nb = nb[:nb.rfind(".") + average] + size_format
        return nb    
        
# 音频和视频文件: audio/mpeg , # 支持大多数音频格式
#              video/webm ,  
#              video/x-msvideo, # 支持大多数视频格式.
#=========Test============
def show_open_window_button(widget):        
    open_dialog = OpenDialog() 
    open_dialog.connect("get-path-name", get_path_name)
    open_dialog.set_filter({"所有文件":".*",
                            "文本文件":".txt",
                            # "音频文件":".mp3|.webm",
                            "音频文件":"audio/mpeg", # 所有音频格式.
                            "视频文件":"video/x-msvideo|.rmvb", 
                            # "视频文件":".rmvb"
                            })        
    open_dialog.init_dir("/")
    open_dialog.set_title("深度影音打开")
    # open_dialog.filter_to_file_type("所有文件")    
    # open_dialog.filter_to_file_type("音频文件")
    open_dialog.filter_to_file_type("视频文件")
    open_dialog.show_open_window()    
    
def get_path_name(OpenDialog, str):    
    print str
    
if __name__ == "__main__":
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    win.connect("destroy", gtk.main_quit)
    win.set_size_request(100, 100)
    btn = gtk.Button()
    btn.connect("clicked", show_open_window_button)
    win.add(btn)        
    win.show_all()
    gtk.main()
    
