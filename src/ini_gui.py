#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Wang Yong
# 
# Author:     Hailong Qiu <qiuhailong@linuxdeepin.com>
# Maintainer: Hailong Qiu <qiuhailong@linuxdeepin.com>
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


from dtk.ui.draw import draw_pixbuf
from ini import INI
from tabControl import TabPage
from tabControl import Button
from utils import app_theme
import gtk
import os


class IniGui(gtk.Window):    
    def __init__ (self):
        gtk.Window.__init__(self)
        
        self.window_bg_pixbuf = app_theme.get_pixbuf("bg.png")
        
        # Init ini.
        self.ini = INI(os.path.expanduser("~") + "/.config/deepin-media-player/config.ini")        
        # self.ini.connect("Send-Error", self.error_messagebox)        
        self.ini.start()
                                
        self.set_size_request(570, 400)
        self.set_title("配置界面")
        self.set_modal(True)
        self.add_events(gtk.gdk.ALL_EVENTS_MASK)
        
        self.connect("expose-event", self.draw_background)
        self.connect("destroy", gtk.main_quit)        
        
        # TabPage.
        self.tabpage = TabPage()
        self.tabpage.create_title("文件播放")
        self.tabpage.create_title("系统设置")
        self.tabpage.create_title("热键/鼠标")
        self.tabpage.create_title("高清加速")
        self.tabpage.create_title("字幕设置")
        self.tabpage.create_title("视频截图")
        self.tabpage.create_title("声音设置")
        self.tabpage.create_title("画面设置")
        self.tabpage.create_title("其它设置")
        self.main_vbox = gtk.VBox()
        
        # Button.
        self.buton_hbox_frame = gtk.Alignment()
        self.buton_hbox_frame.set(1, 0.5, 0, 0)
        self.buton_hbox_frame.set_padding(5, 5, 1, 1)
        self.buton_hbox = gtk.HBox()
        self.buton_hbox_frame.add(self.buton_hbox)
                
        self.ok_btn = Button("确定")
        self.ok_btn.set_size(90, 25)
        self.cancel_btn_frame = gtk.Alignment()
        cancel_btn_padding = 10
        self.cancel_btn_frame.set_padding(0, 0, cancel_btn_padding, cancel_btn_padding)
        self.cancel_btn = Button("取消")
        self.cancel_btn_frame.add(self.cancel_btn)
        self.cancel_btn.set_size(90, 25)
        
        self.buton_hbox.pack_start(self.ok_btn, False, False)
        self.buton_hbox.pack_start(self.cancel_btn_frame, False, False)
        
        self.main_vbox.pack_start(self.tabpage, False, False)
        self.main_vbox.pack_start(self.buton_hbox_frame, False, False)
        self.add(self.main_vbox)
        self.show_all()
               
        
        
    def draw_background(self, widget, event):    
        cr = widget.window.cairo_create()
        x, y, w, h = widget.get_allocation()        
        cr.set_source_rgba(0, 0, 0, 0.7)
        cr.rectangle(x, y, w, h)
        cr.fill()
        
        window_bg_pixbuf = self.window_bg_pixbuf.get_pixbuf().scale_simple(w, h, gtk.gdk.INTERP_BILINEAR)
        draw_pixbuf(cr, window_bg_pixbuf, x, y)       
        
        if "get_child" in dir(widget) and widget.get_child() != None:
            widget.propagate_expose(widget.get_child(), event)    
        return True
        
        
if __name__ == "__main__":        
    IniGui()    
    gtk.main()
