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


from dtk.ui.draw import draw_pixbuf
from dtk.ui.listview import ListView
from dtk.ui.listview import get_content_size
from dtk.ui.listview import render_text
from dtk.ui.scrolled_window import ScrolledWindow
import gtk
import gobject

        
class OpenItem(gobject.GObject):
    '''List item.'''    
    __gsignals__ = {
        "redraw-request" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
    }    
    
    def __init__(self, pixbuf, title, length, type, modify_date):
        '''Init list item.'''
        gobject.GObject.__init__(self)
        self.update(pixbuf, title, length, type, modify_date)
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
        
    def update(self, pixbuf, title, length, type, modify_date):
        '''Update.'''
        # Update.
        self.pixbuf = pixbuf
        self.title = title
        self.length = length
        self.type = type
        self.modify_date = modify_date
        
        
        # Calculate item size.
        self.title_padding_x = 10
        self.title_padding_y = 5
        (self.title_width, self.title_height) = get_content_size(self.title, 4) #DEFAULT_FONT_SIZE
        self.title_width = 90
        
        self.length_padding_x = 10
        self.length_padding_y = 5
        (self.length_width, self.length_height) = get_content_size(self.length, 4) #DEFAULT_FONT_SIZE
        self.length_width = 80
        
        self.type_padding_x = 10
        self.type_padding_y = 5
        (self.type_width, self.type_height) = get_content_size(self.length, 4) #DEFAULT_FONT_SIZE
        self.type_width = 80
        
        self.modify_date_padding_x = 10
        self.modify_date_padding_y = 5
        (self.modify_date_width, self.modify_date_height) = get_content_size(self.length, 4) #DEFAULT_FONT_SIZE
        self.modify_date_width = 80
        
        
    def render_title(self, cr, rect, in_selection, in_highlight):
        '''Render title.'''
        draw_pixbuf(cr, self.pixbuf, rect.x, rect.y)        
        rect.x += self.title_padding_x + self.pixbuf.get_width() 
        rect.x += self.title_padding_x
        rect.width -= self.title_padding_x * 2 
        render_text(cr, rect, self.title)                
        
        
    
    def render_length(self, cr, rect, in_selection, in_highlight):
        '''Render length.'''
        rect.x += self.title_padding_x
        rect.width -= self.title_padding_x * 2
        render_text(cr, rect, self.length)
            
        
    def render_type(self, cr, rect):    
        rect.x += self.title_padding_x
        rect.width -= self.title_padding_x * 2
        render_text(cr, rect, self.type)
        
    
    def render_modify_date(self, cr, rect):
        rect.x += self.title_padding_x
        rect.width -= self.title_padding_x * 2
        render_text(cr, rect, self.modify_date)
        
    def get_column_sizes(self):
        '''Get sizes.'''
        return [(self.title_width + self.title_padding_x * 2, 
                 self.title_height + self.title_padding_y * 2),
                (self.length_width + self.length_padding_x * 2, 
                 self.length_height + self.length_padding_y * 2),
                (self.type_width + self.type_padding_x * 2, 
                 self.type_height + self.type_padding_y * 2),
                # (self.modify_date_width + self.modify_date_padding_x * 2, 
                (200,
                 self.modify_date_height + self.modify_date_padding_y * 2),
                ]    
    
    def get_renders(self):
        '''Get render callbacks.'''
        return [self.render_title,
                self.render_length,
                self.render_type,
                self.render_modify_date]
    
        
############################################    
# Test funcation.    #######################
############################################    
def clicked_button(widget, list_view):    
    print list_view
    
def double_click_item(list_view, list_item, colume, offset_x, offset_y):    
    print "* Button press: %s" % (str((list_item.title, list_item.length)))
