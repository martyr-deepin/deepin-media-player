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

from dtk.ui.theme import ui_theme
from dtk.ui.draw import draw_text, draw_vlinear 
from dtk.ui.utils import container_remove_all, color_hex_to_cairo
from dtk.ui.listview import ListView
from dtk.ui.listview import get_content_size
from dtk.ui.scrolled_window import ScrolledWindow
from dtk.ui.constant import DEFAULT_FONT_SIZE,ALIGN_END, ALIGN_START

from skin import app_theme
from tooltip import tooltip_text
from play_list_control_panel import PlayListControlPanel

import gtk
import gobject

LIST_VIEW_FONT_SIZE = 9

class PlayList(gtk.VBox):
    
    def __init__(self):
        # Init.
        gtk.VBox.__init__(self)
        self.item_array = []
        
        # Init play list container.
        self.play_list_vbox = gtk.VBox()
        self.play_list_width = 160 + 25
        self.play_list_vbox.set_size_request(self.play_list_width, -1)
        
        # Init play list view.
        self.scrolled_window = ScrolledWindow(0, 0)    
        self.scrolled_window.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        
        self.list_view = ListView(drag_icon_pixbuf=app_theme.get_pixbuf("playlist/drag_video.png"))
        self.list_view.connect("motion-notify-item", self.motion_mouse_move_event)
        self.list_view.draw_mask = self.draw_mask
        
        # Init play list control panel.
        self.play_list_control_panel = PlayListControlPanel()
        
        # Connect widgets.
        self.pack_start(self.play_list_vbox)
        self.scrolled_window.add_child(self.list_view)
        self.play_list_vbox.pack_start(self.scrolled_window, True, True)
        self.play_list_vbox.pack_start(self.play_list_control_panel, False, False)
        
    def motion_mouse_move_event(self, listview, list_item, colume, offset_x, offset_y):
        try:
            tooltip_text(listview, list_item.title)
        except Exception, e:
            print "motion_mouse_move_event[error]:", e
            
    
    def draw_mask(self, cr, x, y, w, h):    
        cr.set_source_rgb(*color_hex_to_cairo("#1F1F1F"))# 101112
        cr.rectangle(x, y, w, h)
        cr.fill()
        
    def show_play_list(self):
        if self.get_children() == []:
            self.pack_start(self.play_list_vbox)
           
    def hide_play_list(self):
        container_remove_all(self)    
        
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
        self.hover_flags = False
        self.double_flags = False
        self.single_flags = False
        
    def hover(self):    
        self.hover_flags = True
        self.emit_redraw_request()
        
    def un_hover(self):    
        self.hover_flags = False
        self.emit_redraw_request()
        
    def double(self):    
        self.double_flags = not self.double_flags
        self.emit_redraw_request()        
        
    def single(self):    
        self.single_flags = not self.single_flags
        self.emit_redraw_request()
        
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
        (self.title_width , self.title_height) = get_content_size(self.title, LIST_VIEW_FONT_SIZE-1) #DEFAULT_FONT_SIZE
        # self.title_width = 68
        self.title_width = 85
        
        # self.length_padding_x = 60 - 5 + 15
        self.length_padding_x = 50 + 3
        self.length_padding_y = 5
        (self.length_width, self.length_height) = get_content_size(self.length, LIST_VIEW_FONT_SIZE-1) #DEFAULT_FONT_SIZE
        self.length_width = 10
        
        
    def render_title(self, cr, rect, in_selection, in_highlight):
        '''Render title.'''
        rect.x += self.title_padding_x
        color = "#FFFFFF"
        if self.hover_flags and (not in_selection):
            color = "#161616"
        #
        if self.single_flags:  # 单击
            draw_vlinear(cr,
                         0, rect.y, self.list_view.allocation.width, rect.height,
                         ui_theme.get_shadow_color("listview_highlight").get_color_info())
                    
        if self.double_flags: # 双击
            draw_vlinear(cr, 
                         0, rect.y, self.list_view.allocation.width + 10000, rect.height, 
                         ui_theme.get_shadow_color("listview_select").get_color_info())            
        #    
        draw_text(cr, self.title, 
                  rect.x, rect.y, rect.width, rect.height, 
                  LIST_VIEW_FONT_SIZE - 1, color, 
                  alignment=ALIGN_START)
    
    def render_length(self, cr, rect, in_selection, in_highlight):
        '''Render length.'''
        rect.width -= self.length_padding_x
        color = "#FFFFFF"
        if self.hover_flags and (not in_selection):
            color = "#161616"
                    
        if self.single_flags:  # 单击
            draw_vlinear(cr,
                         0, rect.y, self.list_view.allocation.width, rect.height,
                         ui_theme.get_shadow_color("listview_highlight").get_color_info())
                    
        if self.double_flags: # 双击
            draw_vlinear(cr, 
                         0, rect.y, self.list_view.allocation.width + 10000, rect.height, 
                         ui_theme.get_shadow_color("listview_select").get_color_info())            
        #    
        draw_text(cr, self.length, 
                  rect.x, rect.y, rect.width, rect.height, 
                  LIST_VIEW_FONT_SIZE - 1, color, 
                  alignment=ALIGN_END)
        
    def get_column_sizes(self):
        '''Get sizes.'''
        return [(self.title_width + self.title_padding_x * 2 - 3, 
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


