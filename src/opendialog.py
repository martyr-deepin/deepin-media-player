#! /usr/bin/env python
# -*- coding: utf-8 -*-

# houshaohui:code->[str_size function, get size, type, mtime, combox]. 
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

from skin import app_theme
from dtk.ui.entry import TextEntry
from dtk.ui.titlebar import Titlebar
from dtk.ui.listview import ListView
from dtk.ui.scrolled_window import ScrolledWindow
from dtk.ui.window import Window
from dtk.ui.button import Button
from dtk.ui.combo import ComboBox

from scrolled_button import ScrolledButton
from openlist import OpenItem
from unicode_to_ascii import UnicodeToAscii
import gio
import gtk
import os
import datetime
import gobject

# 音频和视频文件[file format]: audio/mpeg , # 支持大多数音频格式
#              video/webm ,  
#              video/x-msvideo, # 支持大多数视频格式.    

class FilterItem(object):
    def __init__(self, filter_name):        
        self.filter_name = filter_name
        
    def get_label(self):    
        return self.filter_name           
    

class OpenDialog(Window):
    '''Open dialog window.'''
    __gsignals__ = {
        "get-path-name" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),
    }    
    
    def __init__(self, path_name="~", Filter = {"所有文件":".*"}, width=500, height=350):
        
        Window.__init__(self)
        # Init unicode.
        self.utf = UnicodeToAscii()
        # file type.
        self.filter = Filter # Save Filter.
        self.filter_format = ""
        # init file type.
        self.filter_to_file_type("所有文件")
        
        
        # Set open window -> dialog.
        self.set_modal(True)
        # Set open dialog above.
        # self.set_keep_above(True)
        # Set window center.
        self.set_position(gtk.WIN_POS_MOUSE)
        
        self.set_size_request(width, height)
        self.scrolled_window = ScrolledWindow()
        
        self.list_view = ListView()
        # Add list view events.
        self.list_view.connect("delete-select-items", self.no_delete_file)
        self.list_view.connect("double-click-item", self.open_path_file)
        
        # List view title.
        self.list_view.add_titles(["名称", "大小", "类型", "修改日期"]) 
        self.list_item = []
        self.path_name = ""
        self.path_list = ""
        self.input_path_list = []
        self.input_string = ""
        self.input_path = ""
        self.entry_color_bool = False
        self.tab_path_entry_input = ""
        
        # Init dir(path).
        self.init_dir(path_name)
        self.input_path = self.path_name # Save entry intpu path.
        
        self.scrolled_window.add_child(self.list_view)             
        self.main_vbox = gtk.VBox()
        
        # titlebar.
        self.titlebar = Titlebar(["min", "close"], app_name="打开对话框")
        
        self.main_vbox.pack_start(self.titlebar, False, False)
        
        
        # input path name ->text widget.
        open_window_borde_width = 3
        open_window_borde_height = 2
        
        self.top_hbox = gtk.HBox()
        self.path_entry_frame = gtk.Alignment()
        self.path_entry_frame.set(1, 1, 1, 1)        
        self.path_entry_frame.set_padding(open_window_borde_height, open_window_borde_height, 
                                          open_window_borde_width, open_window_borde_width)
        self.path_entry = TextEntry(self.path_name)
        # entry events.
        # draw_entry_background select_all
        self.path_entry.entry.connect("key-release-event", self.input_path_entry_query)
        self.path_entry.entry.connect("key-press-event", self.input_path_entry)
        
        self.path_entry.set_size(1, 30)
        self.path_entry_frame.add(self.path_entry)
        
        self.return_upper_button_frame = gtk.Alignment()
        self.return_upper_button_frame.set(0, 0.5, 0, 0)
        self.return_upper_button_frame.set_padding(0, 0, 5, 20)
        self.return_upper_button = Button("返回上一层")
        self.return_upper_button.connect("clicked", self.return_upper_button_clicked)
        self.return_upper_button_frame.add(self.return_upper_button)
        # self.new_file_button = Button("创建文件夹")
        
        self.top_hbox.pack_start(self.path_entry_frame)
        self.top_hbox.pack_start(self.return_upper_button_frame, False, False)
        # self.top_hbox.pack_start(self.new_file_button, False, False)
        
        self.main_vbox.pack_start(self.top_hbox, False, False)
        
        # scrolled buton.
        self.scrol_btn = ScrolledButton()
        self.add_widget(self.path_name)
        self.main_vbox.pack_start(self.scrol_btn, False, False)
        
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
        
        # init filter combo_box
        self.combo_box = ComboBox()
        self.combo_box.connect("item-selected", self.filter_selected_cb)
        
        # Open Button.
        self.open_button_frame = gtk.Alignment()
        self.open_button_frame.set_padding(0, 0, 5, 5)
        self.open_button = Button("打开")
        self.open_button.connect("clicked", self.open_button_clicked)            
        self.open_button_frame.add(self.open_button)
        
        # Cancel Button.
        self.cancel_button_frame = gtk.Alignment()
        self.cancel_button = Button("取消")
        # cancel_button event[destroy open window].
        self.cancel_button.connect("clicked", lambda w:self.destroy())
        self.cancel_button_frame.add(self.cancel_button)
        
        self.button_hbox.pack_start(self.combo_box, False, False)        
        self.button_hbox.pack_start(self.open_button_frame)
        self.button_hbox.pack_start(self.cancel_button_frame)
        
        self.main_vbox.pack_start(self.button_hbox_frmae, False, False)
  
        
        # move open window.
        self.add_move_event(self.titlebar.drag_box)
        self.titlebar.close_button.connect("clicked", lambda w:self.destroy())
        self.titlebar.min_button.connect("clicked", lambda w: self.min_window())
        self.window_frame.add(self.main_vbox)
        
    def set_entry_color(self, start, end):    
        self.path_entry.entry.select_start_index = start
        self.path_entry.entry.select_end_index = end
        self.path_entry.entry.queue_draw()
        
    def return_upper_button_clicked(self, widget):
        path_name = ""
        path_name_list = self.path_name[:-1].split("/")
        path_name_list[0] = '/'
        path_name_len = len(path_name_list)                
                    
        for num in range(0, path_name_len-1):                
            path_name += path_name_list[num]
            if "/" != path_name:
                path_name += "/"
            
        self.path_list_show(path_name)
        
    def open_button_clicked(self, widget):
        try:
            item = self.list_view.items[self.list_view.select_rows[0]]
        except:
            item = self.list_view.items[0]
            
        # open file and dir.
        temp_path_name = self.path_name + item.title
        self.emit("get-path-name", temp_path_name)
        self.destroy()
        
        # open file.
        # self.open_path_file(self.list_view, 
        #                     item,
        #                     -1, 0, 0)
            
            
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
        
    def input_path_entry_query(self, widget, event):
        text = self.path_entry.entry.get_text()        
        if self.utf.unicode_bool(text.decode("utf-8")[len(text.decode("utf-8")) - 1]) and not self.entry_color_bool:
            self.input_path_entry(widget, event)
        
    def input_path_entry(self, widget, event):
        '''input path entry.'''    
        try:
            keyval = event.keyval
            keyval = gtk.gdk.keyval_name(keyval)
        except Exception, e:    
            print "input_path_entry:%s" % (e)
            keyval = ""
            
        # print keyval
        
        self.entry_color_bool = False            
        if "Return" == keyval:
            temp_path_name = widget.get_text()
            if os.path.exists(temp_path_name):
                # file.
                if os.path.isfile(temp_path_name):
                    self.open_button_clicked(self.open_button)
                # dir.    
                elif os.path.isdir(temp_path_name):                         
                    if "/" != temp_path_name[-1:]:
                        temp_path_name += "/"                            
                    self.path_list_show(temp_path_name)
            else:    
                print "input_path_entry:%s" % ("Dir or File Error... ...")
        elif keyval in ["Left", "Right", "Shift_L", "Shift_R", "Caps_Lock", "Control_R", "Control_L", "Alt_L", "Alt_R", "/"]: 
            pass
        elif "Tab" == keyval :
            if "" != self.tab_path_entry_input:
                temp_tab_path = self.input_path + self.tab_path_entry_input
                if os.path.isdir(self.input_path + self.tab_path_entry_input):
                    temp_tab_path += "/"
                self.path_entry.set_text(temp_tab_path)                 
        else:# 路径补足
            temp_path_name = widget.get_text()
            
            # print "路径补足：" + str(temp_path_name)
            if os.path.exists(temp_path_name) and "/" == temp_path_name[-1:]:         
                # Get path list.
                if os.path.isdir(temp_path_name):                   
                    if not self.entry_color_bool:
                        self.input_path = temp_path_name # Save input path.        
                    self.input_path_list = os.listdir(temp_path_name)                        
            else:            
                path_list = ""
                temp_path_list = temp_path_name.split("/")
                temp_path_len  = len(temp_path_name.split("/"))
                temp_path_list[0] = "/"
                
                for path_num in range(0, temp_path_len - 1):   
                    path_list += temp_path_list[path_num]
                    
                    if "/" != path_list:
                        path_list += "/"
                    # Save entry input path.    
                    if os.path.exists(path_list):    
                        self.input_path = path_list
                        
                try:                                
                    self.input_path_list = os.listdir(path_list)        
                except Exception, e:    
                    print "input_path_entry:%s" % (e)
                                            
            # input_path   input_string    input_path_list        
            # Save entry input strings.
            if not self.entry_color_bool:
                self.input_string = temp_path_name.split("/")[len(temp_path_name.split("/")) - 1]                        
            
            temp_input_path_list = self.input_path_list            
            input_str_num = 0
            save_temp_input_path_list = []
            # Delete . file.
            for path_list in temp_input_path_list:
                if "." == path_list[0]:
                    continue
                save_temp_input_path_list.append(path_list)
            temp_input_path_list = save_temp_input_path_list    
            
            for input_str in self.input_string.decode('utf-8'):
                save_temp_input_path_list = self.return_cmp_list(input_str, temp_input_path_list, input_str_num)
                temp_input_path_list = save_temp_input_path_list
                if len(temp_input_path_list) < 1:
                    break                
                input_str_num += 1
                               
            if len(temp_input_path_list) == 1: 
                self.entry_color_bool = True
                if "BackSpace" != keyval:
                    
                    self.path_entry.set_text(self.input_path + temp_input_path_list[0])
                    self.tab_path_entry_input = temp_input_path_list[0] # Save .
                    start_index = len(self.path_entry.get_text()) - len(temp_input_path_list[0]) + len(self.input_string)
                    end_index = len(self.path_entry.get_text())                
                    self.set_entry_color(start_index, 
                                         end_index)                    

            else:
                self.tab_path_entry_input = ""        
        return True
        
    def return_cmp_list(self, token, symbol_table, index):              
        temp_symbol_table = []
        # print token
        for symbol in symbol_table:
            temp_symbol = symbol.decode('utf-8')
            temp_symbol_len = len(temp_symbol)
            
            if temp_symbol_len > index:            
                if  temp_symbol[index] == token:
                    temp_symbol_table.append(symbol)                
                
        return temp_symbol_table
    
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
                self.add_widget(temp_path_name)
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
                # Loop show path file ->name, size, type, modify time.
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
        self.combo_box.clear()
        self.filter = filter_dict
        for filter_str in filter_dict.keys():
            self.combo_box.add_item(FilterItem(filter_str))
        self.combo_box.set_top_index(2)    
        
    def filter_to_file_type(self, type_name):
        '''{type_name:.*, type_name1:.txt|.c|.cpp, type_name2:.out... ...}'''
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
        file_type_atrr = ",".join([gio.FILE_ATTRIBUTE_STANDARD_CONTENT_TYPE,
                                   gio.FILE_ATTRIBUTE_STANDARD_TYPE, 
                                   gio.FILE_ATTRIBUTE_STANDARD_NAME,
                                   gio.FILE_ATTRIBUTE_STANDARD_SIZE,
                                   gio.FILE_ATTRIBUTE_STANDARD_DISPLAY_NAME,
                                   gio.FILE_ATTRIBUTE_TIME_MODIFIED,
                                   gio.FILE_ATTRIBUTE_STANDARD_ICON,
                                   ])
        gio_file_info = gio_file.query_info(file_type_atrr)                
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

    def filter_selected_cb(self, widget, item):
        self.filter_to_file_type(item.get_label())
        self.path_list_show(self.path_name)
        
    def add_widget(self, text):
        self.clear_widget()        
        child_list = text[:-1].split("/")
        child_list[0] = "/"
        
        for child in child_list:
            button = Button(str(child))
            button.connect("clicked", self.jmp_dir_btn_clicked, child)
            self.scrol_btn.scrol_hbox.pack_start(button, False, False)
            
        hadju = self.scrol_btn.scrol_win.get_hadjustment()    
        hadju.set_value(hadju.get_upper())
        
        self.scrol_btn.scrol_hbox.show_all()
        
    def jmp_dir_btn_clicked(self, widget, text):    
        path = ""
        for child in self.scrol_btn.scrol_hbox.get_children():
            path += child.label
            if child.label != "/":
                path += "/"
            if child.label == text:
                break
        self.path_list_show(path)    
            
    def clear_widget(self):     
        for child in self.scrol_btn.scrol_hbox.get_children():
            self.scrol_btn.scrol_hbox.remove(child)
        
#=========Test============
def show_open_window_button(widget):
    open_dialog = OpenDialog()
    # Init open_dialog connect event.
    open_dialog.connect("get-path-name", get_path_name)
    open_dialog.set_filter({"所有文件":".*",
                            "文本文件":".txt",
                            # "音频文件":".mp3|.webm",
                            "音频文件":"audio/mpeg", # 所有音频格式.
                            "视频文件":"video/x-msvideo|.rmvb",
                            # "视频文件":".rmvb"
                            })
    # open_dialog.init_dir("/home")
    open_dialog.set_title("深度影音打开")
    # open_dialog.filter_to_file_type("所有文件")    
    # open_dialog.filter_to_file_type("音频文件")
    # open_dialog.filter_to_file_type("视频文件")
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
    
