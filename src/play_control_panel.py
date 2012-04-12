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

from dtk.ui.frame import *

from utils import *
from constant import *
from ImageButton import *


class PlayControlPanel(object):    
    def __init__(self):
        self.input_string = "play_control_panel: " 
        self.hbox_hframe = HorizontalFrame()
        self.hbox = gtk.HBox()
        self.hbox_hframe.add(self.hbox)
        
        
        self.stop_btn = ImageButton(app_theme.get_pixbuf("big_button_background.png"),
                                    app_theme.get_pixbuf("stop.png"))
        self.pre_btn = ImageButton(app_theme.get_pixbuf("big_button_background.png"),
                                   app_theme.get_pixbuf("pre_button.png"))
        self.start_btn = StartButton()
        self.next_btn = ImageButton(app_theme.get_pixbuf("big_button_background.png"),
                                     app_theme.get_pixbuf("next_button.png"))
        self.open_btn = ImageButton(app_theme.get_pixbuf("big_button_background.png"),
                                    app_theme.get_pixbuf("open.png"))
                
        self.hbox.pack_start(self.stop_btn, False, False)
        self.hbox.pack_start(self.pre_btn, False, False)
        self.hbox.pack_start(self.start_btn, False, False)
        self.hbox.pack_start(self.next_btn, False, False)
        self.hbox.pack_start(self.open_btn, False, False)
            
        
class StartButton(gtk.Button):
    def __init__(self,
                 bg_pixbuf=app_theme.get_pixbuf("big_button_background.png"),
                 button_pixbuf=app_theme.get_pixbuf("play_button.png"),
                 press_pixbuf=app_theme.get_pixbuf("pause_button.png")):
        gtk.Button.__init__(self)
        self.start_bool = True
        self.bg_pixbuf = bg_pixbuf
        self.button_pixbuf = button_pixbuf
        self.press_pixbuf = press_pixbuf
        
        self.connect("expose-event", self.expose_button)
        self.connect("clicked", self.clicked_button)
        
    def clicked_button(self, widget):
        self.start_bool = not self.start_bool
        self.queue_draw()
        
    def expose_button(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        x,y,w,h = rect.x, rect.y, rect.width, rect.height
        
        if self.start_bool:
            image = self.button_pixbuf.get_pixbuf()
        else:
            image = self.press_pixbuf.get_pixbuf()
            
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


        
 
