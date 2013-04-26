#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Wang Yong
# 
# Author:     Wang Yong <lazycat.manatee@gmail.com>
# Maintainer: Wang Yong <lazycat.manatee@gmail.com>
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


from dtk.ui.draw import draw_text
from dtk.ui.utils import color_hex_to_rgb 
from locales import _
import gtk

class LabelButton(gtk.Button):
    def __init__(self):
        gtk.Button.__init__(self)
        self.text = _("Advanced settings")
        width = eval(_("('button_size', 100)"))
        # width = 50
        width = width[1]
        height = 20
        self.set_size_request(width, height)
        # Init event.
        self.connect("expose-event", self.label_button_expose_event)
        
        
    def label_button_expose_event(self, widget, event):    
        cr = widget.window.cairo_create()
        rect = widget.allocation
        color = "#2685e3"
        draw_line_bool = False
        
        if widget.state == gtk.STATE_NORMAL:
            color = "#2685e3"
            draw_line_bool = False
        elif widget.state == gtk.STATE_PRELIGHT:
            color = "#257bd0"
            draw_line_bool = True
        elif widget.state == gtk.STATE_ACTIVE:
            color = "#257bd0"
            draw_line_bool = True
        
        # draw text.
        draw_text(cr, _("Advanced settings"), rect.x, rect.y, rect.width, rect.height, text_color=color, underline=draw_line_bool)
        return True            
            
if __name__ == "__main__":            
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    fixed = gtk.Fixed()
    win.set_size_request(300, 300)
    fixed.put(LabelButton(), 30, 30)
    win.add(fixed)
    win.show_all()
    gtk.main()
