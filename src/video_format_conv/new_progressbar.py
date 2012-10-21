#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Hai longqiu.
# 
# Author:     Hai longqiu <qiuhailong@linuxdeepin.com>
# Maintainer: Hai longqiu <qiuhailong@linuxdeepin.com>
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

from skin import app_theme
from dtk.ui.progressbar import ProgressBar

class NewProgressBar(ProgressBar):
    def __init__(self):
        ProgressBar.__init__(self)
        
    def set_text(self, text):
        pass
    
    def set_fraction(self, value):
        if 0.0 <= value <= 1.0:
            print ":value:", value
            # 0.5 * 100 = 50
            # 1.0 * 100 = 100
            # 0.1 * 100 = 10
            self.progress_buffer.progress = int(float(value) * 100.0) 

