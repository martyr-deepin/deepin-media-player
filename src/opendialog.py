#! /usr/bin/env python
# -*- coding: utf-8 -*-

# houshaohui:code->[str_size, size, type, mtime]. 
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
from openlist import OpenItem


import gio
import gtk
import os
import datetime

class OpenDialog(Window):
    def __init__(self, path_name="~", width=500, height=350):
        Window.__init__(self)
        # Set open window -> dialog.
        self.set_modal(True)
        # Set open dialog above.
        self.set_keep_above(True)
        
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
        
        if "~" == path_name:
            self.path_name = os.path.expanduser("~") + "/"
        else:    
            if os.path.exists(path_name): # File path ok.
                self.path_name = path_name
            else: # File Error.
                self.path_name = os.path.expanduser("~") + "/"
        # init open window.        
        self.path_list_show(self.path_name)        
        self.scrolled_window.add_child(self.list_view)     
        
        self.main_vbox = gtk.VBox()
        
        # titlebar .
        self.titlebar = Titlebar(["min", "close"], title="打开对话框")
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
        
        # move open window.
        self.add_move_event(self.titlebar.drag_box)
        self.titlebar.close_button.connect("clicked", lambda w:self.destroy())
        self.titlebar.min_button.connect("clicked", lambda w: self.min_window())
        self.window_frame.add(self.main_vbox)
        self.show_all()
        
    def input_path_entry(self, entry, text):    
        if os.path.exists(text):
            if os.path.isdir(text): # Dir.
                for path in os.listdir(text):
                    if "." != path[0:1]:
                        self.path_entry.select_start_index = 5
                        self.path_entry.entry.select_to_end()
                        print path
                        
            else: # File.
                print "This is File type."
        
    def show_open_window(self):    
        self.show_all()        
        
    def open_path_file(self, list_view, item, column, offset_x, offset_y):    

        temp_path_name = self.path_name + item.title + "/"        
        self.path_list_show(temp_path_name)
        
    def path_list_show(self, temp_path_name):    
        if os.path.isdir(temp_path_name):
            # clear list item.
            self.list_view.clear()
            self.list_item = []
            # file list.
            self.path_name = temp_path_name
            self.path_list = os.listdir(self.path_name)
            if self.path_list:
                for path_str in self.path_list:
                    if "." != path_str[0:1]:
                        pixbuf, size_num, file_type, modify_time  = self.icon_to_pixbuf(self.path_name + path_str, 16)        
                        real_path = os.path.realpath(self.path_name + path_str)
                        if os.path.isdir(real_path):
                            file_size = "%d %s" % (len(os.listdir(real_path)), "项")
                        else:    
                            file_size  = self.str_size(size_num)
                            
                            
                        file_ctime = datetime.datetime.fromtimestamp(os.path.getmtime(real_path)).strftime("%x %A %X")   
                        self.list_item.append(OpenItem(pixbuf, path_str, file_size, file_type, file_ctime))
                    
                self.list_view.add_items(self.list_item)
        
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
        return icon_info.load_icon(), display_size, display_type, display_modify_time
        
    
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
        
#=========Test============
def show_open_window(widget):    
    open_dialog = OpenDialog("/home/") 
    
if __name__ == "__main__":
    open_dialog = OpenDialog("/home/") 
    # win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    # win.set_size_request(100, 100)
    # btn = gtk.Button()
    # btn.connect("clicked", show_open_window)
    # win.add(btn)        
    # win.show_all()
    gtk.main()
    
