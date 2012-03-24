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
                 bg_pixbuf=app_theme.get_pixbuf("progressbar_bg.png"),
                 fg_pixbuf=app_theme.get_pixbuf("progressbar_fg.png"),
                 hight_pixbuf=app_theme.get_pixbuf("进度条高光.png"),
                 drag_pixbuf=app_theme.get_pixbuf("滑块.png")):
        '''Init progressbar.'''
        # Init pixbuf.
        self.bg_pixbuf = bg_pixbuf
        self.fg_pixbuf = fg_pixbuf
        self.hight_pixbuf = hight_pixbuf
        self.drag_pixbuf = drag_pixbuf
        
        self.max = 3000
        self.pos = 0
        self.save_pos = 0

        self.drag_pixbuf_bool = False
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
        self.pb.connect("button-release-event", self.release_progressbar)
        self.pb.connect("motion-notify-event", self.motion_notify_progressbar)
        
    def set_pos(self, pos):
        self.pos = float(pos)
        self.pb.queue_draw()
        
    def press_progressbar(self, widget, event):
        '''Click show point.'''
        self.save_pos = self.pos
        self.pos = (float(int(event.x))/widget.allocation.width*self.max)  # Get pos.
        self.drag_bool = True
        self.drag_pixbuf_bool = True
        if media_player["mp"].state == 1:
            if self.pos >= self.save_pos:
                media_player["mp"].fseek(self.pos - self.save_pos)
            else:
                media_player["mp"].bseek(self.save_pos - self.pos)
                
        widget.queue_draw()        
        
    def release_progressbar(self, widget, event):
        ''''''
        self.drag_bool = False
        
    def motion_notify_progressbar(self, widget, event):
        '''drag progressbar.'''
        if self.drag_bool:
            if 0 <= event.x <= widget.allocation.width:
                self.save_pos = self.pos
                self.pos = (float(event.x)/widget.allocation.width*self.max)
                
                if media_player["mp"].state == 1:
                    if self.pos >= self.save_pos:
                        media_player["mp"].fseek(self.pos - self.save_pos)
                    else:
                        media_player["mp"].bseek(self.save_pos - self.pos)
        else:        
            if 2 <= event.y <= 7:
                self.drag_pixbuf_bool = True
            else:
                self.drag_pixbuf_bool = False
                
        widget.queue_draw()
        
    def expose_progressbar(self, widget, event):
        cr, x, y, w, h = allocation(widget)
        
        bg_pixbuf = self.bg_pixbuf.get_pixbuf()
        fg_pixbuf = self.fg_pixbuf.get_pixbuf()
        hight_pixbuf = self.hight_pixbuf.get_pixbuf()
        drag_pixbuf = self.drag_pixbuf.get_pixbuf()
        
        # Draw bg.
        for i in range(0, w):
            draw_pixbuf(cr, 
                        bg_pixbuf, 
                        x + i, 
                        y + 2)

        # Draw fg.
        pos = int(float(self.pos)/self.max * w)    
        for i in range(0, pos):    
            draw_pixbuf(cr, 
                        fg_pixbuf,
                        x + i, 
                        y + 2)
            
        # Draw hight point.    
        if pos > hight_pixbuf.get_width():    
            draw_pixbuf(cr, 
                        hight_pixbuf, 
                        x + pos - hight_pixbuf.get_width(), 
                        y + 2)
        
        # Draw mouse point.    
        if self.drag_pixbuf_bool:
            draw_pixbuf(cr, 
                        drag_pixbuf, 
                        x + DRAW_PROGRESSBAR_WIDTH_PADDING + pos - drag_pixbuf.get_width()/2, 
                        y)
        return True
       
    def show_progressbar(self):
        if self.hbox.get_children() == [] and self.pb != None:
            self.hbox.pack_start(self.pb)
        
    def hide_progressbar(self):
        container_remove_all(self.hbox) 
             
#gobject.type_register(ProgressBar.hbox)



