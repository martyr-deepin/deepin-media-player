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
import gobject

class SearchInfo(gtk.HBox):
    def __init__(self):
        gtk.HBox.__init__(self)
        self.pre_page_btn = PageBtn("上一页")
        self.next_page_btn = PageBtn("下一页")
        self.save_info_btn = InfoBtn([
                "乱世佳人(国产剧)", "国产凌凌漆(国语)", "国产凌凌漆(粤语)",
                "兵临城下(国产) ", "(国产方兵临城下方阵 ", "(国兵临城下(百家争鸣",
                "(国产)兵临城下武器", "COCO兵临城下泳装秀", "(国产兵临城下与启发"])        
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
    __gsignals__ = {
        "select-index-event":(gobject.SIGNAL_RUN_LAST,
                              gobject.TYPE_NONE,(gobject.TYPE_INT, gobject.TYPE_STRING,))
        }    
    def __init__(self, text_list=["", "", "", "", "", "", "", "", ""]):
        gtk.Button.__init__(self)
        width = 180 * 3 + 2 * 10 + 50
        height = 128 * 3 + 50       
        self.big_index = 0
        self.text_list = text_list
        self.set_size_request(width, height)
        self.add_events(gtk.gdk.ALL_EVENTS_MASK)
        self.connect("button-press-event", self.infobtn_press_event)
        self.connect("motion-notify-event", self.infobtn_motion_notify_event)
        self.connect("expose-event", self.infobtn_expose_event)
        
    def infobtn_press_event(self, widget, event):
        w_padding = 180
        h_padding = 120
        index = min(2, int(event.x / (w_padding + 20))) + 3 * min(2, int(event.y / (h_padding + 20)))
        self.emit("select-index-event", index, self.text_list[index])
        
    def infobtn_motion_notify_event(self, widget, event):    
        w_padding = 180
        h_padding = 120
        self.big_index = min(2, int(event.x / (w_padding + 20))) + 3 * min(2, int(event.y / (h_padding + 20)))
        self.queue_draw()
        
    def set_text_list(self, text_list):    
        self.text_list = text_list
    
    def infobtn_expose_event(self, widget, event):    
        cr = widget.window.cairo_create()
        rect = widget.allocation
        #
        w_padding = 180
        h_padding = 120
        x_padding = 10
        y_padding = 10
        info_9_list = [(20 + rect.x, 20 + rect.y, "#3399FF", self.text_list[0]), # 第一行
                       (20 + rect.x + w_padding + x_padding, 20 + rect.y, "#CC3333", self.text_list[1]),
                       (20 + rect.x + 2 * w_padding + 2 * x_padding, 20 + rect.y, "#FF9900", self.text_list[2]), 
                       (20 + rect.x, 20 + rect.y + h_padding + y_padding, "#33FF33", self.text_list[3]), # 第二行
                       (20 + rect.x + w_padding + x_padding, 20 + rect.y + h_padding + y_padding, "#99CC66", self.text_list[4]),
                       (20 + rect.x + 2 * w_padding + 2 * x_padding, 20 + rect.y + h_padding + y_padding, "#FF66CC", self.text_list[5]),
                       (20 + rect.x, 20 + rect.y + 2 * h_padding + 2 * y_padding, "#CC3366", self.text_list[6]), # 第三行
                       (20 + rect.x + w_padding + x_padding, 20 + rect.y + 2 * h_padding + 2 * y_padding, "#6666FF", self.text_list[7]),
                       (20 + rect.x + 2 * w_padding + 2 * x_padding, 20 + rect.y + 2 * h_padding + 2 * y_padding, "#66CCCC", self.text_list[8])
                       ]
        for x, y, color, text in info_9_list:
            cr.set_source_rgb(*color_hex_to_cairo(color))                        
            cr.rectangle(x, y, w_padding, h_padding)
            cr.fill()            
            if len(text) > 7:
                text = text.decode('utf-8')
                text = text[:4] + "..." + text[-4:]
            draw_text(cr, x + w_padding/2, y + h_padding/2, text, ("#FFFFFF", 1))
        # big rectangle.    
        cr.set_source_rgb(*color_hex_to_cairo(info_9_list[self.big_index][2]))    
        cr.rectangle(info_9_list[self.big_index][0] - 10, 
                     info_9_list[self.big_index][1] - 10,
                     w_padding + 20, h_padding + 20)            
        cr.fill()
        big_text = info_9_list[self.big_index][3].decode("utf-8")
        if len(big_text) > 7:
            big_text = big_text[:4] + "..." + big_text[-4:]
        draw_text(cr, 
                  info_9_list[self.big_index][0] + w_padding/2, 
                  info_9_list[self.big_index][1] + h_padding/2, 
                  big_text, ("#FFFFFF", 1))        
        return True


