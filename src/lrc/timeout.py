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

import gtk
import gobject

class Timer(object):
    __gsignals__ = {
        "config-changed" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                            (gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING))
        }    
    def __init__(self):
        self.__enable_time_run_bool = False
        self.__delay = 500
        
        gtk.timeout_add(self.__delay, self.print_function)
                
    def print_function(self):        
        print "i love c and linux"    
            
if __name__ == "__main__":
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    btn1 = gtk.Button("改变时间")
    btn2 = gtk.Button("改变时间")
    timer = Timer()
    btn_hbox = gtk.HBox()
    btn_hbox.pack_start(btn1)
    btn_hbox.pack_start(btn2)
    win.add(btn_hbox)
    win.show_all()
    gtk.main()
