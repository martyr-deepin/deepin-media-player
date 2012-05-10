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

from dtk.ui.entry import TextEntry
from dtk.ui.utils import propagate_expose
from dtk.ui.utils import move_window
from dtk.ui.titlebar import Titlebar
from dtk.ui.scrolled_window import ScrolledWindow
from dtk.ui.button import Button
from dtk.ui.draw import draw_pixbuf
from dtk.ui.draw import draw_font
# from dtk.ui.utils import propagate_expose
from unicode_to_ascii import UnicodeToAscii
from utils import app_theme
from utils import allocation
import os
import gtk
import gobject

class OpenDialog(gobject.GObject):
    __gsignals__ = {
        "get-path-name":(gobject.SIGNAL_RUN_LAST,
                         gobject.TYPE_NONE,(gobject.TYPE_STRING,))
        }    
    def __init__ (self, titlebar_name = "打开"):        
        gobject.GObject.__init__(self)
        
        self.unicoe_to_ascii = UnicodeToAscii()
        
        self.button_x_offset = 0
        self.button_y_offset = 0
        self.save_path = self.get_home_path()
        self.save_split_path = self.save_path.split("/")
        
        self.init_bool = True
        self.file_name = ""
        self.play_file_geshi = [".rmvb", ".avi", ".mp3", ".mp4", "wav"]
                
        # show file or path of image.
        self.vide_pixbuf = app_theme.get_pixbuf("Videos.ico")
        self.music_pixbuf = app_theme.get_pixbuf("Music.ico")
        self.folder_pixbuf = app_theme.get_pixbuf("Folder.ico")
        
        self.window_bg_pixbuf = app_theme.get_pixbuf("my_bg2.jpg")
        
        # input text.
        self.text_entry_frame = gtk.Alignment()
        self.text_entry_frame.set(0, 0, 0, 0)
        self.text_entry_frame.set_padding(0, 0, 8, 8)
        self.text_entry = TextEntry()
        self.text_entry.connect("key-release-event", self.text_entry_action)
        self.text_entry_frame.add(self.text_entry)
        self.text_entry.set_size(500, 24)
        
        # up button.
        self.top_hbox_all = gtk.HBox()        
        self.up_btn_frame = gtk.Alignment()                
        self.up_btn_frame.set(0, 0, 0, 0)
        self.up_btn_frame.set_padding(2, 2, 8, 8)        
        self.up_btn = Button("UP")        
        self.up_btn.connect("clicked", self.up_chdir_button)
        self.up_btn_frame.add(self.up_btn)
        
        self.top_hbox = gtk.HBox()
        self.top_hbox_all.pack_start(self.up_btn_frame, False, False)
        self.top_hbox_all.pack_start(self.top_hbox)
        
        # self.open_window = Application("OpenDialog", True)
        self.open_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        
        self.open_window.connect("expose-event", self.draw_window_background)
        self.open_window.connect("destroy", lambda w: self.open_window.destroy())
        self.open_window.set_decorated(False)
        self.title_bar = Titlebar(["close"])
        self.title_bar.close_button.connect("clicked", lambda w:self.open_window.destroy())
        self.title_bar.drag_box.connect('button-press-event', lambda w, e: move_window(w, e, self.open_window))
        
        self.main_vbox = gtk.VBox()
        self.main_vbox.pack_start(self.title_bar, False, False)
        self.open_window.add(self.main_vbox)
        
        window_width = 560
        window_height = 400
        self.open_window.set_size_request(window_width, window_height) 
        
        
        self.scrolled_window_frame = gtk.Alignment()
        self.scrolled_window_frame.set(1, 1, 1, 1)
        self.scrolled_window_frame.set_padding(1, 2, 2, 2)
        self.scrolled_window = ScrolledWindow()
        self.scrolled_window_frame.add(self.scrolled_window)
        self.fixed = gtk.Fixed()

        self.scrolled_window.add_child(self.fixed)    
        
        # bottom button. ok and cancel button.
        self.hbox_frame = gtk.Alignment()
        self.hbox_frame.set(1, 0, 0, 0)
        self.hbox_frame.set_padding(0, 2, 0, 20)
        self.hbox = gtk.HBox()        
        self.hbox_frame.add(self.hbox)
        self.ok_btn = Button(titlebar_name)
        self.cancel_btn = Button("取消")
        self.cancel_btn.connect("clicked", lambda w:self.open_window.destroy())
        self.hbox.pack_start(self.ok_btn, False, False)
        self.hbox.pack_start(self.cancel_btn, False, False)
        
        
        # main_vbox add input text.
        self.main_vbox.pack_start(self.text_entry_frame, False, False)
        self.main_vbox.pack_start(self.top_hbox_all, False, False)
        # main_box add fixed.
        self.main_vbox.pack_start(self.scrolled_window_frame, True, True)
        # main_box add hbox_frame        
        self.main_vbox.pack_start(self.hbox_frame, False, False)
        
        self.open_window.show_all()    
        self.open_window.hide_all()
                
    def text_entry_action(self, widget, event):                        
        str1 = self.text_entry.get_text()    
        if len(str1) > 0:            
        
            list = self.unicoe_to_ascii.get_key_list(self.unicoe_to_ascii.unicode_to_ascii(str1))    
            save_list = []
        
            if list:
                for str2 in list:
                    if self.unicoe_to_ascii.get_strcmp_bool(str1, str2):
                        save_list.append(str2)
        
            # print save_list            
            # print len(str1.decode('utf-8'))
            buquan_font = self.unicoe_to_ascii.get_max_index(save_list, len(str1.decode('utf-8')))            
            if buquan_font:
                self.text_entry.set_text(buquan_font)
                # print buquan_font

    
    def up_chdir_button(self, widget):            
        save_split_text = self.save_path.split("/")
        
        if len(save_split_text) > 2:         
            # print save_split_text
            del_name = save_split_text[len(save_split_text)-1]
            save_split_text.remove(del_name)
            # print save_split_text
            self.save_path = "/".join(save_split_text)

            
        for i in self.get_fixed_childs():
            self.fixed.remove(i)                
                
                
        self.button_y_offset = 0   
        self.show_file_and_dir(self.save_path)
        self.show_split_path_name()
        
            
    def up_chdir_split_button(self, widget, text):    
        
        save_split_text = []
        for i in self.save_split_path:            
            save_split_text.append(i)
            if i == text:
                break
            
        temp_path = "/".join(save_split_text)
        self.save_path = temp_path
        
        for i in self.get_fixed_childs():
                self.fixed.remove(i)                
                
                
        self.button_y_offset = 0   
        self.show_file_and_dir(temp_path)
        self.show_split_path_name()
        
    def fixed_add_button_child(self, text, x, y):
        temp_path = self.save_path + "/" + text
        isfile_bool = False
        
        if os.path.isfile(temp_path):
            # if os.path.splitext(text)
            file1, file2 = os.path.splitext(text)
            if file2.lower() in self.play_file_geshi:
                isfile_bool = True
            
        
        if os.path.isdir(temp_path) or isfile_bool:            
            button = gtk.Button(str(text))
            button.set_size_request(400, -1)
            button.connect("clicked", self.open_file_or_dir, str(text))
            button.connect("expose-event", self.draw_button_bacbground, str(text))                            
            self.fixed.put(button, int(x), int(y))
            self.button_y_offset += 23
            
    def draw_window_background(self, widget, event):        
        cr, x, y, w, h = allocation(widget)
        window_bg_pixbuf = self.window_bg_pixbuf.get_pixbuf().scale_simple(w, h, gtk.gdk.INTERP_BILINEAR)
        draw_pixbuf(cr, window_bg_pixbuf, x, y)       
        propagate_expose(widget, event)
        return True
    
    def draw_button_bacbground(self, widget, event, text):    
        cr, x, y, w, h = allocation(widget)
        temp_path = self.save_path + "/" + text
        
        pixbuf_width = 20
        music_pixbuf = self.music_pixbuf.get_pixbuf().scale_simple(pixbuf_width, pixbuf_width, gtk.gdk.INTERP_BILINEAR)
        vide_pixbuf = self.vide_pixbuf.get_pixbuf().scale_simple(pixbuf_width, pixbuf_width, gtk.gdk.INTERP_BILINEAR)
        folder_pixbuf = self.folder_pixbuf.get_pixbuf().scale_simple(pixbuf_width, pixbuf_width, gtk.gdk.INTERP_BILINEAR)
        
        
        pixbuf_padding = 2
        if os.path.isdir(temp_path):
            draw_pixbuf(cr, folder_pixbuf, x, y + pixbuf_padding)       
            
        if os.path.isfile(temp_path):        
            file1, file2 = os.path.splitext(text)
            if file2.lower() in [".mp3","wav"]:            
                draw_pixbuf(cr, music_pixbuf, x, y + pixbuf_padding)    
            else:    
                draw_pixbuf(cr, vide_pixbuf, x, y + pixbuf_padding)
        draw_font(cr, text, 10, "#000000", 
                  x +18 , y , w, h)
        
        if widget.state == gtk.STATE_PRELIGHT:
            cr.set_source_rgba(1, 0, 0, 0.1)
            cr.rectangle(x, y ,w , h)
            cr.fill()
        return True
    
    def open_file_or_dir(self, widget, text):          
        temp_path = self.save_path + "/" + text
        
        if os.path.isfile(temp_path):
            self.filename = temp_path
            self.open_window.destroy()
            self.emit("get-path-name", self.filename)
            
        if os.path.isdir(temp_path):
            self.save_path += "/" + text # save path.
            # clear all button.
            for i in self.get_fixed_childs():
                self.fixed.remove(i)                
                
            
            self.button_y_offset = 0   
            self.show_file_and_dir(temp_path)
            self.show_split_path_name()
            
    def get_fixed_childs(self):
        return self.fixed.get_children() #return list.
    
    def show_split_path_name(self):    
        for i in self.top_hbox.get_children():
                self.top_hbox.remove(i)
        self.save_split_path = self.save_path.split("/")
        
        for i in self.save_split_path:
            if len(i) > 0:
                button = Button(i)                
                button.connect("clicked", self.up_chdir_split_button, i)
                self.top_hbox.pack_start(button, False, False)                                
        self.top_hbox_all.show_all()
        self.text_entry.set_text(self.save_path)    
        

        self.unicoe_to_ascii.clear_dict()
        temp_list = os.listdir(self.save_path)                        
        for list_strs in temp_list:
            str1 = self.save_path + "/" + list_strs
            self.unicoe_to_ascii.dict_add_strings(str1)
            
        
    def show_dialog(self):
        if self.init_bool:
            self.show_split_path_name()
            self.show_file_and_dir(self.save_path)
            self.init_bool = False
            
        self.open_window.show_all()
        
    def show_file_and_dir(self, path):
        if os.path.isdir(path): # is dir.            
            all_dir_and_file = os.listdir(path)
            # print all_dir_and_file
            for file_name in all_dir_and_file:
                self.fixed_add_button_child(str(file_name), self.button_x_offset, self.button_y_offset)
        self.open_window.show_all()
        
    def get_home_path(self):
        return os.path.expanduser("~")
        
def test_open(OpenDialog, text):
    print text
    
if __name__ == "__main__":
    open_dialog = OpenDialog()
    open_dialog.show_dialog()
    open_dialog.connect("get-path-name", test_open)
    gtk.main()

