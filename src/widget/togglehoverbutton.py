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
from dtk.ui.utils import propagate_expose
from dtk.ui.cache_pixbuf import CachePixbuf

from skin import app_theme
from tooltip import tooltip_text 
from locales import _

import gtk
import gobject

class ToggleHoverButton(gtk.Button):
    def __init__(self, 
                 connect_function, argv,
                 normal_pixbuf_1 = app_theme.get_pixbuf("top_toolbar/cacel_window_above_normal.png"), 
                 hover_pixbuf_1 = app_theme.get_pixbuf("top_toolbar/cacel_window_above_hover.png"), 
                 normal_pixbuf_2 = app_theme.get_pixbuf("top_toolbar/window_above_normal.png"), 
                 hover_pixbuf_2 = app_theme.get_pixbuf("top_toolbar/window_above_hover.png")):
        gtk.Button.__init__(self)
        self.connect_function = connect_function
        self.argv = argv
        
        self.flags = True
        self.normal_pixbuf_1 = normal_pixbuf_1
        self.normal_pixbuf_2 = normal_pixbuf_2
        self.hover_pixbuf_1 = hover_pixbuf_1
        self.hover_pixbuf_2 = hover_pixbuf_2
        self.add_events(gtk.gdk.ALL_EVENTS_MASK)
        self.togglehoverbutton_event(self)
        self.cache_pixbuf = CachePixbuf()
        
    def togglehoverbutton_event(self, widget):    
        widget.connect("clicked", self.button_flags)
        widget.connect("expose-event", self.draw_button)
        widget.connect("motion-notify-event", self.show_toolbar)
        
    def draw_button(self, widget, event):
        if widget.state == gtk.STATE_NORMAL:
            if self.flags:
                image = self.normal_pixbuf_1.get_pixbuf()
            else:    
                image = self.normal_pixbuf_2.get_pixbuf()
        elif widget.state == gtk.STATE_PRELIGHT:
            if self.flags:
                image = self.hover_pixbuf_1.get_pixbuf()
            else:
                image = self.hover_pixbuf_2.get_pixbuf()
        elif widget.state == gtk.STATE_ACTIVE:
            if self.flags:
                image = self.hover_pixbuf_1.get_pixbuf()
            else:
                image = self.hover_pixbuf_2.get_pixbuf()
                
        widget.set_size_request(image.get_width(), image.get_height())        
        
        self.cache_pixbuf.scale(image, image.get_width(), image.get_height())
        cr = widget.window.cairo_create()
        draw_pixbuf(cr, self.cache_pixbuf.get_cache(), widget.allocation.x, widget.allocation.y)
        propagate_expose(widget, event)
        return True    
        
    def button_flags(self, widget):        
        self.flags = not self.flags
        
    def show_toolbar(self, widget, event):    
        pass
        
gobject.type_register(ToggleHoverButton)


