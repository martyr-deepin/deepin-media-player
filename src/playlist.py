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

from dtk.ui.draw import draw_line
from dtk.ui.utils import container_remove_all
from dtk.ui.listview import ListView
from dtk.ui.listview import get_content_size
from dtk.ui.listview import render_text
from dtk.ui.scrolled_window import ScrolledWindow
from dtk.ui.box import EventBox
# from dtk.ui.frame import VerticalFrame
from dtk.ui.constant import DEFAULT_FONT_SIZE,ALIGN_END
from mplayer import Mplayer    
from utils import app_theme
from utils import allocation
import gtk

# from constant import *
# from utils import *

# import time
import gobject

class PlayList(object):
    
    def __init__(self):
        self.vbox = gtk.VBox()
        self.playlist_vbox = gtk.VBox()
        self.play_list_width = 220
        self.play_list_height = 50
        self.playlist_vbox.set_size_request(self.play_list_width, self.play_list_height)
        self.vbox_vframe = gtk.Alignment()
        self.vbox_vframe.set(0.0, 0.0, 1.0, 1.0)        
        self.vbox_vframe.set_padding(0, 2, 0, 0)
                
        self.scrolled_window = ScrolledWindow()    
        self.list_view = ListView(background_pixbuf=app_theme.get_pixbuf("play_list_bg.jpg"))
        self.item_array = []
        # self.list_view.connect("configure-event", self.init_playlist_path)
        # self.list_view.connect("double-click-item", self.double_click_item)
        self.scrolled_window.add_child(self.list_view)
                
        self.playlist_vbox.pack_start(self.scrolled_window)
        self.vbox_vframe.add(self.playlist_vbox)
        self.vbox.pack_start(self.vbox_vframe, True, True)
        
        self.draw_line_event_box = EventBox()
        self.draw_line_event_box.connect("expose-event", self.draw_lien_expose_event)
        self.vbox.pack_start(self.draw_line_event_box, False, False)
        
        
        
        
    def draw_lien_expose_event(self, widget, event):    
        cr, x, y, w, h = allocation(widget)
        cr.set_source_rgba(1, 1, 1, 0.1) # 10% #FFFFFF
        draw_line(cr, x, y+h-2, x+w, y+h-2)
        return True
        
    # def double_click_item(self, list_view, list_item, colume, offset_x, offset_y):    
    #     pass
    
    # def init_playlist_path(self, widget, event):                     
    #     pass
            
                
    def show_play_list(self):
        if self.vbox.get_children() == [] and self.vbox_vframe != None:
           self.vbox.add(self.vbox_vframe)
           self.vbox.pack_start(self.draw_line_event_box, False, False) 
           
    def hide_play_list(self):
        container_remove_all(self.vbox)    
        
class MediaItem(gobject.GObject):
    '''List item.'''    
    __gsignals__ = {
        "redraw-request" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
    }    
    def __init__(self, title, length):
        '''Init list item.'''
        gobject.GObject.__init__(self)
        self.update(title, length)
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
        
    def update(self, title, length):
        '''Update.'''
        # Update.
        self.title = title
        self.length = length
        
        # Calculate item size.
        self.title_padding_x = 10
        self.title_padding_y = 5
        (self.title_width, self.title_height) = get_content_size(self.title, 4) #DEFAULT_FONT_SIZE
        self.title_width = 100
        
        self.length_padding_x = 10
        self.length_padding_y = 5
        (self.length_width, self.length_height) = get_content_size(self.length, 4) #DEFAULT_FONT_SIZE
        self.length_width = 80
        
        
    def render_title(self, cr, rect):
        '''Render title.'''
        rect.x += self.title_padding_x
        render_text(cr, rect, self.title)
    
    def render_length(self, cr, rect):
        '''Render length.'''
        rect.width -= self.length_padding_x
        render_text(cr, rect, self.length, ALIGN_END)
        
    def get_column_sizes(self):
        '''Get sizes.'''
        return [(self.title_width + self.title_padding_x * 2, 
                 self.title_height + self.title_padding_y * 2),
                (self.length_width + self.length_padding_x * 2, 
                 self.length_height + self.length_padding_y * 2),
                ]    
    
    def get_renders(self):
        '''Get render callbacks.'''
        return [self.render_title,
                self.render_length]
    
    
############################################    
# Test funcation.    #######################
############################################    
def clicked_button(widget, list_view, mp):    
    print list_view
    
def double_click_item(list_view, list_item, colume, offset_x, offset_y):    
    print "* Button press: %s" % (str((list_item.title, list_item.length)))


if __name__ == "__main__":        
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    win.connect("destroy", gtk.main_quit)
    vbox = gtk.VBox()
    
    scrolled_window = ScrolledWindow()
    mp = Mplayer()
    list_item = [MediaItem("你是子厚道的,这个非常好看的电影.rmvb", "120小时30分40秒"),
                 MediaItem("测试二你是的附近的看附近思考的了附近哭附近的思考了附近的死了看法.rmvb", "120小时30分40秒")]
    
    list_view = ListView()
    list_view.add_items(list_item)
        
    # print list_item[0].get_column_sizes()
    # print list_item[1].update(list_item[1].title,"你的")
    # list_item[1].emit_redraw_request()
    
    # list_view.items[0].update(list_view.items[0].title, "改变时间")
    # list_view.items[0].length = "改变时间,离家出家吧..."
    # list_view.items[0].emit_redraw_request()        
    
    list_view.set_size_request(500, 500)
    list_view.connect("double-click-item", double_click_item)
    scrolled_window.add_child(list_view)    
    vbox.pack_start(scrolled_window, True,True)
    btn = gtk.Button()
    btn.connect("clicked", clicked_button, list_view, mp)
    vbox.pack_start(btn, False, False)
    win.add(vbox)
    win.show_all()
    gtk.main()
