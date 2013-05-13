#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2013 Deepin, Inc.
#               2013 Hailong Qiu
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

from skin import app_theme
from draw import draw_pixbuf
from dtk.ui.entry import Entry
from dtk.ui.utils import (propagate_expose, color_hex_to_cairo, alpha_color_hex_to_cairo)
import gtk


class Search(gtk.HBox):
    def __init__(self):
        gtk.HBox.__init__(self)
        self.__init_values()
        #
        self.align = gtk.Alignment(0, 0, 1, 1)
        self.ok_btn  = gtk.Button("查询")
        self.text = Entry(
                    content="搜视频...",
                    text_color=self.search_none_color,
                    #enable_clear_button=True
                    )
        #
        w, h = self.search_bg_pixbuf.get_width(), self.search_bg_pixbuf.get_height()
        self.align.set_size_request(w, h)
        ok_w, ok_h = self.search_hover_pixbuf.get_width(), self.search_normal_pixbuf.get_height()
        self.ok_btn.set_size_request(ok_w, ok_h)
        #
        self.text.add_events(gtk.gdk.ALL_EVENTS_MASK)
        self.text.connect("button-press-event", self.__text_button_press_event)
        self.text.connect("motion-notify-event", self.__text_motion_notify_event)
        self.text.connect("enter-notify-event", self.__text_entry_notify_event)
        self.text.connect("leave-notify-event", self.__text_leave_notify_event)
        self.text.clear_button.render = self.paint_clear_button
        #
        self.ok_btn.connect("expose-event", self.__ok_btn_expose_event)
        #
        self.align.add(self.text)
        self.align.connect("expose-event", self.__expose_text_entry)
        #
        self.pack_start(self.align, True, True)
        self.pack_start(self.ok_btn, False, False)

    def paint_clear_button(self, cr, rect, offset_y=0):
        if self.clear_check:
            pixbuf = self.clear_hover_pixbuf
        else:
            pixbuf = self.clear_normal_pixbuf
        #
        draw_pixbuf(cr, pixbuf, 
                    rect.x + rect.width + pixbuf.get_width()/2 + 4, 
                    rect.y + rect.height/2 - pixbuf.get_height()/2)

    def __text_button_press_event(self, widget, event):
        if self.text.enable_clear_button and not (event.x < self.text.clear_button_x):
            self.text.set_text("搜视频...")
            self.text.enable_clear_button = False
            self.text.set_editable(False)
            self.text.entry_buffer.text_color = self.search_none_color
        else:
            # 清空掉上面的搜索视频的文本.
            self.text.set_editable(True)
            if self.text.get_text() == "搜视频...":
                self.text.set_text("")
            self.text.entry_buffer.text_color = self.search_input_color
            self.text.enable_clear_button = True
        self.text.queue_draw()

    def __text_entry_notify_event(self, widget, event):
        self.clear_check = True
        self.text.queue_draw()

    def __text_leave_notify_event(self, widget, event):
        self.clear_check = False
        self.text.queue_draw()

    def __text_motion_notify_event(self, widget, event):
        if self.text.enable_clear_button:
            if not (event.x < self.text.clear_button_x):
                self.clear_check = True
                self.text.queue_draw()
            else:
                self.clear_check = False
                self.text.queue_draw()

    def __init_values(self):
        self.clear_check = False
        self.search_none_color = app_theme.get_color("searchNone").get_color()
        self.search_input_color = app_theme.get_color("searchInput").get_color()
        #
        self.search_bg_pixbuf = app_theme.get_pixbuf("net_search/search_bg.png").get_pixbuf()
        self.clear_normal_pixbuf = app_theme.get_pixbuf("net_search/clean_normal.png").get_pixbuf()
        self.clear_hover_pixbuf  = app_theme.get_pixbuf("net_search/clean_hover.png").get_pixbuf()
        self.search_hover_pixbuf = app_theme.get_pixbuf("net_search/search_hover.png").get_pixbuf()
        self.search_normal_pixbuf = app_theme.get_pixbuf("net_search/search_normal.png").get_pixbuf()

    def __expose_text_entry(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        x, y, w, h = rect.x, rect.y, rect.width, rect.height

        draw_pixbuf(cr, self.search_bg_pixbuf, rect.x, rect.y)
        
        propagate_expose(widget, event)
        
        return True
    
    def __ok_btn_expose_event(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        #
        if widget.state:
            pixbuf = self.search_normal_pixbuf
        else:
        #elif widget.state:
            pixbuf = self.search_hover_pixbuf
        draw_pixbuf(cr, pixbuf, rect.x, rect.y)
        return True



