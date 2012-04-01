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
from utils import *


class Dialog(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        self.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
        self.set_modal(True)
        self.pixbuf = app_theme.get_pixbuf("bg.png")
        self.main_vbox = gtk.VBox()
        # Set window.
        # self.set_keep_above(True)
        #self.set_decorated(False)
        # self.set_flags(gtk.DOUBLE_BUFFERED)
        # Test add child.
        fixed = gtk.Fixed()
        btn = gtk.Button("确定")
        btn2 = gtk.Button("取消")
        fixed.put(btn, 100, 200)
        fixed.put(btn2, 150, 200)
        
        self.main_vbox.pack_start(fixed)

        # Set signal.
        self.connect("expose-event", self.draw_window_background)
        self.connect("destroy", self.quit)
        self.add(self.main_vbox)        
        self.show_all()
        
    def set_move(self, x, y):    
        self.move(x, y)
        
    def size(self, width, height):    
        self.resize(width, height)
        
    def background(self, path):    
        self.pixbuf = path # Save image path.
        self.queue_draw() # Draw.
        
    def draw_window_background(self, widget, event):    
        cr, x, y, w, h = allocation(widget)
        cr = widget.window.cairo_create()
        # Set pixbuf.
        pixbuf = self.pixbuf.get_pixbuf()
        image = pixbuf.scale_simple(w, h, gtk.gdk.INTERP_BILINEAR)
        # Draw background.
        cr.set_source_pixbuf(image, x, y)
        cr.paint_with_alpha(1)
        
        # Draw top widget.
        if widget.get_child() != None:
            widget.propagate_expose(widget.get_child(), event)

        return True
    
    def quit(self, widget):
        widget.destroy()

def test(widget, win):
    d = Dialog()        
    d.size(300, 400)    
    d.set_move(win.allocation.x, win.allocation.y)
    
if __name__ == "__main__":        
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    btn = gtk.Button()
    win.add(btn)
    win.connect("destroy", gtk.main_quit)
    btn.connect("clicked", test, win)
    win.show_all()
    gtk.main()

