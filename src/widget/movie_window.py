#!coding:utf-8
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

import gobject
import gtk
from gtk import gdk
  
  
class MovieWindow(gtk.Bin):
    def __init__(self):
        gtk.Bin.__init__(self)
        self.add_events(gtk.gdk.ALL_EVENTS_MASK)
        #
        self.__init_values()

    def __init_values(self):
        self.__top_child    = None
        self.__bottom_child = None

    def do_realize(self):
        gtk.Bin.do_realize(self)
        # 
        self.__create_bin_window()
        self.__create_viewport_window()
        self.__create_top_toolbar_window()
        self.__create_bottom_toolbar_window()
        #
        self.queue_resize()

    def __create_bin_window(self):
        self.__bin_window = gdk.Window(
            self.get_parent_window(),
            window_type=gdk.WINDOW_CHILD,
            x=self.allocation.x,
            y=self.allocation.y,
            width=self.allocation.width,
            height=self.allocation.height,
            colormap=self.get_colormap(),
            wclass=gdk.INPUT_OUTPUT,
            visual=self.get_visual(),
            event_mask=(self.get_events() 
                      | gdk.EXPOSURE_MASK 
                      | gdk.VISIBILITY_NOTIFY_MASK
                      ))
        self.__bin_window.set_user_data(self)
        self.style.set_background(self.__bin_window, gtk.STATE_NORMAL)
        #

    def __create_viewport_window(self):
        self.__viewport_window = gdk.Window(
            self.__bin_window,
            window_type=gdk.WINDOW_CHILD,
            x=0,
            y=0,
            width=self.allocation.width,
            height=self.allocation.height,
            visual=self.get_visual(),
            colormap=self.get_colormap(),
            wclass=gdk.INPUT_OUTPUT,
            event_mask=(self.get_events() 
                      | gdk.EXPOSURE_MASK
                      | gdk.BUTTON_MOTION_MASK
                      | gdk.ENTER_NOTIFY_MASK
                      | gdk.LEAVE_NOTIFY_MASK
                      | gdk.POINTER_MOTION_HINT_MASK
                      | gdk.BUTTON_PRESS_MASK
                      ))
        self.__viewport_window.set_user_data(self)
        self.style.set_background(self.__viewport_window, gtk.STATE_NORMAL)
        if self.child:
            self.child.set_parent_window(self.__bin_window)

    def __create_top_toolbar_window(self):
        self.top_toolbar_expose_event = None
        self.__top_toolbar_h = 30 
        self.__top_toolbar_window = gdk.Window(
            self.__bin_window,
            window_type=gdk.WINDOW_CHILD,
            x=0,
            y=0,
            width=self.allocation.width,
            height=self.__top_toolbar_h,
            visual=self.get_visual(),
            colormap=self.get_colormap(),
            wclass=gdk.INPUT_OUTPUT,
            event_mask=(self.get_events() 
                      | gdk.EXPOSURE_MASK
                      | gdk.BUTTON_MOTION_MASK
                      | gdk.ENTER_NOTIFY_MASK
                      | gdk.LEAVE_NOTIFY_MASK
                      | gdk.POINTER_MOTION_HINT_MASK
                      | gdk.BUTTON_PRESS_MASK
                      ))
        self.__top_toolbar_window.set_user_data(self)
        self.style.set_background(self.__top_toolbar_window, gtk.STATE_NORMAL)
        #
        if self.__top_child:
            self.__top_child.set_parent_window(self.__top_toolbar_window)

        
    def __create_bottom_toolbar_window(self):
        self.bottom_toolbar_expose_event = None
        self.__bottom_toolbar_h = 120
        self.__bottom_toolbar_window = gdk.Window(
            self.__bin_window,
            window_type=gdk.WINDOW_CHILD,
            x=0,
            y=0,
            width=self.allocation.width,
            height=self.__bottom_toolbar_h,
            visual=self.get_visual(),
            colormap=self.get_colormap(),
            wclass=gdk.INPUT_OUTPUT,
            event_mask=(self.get_events() 
                      | gdk.EXPOSURE_MASK
                      | gdk.BUTTON_MOTION_MASK
                      | gdk.ENTER_NOTIFY_MASK
                      | gdk.LEAVE_NOTIFY_MASK
                      | gdk.POINTER_MOTION_HINT_MASK
                      | gdk.BUTTON_PRESS_MASK
                      ))
        self.__bottom_toolbar_window.set_user_data(self)
        self.style.set_background(self.__bottom_toolbar_window, gtk.STATE_NORMAL)
        if self.__bottom_child:
            self.__bottom_child.set_parent_window(self.__bottom_toolbar_window)

    def do_motion_notify_event(self, e):
        bo_size = self.__bottom_toolbar_window.get_size()
        self.allocation
        y = int(e.y)
        if not e.window in [self.__bottom_toolbar_window, self.__top_toolbar_window]:
            self.hide_top_toolbar()
            self.hide_bottom_toolbar()

        if self.allocation.y + self.allocation.height - bo_size[1] < y < self.allocation.y + self.allocation.height:
            self.show_bottom_toolbar()
        elif self.allocation.y < y < self.allocation.y + self.__top_toolbar_h:
            if e.window != self.__bottom_toolbar_window:
                self.show_top_toolbar()

        return False

    def do_button_press_event(self, e):
        return False

    def do_button_release_event(self, e):
        return False

    def do_enter_notify_event(self, e):
        return False
        
    def do_leave_notify_event(self, e):
        if e.window == self.__top_toolbar_window:
            position = self.get_parent_window().get_position()
            temp_x = int(e.x_root)
            temp_y = int(e.y_root)
            t_size = self.__top_toolbar_window.get_size()
            if ((position[1] >= temp_y) or 
                (position[0] >= temp_x) or 
                (position[0] + t_size[0] <= temp_x)):
                self.hide_top_toolbar()
        elif e.window == self.__bottom_toolbar_window:
            position = self.get_parent_window().get_position()
            temp_x = int(e.x_root)
            temp_y = int(e.y_root)
            if (temp_y >= position[1] + self.allocation.height or
                temp_x >= position[0] + self.allocation.width  or
                temp_x < position[0]):
                self.hide_bottom_toolbar()
        return False
        
    def do_unrealize(self):
        self.__bin_window.set_user_data(None)
        self.__bin_window.destroy()
        self.__bin_window = None
        #
        self.__viewport_window.set_user_data(None)
        self.__viewport_window.destroy()
        self.__viewport_window = None
        #
        self.__top_toolbar_window.set_user_data(None)
        self.__top_toolbar_window.destroy()
        self.__top_toolbar_window = None
        #
        self.__bottom_toolbar_window.set_user_data(None)
        self.__bottom_toolbar_window.destroy()
        self.__bottom_toolbar_window = None
        #
        gtk.Bin.do_unrealize(self)
  
    def do_expose_event(self, event):
        if event.window == self.__top_toolbar_window:
            if self.top_toolbar_expose_event:
                self.top_toolbar_expose_event(self.__top_toolbar_window, self.allocation)
            gtk.Bin.do_expose_event(self, event)
            return True
        if event.window == self.__bottom_toolbar_window:
            if self.bottom_toolbar_expose_event:
                self.bottom_toolbar_expose_event(self.__bottom_toolbar_window, self.allocation)
            gtk.Bin.do_expose_event(self, event)
            return True
        else:
            gtk.Bin.do_expose_event(self, event)
        return False

    def do_map(self):
        gtk.Bin.do_map(self)
        self.set_flags(gtk.MAPPED)
        #self.__viewport_window.show()
        self.__bin_window.show()

    def do_unmap(self):
        self.__bin_window.hide()
        self.__viewport_window.hide()
        self.__top_toolbar_window.hide()
        self.__bottom_toolbar_window.hide()
        gtk.Bin.do_unmap(self)
  
    def do_show(self):
        gtk.Bin.do_show(self)
        #print self.__viewport_window.xid



    def do_size_request(self, req):
        if self.child:
            self.child.size_request()
        if self.__top_child:
            self.__top_child.size_request()
        if self.__bottom_child:
            self.__bottom_child.size_request()
  
    def do_size_allocate(self, allocation):
        self.allocation = allocation
        self.allocation.x = 0
        self.allocation.y = 0
        # set child widget.
        if self.child:
            allocation = gdk.Rectangle()
            allocation.x = self.allocation.x
            allocation.y = self.allocation.y
            allocation.width = self.allocation.width
            allocation.height = self.allocation.height
            self.child.size_allocate(allocation)

        if self.flags() & gtk.REALIZED:
            self.__bin_window.move_resize(*self.allocation)
                                     
            # 布局窗口.
            self.__viewport_window.move_resize(*self.allocation)
            #
            top_toolbar_allocation        = gdk.Rectangle()
            top_toolbar_allocation.x      = self.allocation.x
            top_toolbar_allocation.y      = self.allocation.y
            top_toolbar_allocation.width  = self.allocation.width
            top_toolbar_allocation.height = self.__top_toolbar_h
            self.__top_toolbar_window.move_resize(*top_toolbar_allocation)
            if self.__top_child:
                self.__top_child.size_allocate(top_toolbar_allocation)
            #
            bottom_toolbar_allocation        = gdk.Rectangle()
            bottom_toolbar_allocation.x      = self.allocation.x
            bottom_toolbar_allocation.y      = self.allocation.y + self.allocation.height - self.__bottom_toolbar_h
            bottom_toolbar_allocation.width  = self.allocation.width
            bottom_toolbar_allocation.height = self.__bottom_toolbar_h
            self.__bottom_toolbar_window.move_resize(*bottom_toolbar_allocation)
            if self.__bottom_child:
                bottom_toolbar_allocation.y = self.allocation.x
                self.__bottom_child.size_allocate(bottom_toolbar_allocation)

    def do_add(self, widget):
        gtk.Bin.do_add(self, widget)
        self.add_widget(widget)
  
    def do_remove(self, widget):
        widget.unparent()

    def add_widget(self, child):
        self.child = child
        if self.flags() & gtk.REALIZED:
            child.set_parent_window(self.__viewport_window)

    def top_add_widget(self, child):
        self.__top_child = child
        if self.flags() & gtk.REALIZED:
            child.set_parent_window(self.__top_toolbar_window)
        self.__top_child.set_parent(self)
  
    def bottom_add_widget(self, child):
        self.__bottom_child = child
        if self.flags() & gtk.REALIZED:
            child.set_parent_window(self.__bottom_toolbar_window)
        self.__bottom_child.set_parent(self)

    def set_size_request(self, w, h):
        if self.flags() & gtk.REALIZED:
            self.__viewport_window.size(w, h)

    def do_forall(self, include_internals, callback, data):
        if self.child:
            callback(self.child, data)
        if self.__top_child:
            callback(self.__top_child, data)
        if self.__bottom_child:
            callback(self.__bottom_child, data)

    def show_top_toolbar(self):
        self.__top_toolbar_window.show()

    def hide_top_toolbar(self):
        self.__top_toolbar_window.hide()

    def show_bottom_toolbar(self):
        self.__bottom_toolbar_window.show()

    def hide_bottom_toolbar(self):
        self.__bottom_toolbar_window.hide()