class ToolbarRadioButton(gtk.HBox):
    def __init__(self,
                 connect_function, argv,
                 ##############
                 full_normal_pixbuf = app_theme.get_pixbuf("top_toolbar/full_window_normal.png"),
                 full_hover_pixbuf = app_theme.get_pixbuf("top_toolbar/full_window_hover.png"),                 
                 ##########################
                 window_mode_normal_pixbuf = app_theme.get_pixbuf("top_toolbar/window_mode_normal.png"),
                 window_mode_hover_pixbuf = app_theme.get_pixbuf("top_toolbar/window_mode_hover.png"),
                 ###########################################
                 concise_normal_pixbuf = app_theme.get_pixbuf("top_toolbar/concise_window_normal.png"),
                 concise_hover_pixbuf = app_theme.get_pixbuf("top_toolbar/concise_hover.png")
                 ):
        gtk.HBox.__init__(self)        
        
        self.connect_function = connect_function
        self.argv = argv
        # Init pixbuf.
        self.full_normal_pixbuf = full_normal_pixbuf
        self.full_hover_pixbuf = full_hover_pixbuf
        self.window_mode_normal_pixbuf = window_mode_normal_pixbuf
        self.window_mode_hover_pixbuf = window_mode_hover_pixbuf
        self.concise_normal_pixbuf = concise_normal_pixbuf
        self.concise_hover_pixbuf = concise_hover_pixbuf
        # Init value.
        self.window_state = 0   # 0-> window mode state; 1-> concise state.
        self.full_state = 1   # 0-> quit full state; 1-> full state.
        
        # Init buttons.
        self.full_button_align = gtk.Alignment()
        self.full_button_align.set_padding(0, 0, 5, 5)
        self.full_button = gtk.Button()
        self.full_button_align.add(self.full_button)
        tooltip_text(self.full_button, _("Full Screen"))
        self.full_button.add_events(gtk.gdk.ALL_EVENTS_MASK)
        self.full_button.connect("expose-event",     self.expose_draw_full_button)
        self.full_button.connect("motion-notify-event", self.show_toolbar)
        
        self.win_mode_button_align = gtk.Alignment()
        self.win_mode_button_align.set_padding(0, 0, 5, 5)
        self.win_mode_button = gtk.Button()
        self.win_mode_button_align.add(self.win_mode_button)        
        tooltip_text(self.win_mode_button, _("Normal Mode"))
        self.win_mode_button.add_events(gtk.gdk.ALL_EVENTS_MASK)
        self.win_mode_button.connect("expose-event", self.expose_draw_win_mode_button)
        self.win_mode_button.connect("motion-notify-event", self.show_toolbar)
        
        self.concise_button_align = gtk.Alignment()
        self.concise_button_align.set_padding(0, 0, 5, 5)
        self.concise_button = gtk.Button()
        self.concise_button_align.add(self.concise_button)
        tooltip_text(self.concise_button, _("Compact Mode"))
        self.concise_button.add_events(gtk.gdk.ALL_EVENTS_MASK)
        self.concise_button.connect("expose-event",  self.expose_draw_concise_button)
        self.concise_button.connect("motion-notify-event", self.show_toolbar)
        
        # add buttons.
        self.pack_start(self.full_button_align, False, False)
        self.pack_start(self.win_mode_button_align, False, False)
        self.pack_start(self.concise_button_align, False, False)
        
        self.show_all()
        
    def show_toolbar(self, widget, event):
        pass

    def set_full_state(self, state):
        self.full_state = state

    def set_window_mode(self, state):
        self.window_state = state

    def expose_draw_full_button(self, widget, event):
        cr = widget.window.cairo_create()
        x, y, w, h = widget.allocation
        # widget.state        
        
        pixbuf = self.full_normal_pixbuf
        
        if widget.state == gtk.STATE_NORMAL:
            pixbuf = self.full_normal_pixbuf
        elif widget.state == gtk.STATE_PRELIGHT:
            pixbuf = self.full_hover_pixbuf
        
        image_w = pixbuf.get_pixbuf().get_width()
        image_h = pixbuf.get_pixbuf().get_height()
        widget.set_size_request(image_w, image_h)
        
        if self.full_state:
            pixbuf = self.full_hover_pixbuf
            
        draw_pixbuf(cr, pixbuf.get_pixbuf(), x, y)    
        
        return True
    
    def expose_draw_win_mode_button(self, widget, event):
        cr = widget.window.cairo_create()
        x, y, w, h = widget.allocation
        
        pixbuf = self.window_mode_normal_pixbuf
        
        if widget.state == gtk.STATE_NORMAL:
            pixbuf = self.window_mode_normal_pixbuf
        elif widget.state == gtk.STATE_PRELIGHT:
            pixbuf = self.window_mode_hover_pixbuf
        
        image_w = pixbuf.get_pixbuf().get_width()
        image_h = pixbuf.get_pixbuf().get_height()
        widget.set_size_request(image_w, image_h)
        
        if not self.full_state:
            if not self.window_state:
                pixbuf = self.window_mode_hover_pixbuf
                
        draw_pixbuf(cr, pixbuf.get_pixbuf(), x, y)        
        
        return True
    
    def expose_draw_concise_button(self, widget, event):
        cr = widget.window.cairo_create()
        x, y, w, h = widget.allocation
        
        pixbuf = self.concise_normal_pixbuf
        
        if widget.state == gtk.STATE_NORMAL:
            pixbuf = self.concise_normal_pixbuf
        elif widget.state == gtk.STATE_PRELIGHT:
            pixbuf = self.concise_hover_pixbuf
        
        image_w = pixbuf.get_pixbuf().get_width()
        image_h = pixbuf.get_pixbuf().get_height()
        widget.set_size_request(image_w, image_h)
        
        if not self.full_state:
            if self.window_state:
                pixbuf = self.concise_hover_pixbuf
                
        draw_pixbuf(cr, pixbuf.get_pixbuf(), x, y)        
        
        return True

        
        
        
