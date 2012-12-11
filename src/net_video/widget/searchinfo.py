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
from function import color_hex_to_cairo, draw_text, alpha_color_hex_to_cairo

class SearchInfo(gtk.HBox):
    def __init__(self):
        gtk.HBox.__init__(self)
        self.pre_page_btn = PageBtn("上一页")
        self.next_page_btn = PageBtn("下一页")
        self.save_info_btn = InfoBtn()
        self.pack_start(self.pre_page_btn, False, False)        
        self.pack_start(self.save_info_btn, False, False)
        self.pack_start(self.next_page_btn, False, False)
        
class PageBtn(gtk.Button):
    def __init__(self, text=""):
        gtk.Button.__init__(self)
        self.text = text
        height = 128 * 3        
        self.set_size_request(80, height)
        self.connect("expose-event", self.pagebtn_expose_event)
        
    def pagebtn_expose_event(self, widget, event):    
        cr = widget.window.cairo_create()
        rect = widget.allocation
        height = 128 * 3
        draw_x_padding = 15
        draw_w = 50
        draw_h = 150
        cr.set_source_rgba(*alpha_color_hex_to_cairo(("#000000", 0.5)))
        cr.rectangle(rect.x + draw_x_padding, 
                     rect.y + height/2 - draw_h/2, 
                     draw_w, 
                     draw_h)
        cr.fill()
        draw_text_padding_x = 24
        #
        if widget.state == gtk.STATE_NORMAL:
            text_color = "#FFFFFF"
        elif widget.state == gtk.STATE_PRELIGHT:
            text_color = "#FF0033"
        elif widget.state == gtk.STATE_ACTIVE:
            text_color = "#6600CC"

        draw_text(cr, 
                  rect.x + draw_x_padding + draw_text_padding_x, 
                  rect.y + height/2, 
                  self.text, 
                  (text_color, 1))
        return True

class InfoBtn(gtk.Button):
    def __init__(self):
        gtk.Button.__init__(self)
        width = 180 * 3 + 2 * 10
        height = 128 * 3
        self.text_list = []
        self.set_size_request(width, height)
        self.connect("button-press-event", self.infobtn_press_event)
        self.connect("expose-event", self.infobtn_expose_event)
        
    def infobtn_press_event(self, widget, event):
        print "event:", event.x
        
    def set_text_list(self, text_list):    
        self.text_list = text_list
    
    def infobtn_expose_event(self, widget, event):    
        cr = widget.window.cairo_create()
        rect = widget.allocation
        w_padding = 180
        h_padding = 120
        x_padding = 10
        y_padding = 10
        for x, y, color, text in [(rect.x, rect.y, "#3399FF", "乱世佳人(国产剧)"), # 第一行
                                  (rect.x + w_padding + x_padding, rect.y, "#CC3333", "国产凌凌漆(国语)"),
                                  (rect.x + 2 * w_padding + 2 * x_padding, rect.y, "#FF9900", "国产凌凌漆(粤语)"), 
                                  (rect.x, rect.y + h_padding + y_padding, "#33FF33", "兵临城下(国产) "), # 第二行
                                  (rect.x + w_padding + x_padding, rect.y + h_padding + y_padding, "#99CC66", "(国产方...方阵 "),
                                  (rect.x + 2 * w_padding + 2 * x_padding, rect.y + h_padding + y_padding, "#FF66CC", "(国...百家争鸣"),
                                  (rect.x, rect.y + 2 * h_padding + 2 * y_padding, "#CC3366", "(国产)...武器"), # 第三行
                                  (rect.x + w_padding + x_padding, rect.y + 2 * h_padding + 2 * y_padding, "#6666FF", "COCO...泳装秀"),
                                  (rect.x + 2 * w_padding + 2 * x_padding, rect.y + 2 * h_padding + 2 * y_padding, "#66CCCC", "(国产...与启发")
                                  ]:
            cr.set_source_rgb(*color_hex_to_cairo(color))
            cr.rectangle(x, y, w_padding, h_padding)
            cr.fill()
            draw_text(cr, x + w_padding/2, y + h_padding/2, text, ("#FFFFFF", 1))
        return True


