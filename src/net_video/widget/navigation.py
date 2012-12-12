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

import gtk
import gobject

from function import draw_text

class Navigation(gtk.HBox):
    __gsignals__ = {
        "select-index-event":(gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_NONE,(gobject.TYPE_INT, gobject.TYPE_STRING,))
        }
    def __init__(self, title_list = []):
        gtk.HBox.__init__(self)
        #
        self.ali_hbox = gtk.Alignment()
        self.hbox = gtk.HBox()
        self.ali_hbox.add(self.hbox)
        self.ali_hbox.set_padding(5, 5, 5, 5)
        # add title.
        widget_index = 1
        for title in title_list:
            temp_nav_title = NavTitle(title)
            temp_nav_title.connect("clicked", self.temp_nav_title_clicked, widget_index, title)
            self.hbox.pack_start(temp_nav_title, False, False)
            widget_index += 1
        #    
        self.pack_start(self.ali_hbox, True, True)
        self.connect("expose-event", self.navigation_expose_event)
        
    def temp_nav_title_clicked(self, widget, widget_index, title):    
        self.emit("select-index-event", widget_index, title)
        
    def navigation_expose_event(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        cr.set_source_rgba(0, 0, 0, 0.7)
        cr.rectangle(rect.x, rect.y, rect.width, rect.height)
        cr.fill()
            
class NavTitle(gtk.Button):
    def __init__(self, text, width=80, height=30):
        gtk.Button.__init__(self)
        # init value.
        self.text = text
        #
        self.set_size_request(width, height)
        self.add_events(gtk.gdk.ALL_EVENTS_MASK)
        self.connect("expose-event", self.navtitle_expose_event)
                
    def navtitle_expose_event(self, widget, event):    
        cr = widget.window.cairo_create()
        rect = widget.allocation
        text_x = rect.x + rect.width/2 
        text_y = rect.y + rect.height/2
        if widget.state == gtk.STATE_NORMAL:
            draw_text(cr, text_x, text_y, self.text, ("#FFFFFF", 0.5))
        elif widget.state == gtk.STATE_PRELIGHT:    
            draw_text(cr, text_x, text_y, self.text, ("#FFFFFF", 1))
        elif widget.state == gtk.STATE_ACTIVE:    
            draw_text(cr, text_x, text_y, self.text, ("#FFFFFF", 1))
            cr.set_dash([1], 1)
            cr.rectangle(rect.x + 1, 
                         rect.y + 1, 
                         rect.width - 2, 
                         rect.height - 2)
            cr.stroke()
        return True
            
gobject.type_register(Navigation)    

