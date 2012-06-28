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

from skin import app_theme
import gobject
import gtk

# open button state.
OPEN_BUTTON_STATE_NORMAL = 0
OPEN_BUTTON_STATE_PRESS  = 1
OPEN_BUTTON_STATE_HOVER  = 2


class OpenButton(gobject.GObject):    
    __gsignals__ = {
        "openbutton-clicked-event":(gobject.SIGNAL_RUN_LAST,
                                    gobject.TYPE_NONE,(gobject.TYPE_PYOBJECT,)),        
        "openbutton-press-event":(gobject.SIGNAL_RUN_LAST,
                                    gobject.TYPE_NONE,(gobject.TYPE_PYOBJECT,)),
        "openbutton-release-event":(gobject.SIGNAL_RUN_LAST,
                                    gobject.TYPE_NONE,(gobject.TYPE_PYOBJECT,)),
        "openbutton-motion-event":(gobject.SIGNAL_RUN_LAST,
                                   gobject.TYPE_NONE,(gobject.TYPE_PYOBJECT,)),
        "openbutton-leave-event":(gobject.SIGNAL_RUN_LAST,
                                   gobject.TYPE_NONE,(gobject.TYPE_PYOBJECT,)),
        "openbutton-enter-event":(gobject.SIGNAL_RUN_LAST,
                                   gobject.TYPE_NONE,(gobject.TYPE_PYOBJECT,)),        
        }
    def __init__(self,
                 draw_window,
                 width=120, height=40,  
                 normal_pixbuf = app_theme.get_pixbuf("normal_button_left.png"),
                 hover_button_pixbuf = app_theme.get_pixbuf("hover_button_left.png"),
                 press_button_pixbuf = app_theme.get_pixbuf("press_button_left.png")):
        gobject.GObject.__init__(self)
        '''Init set openbutton attr.'''
        self.draw_window = draw_window
        '''Init pixbuf.'''
        self.normal_pixbuf       = normal_pixbuf
        self.hover_button_pixbuf = hover_button_pixbuf
        self.press_button_pixbuf = press_button_pixbuf
        '''Init events.'''
        self.draw_window.add_events(gtk.gdk.ALL_EVENTS_MASK)
        self.draw_window.connect("button-press-event", self.emit_open_button_press)
        self.draw_window.connect("button-release-event", self.emit_open_button_release)
        self.draw_window.connect("motion-notify-event", self.emit_open_button_motion)
        '''Init state'''
        self.state = OPEN_BUTTON_STATE_NORMAL
        '''Init value.'''
        self.__padding_x = 0
        self.__padding_y = 0
        self.__x      = 0
        self.__y      = 0
        self.width  = width
        self.height = height
        
        self.visible_bool = False
        
        self.leave_bool = False
        self.clicked_bool = False
        self.press_bool = False        
        
                
    def move(self, x, y):    
        self.__padding_x = x
        self.__padding_y = y
        self.draw_window.queue_draw()
        
    def set_visible(self, visible_bool):    
        self.visible_bool = visible_bool        
        self.queue_draw()
        
    def set_size(self, w, h):    
        self.width = w
        self.height = h
        
    def emit_open_button_motion(self, widget, event):    
        temp_x = event.x
        temp_y = event.y
        
        
        if (self.__x + self.__padding_x <= temp_x <= self.__x + self.width + self.__padding_x) and (self.__y + self.__padding_y <= temp_y <= self.__y + self.__padding_y + self.height):        
            if not self.leave_bool:
                self.emit("openbutton-enter-event", event)
                if not self.press_bool:
                    self.state = OPEN_BUTTON_STATE_HOVER
                    self.queue_draw()
                
            if not self.visible_bool:    
                self.leave_bool = True                
                
            self.emit("openbutton-motion-event", event)            
        else:    
            if self.leave_bool:
                self.emit("openbutton-leave-event", event)                                
                if not self.press_bool:
                    self.state = OPEN_BUTTON_STATE_NORMAL
                    self.queue_draw()
                self.leave_bool = False
                
                
    def queue_draw(self):            
        self.draw_window.queue_draw_area(self.__x, self.__x, self.width, self.height)
        
    def emit_open_button_press(self, widget, event):    
        temp_x = event.x
        temp_y = event.y
        
        if (self.__x + self.__padding_x <= temp_x <= self.__x + self.width + self.__padding_x) and (self.__y + self.__padding_y <= temp_y <= self.__y + self.__padding_y + self.height):
            self.emit("openbutton-press-event", event)
            if not self.visible_bool:
                self.press_bool = True                                
                self.state = OPEN_BUTTON_STATE_PRESS
            self.queue_draw()    
            
    def emit_open_button_release(self, widget, event):        
        temp_x = event.x
        temp_y = event.y
        if self.press_bool:
            self.emit("openbutton-release-event", event)
            self.queue_draw()
        if (self.__x + self.__padding_x <= temp_x <= self.__x + self.width + self.__padding_x) and (self.__y + self.__padding_y <= temp_y <= self.__y + self.__padding_y + self.height):           
            if self.press_bool:
                self.emit("openbutton-clicked-event", event)
                self.state = OPEN_BUTTON_STATE_HOVER                
        else:        
            self.state = OPEN_BUTTON_STATE_NORMAL

        self.press_bool = False
        self.queue_draw()
        # self.draw_window.queue_draw()        
                                
    def draw_open_button(self, widget, event):
        if not self.visible_bool:
            cr = widget.window.cairo_create()
            x, y, w, h = widget.allocation
        
            self.__x = x + w/2 - self.width/2
            self.__y = y + h/2 - self.height/2
            if self.state == OPEN_BUTTON_STATE_NORMAL:            
                pixbuf  = self.normal_pixbuf
            elif self.state == OPEN_BUTTON_STATE_HOVER:
                pixbuf  = self.hover_button_pixbuf
            elif self.state == OPEN_BUTTON_STATE_PRESS:                            
                pixbuf  = self.press_button_pixbuf
            print self.state    
            image = pixbuf.get_pixbuf().scale_simple(self.width,
                                        self.height,
                                        gtk.gdk.INTERP_NEAREST)
                
            cr.set_source_pixbuf(image,
                                 self.__x + self.__padding_x,
                                 self.__y + self.__padding_y)
            cr.paint_with_alpha(1)        
    
