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
        self.time_font1 = "Deepin media player"
        self.time_font2 = ""
        self.time_box = EventBox()       
        self.time_box.connect("expose-event", self.draw_play_time)
        
    def set_time_font(self, time_font1, time_font2):    
        self.time_font1 = str(time_font1)
        self.time_font2 = str(time_font2)
        self.time_box.queue_draw()
        
    def draw_play_time(self, widget, event):
        '''Draw media player time.'''
        cr, x, y, w, h = allocation(widget)
        cr.set_source_rgb(1, 1, 1)
        cr.select_font_face("Purisa",
                            cairo.FONT_SLANT_NORMAL,
                            cairo.FONT_WEIGHT_BOLD)
        
        cr.set_font_size(12)
        # Get first show time font width.
        font_width = cr.text_extents(self.time_font1)
        # first show time.
        cr.move_to(20, y + h/2)
        cr.show_text(self.time_font1)
        #draw_font(cr, self.time_font,12, self.font_color.get_color(),x,y,w,h)
        
        # Second show time.
        cr.set_source_rgb(0.6, 0.6, 0.6)
        cr.move_to(x + 20 + font_width[2], y + h/2)
        cr.show_text(self.time_font2)        
        return True
    
