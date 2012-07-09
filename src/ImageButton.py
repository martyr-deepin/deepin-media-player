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

# from dtk.ui.draw import *

from dtk.ui.draw import draw_pixbuf
from dtk.ui.utils import propagate_expose
from dtk.ui.cache_pixbuf import CachePixbuf
from skin import app_theme
import gtk


class ImageButton(gtk.Button):
    def __init__(self, 
                 bg_pixbuf=app_theme.get_pixbuf("bottom_buttons/big_button_background.png"),
                 button_pixbuf=app_theme.get_pixbuf("bottom_buttons/play_button.png")):
        gtk.Button.__init__(self)
        self.bg_pixbuf = bg_pixbuf
        self.button_pixbuf = button_pixbuf
        self.connect("expose-event", self.expose_button)
        
        self.cache_pixbuf = CachePixbuf()
        self.bg_cache_pixbuf = CachePixbuf()
        
    def expose_button(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        x,y,w,h = rect.x, rect.y, rect.width, rect.height

        image = self.button_pixbuf.get_pixbuf()
        if widget.state == gtk.STATE_PRELIGHT:
            bg_image = self.bg_pixbuf.get_pixbuf()
            self.bg_cache_pixbuf.scale(bg_image, image.get_width(), image.get_height())
            draw_pixbuf(cr, self.bg_cache_pixbuf.get_cache(), x, y)
            
        widget.set_size_request(image.get_width(), image.get_height())        
        self.cache_pixbuf.scale(image, image.get_width(), image.get_height())
        draw_pixbuf(cr, self.cache_pixbuf.get_cache(), widget.allocation.x, widget.allocation.y)
        
        propagate_expose(widget, event)
        return True
