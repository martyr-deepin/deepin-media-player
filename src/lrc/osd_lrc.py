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

from dtk.ui.utils import color_hex_to_rgb
import gtk
import cairo
import pangocairo
import pango
import gobject
TEST_LRC = "深度影音播放器 歌词测试播放"
INIT_FONT_TYPE = "文泉驿等宽微米黑"
INIT_FONT_SIZE = 25

class Lrc(gobject.GObject):
    __gsignals__ = {
        "lrc-changed" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                         ())
        }
    def __init__(self):
        gobject.GObject.__init__(self)
        self.pango_list = pango.AttrList()
        
        self.lrc_text = ""
        self.end_index = 0
        self.alpha = 0.5        
        self.time_delay = 250
        self.show_lrc_bool = True
        self.timeout_add_bool = True
        self.timeout_add_id = None
        self.init_font()
        
    def start_lrc(self):    
        self.timeout_add_bool = True
        
    def stop_lrc(self):    
        self.timeout_add_bool = False
        
    def init_timeout(self, time_delay=0):     
        if self.timeout_add_id:
            gtk.timeout_remove(self.timeout_add_id) # remove timeout id.
        self.time_delay = time_delay
        self.timeout_add_id = gtk.timeout_add(self.time_delay, self.draw_lrc_timeout_add)
        
    def draw_lrc_timeout_add(self):    
        self.pango_list.insert(pango.AttrForeground(65535, 0, 0, 0, self.end_index))
        self.end_index += 1
        self.emit("lrc-changed")
        return self.timeout_add_bool
    
    def init_font(self, font_type=INIT_FONT_TYPE, font_size=INIT_FONT_SIZE):
        self.font_type = font_type
        self.font_size = font_size
        
    def show_text(self, lrc_text): 
        self.lrc_text = lrc_text
        self.emit("lrc-changed")
        
    def expose_lrc_text_function(self, cr):
        if self.show_lrc_bool:                   
            self.draw_lrc_text(self.lrc_text, cr)
            
    def draw_lrc_text(self, ch, cr, init_fg_color="#FFFFFF"):
        context = pangocairo.CairoContext(cr)
        layout = context.create_layout()
        layout.set_font_description(pango.FontDescription("%s %s" % (self.font_type, self.font_size)))
        
        # Set font position.
        layout.set_text(ch)
        layout.set_attributes(self.pango_list)
        # ch_width, ch_height = layout.get_pixel_size()
        cr.move_to(0, 0)
        # Set font rgb.
        cr.set_source_rgb(*color_hex_to_rgb(init_fg_color))
        # Show font.
        context.update_layout(layout)
        context.show_layout(layout)

if __name__ == "__main__":
    def test_osd_lrc_function(widget, event):
        cr = widget.window.cairo_create()
        lrc.expose_lrc_text_function(cr)
        return True
    
    def active_expose_window(LRC):
        win.queue_draw()
        
    def modify_lrc_time(widget):    
        lrc.show_text("深度LINUX DEEPIN 深度影音")
        lrc.init_timeout(500)
        
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    btn = gtk.Button("改变时间")
    btn.connect("clicked", modify_lrc_time)
    lrc = Lrc()    
    lrc.connect("lrc-changed", active_expose_window)
    win.add_events(gtk.gdk.ALL_EVENTS_MASK)
    ##############
    win.connect("expose-event", test_osd_lrc_function)
    win.add(btn)
    win.show_all()
    gtk.main()
