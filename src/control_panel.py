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

from constant import *
from utils import *
from dtk.ui.frame import *
from dtk.ui.draw import *
from volumebutton import *


class ControlPanel(object):
    def __init__(self):
        self.hbox = gtk.HBox()
        self.stop_btn = ImageButton(app_theme.get_pixbuf("大按钮背景.png"),
                                    app_theme.get_pixbuf("停止.png"))
        self.pre_btn = ImageButton(app_theme.get_pixbuf("大按钮背景.png"),
                                   app_theme.get_pixbuf("上一首.png"))
        self.start_btn = StartButton()
        self.next_btn = ImageButton(app_theme.get_pixbuf("大按钮背景.png"),
                                     app_theme.get_pixbuf("下一首.png"))
        self.open_btn = ImageButton(app_theme.get_pixbuf("大按钮背景.png"),
                                    app_theme.get_pixbuf("打开.png"))
        self.play_list_btn = ImageButton(app_theme.get_pixbuf("大按钮背景.png"),
                                         app_theme.get_pixbuf("播放列表.png"))
        
        self.play_hbox = gtk.HBox()
        self.play_hbox.pack_start(self.stop_btn,False)
        self.play_hbox.pack_start(self.pre_btn,False)
        self.play_hbox.pack_start(self.start_btn,False)
        self.play_hbox.pack_start(self.next_btn,False)
        self.play_hbox.pack_start(self.open_btn,False)
        
        self.play_frame = HorizontalFrame(padding=20)
        self.play_frame.add(self.play_hbox)
        
        self.volume = VolumeButton(50)
        self.volume.set_size_request(57,4)
        self.volume_frame = HorizontalFrame(padding=20)
        self.volume_frame.add(self.volume)
        
        self.play_list_hbox = gtk.HBox()
        self.play_list_frame = HorizontalFrame(padding=20)
        self.play_list_frame.add(self.play_list_hbox)
        
        self.show_time_label, self.show_time_hframe = self.show_time_init()
        
        self.hbox.pack_start(self.show_time_hframe, False)
        self.hbox.pack_start(self.play_frame)
        self.hbox.pack_start(self.volume_frame, True)
        self.hbox.pack_start(self.play_list_frame, True)
        
    def show_time_init(self):
        show_time_label = gtk.Label()
        show_time_hframe = HorizontalFrame(7)
        show_time_hframe.add(show_time_label)
        return show_time_label, show_time_hframe
    
    def control_init(self):
        pass
        
class StartButton(gtk.Button):
    def __init__(self,
                 bg_pixbuf=app_theme.get_pixbuf("大按钮背景.png"),
                 button_pixbuf=app_theme.get_pixbuf("播放.png"),
                 press_pixbuf=app_theme.get_pixbuf("暂停.png")):
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
        
    
class ImageButton(gtk.Button):
    def __init__(self, 
                 bg_pixbuf=app_theme.get_pixbuf("大按钮背景.png"),
                 button_pixbuf=app_theme.get_pixbuf("播放.png")):
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
        