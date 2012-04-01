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
from dtk.ui.panel import *
from dtk.ui.utils import *

from utils import *
from constant import *

from progressbar import *
from show_time import *
from play_control_panel import *
from volume_button import *


class ToolBar2(object):            
    def __init__(self):
        self.panel = Panel(APP_WIDTH - 4, PANEL_HEIGHT)
        self.vbox = gtk.VBox()
        self.progressbar = ProgressBar()        
        #self.hbox = gtk.HBox()
        self.vbox.pack_start(self.progressbar.hbox, False, False)
        
        #self.vbox.pack_start(self.hbox, False, False)
        self.panel.add(self.vbox)        
        
    def show_toolbar2(self):    
        self.panel.show_all()
        
    def hide_toolbar2(self):    
        self.panel.hide_all()
        
        
if __name__ == "__main__":    
    tb = ToolBar2()
    tb.show_all()
    gtk.main()