gobject.type_register(OpenButton)        


if __name__ == "__main__":
    
    def draw_expose_event(widget, event):
        cr = widget.window.cairo_create()
        x, y, w, h = widget.allocation
        cr.rectangle(x, y, w, h)
        cr.fill()
        open_button.draw_open_button(widget, event)        
        open_button2.draw_open_button(widget, event)
        open_button3.draw_open_button(widget, event)
        return True
    
    def test_openbutton_clicked_event(widget, event):        
        print "单击事件"
    
    def test_openbutton_press_event(widget, event):        
        print "print 你触发按下事件"
        
    def test_openbutton_release_event(widget, event):    
        print "print 松开了"
        
    def test_openbutton_motion_event(widget, event):    
        print "你处罚了 移动时间"
        
    def test_openbutton_enter_event(widget, event):    
        print "鼠标进入了"
        
    def test_openbutton_leave_event(widget, event):    
        print "鼠标离开了"
        
    
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    win.connect("destroy", gtk.main_quit)    
    screen = gtk.DrawingArea()
    open_button = OpenButton(screen)
    open_button2 = OpenButton(screen)
    open_button3 = OpenButton(screen)
    open_button2.move(130, 100)
    open_button3.move(50, 100)
    open_button.connect("openbutton-press-event", test_openbutton_press_event)
    open_button.connect("openbutton-release-event", test_openbutton_release_event)
    open_button.connect("openbutton-motion-event", test_openbutton_motion_event)
    open_button.connect("openbutton-enter-event", test_openbutton_enter_event)
    open_button.connect("openbutton-leave-event",  test_openbutton_leave_event)
    open_button.connect("openbutton-clicked-event", test_openbutton_clicked_event)
    
    screen.connect("expose-event", draw_expose_event)
    
    win.add(screen)
    win.show_all()
    gtk.main()
    
