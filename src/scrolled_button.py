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

import gtk
import gobject

class ScrolledButton(gtk.HBox):     
    def __init__(self):
        gtk.HBox.__init__(self)
        
        self.scrol_win = gtk.ScrolledWindow()
        # Set Scrolled Window policy type.
        self.scrol_win.set_policy(gtk.POLICY_NEVER,
                                  gtk.POLICY_NEVER)
        self.scrol_hbox = gtk.HBox()
        
        # Scrolled Window add scrol_hbox.
        self.scrol_win.add_with_viewport(self.scrol_hbox)
        
        self.left_btn = gtk.Button("<")
        self.left_btn.set_size_request(30, 30)
        # Left button events.
        self.left_btn.connect("clicked", self.left_button_clicked)
        
        self.right_btn = gtk.Button(">")
        self.right_btn.set_size_request(30, 30)
        # Right buton events.
        self.right_btn.connect("clicked", self.right_buton_clicked)
        self.pack_start(self.left_btn, False, False)
        self.pack_start(self.scrol_win, True, True)
        self.pack_start(self.right_btn, False, False)
                
        self.value = 0
        
    def get_hbox_child_width(self):    
        child_width = 0
        child_num   = 0
        for child in self.scrol_hbox.get_children():
            child_num += 1  
            child_width += child.allocation.width
        if child_width:    
            child_width = child_width / child_num          
        return child_width
    
    
    # def left_button_clicked(self, widget):
        # '''Left'''
    def right_buton_clicked(self, widget):
        # '''Right'''
        # Get scrol_win hadju.                    
        hadju = self.scrol_win.get_hadjustment()
        child_width = self.get_hbox_child_width()
        if self.value < hadju.get_upper() - self.scrol_win.allocation.width - child_width:
            hadju.set_value(hadju.get_value() + child_width) # Set hadju value.
            self.value = hadju.get_value() # Save hadju value.
            
    # def right_buton_clicked(self, widget):
        # '''Right'''
    def left_button_clicked(self, widget):
        '''Left'''    
        hadju = self.scrol_win.get_hadjustment()
        child_width = self.get_hbox_child_width()
        # hadju = self.scrol_win.get_hadjustment()
        hadju.set_value(hadju.get_value() - child_width)
        self.value = hadju.get_value() # Save hadju value.
                    
        
# Register widget.
gobject.type_register(ScrolledButton)        


if __name__ == "__main__":
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    win.set_size_request(200, 200)
    scrol_btn=ScrolledButton()
    scrol_btn.add_widget(gtk.Button("aaa"))
    scrol_btn.add_widget(gtk.Button("bbbb"))
    scrol_btn.add_widget(gtk.Button("ccc"))
    scrol_btn.add_widget(gtk.Button("ddd"))
    scrol_btn.add_widget(gtk.Button("eeee"))
    scrol_btn.add_widget(gtk.Button("fff"))
    scrol_btn.add_widget(gtk.Button("ggg"))
    scrol_btn.add_widget(gtk.Button("iii"))
    scrol_btn.add_widget(gtk.Button("jjj"))
    scrol_btn.add_widget(gtk.Button("ggg"))
    win.add(scrol_btn)
    win.show_all()
    gtk.main()
