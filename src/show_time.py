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
from dtk.ui.box import *

from utils import*
from constant import *

class ShowTime(object):
    def __init__(self,
                 #font_color=app_theme.get_color("show_time")):
                 ):     
        #self.font_color = font_color
        self.time_font1 = ""
        self.time_font2 = ""
        self.time_box = EventBox()       
        self.time_box.connect("expose-event", self.draw_play_time)
        
    def set_time_font(self, time_font1, time_font2):    
        self.time_font1 = str(time_font1)
        self.time_font2 = str(time_font2)
        hbox = self.time_box.get_parent()
        hbox.queue_draw()
        
    def draw_play_time(self, widget, event):
        '''Draw media player time.'''
        cr, x, y, w, h = allocation(widget)
        
        draw_font(cr, self.time_font1, 8, "#FFFFFF", 
                  x , y, w, h)
        
        (font1_width, font1_height) = get_content_size(self.time_font1, 8)
        
        draw_font(cr, self.time_font2, 8 , "#000000", 
                  x  + font1_width, y, w, h)
        
        # Propagate expose.
        propagate_expose(widget, event)
        
        return True
    
