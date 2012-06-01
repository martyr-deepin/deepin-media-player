#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Wang Yong
# 
# Author:     Hailong Qiu <qiuhailong@linuxdeepin.com>
# Maintainer: Hailong Qiu <qiuhailong@linuxdeepin.com>
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

class TreeView(gtk.DrawingArea):
    def __init__(self, height = 30):
        gtk.DrawingArea.__init__(self)
        self.set_can_focus(True)
        # Init DrawingArea event.
        self.add_events(gtk.gdk.ALL_EVENTS_MASK)        
        self.connect("button-press-event", self.press_notify_event)
        self.connect("motion-notify-event", self.move_notify_event)
        self.connect("expose-event", self.draw_expose_event)
        self.connect("key-press-event", self.key_press_tree_view)
        # 
        self.height = height # child widget height.
        self.move_height = 0 #
        self.press_height = 0
        self.draw_y_padding = 0
        self.modify_color = False
        
    def key_press_tree_view(self, widget, event):
        keyval = gtk.gdk.keyval_name(event.keyval)        
        # Up Left.
        if "Up" == keyval:
            self.move_height -= self.height
        elif "Down" == keyval:    
            self.move_height += self.height
            
        # Set 0 < self.move_height > self.allocation.height ->
        if self.move_height < 0:    
            self.move_height = 0
        elif self.move_height > self.allocation.height:
            self.move_height = int(self.allocation.height) / self.height * self.height
        
        self.queue_draw()    
        
    def draw_expose_event(self, widget, event):                    
        cr = widget.window.cairo_create()
        rect = widget.allocation        
        x, y, w, h = rect.x, rect.y, rect.width, rect.height
        
        if self.modify_color:
            cr.set_source_rgba(1, 0, 0, 0.3)
            self.draw_y_padding = int(self.press_height) / self.height * self.height
            cr.rectangle(x, y + self.draw_y_padding, w, self.height)
            cr.fill()
                    
        cr.set_source_rgba(0, 0, 1, 0.3)
            
        self.draw_y_padding = int(self.move_height) / self.height * self.height
        cr.rectangle(x, y + self.draw_y_padding, w, self.height)
        cr.fill()
        
        return True
    
    def press_notify_event(self, widget, event):    
        self.modify_color = True
        self.press_height = event.y
        self.queue_draw()
        
    def move_notify_event(self, widget, event):    
        self.move_height = event.y
        self.queue_draw()        

#======== Test ===============        
if __name__ == "__main__":        
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)        
    win.connect("destroy", gtk.main_quit)
    tree_view = TreeView()        

    win.add(tree_view)
    win.show_all()
    gtk.main()

    
