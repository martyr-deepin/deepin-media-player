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

from mplayer import *
from dtk.ui.window import *
from dtk.ui.draw import *

import sys

class Preview(object):
    def __init__(self, sou_path, pos, dec_save_path, x, y):
        
        self.pos = pos
        self.preview_win = Window()
        
        self.preview_win.set_keep_above(True)
        self.preview_win.move(x, y)
        self.preview_win.set_size_request(130, 100)

        self.preview_win.connect("focus-out-event", self.quit)
        self.preview_win.show_all()

        self.preview_mp = Mplayer(self.preview_win.window.xid)
        self.preview_mp.play(sou_path)
        self.preview_mp.fseek(self.pos - 2)
        self.preview_mp.nomute()
        self.preview_mp.connect("get-time-pos", self.get_time_pos, sou_path)
        
    def get_time_pos(self, widget, value, path):
        if value > self.pos+10:
            self.preview_mp.quit()
            self.preview_mp.play(path)
            self.preview_mp.fseek(self.pos - 2)
            
    def preview_expose_event(self, widget, event):    
        cr = widget.window.cairo_create()
        rect = widget.allocation
        x,y,w,h = rect.x, rect.y, rect.width, rect.height
        pixbuf = self.preview_pixbuf.scale_simple(200, 100, gtk.gdk.INTERP_BILINEAR)
        draw_pixbuf(cr,pixbuf, x, y)
        return True
    
    def quit(self, widget, event): 
        self.quit_preview()
        
    def quit_preview(self):
        self.preview_mp.quit()
        self.preview_win.destroy()
   
if __name__ == "__main__":        
    Preview("/home/long/音乐/憨豆特工2.rmvb", 4500, "/home/long/", 500, 300)        
    gtk.main()