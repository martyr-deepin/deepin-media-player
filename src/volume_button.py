#! /usr/bin/env python
# -*- coding: utf-8 -*-

# houshaohui:code->[str_size function, get size, type, mtime, combox]. 
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

# Deein ui.
from dtk.ui.utils import alpha_color_hex_to_cairo
# from dtk.ui.utils import propagate_expose
from dtk.ui.draw import draw_pixbuf

from skin import app_theme

import gtk
import gobject

'''
100 / 500 = 0.2
x = 100 -> 100 * 0.2 = 20
x = 500 -> 500 * 0.2 = 100
x = 100 -> 100 * 0.2 = 20 
'''

#volume state.
MIN_STATE = 1
MID_STATE = 2
MAX_STATE = 3
MUTE_STATE = -1
# volume type.
VOLUME_RIGHT = "right"
VOLUME_LEFT   = "left"


class VolumeButton(gtk.EventBox):
    __gsignals__ = {
        "get-value-event":(gobject.SIGNAL_RUN_LAST,
                           gobject.TYPE_NONE,(gobject.TYPE_INT,gobject.TYPE_INT,))
        }
    def __init__(self,
                 volume_max_value = 100,
                 volume_width     = 52,
                 volume_x         = 0,
                 volume_y         = 15,
                 line_width       = 3,
                 volume_left_right_padding_x = 3,
                 volume_left_show_value = [(0, 33),(34, 66),(67, 100)],
                 scroll_bool = False,
                 press_emit_bool = False,
                 bg_color = app_theme.get_alpha_color("volumebutton_bg"),
                 fg_color = app_theme.get_alpha_color("volumebutton_fg"),
                 min_volume_pixbuf   = app_theme.get_pixbuf("min_volume.png"),
                 mid_volume_pixbuf   = app_theme.get_pixbuf("mid_volume.png"),
                 max_volume_pixbuf   = app_theme.get_pixbuf("max_volume.png"),
                 mute_volume_pixbuf  = app_theme.get_pixbuf("mute.png"),
                 point_volume_pixbuf = app_theme.get_pixbuf("volume_button.png")                 
                 ):        
        gtk.EventBox.__init__(self)
        ###########################
        if volume_x < max_volume_pixbuf.get_pixbuf().get_width() + 10:
            volume_x = max_volume_pixbuf.get_pixbuf().get_width() + 10
        '''Init pixbuf.'''
        self.__bg_color               = bg_color
        self.__fg_color               = fg_color
        self.__min_volume_pixbuf      = min_volume_pixbuf
        self.__mid_volume_pixbuf      = mid_volume_pixbuf
        self.__max_volume_pixbuf      = max_volume_pixbuf
        self.__mute_volume_pixbuf     = mute_volume_pixbuf
        self.__point_volume_pixbuf    = point_volume_pixbuf        
        '''Init Set VolumeButton attr.'''
        self.set_size_request(volume_width, 30)
        self.set_visible_window(False)
        '''Init value.'''
        self.__press_emit_bool  = press_emit_bool
        self.__line_width       = line_width
        self.__current_value    = 0
        self.__mute_bool        = False
        self.__drag             = False 
        self.__volume_max_value = volume_max_value
        self.__volume_width     = volume_width
        
        self.__volume_left_x    = volume_x - self.__max_volume_pixbuf.get_pixbuf().get_width() - volume_left_right_padding_x
        self.__volume_left_y    = volume_y - self.__max_volume_pixbuf.get_pixbuf().get_height()/2 + self.__point_volume_pixbuf.get_pixbuf().get_height()/2
        self.__volume_right_x   = volume_x
        self.__volume_right_y   = volume_y
        '''Left'''
        self.volume_left_show_value = volume_left_show_value
        self.volume_state = MIN_STATE
        
        '''Right'''
        # bg value.
        self.__bg_x         = 0
        self.__bg_y         = self.__volume_right_y
        self.__bg_padding_x = self.__volume_right_x
        # fg value.
        self.__fg_x         = 0
        self.__fg_y         = self.__volume_right_y
        self.__fg_padding_x = self.__volume_right_x
        # point value.
        self.__point_x         = 0
        self.__point_y         = self.__volume_right_y
        self.__point_padding_x = self.__volume_right_x
        
        '''Init VolumeButton event.'''
        self.add_events(gtk.gdk.ALL_EVENTS_MASK)
        self.connect("expose-event",         self.__expose_draw_volume)
        self.connect("motion-notify-event",  self.__motion_mouse_set_point)
        self.connect("button-press-event",   self.__press_mouse_set_point)
        self.connect("button-release-event", self.__release_mouse_set_point)
        # scroll event.
        if scroll_bool:
            self.connect("scroll-event",     self.__scroll_mouse_set_point)
            
    def set_press_emit_bool(self, emit_bool):
        self.__press_emit_bool = emit_bool
        
    def __set_point_padding_x(self, event):
        self.__mute_bool = False
        self.__point_padding_x = int(event.x)   
        self.queue_draw()        
                            
    def __press_mouse_set_point(self, widget, event):    
        temp_x = int(event.x)
        temp_min_x = self.__bg_x + self.__bg_padding_x - self.__point_volume_pixbuf.get_pixbuf().get_width()/2
        temp_max_x = self.__bg_x + self.__bg_padding_x + self.__volume_width + self.__point_volume_pixbuf.get_pixbuf().get_width()/2
        if temp_min_x < temp_x < temp_max_x:            
            self.__set_point_padding_x(event)
            self.__drag = True
        else:    
            if self.__volume_left_x <= temp_x <= temp_min_x:
                self.__mute_bool = not self.__mute_bool
                self.queue_draw()
                            
    def __release_mouse_set_point(self, widget, event):        
        self.__drag = False
        if self.__press_emit_bool:
            self.emit("get-value-event", self.__current_value, self.volume_state)        
        
    def __motion_mouse_set_point(self, widget, event):
        if self.__drag:
            self.__set_point_padding_x(event)        
                    
    def __scroll_mouse_set_point(self, widget, event):    
        if event.direction == gtk.gdk.SCROLL_UP:
            self.volume_other_set_value(VOLUME_RIGHT)
        elif event.direction == gtk.gdk.SCROLL_DOWN:
            self.volume_other_set_value(VOLUME_LEFT)
            
    def volume_other_set_value(self, volume_type):    
        point_width_average      = self.__point_volume_pixbuf.get_pixbuf().get_width() / 2 
        temp_min = (self.__point_x + self.__point_padding_x - point_width_average)
        temp_max = (self.__point_x + self.__point_padding_x + self.__volume_width - point_width_average)
        
        self.__mute_bool = False
        
        if volume_type == VOLUME_RIGHT:
            if self.__point_padding_x >= temp_max:
                self.__point_padding_x = temp_max
            else:    
                self.__point_padding_x += 1
        elif volume_type == VOLUME_LEFT:
            if self.__point_padding_x <= temp_min:
                self.__point_padding_x = temp_min
            else:    
                self.__point_padding_x -= 1
            
        self.queue_draw()
        
    def __expose_draw_volume(self, widget, event):                        
        self.__draw_volume_right(widget, event)              # 1: get current value.
        self.__set_volume_value_to_state(self.__current_value) # 2: value to state.
        self.__draw_volume_left(widget, event)               # 3: draw state pixbuf.        
        if not self.__press_emit_bool:
            self.emit("get-value-event", self.__current_value, self.volume_state)
        # propagate_expose(widget, event)
        return True

        
    '''Left function'''        
    def set_volume_state(self, state):
        if state == MIN_STATE:
            self.volume_state = MIN_STATE
        elif state == MID_STATE:    
            self.volume_state = MID_STATE
        elif state == MAX_STATE:    
            self.volume_state = MAX_STATE
        elif state == MUTE_STATE:    
            self.volume_state = MUTE_STATE
            
    def get_volume_state(self):
        return self.volume_state
        
    def set_volume_left_show_value(self, show_value):
        try:
            show_value[0][0] - show_value[0][1]
            show_value[1][0] - show_value[1][1]
            show_value[2][0] - show_value[2][1]
            
            self.volume_left_show_value = show_value
        except:    
            print "Error show value!!"
        
    def __set_volume_value_to_state(self, value):
        if not self.__mute_bool:
            temp_show_value = self.volume_left_show_value
            if temp_show_value[0][0] <= value <= temp_show_value[0][1]:
                self.volume_state = MIN_STATE
            elif temp_show_value[1][0] <= value <= temp_show_value[1][1]:
                self.volume_state = MID_STATE
            elif temp_show_value[2][0] <= value <= temp_show_value[2][1]:
                self.volume_state = MAX_STATE
        else:        
            self.volume_state = MUTE_STATE
                    
    def set_volume_mute(self):
        self.volume_state = MUTE_STATE
            
    def __draw_volume_left(self, widget, event):
        cr = widget.window.cairo_create()
        x, y, w, h = widget.allocation
        
        if self.volume_state == MUTE_STATE:                    
            pixbuf = self.__mute_volume_pixbuf
        elif self.volume_state == MIN_STATE:    
            pixbuf = self.__min_volume_pixbuf
        elif self.volume_state == MID_STATE:        
            pixbuf = self.__mid_volume_pixbuf
        elif self.volume_state == MAX_STATE:
            pixbuf = self.__max_volume_pixbuf
            
        draw_pixbuf(cr,
                    pixbuf.get_pixbuf(),
                    x + self.__volume_left_x,
                    y + self.__volume_left_y,
                    )
    
    '''Right function'''            
    def set_line_width(self, width):
        self.__line_width = width
        self.queue_draw()
        
    def set_value(self, value):        
        if 0 <= value <= self.__volume_max_value:
            temp_padding = (float(self.__volume_max_value) / self.__volume_width)
            temp_padding_x = float(value) / temp_padding            
            self.__point_padding_x = temp_padding_x + ((self.__fg_padding_x))
            self.queue_draw()
            
    def get_value(self):        
        return self.__current_value
        
    def set_volume_position(self, x, y):        
        self.__volume_right_x = x
        self.__volume_right_y = y
        # Set x.
        self.__bg_padding_x    = self.__volume_right_x
        self.__fg_padding_x    = self.__volume_right_x
        self.__point_padding_x = self.__volume_right_x
        # Set y.
        self.__bg_y    = self.__volume_right_y
        self.__fg_y    = self.__volume_right_y
        self.__point_y = self.__volume_right_y
        
    def set_volume_max_value(self, value):    
        self.__volume_max_value = value
                
    def __draw_volume_right(self, widget, event):
        cr = widget.window.cairo_create()
        cr.set_line_width(self.__line_width)
        x, y, w, h = widget.allocation
    
        point_width_average      = self.__point_volume_pixbuf.get_pixbuf().get_width() / 2 
        ##################################################
        # Draw bg.
        cr.set_source_rgba(*alpha_color_hex_to_cairo(self.__bg_color.get_color_info()))
        cr.move_to(x + self.__bg_x + self.__bg_padding_x,
                   y + self.__bg_y + point_width_average)
        cr.line_to(x + self.__bg_x + self.__bg_padding_x + self.__volume_width,
                   y + self.__bg_y + point_width_average)
        cr.stroke()
        ##################################################
        
        temp_fg_padding_x = self.__point_padding_x - (self.__fg_x + self.__fg_padding_x) 
        
        if temp_fg_padding_x < 0:
            temp_fg_padding_x = 0
        if temp_fg_padding_x > self.__volume_width:    
            temp_fg_padding_x = self.__volume_width
        # Get current value.    
        self.__current_value = temp_fg_padding_x * (float(self.__volume_max_value) / self.__volume_width)
        
        # Draw fg. 
        cr.set_source_rgba(*alpha_color_hex_to_cairo((self.__fg_color.get_color_info())))
        cr.move_to(x + self.__fg_x + self.__fg_padding_x,
                   y + self.__fg_y + point_width_average)
        cr.line_to(x + self.__fg_x + self.__fg_padding_x + temp_fg_padding_x,
                   y + self.__fg_y + point_width_average)
        cr.stroke()        
        #################################################
        # Draw point.                        
        temp_point_padding_x     = (self.__point_x + self.__point_padding_x - point_width_average)

        temp_min = (self.__point_x + self.__volume_right_x - point_width_average)
        temp_max = (self.__point_x + self.__volume_right_x + self.__volume_width - point_width_average)
        if temp_point_padding_x < temp_min:
            temp_point_padding_x = temp_min
        if temp_point_padding_x > temp_max:    
            temp_point_padding_x = temp_max
            
        draw_pixbuf(cr, 
                    self.__point_volume_pixbuf.get_pixbuf(), 
                    x + temp_point_padding_x,
                    y + self.__point_y)    
        
