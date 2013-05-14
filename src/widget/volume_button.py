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

from dtk.ui.cache_pixbuf import CachePixbuf
from dtk.ui.theme import ui_theme
from dtk.ui.utils import set_clickable_cursor
#import dtk.ui.tooltip as Tooltip
from draw import draw_pixbuf, draw_text
from color import alpha_color_hex_to_cairo
from utils import get_text_size
#from tooltip import tooltip_text
from skin import app_theme
import gobject
import gtk

'''
100 / 500 = 0.2
x = 100 -> 100 * 0.2 = 20
x = 500 -> 500 * 0.2 = 100
x = 100 -> 100 * 0.2 = 20 
'''

ZERO_STATE = 0
MIN_STATE = 1
MID_STATE = 2
MAX_STATE = 3
MUTE_STATE = -1

MOUSE_VOLUME_STATE_PRESS  = 1
MOUSE_VOLUME_STATE_HOVER  = 2
MOUSE_VOLUME_STATE_NORMAL = -1

VOLUME_RIGHT = "right"
VOLUME_LEFT   = "left"

class VolumeButton(gtk.HBox):
    def __init__(self,
                 volume_max_value = 100,
                 line_height = 3,
                 ):        
        gtk.HBox.__init__(self) 
        self.mute_btn = gtk.Button()
        self.volume_btn = gtk.Button()
        self.tooltip_win = gtk.Window(gtk.WINDOW_POPUP)
        self.show_tooltext = gtk.Button("volume")
        self.show_tooltext.set_size_request(25, 20)
        self.tooltip_win.add(self.show_tooltext)
        self.show_tooltext.connect('expose-event', self.tooltip_btn_expose_event)
        self.show_tooltext.connect('enter-notify-event', self.tooltip_btn_enter_notify_event)

        self.__init_values()
        self.__init_events()

        self.pack_start(self.mute_btn, False, False)
        self.pack_start(self.volume_btn, False, False, 4)

    def tooltip_btn_expose_event(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        #
        cr.set_source_rgba(*alpha_color_hex_to_cairo(("#fffacc", 1.0)))
        cr.rectangle(*rect)
        cr.fill()
        #
        text = widget.get_label()
        size = get_text_size(text)
        import pango
        draw_text(cr, 
                  text, 
                  rect.x - 1, rect.y, rect.width, rect.height,
                  text_color="#000000",
                  alignment=pango.ALIGN_CENTER)
        cr.set_source_rgba(*alpha_color_hex_to_cairo(("#e7e77c", 1.0)))
        cr.rectangle(*rect)
        cr.stroke()
        return True
    
    def tooltip_btn_enter_notify_event(self, widget, event):
        if not self.move_check:
            self.tooltip_win.hide_all()

    def __init_values(self):
        self.max_value = 100
        self.min_value = 0
        self.value = 100
        self.mute_check = False
        self.move_check = False
        self.volume_level_values = [(1, 33),(34, 66),(67, 100)],

        self.bg_pixbuf = ui_theme.get_pixbuf("volumebutton/bg.png")
        self.fg_pixbuf = ui_theme.get_pixbuf("volumebutton/fg.png")

        self.zero_volume_normal_pixbuf = app_theme.get_pixbuf("volume_button/zero_normal.png")
        self.zero_volume_hover_pixbuf = app_theme.get_pixbuf("volume_button/zero_hover.png")
        self.zero_volume_press_pixbuf = app_theme.get_pixbuf("volume_button/zero_press.png")

        self.min_volume_normal_pixbuf = app_theme.get_pixbuf("volume_button/lower_normal.png")
        self.min_volume_hover_pixbuf = app_theme.get_pixbuf("volume_button/lower_hover.png")
        self.min_volume_press_pixbuf = app_theme.get_pixbuf("volume_button/lower_press.png")
        
        self.mid_volume_normal_pixbuf = app_theme.get_pixbuf("volume_button/middle_normal.png")
        self.mid_volume_hover_pixbuf = app_theme.get_pixbuf("volume_button/middle_hover.png")
        self.mid_volume_press_pixbuf = app_theme.get_pixbuf("volume_button/middle_press.png")

        self.max_volume_normal_pixbuf = app_theme.get_pixbuf("volume_button/high_normal.png")
        self.max_volume_hover_pixbuf = app_theme.get_pixbuf("volume_button/high_hover.png")
        self.max_volume_press_pixbuf = app_theme.get_pixbuf("volume_button/high_press.png")

        self.mute_volume_normal_pixbuf = app_theme.get_pixbuf("volume_button/mute_normal.png")
        self.mute_volume_hover_pixbuf = app_theme.get_pixbuf("volume_button/mute_hover.png")
        self.mute_volume_press_pixbuf = app_theme.get_pixbuf("volume_button/mute_press.png")

        self.point_volume_pixbuf = ui_theme.get_pixbuf("volumebutton/point_normal.png")

        mute_w = self.mute_volume_normal_pixbuf.get_pixbuf().get_width()
        mute_h = self.mute_volume_normal_pixbuf.get_pixbuf().get_height()
        volume_w = 54 +  12 #self.point_volume_pixbuf.get_width()
        volume_h = mute_h
        
        self.mute_btn.set_size_request(mute_w, mute_h)
        self.volume_btn.set_size_request(volume_w, volume_h)

    def __init_events(self):
        self.volume_btn.add_events(gtk.gdk.ALL_EVENTS_MASK)
        self.mute_btn.connect("expose-event",   self.mute_btn_expose_event)
        self.volume_btn.connect("expose-event", self.volume_btn_expose_event)
        self.volume_btn.connect("button-press-event",   self.volume_btn_button_press_event)
        self.volume_btn.connect("button-release-event", self.volume_btn_button_release_event)
        self.volume_btn.connect("motion-notify-event",  self.volume_btn_motion_notify_event)
        self.volume_btn.connect("enter-notify-event", self.volume_btn_enter_notify_event)
        self.volume_btn.connect("leave-notify-event", self.volume_btn_leave_notify_event)

    def volume_btn_enter_notify_event(self, widget, event):
        self.__volume_init_value(widget, event)
        # 设置提示.
        self.show_tooltext.set_label(str(int(self.value)))

    def volume_btn_leave_notify_event(self, widget, event):
        if not self.move_check:
            self.tooltip_win.hide_all()

    def volume_btn_button_press_event(self, widget, event):
        self.move_check = True
        self.set_event_value(widget, event)

    def volume_btn_button_release_event(self, widget, event):
        self.move_check = False
        self.tooltip_win.hide_all()

    def volume_btn_motion_notify_event(self, widget, event):
        if self.move_check:
            self.__volume_init_value(widget, event)
            # 获取音量的值.
            self.set_event_value(widget, event)
            # 设置提示.
            self.show_tooltext.set_label(str(int(self.value)))

    def __volume_init_value(self, widget, event):
        # 设置 tooltip_win 位置.
        parent_win = widget.get_parent_window()
        pos = parent_win.get_position()
        # bug: 简洁模式的提示有问题，所以不得不暂时关闭.
        if pos[0]:
            move_x = widget.allocation.x
            move_y = widget.allocation.y
            tool_all = self.tooltip_win.allocation
            rect = widget.allocation
            if 0 <= event.x <= rect.width:
                self.tooltip_win.move(int(pos[0] + move_x + event.x), 
                                      int(pos[1] + move_y + tool_all.height + 5))
            self.tooltip_win.show_all()

    def set_event_value(self, widget, event):
        rect = widget.allocation
        value = (event.x - 6) / (float(rect.width - 12) / self.max_value)
        self.value = max(min(value, self.max_value), self.min_value)
        # 添加提示信息.
        #tooltip_text(widget, str(int(self.value)))
        self.mute_check = False
        self.queue_draw()

    def set_mute_state(self, state):
        self.mute_check = state
        self.queue_draw()

    def set_value(self, value):
        self.value = max(min(value, self.max_value), self.min_value)
        self.mute_check = False
        self.queue_draw()

    def mute_btn_expose_event(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        #
        if widget.state == gtk.STATE_NORMAL:
            pixbuf = self.get_normal_pixbuf()
        elif widget.state == gtk.STATE_PRELIGHT: 
            pixbuf = self.get_hover_pixbuf()
        elif widget.state == gtk.STATE_ACTIVE:
            pixbuf = self.get_press_pixbuf()

        pixbuf_w, pixbuf_h = pixbuf.get_width(), pixbuf.get_height() 
        draw_pixbuf(cr, 
                    pixbuf, 
                    rect.x + rect.width/2 - pixbuf_w/2, 
                    rect.y + rect.height/2 - pixbuf_h/2)
    
        return True

    def get_hover_pixbuf(self):
        if self.mute_check:
            return self.mute_volume_hover_pixbuf.get_pixbuf()
        else:
            value = self.value
            min_value = self.volume_level_values[0][0]
            mid_value = self.volume_level_values[0][1]
            max_value = self.volume_level_values[0][2]

            if min_value[0] <= value <= min_value[1]:
                return self.min_volume_hover_pixbuf.get_pixbuf()
            elif mid_value[0] <= value <= mid_value[1]:
                return self.mid_volume_hover_pixbuf.get_pixbuf()
            elif max_value[0] <= value <= max_value[1]:
                return self.max_volume_hover_pixbuf.get_pixbuf()
            else:
                return self.zero_volume_hover_pixbuf.get_pixbuf()

    def get_press_pixbuf(self):
        if self.mute_check:
            return self.mute_volume_press_pixbuf.get_pixbuf()
        else:
            value = self.value
            min_value = self.volume_level_values[0][0]
            mid_value = self.volume_level_values[0][1]
            max_value = self.volume_level_values[0][2]

            if min_value[0] <= value <= min_value[1]:
                return self.min_volume_press_pixbuf.get_pixbuf()
            elif mid_value[0] <= value <= mid_value[1]:
                return self.mid_volume_press_pixbuf.get_pixbuf()
            elif max_value[0] <= value <= max_value[1]:
                return self.max_volume_press_pixbuf.get_pixbuf()
            else:
                return self.zero_volume_press_pixbuf.get_pixbuf()

    def get_normal_pixbuf(self):
        if self.mute_check:
            return self.mute_volume_normal_pixbuf.get_pixbuf()
        else:
            value = self.value
            min_value = self.volume_level_values[0][0]
            mid_value = self.volume_level_values[0][1]
            max_value = self.volume_level_values[0][2]
            #
            if min_value[0] <= value <= min_value[1]:
                return self.min_volume_normal_pixbuf.get_pixbuf()
            elif mid_value[0] <= value <= mid_value[1]:
                return self.mid_volume_normal_pixbuf.get_pixbuf()
            elif max_value[0] <= value <= max_value[1]:
                return self.max_volume_normal_pixbuf.get_pixbuf()
            else:
                return self.zero_volume_normal_pixbuf.get_pixbuf()

    def volume_btn_expose_event(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        self.__paint_volume_btn(cr, rect, widget.state)
        return True

    def __paint_volume_btn(self, cr, rect, state):
        # 画背景.
        bg_pixbuf = self.bg_pixbuf.get_pixbuf()
        bg_pixbuf = bg_pixbuf.scale_simple(rect.width - 12,
                                           bg_pixbuf.get_height(),
                                           gtk.gdk.INTERP_BILINEAR)
        draw_pixbuf(cr, 
                    bg_pixbuf, 
                    rect.x + 6, 
                    rect.y + rect.height/2 - bg_pixbuf.get_height()/2)
        point_x_padding = float(rect.width - 12) / self.max_value * self.value
        # 画前景.
        fg_pixbuf = self.fg_pixbuf.get_pixbuf()
        if self.value > 1:
            fg_pixbuf = fg_pixbuf.scale_simple(int(point_x_padding), 
                                               fg_pixbuf.get_height(),
                                               gtk.gdk.INTERP_BILINEAR)
            if fg_pixbuf:
                draw_pixbuf(cr, 
                            fg_pixbuf, 
                            rect.x + 6, 
                            rect.y + rect.height/2 - bg_pixbuf.get_height()/2)
        # 画拖动的点.
        point_pixbuf = self.point_volume_pixbuf.get_pixbuf()
        point_w, point_h = point_pixbuf.get_width(), point_pixbuf.get_height()
        x = rect.x + point_x_padding - point_w/2
        draw_pixbuf(cr, 
                    point_pixbuf, 
                    x + 6,
                    rect.y + rect.height/2 - point_h/2)
            


