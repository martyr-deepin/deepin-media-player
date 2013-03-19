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

import cairo
import gtk
import math
from dtk.ui.utils import alpha_color_hex_to_cairo
from dtk.ui.utils import propagate_expose

class PreViewWin(gtk.Window):
    def __init__(self):
        #gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        gtk.Window.__init__(self, gtk.WINDOW_POPUP)
        # init values.
        self.init_values()
        self.init_trayicon_settings()
        self.init_trayicon_events()
        self.hide_all() 

    def init_values(self):
        ARROW_WIDTH = 12
        self.radius = 2
        self.arrow_width = ARROW_WIDTH
        self.arrow_height = ARROW_WIDTH/2 
        self.offset = 3
        self.alpha = 1.0
        # colors.
        self.border_out_color = ("#ffffff", 0.3)
        self.in_border_color = ("#000000", 1.0)

    def init_trayicon_settings(self):
        self.set_colormap(gtk.gdk.Screen().get_rgba_colormap())
        #
        self.set_decorated(False)
        self.set_app_paintable(True)
        self.set_skip_pager_hint(True)
        self.set_skip_taskbar_hint(True)
        self.set_position(gtk.WIN_POS_NONE)
        self.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_MENU)
        self.set_opacity(self.alpha)
        #
        self.draw = gtk.EventBox()
        self.main_ali  = gtk.Alignment(1, 1, 1, 1)
        self.main_ali.set_padding(2, self.arrow_height + 2, 2, 2)
        self.show_time_label = gtk.Label("12:12:12")
        self.main_ali.add(self.show_time_label)
        self.add(self.draw)
        self.draw.add(self.main_ali)
        self.hide_all()

    def init_trayicon_events(self):
        self.add_events(gtk.gdk.ALL_EVENTS_MASK)
        self.draw.connect("expose-event", self.draw_expose_event)
        self.connect("destroy", lambda w : gtk.main_quit())
        
    def draw_expose_event(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        #
        cr.rectangle(*rect)
        cr.set_source_rgba(1, 1, 1, 0.0)
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()

        cr = widget.window.cairo_create()
        x, y, w, h = rect
        self.expose_event_draw(cr, rect)
        propagate_expose(widget, event)
        return True

    def expose_event_draw(self, cr, rect):
        x, y, w, h = rect
        # out border.
        cairo_popover(cr, x, y, w, h, self.radius, 
                      self.arrow_width, self.arrow_height, self.offset)
        cr.set_source_rgba(*alpha_color_hex_to_cairo(self.border_out_color))
        cr.set_line_width(self.border_width)
        cr.fill()
        # in border.
        padding_h = 0.7 
        cairo_popover(cr, x + 1, y + 1, w - 2, h - 2, self.radius, 
                      self.arrow_width, self.arrow_height, self.offset) 
        cr.set_source_rgba(*alpha_color_hex_to_cairo(self.in_border_color)) # set in border color.
        cr.set_line_width(self.border_width)
        cr.fill()

    def set_offset(self, offset):
        min_offset = 3
        max_offset = self.allocation.width - min_offset - self.arrow_width
        # 
        offset = max(min(offset, max_offset), min_offset)
        #
        if min_offset <= offset <= max_offset:
            self.offset = offset
            self.queue_draw_area(*self.allocation)

    def get_offset_mid_value(self):
        return self.allocation.width/2 - self.arrow_width/2

def cairo_popover (surface_context, 
                   trayicon_x, trayicon_y, trayicon_w, trayicon_h, 
                   radius, arrow_width, arrow_height, offs=0):
    cr = surface_context
    x = trayicon_x
    y = trayicon_y
    w = trayicon_w
    h = trayicon_h - arrow_height + trayicon_y
    y = y - arrow_height 
    h -= y  
    # draw.
    cr.arc (x + radius, 
            y + arrow_height + radius,
            radius, math.pi, math.pi * 1.5)
    cr.arc (x + w - radius, 
            y + arrow_height + radius,
            radius, math.pi * 1.5, math.pi * 2.0)
    cr.arc(x + w - radius, 
           y + h - radius, radius, 0, math.pi * 0.5)
    #
    y_padding = trayicon_y + h - arrow_height 
    arrow_height_padding = arrow_height
    cr.line_to(offs + arrow_width, y_padding) 
    cr.rel_line_to(-arrow_width / 2.0, arrow_height_padding)
    cr.rel_line_to(-arrow_width / 2.0, -arrow_height_padding)
    #    
    cr.arc(x + radius,
           y + h - radius,
           radius,
           math.pi * 0.5,
           math.pi)
    cr.close_path()

#######################################################################

if __name__ == "__main__":
    prev_win = PreViewWin()
    screen = gtk.DrawingArea()
    prev_win.main_ali.add(screen)
    prev_win.set_size_request(124, 89)
    prev_win.move(500, 500)
    prev_win.show_all()
    prev_win.set_offset(80)
    gtk.main()


