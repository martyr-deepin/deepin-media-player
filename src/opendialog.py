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
from utils import app_theme
import gtk

class OpenDialog(object):
    def __init__ (self, titlebar_name = "打开"):
        self.open_window = Application("OpenDialog", True)
        self.open_window.window.connect("destroy", self.open_window.destroy)
        self.open_window.window.set_size_request(500, 400) 
        
        self.open_window.add_titlebar(["close"],
                                      app_theme.get_pixbuf("OrdinaryMode.png"),
                                      titlebar_name, " ", add_separator = True)        
        
        self.hbox = gtk.HBox()
        self.open_window.main_box.pack_start(self.hbox)
        self.open_window.window.show_all()        
        self.open_window.window.hide_all()
        
    def add_fixed_child(self):    
        self.hbox.pack_start(gtk.Fixed())
        
    def get_childs(self):    
        return self.hbox.get_children()

    def show_dialog(self):    
        self.open_window.window.show_all()
        
        
open_dialog = OpenDialog()        
open_dialog.add_fixed_child()

open_dialog.show_dialog()
childs = open_dialog.get_childs()
print childs[0]
childs[0].put(gtk.Button("告诉我"), 30, 40)
open_dialog.show_dialog()
gtk.main()

