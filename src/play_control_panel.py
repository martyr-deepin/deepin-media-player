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

from dtk.ui.frame import HorizontalFrame
from dtk.ui.draw import draw_pixbuf
from dtk.ui.utils import propagate_expose
from skin import app_theme
from ImageButton import ImageButton
import gtk


class PlayControlPanel(object):    
    def __init__(self):
        self.input_string = "play_control_panel: " 
        self.hbox_hframe = HorizontalFrame()
        self.hbox = gtk.HBox()
        self.hbox_hframe.add(self.hbox)
        
        
        self.stop_btn = StartButton(app_theme.get_pixbuf("stop_normal.png"),
                                    app_theme.get_pixbuf("stop_hover.png"),
                                    app_theme.get_pixbuf("stop_press.png"),
                                    app_theme.get_pixbuf("stop_normal.png"),
                                    app_theme.get_pixbuf("stop_hover.png"),
                                    app_theme.get_pixbuf("stop_press.png")
                                    )
        self.pre_btn = StartButton(app_theme.get_pixbuf("pre_button_normal.png"),
                                   app_theme.get_pixbuf("pre_button_hover.png"),
                                   app_theme.get_pixbuf("pre_button_press.png"),
                                   app_theme.get_pixbuf("pre_button_normal.png"),
                                   app_theme.get_pixbuf("pre_button_hover.png"),
                                   app_theme.get_pixbuf("pre_button_press.png"))        
        self.start_btn = StartButton()
        
        self.next_btn = StartButton(app_theme.get_pixbuf("next_button_normal.png"),
                                    app_theme.get_pixbuf("next_button_hover.png"),
                                    app_theme.get_pixbuf("next_button_press.png"),
                                    app_theme.get_pixbuf("next_button_normal.png"),
                                    app_theme.get_pixbuf("next_button_hover.png"),
                                    app_theme.get_pixbuf("next_button_press.png"))

        self.open_btn = StartButton(app_theme.get_pixbuf("open_normal.png"),
                                    app_theme.get_pixbuf("open_hover.png"),
                                    app_theme.get_pixbuf("open_press.png"),
                                    app_theme.get_pixbuf("open_normal.png"),
                                    app_theme.get_pixbuf("open_hover.png"),
                                    app_theme.get_pixbuf("open_press.png"))

        self.hbox.pack_start(self.stop_btn, False, False)
        self.hbox.pack_start(self.pre_btn, False, False)
        self.hbox.pack_start(self.start_btn, False, False)
        self.hbox.pack_start(self.next_btn, False, False)
        self.hbox.pack_start(self.open_btn, False, False)
            
        
class StartButton(gtk.Button):
    def __init__(self,
                 start_button_normal=app_theme.get_pixbuf("play_button_normal.png"),
                 start_button_hover=app_theme.get_pixbuf("play_button_hover.png"),
                 start_button_press=app_theme.get_pixbuf("play_button_press.png"),
                 pause_button_normal=app_theme.get_pixbuf("pause_button_normal.png"),
                 pause_button_hover=app_theme.get_pixbuf("pause_button_hover.png"),
                 pause_button_press=app_theme.get_pixbuf("pause_button_press.png")):
        
        gtk.Button.__init__(self)
        self.start_bool = True
        self.start_button_normal = start_button_normal
        self.start_button_hover  = start_button_hover
        self.start_button_press  = start_button_press
        
        self.pause_button_normal = pause_button_normal
        self.pause_button_hover  = pause_button_hover
        self.pause_button_press  = pause_button_press
        
        self.connect("expose-event", self.expose_button)
        self.connect("clicked", self.clicked_button)
        
    def clicked_button(self, widget):
        self.start_bool = not self.start_bool
        self.queue_draw()
        
    def expose_button(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        x,y,w,h = rect.x, rect.y, rect.width, rect.height
        
        if widget.state == gtk.STATE_NORMAL:
            if self.start_bool:                
                image = self.start_button_normal.get_pixbuf()
            else:
                image = self.pause_button_normal.get_pixbuf()                
        elif widget.state == gtk.STATE_PRELIGHT:
            if self.start_bool:
                image = self.start_button_hover.get_pixbuf()
            else:    
                image = self.pause_button_hover.get_pixbuf()
        elif widget.state == gtk.STATE_ACTIVE:
            if self.start_bool:
                image = self.start_button_press.get_pixbuf()
            else:    
                image = self.pause_button_press.get_pixbuf()
            
        pixbuf = image.scale_simple(image.get_width(),
                                    image.get_height(),
                                    gtk.gdk.INTERP_BILINEAR)               
        # Set widget size.
        widget.set_size_request(image.get_width(), image.get_height())
        draw_pixbuf(cr, pixbuf, widget.allocation.x, widget.allocation.y)    
        propagate_expose(widget, event)
        return True


        
 
