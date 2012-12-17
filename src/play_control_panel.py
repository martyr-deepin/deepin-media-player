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
from dtk.ui.cache_pixbuf import CachePixbuf

from tooltip import tooltip_text
from skin import app_theme
from locales import _
import gtk

class PlayControlPanel(object):    
    def __init__(self):
        self.input_string = "play_control_panel: " 
        self.hbox_hframe = HorizontalFrame()
        self.hbox = gtk.HBox()
        self.hbox_hframe.add(self.hbox)
        
        
        self.stop_button = StartButton(app_theme.get_pixbuf("bottom_buttons/stop_normal.png"),
                                    app_theme.get_pixbuf("bottom_buttons/stop_hover.png"),
                                    app_theme.get_pixbuf("bottom_buttons/stop_press.png"),
                                    app_theme.get_pixbuf("bottom_buttons/stop_normal.png"),
                                    app_theme.get_pixbuf("bottom_buttons/stop_hover.png"),
                                    app_theme.get_pixbuf("bottom_buttons/stop_press.png")
                                    )
        tooltip_text(self.stop_button, _("Stop"))        
        
        self.pre_button = StartButton(app_theme.get_pixbuf("bottom_buttons/pre_button_normal.png"),
                                   app_theme.get_pixbuf("bottom_buttons/pre_button_hover.png"),
                                   app_theme.get_pixbuf("bottom_buttons/pre_button_press.png"),
                                   app_theme.get_pixbuf("bottom_buttons/pre_button_normal.png"),
                                   app_theme.get_pixbuf("bottom_buttons/pre_button_hover.png"),
                                   app_theme.get_pixbuf("bottom_buttons/pre_button_press.png"))        
        tooltip_text(self.pre_button, _("Previous"))
        
        self.start_button = StartButton(image_y_padding=1)
        tooltip_text(self.start_button, _("Play"))
        
        self.next_button = StartButton(app_theme.get_pixbuf("bottom_buttons/next_button_normal.png"),
                                    app_theme.get_pixbuf("bottom_buttons/next_button_hover.png"),
                                    app_theme.get_pixbuf("bottom_buttons/next_button_press.png"),
                                    app_theme.get_pixbuf("bottom_buttons/next_button_normal.png"),
                                    app_theme.get_pixbuf("bottom_buttons/next_button_hover.png"),
                                    app_theme.get_pixbuf("bottom_buttons/next_button_press.png"))
        tooltip_text(self.next_button, _("Next"))
        
        self.open_button = StartButton(app_theme.get_pixbuf("bottom_buttons/open_normal.png"),
                                    app_theme.get_pixbuf("bottom_buttons/open_hover.png"),
                                    app_theme.get_pixbuf("bottom_buttons/open_press.png"),
                                    app_theme.get_pixbuf("bottom_buttons/open_normal.png"),
                                    app_theme.get_pixbuf("bottom_buttons/open_hover.png"),
                                    app_theme.get_pixbuf("bottom_buttons/open_press.png"))
        tooltip_text(self.open_button, _("Open File"))

        self.hbox.pack_start(self.stop_button, False, False)
        self.hbox.pack_start(self.pre_button, False, False)
        self.hbox.pack_start(self.start_button, False, False)
        self.hbox.pack_start(self.next_button, False, False)
        self.hbox.pack_start(self.open_button, False, False)
            
        
class StartButton(gtk.Button):
    def __init__(self,                 
                 start_button_normal=app_theme.get_pixbuf("bottom_buttons/play_button_normal.png"),
                 start_button_hover=app_theme.get_pixbuf("bottom_buttons/play_button_hover.png"),
                 start_button_press=app_theme.get_pixbuf("bottom_buttons/play_button_press.png"),
                 pause_button_normal=app_theme.get_pixbuf("bottom_buttons/pause_button_normal.png"),
                 pause_button_hover=app_theme.get_pixbuf("bottom_buttons/pause_button_hover.png"),
                 pause_button_press=app_theme.get_pixbuf("bottom_buttons/pause_button_press.png"),
                 image_y_padding=-2):
        
        gtk.Button.__init__(self)
        self.image_y_padding = image_y_padding
        self.start_bool = True
        self.stop_bool = False
        self.start_button_normal = start_button_normal
        self.start_button_hover = start_button_hover
        self.start_button_press = start_button_press
        
        self.pause_button_normal = pause_button_normal
        self.pause_button_hover = pause_button_hover
        self.pause_button_press = pause_button_press
        
        self.connect("expose-event", self.expose_button)
        self.connect("clicked", self.clicked_button)
        
        self.cache_pixbuf = CachePixbuf()
        
    def clicked_button(self, widget):
        self.set_start_bool(not self.start_bool)
                
    def set_start_bool(self, start_bool):    
        if not self.stop_bool:
            self.start_bool = start_bool            
            self.queue_draw()
            
    def set_stop_bool(self, stop_bool):
        self.stop_bool = stop_bool
            
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

        widget.set_size_request(image.get_width(), image.get_height())
        self.cache_pixbuf.scale(image, image.get_width(), image.get_height())        
        draw_pixbuf(cr, self.cache_pixbuf.get_cache(), widget.allocation.x, widget.allocation.y - self.image_y_padding)
        
        # Set widget size.
        propagate_expose(widget, event)
        return True


        
 
