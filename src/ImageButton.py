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

from dtk.ui.draw import *

from utils import *


class ImageButton(gtk.Button):
    def __init__(self, 
                 bg_pixbuf=app_theme.get_pixbuf("big_button_background.png"),
                 button_pixbuf=app_theme.get_pixbuf("play_button.png")):
        gtk.Button.__init__(self)
        self.bg_pixbuf = bg_pixbuf
        self.button_pixbuf = button_pixbuf
        self.connect("expose-event", self.expose_button)
        
    def expose_button(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        x,y,w,h = rect.x, rect.y, rect.width, rect.height
        

        image = self.button_pixbuf.get_pixbuf()
        if widget.state == gtk.STATE_PRELIGHT:
            bg_image = self.bg_pixbuf.get_pixbuf()
            pixbuf = bg_image.scale_simple(image.get_width(),
                                           image.get_height(),
                                           gtk.gdk.INTERP_BILINEAR)
            
            draw_pixbuf(cr, pixbuf, x, y)
            
        widget.set_size_request(image.get_width(), image.get_height())        
        pixbuf = image.scale_simple(image.get_width(),
                                    image.get_height(),
                                    gtk.gdk.INTERP_BILINEAR)        
        
        draw_pixbuf(cr, pixbuf, widget.allocation.x, widget.allocation.y)    
        propagate_expose(widget, event)
        return True