gobject.type_register(VolumeButton)                       

if __name__ == "__main__":
    import random
    from dtk.ui.window import Window
    def set_time_position():
        volume_button.set_value(random.randint(0, 100))
        return True
    
    def get_volume_value(volume_button, value, volume_state):    
        print "[get_volume_value:]"
        print "volume_button:%s" % volume_button
        print "value:%s" % value
        print "volume_state:%s" % volume_state

    def set_value_button_clicked(widget):    
        volume_button.set_value(100)
        volume_button.set_line_width(4)    # Set draw line width.    
        # volume_button.set_volume_left_show_value([(0,10),(11,80),(81,100)])
        
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    # win = Window()
    win.set_size_request(200, 120)
    win.set_title("测试音量按钮")
    main_vbox = gtk.VBox()
    volume_button = VolumeButton(100,220)
    # volume_button = VolumeButton()
    volume_button.connect("get-value-event", get_volume_value)
    set_value_button = gtk.Button("设置音量的值")
    set_value_button.connect("clicked", set_value_button_clicked)
    main_vbox.pack_start(volume_button, True, True)
    main_vbox.pack_start(set_value_button, True, True)
    # win.add(volume_button)
    win.add(main_vbox)
    # win.window_frame.add(main_vbox)
    # gtk.timeout_add(500, set_time_position)
    win.show_all()
    gtk.main()

