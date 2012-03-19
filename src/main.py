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
from dtk.ui.constant import *
from dtk.ui.menu import *
from dtk.ui.navigatebar import *
from dtk.ui.statusbar import *
from dtk.ui.categorybar import *
from dtk.ui.scrolled_window import *
from dtk.ui.box import *
from dtk.ui.button import *
from dtk.ui.listview import *
from dtk.ui.tooltip import *
from dtk.ui.popup_window import *
from dtk.ui.frame import *
from dtk.ui.dragbar import *
from dtk.ui.draw import *
from dtk.ui.utils import *
from dtk.ui.frame import *
from dtk.ui.mplayer_view import *

from preview import *
from mplayer import *
from screen import *
from playerlist import *
from constant import *
from control_panel import *
from utils import *

class MediaMplayer(object):
    '''Deepin Media Mplayer'''
    def __init__(self):
        self.mp = None
        self.length = 0
        self.pos = 0
        self.pos_bool = True
        self.state = True
        self.preview = None
        self.preview_bool = False
        self.toolbar = None
        
        # Media mplayer window init.
        self.app = Application("mediamplayer", False)
        self.app.set_icon(ui_theme.get_pixbuf("icon.ico"))
        self.app.add_titlebar(["theme", "menu", "max", "min", "close"],
                              app_theme.get_pixbuf("普通模式.png"),
                              "深度影音", " ", add_separator = True)
        
        # Set app window.
        self.app.window.set_size_request(540, 400)
        self.app.window.change_background(app_theme.get_pixbuf("my_bg2.jpg"))
        self.app.window.connect("destroy", self.quit)

        #self.app.window.stick()
        self.hbox   = gtk.HBox()
        self.v_frame = VerticalFrame(padding=5)
        self.v_frame.add(self.hbox)
        
        self.screen = Screen(self.app.window.allocation.x,self.app.window.allocation.y,400)
        self.list   = List()
        self.control = ControlPanel()
        
        # player toolbar and screen and scalebar.
        self.screen.set_flags() 
        self.screen_background = app_theme.get_pixbuf("deepin_player.png").get_pixbuf()
        self.screen_pixbuf = app_theme.get_pixbuf("deepin_player_icon.png").get_pixbuf()
        self.screen_font = app_theme.get_pixbuf("deepin_player_font.png").get_pixbuf()
        
        # player screen event.
        self.screen.screen.add_events(gtk.gdk.ALL_EVENTS_MASK)
        self.screen.screen.connect("expose-event", self.screen_expose_event)
        self.screen.screen.connect("get-xid", self.show_video)
        # player scalebar event.
        self.screen.scalebar.add_events(gtk.gdk.ALL_EVENTS_MASK)
        self.screen.scalebar.connect("button-press-event", self.scalebar_press_event)
        self.screen.scalebar.connect("button-release-event", self.scalebar_release_event)
        self.screen.scalebar.connect("motion-notify-event", self.scalebar_motion_notify_event)
        self.screen.scalebar.connect("enter-notify-event", self.scalebar_enter_notify_event)
        # player list.
        self.hbox.pack_start(self.screen.vbox, True, True)
        self.hbox.pack_start(self.list.vbox, True)
        
        # Test.
        self.control.button.connect("clicked", self.test)
        self.control.button2.connect("clicked", self.test2)
        self.control.volume.connect("get-value-event", self.set_media_volume_value)
        
        self.app.main_box.pack_start(self.v_frame)
        self.app.main_box.pack_start(self.control.hbox, False)
        self.app.window.show_all()     
        
    def set_media_volume_value(self, widget, value, volume_bool):                
        print value
        if self.mp.state == 1:
            
            if volume_bool == 1:
                self.mp.addvolume(value)
            else:    
                self.mp.decvolume(value)
            
        
    def scalebar_enter_notify_event(self, widget, event):
        rect = widget.allocation
        if self.mp.state:
            if 10 <= event.x <= rect.width-11 and 9 <= event.y <= 10:
                average = float(self.length)/float(rect.width-20.9998)
                preview_pos = average * (event.x-10)
                self.preview = Preview(self.mp.path, preview_pos, "/home/long", int(event.x_root), int(event.y_root))
                self.preview_bool = True
            
    def scalebar_motion_notify_event(self, widget, event):    
        if self.mp.state == 1:
            rect = widget.allocation
            if self.preview_bool:
                self.preview.quit_preview()
                self.preview_bool = False
                
    def scalebar_release_event(self, widget, event):
        self.pos_bool = True
    
    def scalebar_press_event(self, widget, event):
        if event.button == 1:
            self.pos_bool = False
            pos = self.screen.scalebar.get_value()
            if pos > self.pos:
                self.mp.fseek(pos - self.pos)
                self.screen.scalebar.set_value(pos)
            else:
                self.mp.bseek(self.pos - pos)
                self.screen.scalebar.set_value(pos)
                        
    def screen_expose_event(self, widget, event):
        if self.state:

            cr = widget.window.cairo_create()
            rect = widget.allocation
            x,y,w,h = rect.x, rect.y, rect.width, rect.height
   
            cr.set_source_rgba(0, 0, 0, 1)
            cr.rectangle(x-2, y-28, w, h+28)
            cr.fill()
            # Draw screen background.
            #image = self.screen_background.scale_simple(
            #    w,h,gtk.gdk.INTERP_BILINEAR)
            #draw_pixbuf(cr, image, rect.x, rect.y - 26)
            # Draw screen icon.
            draw_pixbuf(cr, self.screen_pixbuf, 
                        rect.width/2 - self.screen_pixbuf.get_width()/2 , 
                        rect.height/2 - self.screen_pixbuf.get_height()/2)
            # Draw screen font.
            draw_pixbuf(cr, self.screen_font, 
                        rect.width/2 - self.screen_font.get_width()/2 , 
                        rect.height/2 - self.screen_font.get_height()/2+self.screen_pixbuf.get_height())
            # 
            #cr.set_line_width(1)
            #cr.set_source_rgba(0, 0, 0, 0.1)
            #cr.move_to(x - 2, y - 26)
            #cr.line_to(x + w - 2, y - 26)
            #cr.stroke()
            return True
        
    def test2(self, widget):
        #self.state = True
        #self.screen.screen.queue_draw()
        #self.mp.quit()
        
        self.mp.addvolume(10)
        
    def test(self, widget):
        self.mp.play("/home/long/音乐/憨豆特工2.rmvb") #憨豆特工2.rmvb 老男孩.mp3
        
    def quit(self, widget):
        self.mp.quit()
        
    def show_video(self,widget, xid):
        self.mp = Mplayer(xid)
        self.toolbar = ToolBar(540, self.mp, self.app, self.screen)
        self.toolbar.panel.hide()
        self.mp.connect("get-time-length", self.get_time_length)
        self.mp.connect("get-time-pos", self.get_time_pos)
        self.mp.connect("play-start", self.play_start)
        self.mp.connect("play-end", self.play_ned)
        
        
    def play_start(self, widget, value):    
        print "start play..."
        self.screen.set_flags()
        if self.mp.path[-4:] in ["rmvb"] or self.mp.path[-3:] in ["mkv"] or self.mp.path[-2:] in ["rm"]:
            self.screen.unset_flags() #disable double buffered to avoid video blinking
            self.state = False
        self.screen.scalebar.set_value(0)
        # Set play window title.
        self.app.titlebar.change_title(self.mp.path)
        
    def play_ned(self, widget, value):
        print "end play..."
        self.state = True
        self.screen.screen.queue_draw()
        self.screen.scalebar.set_value(self.length)
        self.control.show_time_label.set_label(" 0 : 0 : 0 / 0 : 0: 0")
        
    def get_time_pos(self, widget, value):
        self.pos = value
        if self.pos_bool:
            self.screen.scalebar.set_value(value)
        pos_hour, pos_min, pos_sec = self.mp.time(value)    
        length_hour, length_min, length_sec = self.mp.time(self.length)
        
        self.control.show_time_label.set_label("%s : %s : %s / %s : %s : %s" % 
                                               (pos_hour, pos_min, pos_sec,
                                                length_hour, length_min, length_sec))
               
    def get_time_length(self, widget, value):
        self.length = value
        self.screen.scalebar.set_range(0, value)
        
mp = MediaMplayer()        
gtk.main()
