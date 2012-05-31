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

from dtk.ui.scrolled_window import ScrolledWindow
from skin import app_theme
from dtk.ui.window import Window
from dtk.ui.entry import TextEntry
from dtk.ui.button import Button

from dtk.ui.listview import ListView
from dtk.ui.listview import get_content_size
from dtk.ui.listview import render_text


import gtk
import gobject

class ComBox(gtk.Alignment):
    __gsignals__ = {
        "get-path-name" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (str,)),
    }    
    def __init__(self):
        gtk.Alignment.__init__(self)                
                            
        self.items = []        
        self.text_string = ""
        self.height = 30
        
        self.hbox = gtk.HBox()
        self.start_btn_frame = gtk.Alignment()
        self.start_btn_frame.set(1, 1, 1, 1)
        self.start_btn = Button("弹出")
        self.start_btn.connect("button-press-event", self.show_pop_win_press)
        self.start_btn_frame.add(self.start_btn)
        
        self.text_frame = gtk.Alignment()
        self.text_frame.set(1, 1, 1, 1)
        self.text = TextEntry()
        self.text.connect("key-release-event", self.set_text_string)
        self.text.set_size(100, 25)
        self.text_frame.add(self.text)
        
        self.hbox.pack_start(self.text_frame, True, True)
        self.hbox.pack_start(self.start_btn_frame)         
        
        self.add(self.hbox)
        
        # self.pop_win = gtk.Window(gtk.WINDOW_POPUP)
        self.pop_win = Window(gtk.WINDOW_POPUP)
        self.pop_win.connect("focus-out-event", lambda w,e:self.pop_win.hide_all())
        self.pop_win.set_keep_above(True) 
        self.pop_win.set_size_request(1, 30)
                        
        # self.list_vbox = gtk.VBox()
        self.list_view = ListView()
        # list view events.
        self.list_view.connect("double-click-item", self.text_show_combox_string)
        self.pop_win_scrolled_window = ScrolledWindow()                
        self.pop_win_scrolled_window.add_child(self.list_view)        
        self.pop_win.window_frame.add(self.pop_win_scrolled_window)
        # self.pop_win.add((self.pop_win_scrolled_window))
        self.pop_win.show_all()
        self.pop_win.hide_all()        
        
    def set_text_string(self, widget, event):    
        self.text.set_text(self.text_string)
        
    def text_show_combox_string(self, listview, item, colume, offset_x, offset_y):    
        self.emit("get-path-name", item.title)
        self.text_string = item.title
        self.text.set_text(item.title)
        self.hide_pop_win()
        
    def hide_pop_win(self):    
        self.pop_win.hide_all()
        
    def show_pop_win(self):    
        self.pop_win.show_all()
        
    def set_size_pop_win(self, w, h):    
        self.pop_win.resize(w, h)
        
    def move_pop_win(self, x, y):    
        self.pop_win.move(x, y)
        
    def show_pop_win_press(self, widget, event):    
        # Set popup window size.
        self.set_size_pop_win(self.text.entry.allocation.width + self.start_btn.allocation.width + 8,
                              self.height)
    
        # Get parent window x, y position.
        x_root, y_root = widget.get_parent_window().get_root_origin()
        # Get text widget x, y position.
        x, y, w, h = self.text.entry.get_allocation()
        x1, y1, w1, h1 = widget.get_allocation()
        
        # Move popup window.
        self.move_pop_win(x_root + x - 4,
                          y_root + y + h1 + h)
        # Show popup window.
        self.show_pop_win()
                
    def add_items(self, items_list):        
        self.clear_items()
        combox_item = []
        for item in items_list:
            self.items.append(item)
            combox_item.append(ComBoxItem(item))
            self.height += 10
            
        self.list_view.add_items(combox_item)    
        if self.height > 120:    
            self.height = 120
            
    def clear_items(self):    
        self.height = 8
        self.items = []
        
    def insert_items(self, items_list):    
        for item in items_list:
            self.items.append(item)            
                                               
class ComBoxItem(gobject.GObject):
    '''List item.'''    
    __gsignals__ = {
        "redraw-request" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
    }    
    def __init__(self, title):
        '''Init list item.'''
        gobject.GObject.__init__(self)
        self.update(title)
        self.index = None
        
    def set_index(self, index):
        '''Update index.'''
        self.index = index
        
    def get_index(self):
        '''Get index.'''
        return self.index
        
    def emit_redraw_request(self):
        '''Emit redraw-request signal.'''
        self.emit("redraw-request")
        
    def update(self, title):
        '''Update.'''
        # Update.
        self.title = title
        
        # Calculate item size.
        self.title_padding_x = 10
        self.title_padding_y = 5
        (self.title_width, self.title_height) = get_content_size(self.title, 4) #DEFAULT_FONT_SIZE
        self.title_width = 90
        
        
    def render_title(self, cr, rect):
        '''Render title.'''
        rect.x += self.title_padding_x
        render_text(cr, rect, self.title)
    
    def get_column_sizes(self):
        '''Get sizes.'''
        return [(self.title_width + self.title_padding_x * 2, 
                 self.title_height + self.title_padding_y * 2)                ]    
    
    def get_renders(self):
        '''Get render callbacks.'''
        return [self.render_title]
            
            
def hide_all_win(widget, event):            
    com_box.hide_pop_win()
            
def get_path_name(combox, text):    
    print text
    
if __name__ == "__main__":        
    
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    fixed = gtk.Fixed()
    com_box = ComBox()
    com_box.connect("get-path-name", get_path_name)
    com_box.add_items(["初中", "高中", "大学", "社会大学", "你是知道的",
                       "你是子厚道的"])
    
    win.connect("destroy", gtk.main_quit)
    win.connect("configure-event", hide_all_win)
    win.set_size_request(500, 500)
    # fixed.put(com_box, 150, 150)
    # win.add(fixed)
    win.add(com_box)
    win.show_all()  
    gtk.main()
