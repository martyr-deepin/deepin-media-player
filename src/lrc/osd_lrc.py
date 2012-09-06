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
        self.offset_x = 0
        self.alpha = 0.5        
        self.time_delay = 250
        self.show_width = 0
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
        # self.offset_x += 100
        self.show_width += 1
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
            # cr.set_source_rgb(0, 0, 0)
            self.draw_lrc_text(self.lrc_text, cr)
            
    def draw_lrc_text(self, ch, cr, init_fg_color="#FF0000"):
        
        context = pangocairo.CairoContext(cr)
        layout = context.create_layout()
        layout.set_font_description(pango.FontDescription("%s %s" % (self.font_type, self.font_size)))
        
        # Set font position.
        cr.set_source_rgb(1, 0, 0)
        layout.set_text(ch)
        layout.set_attributes(self.pango_list)
        ch_width, ch_height = layout.get_pixel_size()
        
        cr.move_to(30, 0)
        #
        cr.save()        
        cr.layout_path(layout) 
        cr.set_source_rgba(0, 0, 1)
        # if #draw 填充的字体.
        # cr.set_line_width(1) # 设置宽        
        # cr.stroke_preserve() # 保存绘制的路径
        # cr.set_source_rgba(0, 1, 0)
        # cr.fill()
        # else 里面空的字体.
        cr.stroke()                
        #
        cr.restore()
        #        
        pattern = cairo.LinearGradient(self.offset_x, 0.0, 
                                       self.offset_x, ch_height )        
        pattern.add_color_stop_rgba(0.0, 0.5, 1.0, 0.5, 1.0)
        pattern.add_color_stop_rgba(0.5, 0.5, 0.5, 0.5, 1.0)
        pattern.add_color_stop_rgba(1.0, 0.1, 0.5, 0.1, 1.5)
        cr.set_source(pattern)
        cr.set_operator(cairo.OPERATOR_OVER)                
        #
        cr.save()
        cr.rectangle(0, 0, self.show_width, 200)
        cr.clip()        
        #
        cr.move_to(30, 0)        
        context.show_layout(layout)
        cr.restore()
        
if __name__ == "__main__":
    def test_osd_lrc_function(widget, event):
        cr = widget.window.cairo_create()
        cr.set_source_rgba(1.0, 1.0, 1.0, 0.1)
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()

        lrc.expose_lrc_text_function(cr)
        return True
    
    def active_expose_window(LRC):
        win.queue_draw()
        
    def modify_lrc_time(widget):    
        pass
        
    def realize_win(widget):
        widget.window.input_shape_combine_region(gtk.gdk.Region(), 0, 0) 
        widget.window.set_back_pixmap(None, False)
        
    ##############################################    
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    win.set_position(gtk.WIN_POS_CENTER)
    win.set_size_request(500, 500)
    
    win.set_decorated(False)
    win.set_skip_taskbar_hint(True)
    # win.set_keep_above(True)
    win.set_colormap(gtk.gdk.Screen().get_rgba_colormap())
    # win.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)    
    win.add_events(gtk.gdk.ALL_EVENTS_MASK)
    
    lrc = Lrc()    
    lrc.show_text("深度LINUX DEEPIN 深度影音")    
    lrc.init_timeout(50)
    lrc.connect("lrc-changed", active_expose_window)
    
    ################################################
    win.connect("expose-event", test_osd_lrc_function)
    win.connect("realize", realize_win)
    win.show_all()
    gtk.main()
