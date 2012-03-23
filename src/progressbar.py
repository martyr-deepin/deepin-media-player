#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Wang Yong
# 
# Author:     Wang Yong <lazycat.manatee@gmail.com>
# Maintainer: Wang Yong <lazycat.manatee@gmail.com>
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
import cairo
from dtk.ui.utils import *
from dtk.ui.draw import *

from utils import *
from constant import *

class ProgressBar(object):
    '''Media player progressbar.'''
	
    def __init__(self,
                 max = 100,
                 bg_color=app_theme.get_alpha_color("progressbar_bg"),
                 fg_color=app_theme.get_alpha_color("progressbar_fg"),
                 hight_pixbuf=app_theme.get_pixbuf("进度条高光.png"),
                 drag_pixbuf=app_theme.get_pixbuf("滑块.png")):
        '''Init progressbar.'''
        # Init.

        
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.hight_pixbuf = hight_pixbuf
        self.drag_pixbuf = drag_pixbuf
        
        self.max = max
        self.pos = 0
        self.drag_bool = False
        
        self.hbox = gtk.HBox()
        self.pb = gtk.Button()
        # Set progressbar size.
        self.pb.set_size_request(-1, 9)
        self.hbox.pack_start(self.pb)
        
        # Init progressbar signal.
        self.pb.add_events(gtk.gdk.ALL_EVENTS_MASK)
        # Draw progressbar.
        self.pb.connect("expose-event", self.expose_progressbar)
        # progressbar click signal.
        self.pb.connect("button-press-event", self.press_progressbar)
        
    def press_progressbar(self, widget, event):
        '''Click show point'''
        pass
    
    def expose_progressbar(self, widget, event):
        cr, x, y, w, h = allocation(widget)
        
        hight_pixbuf = self.hight_pixbuf
        drag_pixbuf = self.drag_pixbuf
        
        # Draw bg.
        cr.set_line_width(DRAW_PROGRESSBAR_LINE_WIDTH_PADDING)
        cr.set_source_rgba(*alpha_color_hex_to_cairo(self.bg_color.get_color_info()))
        for i in range(0, w+1):
            cr.move_to(x , 
                       y + 1 + h/2)
            cr.line_to(x + i , 
                       y + 1 + h/2)
            cr.stroke()
            
        # Draw fg.
        cr.set_source_rgba(*alpha_color_hex_to_cairo(self.fg_color.get_color_info()))
        self.pos = 50
        for i in range(0, self.pos):    
            cr.move_to(x , 
                       y + 1 + h/2)
            cr.line_to(x , 
                       y + 1 + h/2)
            cr.stroke()
            
        # Draw hight point.    
        image = hight_pixbuf.get_pixbuf()            
        draw_pixbuf(cr, 
                    image, 
                    x + self.pos - image.get_width(), 
                    y + 2)
        # Draw mouse point.    
        # Test drag point.
        self.drag_bool = True
        if self.drag_bool:
            image = drag_pixbuf.get_pixbuf()
            draw_pixbuf(cr, 
                    image, 
                    x + DRAW_PROGRESSBAR_WIDTH_PADDING + self.pos - image.get_width(), 
                    y + 1)
        
        
        return True
       
    def show_progressbar(self):
        if self.hbox.get_children() == [] and self.pb != None:
            self.hbox.pack_start(self.pb)
        
    def hide_progressbar(self):
        container_remove_all(self.hbox) 
             
#gobject.type_register(ProgressBar.hbox)



