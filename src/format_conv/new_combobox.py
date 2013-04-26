#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Hai longqiu.
# 
# Author:     Hai longqiu <qiuhailong@linuxdeepin.com>
# Maintainer: Hai longqiu <qiuhailong@linuxdeepin.com>
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

from dtk.ui.combo import ComboBox

import gtk
import gobject

class NewComboBox(ComboBox):
    __gsignals__ = {
        "changed" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING,))
    }
    def __init__(self, fixed_width, droplist_height=80):        # fixed_width=
        ComboBox.__init__(self, droplist_height=droplist_height, fixed_width=fixed_width)
        self.connect("item-selected", self.emit_connect_function)
        self.fixed_width = fixed_width
        self._items = []
        self.set_items = self.add_items

    def emit_connect_function(self, combo, item_content, item_value, item_index):
        # print "item_value:", item_value, item_index
        self.emit("changed", item_value)        
        
    def set_active(self, index):
        self.set_select_index(index)        
        self.emit("changed", self.label.get_text())
        
    def remove_text(self, index):
        self._items.remove(self._items[index])
        self.add_items(self._items, 0)
        
    def prepend_text(self, text):
        temp_items = []
        temp_items.append([text, text])
        for item in self.combo_list.items:
            temp_items.append([item.title, item.item_value])
        self.add_items(temp_items, 0)
        
    def get_active_text(self):
        return self.label.get_text()
    
    def get_active(self):
        return self.get_select_index()
    
    def append_text(self, text):
        self._items.append([text, text])
        self.add_items(self._items, 0)

    def clear_items(self):    
        self._items = []
        
class Test(object):
    def __init__(self):
        def new_combo_box_changed(widget):
            print "触发了信号... ..."
            
        self.win = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.win.connect("destroy", lambda w : gtk.main_quit())                
        new_combo_box = NewComboBox()
        new_combo_box.connect("changed", new_combo_box_changed)
        combo_vbox = gtk.VBox()
        combo_vbox.add(new_combo_box)
        self.win.add(combo_vbox)
        self.win.show_all()
        
        new_combo_box.append_text("明天")
        new_combo_box.append_text("明天2")
        new_combo_box.append_text("明天3")
        new_combo_box.prepend_text("后天")
        
    def get_name_btn_clicked(self, widget):
        print "uri:", self.FileChoose.get_uri()
        print "filename:", self.FileChoose.get_filename()
        
if __name__ == "__main__":
    Test()
    gtk.main()
    



