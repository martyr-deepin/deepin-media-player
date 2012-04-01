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

from dtk.ui.listview import *
from dtk.ui.scrolled_window import*

from mplayer import *
from constant import *
from utils import *

import time


class PlayList(object):
    
    def __init__(self):
        self.vbox = gtk.VBox()
        self.scrolled_window = ScrolledWindow(hscrollbar_policy=gtk.POLICY_NEVER)    
        self.list_view = ListView()
        self.item_array = []
        self.list_view.connect("configure-event", self.init_playlist_path)
        self.list_view.connect("double-click-item", self.double_click_item)
        self.scrolled_window.add_child(self.list_view)
        self.vbox.pack_start(self.scrolled_window)
        
    def double_click_item(self, list_view, list_item, colume, offset_x, offset_y):    
        if media_player["mp"].playList != []:
            if media_player["mp"].state == 0:
                media_player["mp"].play(list_item.title)
            else:
                media_player["mp"].quit()
                media_player["mp"].play(list_item.title)
        
    def init_playlist_path(self, widget, event):                     
        if [] == self.item_array:
            media_player["mp"].findCurrentDir("/home/long/视频")
            self.item_array = []
            for i in range(0, media_player["mp"].playListSum):
                self.item_array.append((media_player["mp"].playList[i], ""))
        
            items = map(lambda (title, length): MediaItem(title, length), self.item_array)
            self.list_view.add_items(items)    
            media_player["mp"].savePlayList("/home/long/media_player.dmp")
        
    def show_playlist(self):
        if self.vbox.get_children() == [] and self.scrolled_window != None:
            self.vbox.pack_start(self.scrolled_window)
        
    def hide_playlist(self):
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
        (self.title_width, self.title_height) = get_content_size(self.title, DEFAULT_FONT_SIZE)
        
        self.length_padding_x = 10
        self.length_padding_y = 5
        (self.length_width, self.length_height) = get_content_size(self.length, DEFAULT_FONT_SIZE)
        
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
    mp.findCurrentDir(get_home_path() + "/视频")
    item_array = []
    for i in range(0, mp.playListSum):
        item_array.append((mp.playList[i], ""))
        
    items = map(lambda (title, length): MediaItem(title, length), item_array)
    list_view.add_items(items)    
    
def double_click_item(list_view, list_item, colume, offset_x, offset_y):    
    print "* Button press: %s" % (str((list_item.title, list_item.length)))

    
if __name__ == "__main__":        
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    win.connect("destroy", gtk.main_quit)
    vbox = gtk.VBox()
    
    scrolled_window = ScrolledWindow(hscrollbar_policy=gtk.POLICY_NEVER)
    mp = Mplayer()
    list_view = ListView()
    list_view.connect("double-click-item", double_click_item)
    scrolled_window.add_child(list_view)    
    vbox.pack_start(scrolled_window, True,True)
    btn = gtk.Button()
    btn.connect("clicked", clicked_button, list_view, mp)
    vbox.pack_start(btn, False, False)
    win.add(vbox)
    win.show_all()
    gtk.main()
