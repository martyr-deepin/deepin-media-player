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

from dtk.ui.label import Label

class ShowTime(object):
    
    def __init__(self):     
        self.time_font1 = ""
        self.time_font2 = ""
        self.time_box = Label("", enable_gaussian=True)
        
    def set_time_font(self, time_font2, time_font1):    
        self.time_font1 = str(time_font1) # 右边显示的时间.
        self.time_font2 = str(time_font2) # 左边显示的时间.
        
        self.time_box.set_text(self.time_font2 + self.time_font1)
        
        
        