gobject.type_register(MovieWindow) 


if __name__ == '__main__':
    def btn_expose_event( widget, event):
        cr = widget.window.cairo_create()
        cr.set_source_rgb(0, 0, 1)
        cr.rectangle(*widget.allocation)
        cr.fill()
        return True
    window = gtk.Window()
    #window.set_decorated(False)
    window.connect('delete-event', gtk.main_quit)
    window.set_size_request(300, 300)
    hbox = gtk.HBox()
    code_edit = MovieWindow()
    ali = gtk.Alignment(0, 0, 1, 1)
    #ali.set_padding(5, 5, 5, 5)
    btn = gtk.Button("fjdskf") #gtk.DrawingArea() 
    #btn.unset_flags(gtk.DOUBLE_BUFFERED)
    btn.connect("expose-event", btn_expose_event)
    ali.add(btn)
    code_edit.add(ali)
    test_ali  = gtk.Alignment(0, 0, 0, 1)
    test_hbox = gtk.HBox()
    test_ali.add(test_hbox)
    test_hbox.pack_start(gtk.Button("fjdsfk"))
    '''
    test_hbox.pack_start(gtk.Button("fjdsfk"))
    test_hbox.pack_start(gtk.Button("fjdsfk"))
    test_hbox.pack_start(gtk.Button("fjdsfk"))
    test_hbox.pack_start(gtk.Button("fjdsfk"))
    '''
    code_edit.top_add_widget(test_ali)
    test_hbox2 = gtk.HBox()
    test_ali2  = gtk.Alignment(0, 0, 0, 1)
    test_ali2.add(test_hbox2)
    test_hbox2.pack_start(gtk.Button("fjdsfk"))
    test_hbox2.pack_start(gtk.Button("fjdsfk"))
    '''
    test_hbox2.pack_start(gtk.Button("fjdsfk"))
    test_hbox2.pack_start(gtk.Button("fjdsfk"))
    test_hbox2.pack_start(gtk.Button("fjdsfk"))
    '''
    code_edit.bottom_add_widget(test_ali2)
    hbox.pack_start(code_edit)
    hbox.pack_start(gtk.Button("fdjskf"), False, False)
    hbox.show_all()
    window.add(hbox)
    window.show_all()
    gtk.main()



