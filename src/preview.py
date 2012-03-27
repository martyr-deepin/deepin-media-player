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

from dtk.ui.application import Application
from dtk.ui.mplayer_view import *
from dtk.ui.box import *

from mplayer import *
from constant import *
from utils import *
import gtk

class PreView(object): 
    def __init__(self, path, pos):
        self.path = path # play path.
        self.pos  = pos  # play pos.
        self.i = 0
        self.mp   = None
        
        self.pv = Application("preview_window", True)
        # Set preview window.
        self.pv.window.set_size_request(120,80)
        self.pv.window.set_keep_above(True)
        self.pv.window.add_events(gtk.gdk.ALL_EVENTS_MASK)
        
     
    def create_mplayer(self):            
        self.mp = Mplayer(self.pv.window.window.xid)
        self.mp.connect("get-time-pos", self.get_time_pos)
        self.mp.play(self.path)
        self.mp.fseek(self.pos)    
        self.mp.nomute()
        
    def move_preview(self, x, y):        
        self.pv.window.move(int(x), int(y))
        
    def show_preview(self):        
        self.pv.window.show_all()
        # Init mplayer.
        self.create_mplayer()
        
    def hide_preview(self):
        self.pv.window.destroy()
        
    def get_time_pos(self, mplayer, pos):    
        print pos
        self.i += 1
        self.i = self.i % PREVIEW_TIME_POS
        if not self.i:
            self.mp.bseek(1)
            
class Test(object):
    def __init__(self):
        self.show_bool = False
        self.move_bool = False
        
        self.win = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.win.set_title("影音测试窗口")
        self.win.add_events(gtk.gdk.ALL_EVENTS_MASK)
        self.win.connect("destroy", gtk.main_quit)
        self.win.connect("motion-notify-event", self.motion_notify_event)
        self.win.connect("leave-notify-event", self.leave_notify_event)
        
        self.win.show_all()
        
    def leave_notify_event(self, widget, event):    
        print "鼠标离开了"
        #现实预览窗口
        if self.show_bool:
            print "显示预览窗口"
            print "现实预览窗口了...."
            self.test(event.x, event.y)
            print "鼠标的X坐标:%f" % event.x_root
            self.show_bool = False
            
    def motion_notify_event(self, widget, event):  
        #如果在制定区域为真后,如果移动了,就改为假                            
        if not self.show_bool:    
            try:
                self.preview.hide_preview()
            except:   
                print "Error preview."
        
        if 10 <= event.y <= 20:
            print "鼠标进入,等待一段时间..."
            self.show_bool = True
        else:
            print "鼠标离开了制定范围"
            self.show_bool = False
                                  
    def test(self, x, y):    
        self.preview = PreView("/home/long/视频/1.rmvb", 500)
        self.preview.move_preview(x, y)
        self.preview.show_preview()        
        
if __name__ == "__main__":        
    # pv = PreView("/home/long/视频/1.rmvb", 500)
    # pv.show_preview()
    test = Test()
    #Test()
    gtk.main()
    
