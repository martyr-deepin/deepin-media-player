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


class PlayListButton(object):
    def __init__(self):
        self.button = ImageButton()        
    
        
class ImageButton(gtk.Button):
    def __init__(self, 
                 bg_pixbuf=app_theme.get_pixbuf("list_button_background.png"),
                 button_pixbuf=app_theme.get_pixbuf("play_list_button.png")):
        gtk.Button.__init__(self)
        #input_string = "play_list_button" # Input test string.
        self.flags = False
        self.bg_pixbuf = bg_pixbuf
        self.button_pixbuf = button_pixbuf
        
        self.connect("clicked", self.show_play_list)
        self.connect("expose-event", self.expose_button)
        
    def show_play_list(self, widget):    
        self.flags = not self.flags
        # True show background.
        # False hide background.
        
    def expose_button(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        x,y,w,h = rect.x, rect.y, rect.width, rect.height
        
        # Draw background image.
        bg_image = self.bg_pixbuf.get_pixbuf()
        if self.flags:
            bg_border_height = bg_image.get_height()/2 - 5
            # bg_border_width  = 2
            pixbuf = bg_image.scale_simple(bg_image.get_width(),
                                           bg_image.get_height(),
                                           gtk.gdk.INTERP_BILINEAR)
            
            draw_pixbuf(cr, pixbuf, x - 2, y + bg_border_height)
                   
        # Draw foreground image.
        button_image = self.button_pixbuf.get_pixbuf()
        pixbuf = button_image.scale_simple(button_image.get_width(),
                                           button_image.get_height(),
                                           gtk.gdk.INTERP_BILINEAR)        
        
        button_border = button_image.get_height()/2
        draw_pixbuf(cr, pixbuf, x, y + button_border)    
        
        # Set button size.    
        widget.set_size_request(button_image.get_width(), bg_image.get_height())        
        
        propagate_expose(widget, event)
        return True        