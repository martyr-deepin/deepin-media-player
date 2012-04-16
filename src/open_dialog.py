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

from dtk.ui.scrolled_window  import ScrolledWindow
from dtk.ui.application import Application
from dtk.ui.draw import *
from utils import *
from mplayer import *

import gtk
import sys

gtk.gdk.threads_init()

class OpenDialog(object):
    def __init__ (self, title_string = " 深度影音-打开", path = get_home_path()):
       self.path = path
       self.show_high = False
       self.fixed_padding = 0
       # Save file name: path.
       self.path_dict = {}       
       self.open_dialog = gtk.Window(gtk.WINDOW_TOPLEVEL)
       #self.open_dialog.set_size_request(500, 400)
       self.image = None
       
       # Set open window.
       

       # # Show file list.
       self.fixed = gtk.Fixed()
    
       self.open_dialog.connect("window-state-event", self.saomiao_dir)
        
       # # Scrolled window init.                       
       self.scrolled_window = ScrolledWindow()
       self.scrolled_window.add_child(self.fixed)
       

       self.open_dialog.add(self.scrolled_window)

       self.open_dialog.show_all()       

               
    def saomiao_dir(self, widget, event):            
        gtk.timeout_add(1, self.time_out, "/home/long/视频")
        #self.time_out(self.path)

        
    def time_out(self, path):
        path_thread = threading.Thread(target=self.path_dir, args=(path,))
        path_thread.start()
        return False
        
    def path_dir(self, path):
        os.chdir(path)
        if os.path.isdir(path):
            for i in os.listdir(path):
                new_path = path + "/" + i
                
                if os.path.isfile(new_path):    #File.
                    #print new_path
                    gtk.gdk.threads_enter()
                    button = gtk.Button(os.path.basename(new_path).strip())
                    button.connect("expose-event", self.draw_background, new_path)
                    button.connect("clicked", self.open_dialog_clicked, new_path)
                    self.fixed.put(button, 0, self.fixed_padding)
                    self.open_dialog.show_all()
                    gtk.gdk.threads_leave()
                    self.fixed_padding += 25                                        
                    
    def open_dialog_clicked(self, widget, new_path):    
        print "I love cna liux " + str(new_path)
        
    def draw_background(self, widget, event, new_path):       
        cr, x, y, w, h = allocation(widget)            
        file1, file2 = os.path.splitext(new_path)
        print file2
        
        self.image = gtk.gdk.pixbuf_new_from_file("/home/long/project/deepin-media-player/src/file.png") 
        
        if file2 in [".mp3",".mp4"]:
            self.image = gtk.gdk.pixbuf_new_from_file("/home/long/project/deepin-media-player/src/mp3.png")
        if file2 in [".avi", ".RMVB", ".rmvb", ".rm", ".mkv"]:    
            self.image = gtk.gdk.pixbuf_new_from_file("/home/long/project/deepin-media-player/src/vide.png")
            
        draw_pixbuf(cr, self.image, x, y)
        draw_font(cr, os.path.basename(new_path), 8, "#000000", x + self.image.get_width(), y, w, h)
        return True
        
        
        
if __name__ == "__main__":        
    OpenDialog()
    gtk.gdk.threads_enter()
    gtk.main()
    gtk.gdk.threads_leave()
        





