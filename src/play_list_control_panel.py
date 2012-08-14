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

from dtk.ui.utils import propagate_expose
from dtk.ui.button import ImageButton
from skin import app_theme
import gtk

class PlayListControlPanel(gtk.Alignment):
    
    def __init__(self):
        # Init.
        gtk.Alignment.__init__(self)
        self.set(1, 0.5, 0, 0)
        self.set_padding(10, 10, 0, 0)
        
        # Init add button.
        self.add_button = ImageButton(
            app_theme.get_pixbuf("bottom_buttons/play_list_add_file.png"),
            app_theme.get_pixbuf("bottom_buttons/play_list_add_file.png"),
            app_theme.get_pixbuf("bottom_buttons/play_list_add_file.png"),
            )
        
        # Init delete button.
        self.delete_button = ImageButton(
            app_theme.get_pixbuf("bottom_buttons/play_list_del_file.png"),
            app_theme.get_pixbuf("bottom_buttons/play_list_del_file.png"),
            app_theme.get_pixbuf("bottom_buttons/play_list_del_file.png"),
            )        
        self.delete_button_frame = gtk.Alignment()        
        self.delete_button_frame.set_padding(0, 0, 10, 10)
        self.delete_button_frame.add(self.delete_button)        
        
        # Init button frame.
        self.hbox = gtk.HBox()
        
        # Connect widgets.
        self.hbox.pack_start(self.add_button, False, False)
        self.hbox.pack_start(self.delete_button_frame, False, False)
        self.add(self.hbox)
        
        # Handle signals.
        self.connect("expose-event", self.draw_background)
        
    def draw_background(self, widget, event):
        cr = widget.window.cairo_create()
        x, y , w, h = widget.allocation
        cr.set_source_rgba(0, 0, 0, 0.5)
        cr.rectangle(x, y - 2, w, h)
        cr.fill()
        
        propagate_expose(widget, event)
        
        return True
        
if __name__ == "__main__":
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    win.connect("destroy", lambda w: gtk.main_quit())
    
    win.add(PlayListControlPanel())
    
    win.show_all()
    gtk.main()
