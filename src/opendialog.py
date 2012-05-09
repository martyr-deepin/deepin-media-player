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

from dtk.ui.application import Application
from dtk.ui.scrolled_window import ScrolledWindow
from dtk.ui.button import Button
from dtk.ui.draw import draw_pixbuf
from dtk.ui.draw import draw_font
# from dtk.ui.utils import propagate_expose
from utils import app_theme
from utils import allocation
import os
import gtk

class OpenDialog(object):
    def __init__ (self, titlebar_name = "打开"):
        self.button_x_offset = 0
        self.button_y_offset = 0
        self.save_path = self.get_home_path()
        self.init_bool = True
        
        # show file or path of image.
        self.vide_pixbuf = app_theme.get_pixbuf("Videos.ico")
        self.music_pixbuf = app_theme.get_pixbuf("Music.ico")
        self.folder_pixbuf = app_theme.get_pixbuf("Folder.ico")
        
        self.open_window = Application("OpenDialog", True)
        # self.open_window.window.connect("destroy", self.open_window.destroy)
        self.open_window.window.set_size_request(500, 400) 
        
        self.open_window.add_titlebar(["close"],
                                      app_theme.get_pixbuf("OrdinaryMode.png"),
                                      titlebar_name, " ", add_separator = True)        
        
        self.scrolled_window_frame = gtk.Alignment()
        self.scrolled_window_frame.set(1, 1, 1, 1)
        self.scrolled_window_frame.set_padding(1, 2, 2, 2)
        self.scrolled_window = ScrolledWindow()
        self.scrolled_window_frame.add(self.scrolled_window)
        self.fixed = gtk.Fixed()

        self.scrolled_window.add_child(self.fixed)    
        
        # main_box add fixed.
        self.open_window.main_box.pack_start(self.scrolled_window_frame, True, True)
        # bottom button.
        self.hbox_frame = gtk.Alignment()
        self.hbox_frame.set(1, 0, 0, 0)
        self.hbox_frame.set_padding(0, 2, 0, 20)
        self.hbox = gtk.HBox()        
        self.hbox_frame.add(self.hbox)
        self.ok_btn = Button(titlebar_name)
        self.cancel_btn = Button("取消")
        self.hbox.pack_start(self.ok_btn, False, False)
        self.hbox.pack_start(self.cancel_btn, False, False)
        # main_box add hbox_frame
        self.open_window.main_box.pack_start(self.hbox_frame, False, False)
        
        self.open_window.window.show_all()        
        self.open_window.window.hide_all()
                
    def fixed_add_button_child(self, text, x, y):
        button = gtk.Button(str(text))
        button.set_size_request(200, -1)
        button.connect("clicked", self.open_file_or_dir, str(text))
        button.connect("expose-event", self.draw_button_bacbground, str(text))
        self.fixed.put(button, int(x), int(y))
        
    def draw_button_bacbground(self, widget, event, text):    
        cr, x, y, w, h = allocation(widget)
        temp_path = self.save_path + "/" + text
        
        music_pixbuf = self.music_pixbuf.get_pixbuf().scale_simple(16, 16, gtk.gdk.INTERP_BILINEAR)
        vide_pixbuf = self.vide_pixbuf.get_pixbuf().scale_simple(16, 16, gtk.gdk.INTERP_BILINEAR)
        folder_pixbuf = self.folder_pixbuf.get_pixbuf().scale_simple(16, 16, gtk.gdk.INTERP_BILINEAR)
        
        if os.path.isdir(temp_path):
            draw_pixbuf(cr, folder_pixbuf, x, y)                            
        if os.path.isfile(temp_path):        
            draw_pixbuf(cr, vide_pixbuf, x, y)                            
            
        draw_font(cr, text, 8, "#000000", 
                  x + 18 , y - 3, w, h)           
        return True
    
    def open_file_or_dir(self, widget, text):          
        temp_path = self.save_path + "/" + text
        
        if os.path.isfile(temp_path):
            # select file open.
            # .pdf.
            # os.system("evince '%s'" % (temp_path))
            os.system("gedit '%s'" % (temp_path))
            print "这是一个文件"
            
        if os.path.isdir(temp_path):
            self.save_path += "/" + text # save path.
            # clear all button.
            for i in self.get_fixed_childs():
                self.fixed.remove(i)                
                
            self.button_y_offset = 0            
            self.show_file_and_dir(temp_path)
        
    def get_fixed_childs(self): 
        return self.fixed.get_children() #return list.   
    
    def show_dialog(self):
        if self.init_bool:
            self.show_file_and_dir(self.save_path)
            self.init_bool = False
            
        self.open_window.window.show_all()
        
    def show_file_and_dir(self, path):
        if os.path.isdir(path): # is dir.
            all_dir_and_file = os.listdir(path)
            for file_name in all_dir_and_file:
                self.fixed_add_button_child(str(file_name), self.button_x_offset, self.button_y_offset)
                self.button_y_offset += 23
        self.open_window.window.show_all()
        
    def get_home_path(self):
        return os.path.expanduser("~")
        
if __name__ == "__main__":    
    open_dialog = OpenDialog()
    open_dialog.show_dialog()
    gtk.main()

