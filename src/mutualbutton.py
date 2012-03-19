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
from dtk.ui.utils import *

from constant import *
from utils import *

class MutualButton(object):
    def __init__(self,
                 button1_pixbuf_1 = app_theme.get_pixbuf("普通模式.png"), 
                 button1_pixbuf_2 = app_theme.get_pixbuf("普通模式1.png"), 
                 button2_pixbuf_1 = app_theme.get_pixbuf("简洁模式.png"), 
                 button2_pixbuf_2 = app_theme.get_pixbuf("简洁模式1.png")):
        
        self.mutual_bool = True
        self.button1 = gtk.Button()
        self.button2 = gtk.Button()
        
        self.button1_pixbuf_1 = button1_pixbuf_1
        self.button1_pixbuf_2 = button1_pixbuf_2
        self.button2_pixbuf_1 = button2_pixbuf_1
        self.button2_pixbuf_2 = button2_pixbuf_2
        
        self.draw_button(self.button1, self.button2)
        
    def draw_button(self, widget1, widget2):
        widget1.connect("expose-event", self.expose_button1)
        widget1.connect("clicked", self.clicked_button1)
        widget2.connect("expose-event", self.expose_button2)
        widget2.connect("clicked", self.clicked_button2)
        
    def clicked_button1(self, widget):
        self.mutual_bool = True
        self.button2.queue_draw()
        
    def clicked_button2(self, widget):
        self.mutual_bool = False
        self.button1.queue_draw()
        
    def expose_button1(self, widget, event):
        if widget.state == gtk.STATE_NORMAL:
            if self.mutual_bool:
                image = self.button1_pixbuf_1.get_pixbuf()
            else:
                image = self.button1_pixbuf_2.get_pixbuf()
                
        if widget.state == gtk.STATE_PRELIGHT:
            image = self.button1_pixbuf_1.get_pixbuf()
            
        if widget.state == gtk.STATE_ACTIVE:
            image = self.button1_pixbuf_1.get_pixbuf()
            
        widget.set_size_request(image.get_width(), image.get_height())        
        pixbuf = image.scale_simple(image.get_width(),
                                    image.get_height(),
                                    gtk.gdk.INTERP_BILINEAR)        
        cr = widget.window.cairo_create()
        draw_pixbuf(cr, pixbuf, widget.allocation.x, widget.allocation.y)    
        propagate_expose(widget, event)
        
        return True
    
    def expose_button2(self, widget, event):
        if widget.state == gtk.STATE_NORMAL:
            if self.mutual_bool:
                image = self.button2_pixbuf_2.get_pixbuf()
            else:
                image = self.button2_pixbuf_1.get_pixbuf()
                
        if widget.state == gtk.STATE_PRELIGHT:
            image = self.button2_pixbuf_1.get_pixbuf()
            
        if widget.state == gtk.STATE_ACTIVE:
            image = self.button2_pixbuf_1.get_pixbuf()
            
        widget.set_size_request(image.get_width(), image.get_height())        
        pixbuf = image.scale_simple(image.get_width(),
                                    image.get_height(),
                                    gtk.gdk.INTERP_BILINEAR)        
        cr = widget.window.cairo_create()
        draw_pixbuf(cr, pixbuf, widget.allocation.x, widget.allocation.y)    
        propagate_expose(widget, event)    
        
        return True
    

        

    


    