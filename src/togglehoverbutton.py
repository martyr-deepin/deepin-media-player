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
from utils import app_theme
import gtk
import gobject

class ToggleHoverButton(gtk.Button):
    def __init__(self, 
                 normal_pixbuf_1 = app_theme.get_pixbuf("Sticky1.png"), 
                 hover_pixbuf_1 = app_theme.get_pixbuf("Sticky.png"), 
                 normal_pixbuf_2 = app_theme.get_pixbuf("noSticky1.png"), 
                 hover_pixbuf_2 = app_theme.get_pixbuf("noSticky.png")):
        gtk.Button.__init__(self)
        self.flags = True
        self.normal_pixbuf_1 = normal_pixbuf_1
        self.normal_pixbuf_2 = normal_pixbuf_2
        self.hover_pixbuf_1 = hover_pixbuf_1
        self.hover_pixbuf_2 = hover_pixbuf_2
        self.add_events(gtk.gdk.ALL_EVENTS_MASK)
        self.togglehoverbutton_event(self)
        
    def togglehoverbutton_event(self, widget):    
        widget.connect("clicked", self.button_flags)
        widget.connect("expose-event", self.draw_button)
        
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
        pixbuf = image.scale_simple(image.get_width(),
                                    image.get_height(),
                                    gtk.gdk.INTERP_BILINEAR)        
        cr = widget.window.cairo_create()
        draw_pixbuf(cr, pixbuf, widget.allocation.x, widget.allocation.y)    
        propagate_expose(widget, event)
        return True    
        
    def button_flags(self, widget):
        self.flags = not self.flags
        
if __name__ == "__main__":    
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)    
    win.connect("destroy", gtk.main_quit)
    button = ToggleHoverButton()
    win.add(button)
    win.show_all()
    gtk.main()

gobject.type_register(ToggleHoverButton)
