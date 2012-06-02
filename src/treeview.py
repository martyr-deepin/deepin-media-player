#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Wang Yong
# 
# Author:     Hailong Qiu <qiuhailong@linuxdeepin.com>
# Maintainer: Hailong Qiu <qiuhailong@linuxdeepin.com>
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

from dtk.ui.draw import draw_pixbuf
from dtk.ui.draw import draw_font
from skin import app_theme


import gtk
from collections import OrderedDict

# 问题: 去掉多余的 鼠标移动和点击下去 画颜色.
# 图标状态转换问题.
# 滚动窗口对 treeview 无效. 

class TreeView(gtk.DrawingArea):
    
    def __init__(self, height = 30, width = 50, 
                 font_size = 10, font_color = "#000000", 
                 normal_pixbuf = app_theme.get_pixbuf("tree_view_0.png"),
                 press_pixbuf=app_theme.get_pixbuf("tree_view_1.png")):
        
        gtk.DrawingArea.__init__(self)
        # pixbuf.
        self.normal_pixbuf = normal_pixbuf
        self.press_pixbuf = press_pixbuf
        # root node.
        self.root = Tree()
        self.set_can_focus(True)
        # Init DrawingArea event.
        self.add_events(gtk.gdk.ALL_EVENTS_MASK)        
        self.connect("button-press-event", self.press_notify_event)
        self.connect("motion-notify-event", self.move_notify_event)
        self.connect("expose-event", self.draw_expose_event)
        self.connect("key-press-event", self.key_press_tree_view)
        self.connect("leave-notify-event", self.clear_move_notify_event)
        self.connect("realize", lambda w: self.grab_focus()) # focus key after realize
        # 
        self.height = height # child widget height.
        self.width = width # draw widget width.
        self.move_height = 0 #
        self.press_height = 0
        # Position y.
        self.draw_y_padding = 0
        # Draw press move bool.
        self.press_draw_bool = False
        self.move_draw_bool = False
        # Font init.
        self.font_size = font_size
        self.font_color = font_color
        # Draw tree view child widget(save postion and Tree).
        self.draw_widget_list = []
        
        # Key map dict.
        self.keymap = {
            "Up"     : self.up_key_press,
            "Down"   : self.down_key_press,
            }
        
    def clear_move_notify_event(self, widget, event): # focus-out-event
        self.move_color = False
        self.queue_draw()
        
    def up_key_press(self):
        self.move_height -= self.height
        
    def down_key_press(self):
        self.move_height += self.height
                
    def key_press_tree_view(self, widget, event):
        keyval = gtk.gdk.keyval_name(event.keyval)
        
        # Up Left.
        if self.keymap.has_key(keyval):
            self.keymap[keyval]()
        
        # Set : 0 < self.move_height > self.allocation.height ->
        if (self.move_height < 0) or (self.move_height > self.allocation.height):
            if self.move_height < 0:
                self.move_height = 0
            elif self.move_height > self.allocation.height:
                self.move_height = int(self.allocation.height) / self.height * self.height
        # expose-evet queue_draw.
        self.queue_draw()
        
    def draw_expose_event(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        x, y, w, h = rect.x, rect.y, rect.width, rect.height
        
        if self.press_draw_bool:
            cr.set_source_rgba(1, 0, 0, 0.3)
            self.draw_y_padding = int(self.press_height) / self.height * self.height
            cr.rectangle(x, y + self.draw_y_padding, w, self.height)
            cr.fill()
                                    
        if self.move_draw_bool:
            cr.set_source_rgba(0, 0, 1, 0.3)
            self.draw_y_padding = int(self.move_height) / self.height * self.height
            cr.rectangle(x, y + self.draw_y_padding, w, self.height)
            cr.fill()
        
        if self.draw_widget_list:    
            # (cr, text, font_size, font_color, x, y, width, height, 
            temp_height = 0
            for draw_widget in self.draw_widget_list:                    
                
                if draw_widget[0].name:
                    draw_font(cr, 
                              "+" + draw_widget[0].name, 
                              self.font_size, 
                              self.font_color, 
                              draw_widget[1], 
                              temp_height + self.height/2, 100, 0)
                    
                if draw_widget[0].child_show_bool:    
                    pixbuf = self.press_pixbuf.get_pixbuf()
                else:    
                    pixbuf = self.normal_pixbuf.get_pixbuf()                                        
                draw_pixbuf(cr, pixbuf, 80 + draw_widget[1], temp_height + self.height/2 - pixbuf.get_height()/2)    
                    
                temp_height += self.height
        return True
    
    def set_font_size(self, size):
        if size > self.height / 2:
            size = self.height / 2        
        self.font_size = size
        
    def press_notify_event(self, widget, event):        
        self.press_draw_bool = True
        self.press_height = event.y
        index = int(self.press_height / self.height)
        print "索引值:%s" % (index)
        if self.draw_widget_list[index][0].child_dict:
            self.draw_widget_list[index][0].child_show_bool = not self.draw_widget_list[index][0].child_show_bool 
        self.sort()
        self.queue_draw()
        
    def move_notify_event(self, widget, event):
        self.move_draw_bool = True
        self.move_height = event.y
        self.queue_draw()
        
    def add_node(self,root_name, node_name):
        self.root.add_node(root_name, node_name, Tree())
        
    def sort(self):                
        self.draw_widget_list = []
        for key in self.root.child_dict.keys():
            temp_list = [] 
            temp_list.append(self.root.child_dict[key])
            temp_list.append(0)
            self.draw_widget_list.append(temp_list)            
            
            if self.root.child_dict[key].child_dict:
                self.sort2(self.root.child_dict[key], self.width)
                
        self.queue_draw()
                    
    def sort2(self, node, width):        
        for key in node.child_dict.keys():
            if node.child_show_bool:
                temp_list = [] 
                temp_list.append(node.child_dict[key])
                temp_list.append(width)
                self.draw_widget_list.append(temp_list)            
            
                if node.child_dict[key].child_dict:
                    self.sort2(node.child_dict[key], width+self.width)
                
        
class Tree(object):
    def __init__(self):
        self.parent_node = None
        self.child_dict = OrderedDict()
        self.child_show_bool = False        
        self.name = ""
        self.pixbuf = None
        
        
    def add_node(self, root_name, node_name, node):
        # Root node add child widget.
        if not root_name:
            if node_name and node:
                # Set node.
                node.name = node_name
                self.parent_node = None
                self.child_dict[node_name] = node
        else:    
            for key in self.child_dict.keys():                
                if key == root_name:                    
                    # Set node.
                    node.name = node_name
                    self.parent_node = None
                    self.child_dict[key].child_dict[node_name] = node
                    break                
                
                self.scan_node(self.child_dict[key], root_name, node_name, node)
                    
    def scan_node(self, node, scan_root_name, node_name, save_node):
        if node.child_dict:
            for key in node.child_dict.keys():
                if key == scan_root_name:                    
                    save_node.name = node_name
                    node.child_dict[key].child_dict[node_name] = save_node
                
                else:    
                    self.scan_node(node.child_dict[key], scan_root_name, node_name, save_node)
                    
                    
    def sort(self):                
        for key in self.child_dict.keys():
            if self.child_dict[key].child_dict:
                self.sort2(self.child_dict[key])
        
    def sort2(self, node):        
        for key in node.child_dict.keys():
            if node.child_dict[key].child_dict:
                self.sort2(node.child_dict[key])
                
                
#======== Test ===============
from dtk.ui.scrolled_window import ScrolledWindow

if __name__ == "__main__":    
    scrolled_window = ScrolledWindow()
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)        
    win.connect("destroy", gtk.main_quit)
    tree_view = TreeView()
    scrolled_window.add_child(tree_view)
    win.add(scrolled_window)
    win.show_all()
    tree_view.add_node(None, "小学")
    tree_view.add_node(None, "初中")
    tree_view.add_node(None, "大学")
    
    tree_view.add_node("小学", "1年级")
    tree_view.add_node("1年级", "1:1:2")    
    tree_view.add_node("小学", "2年级")
    tree_view.add_node("小学", "3年级")
    
    tree_view.add_node("大学", "软件学院")
    tree_view.add_node("软件学院", "ZB48901")
    tree_view.add_node("软件学院", "ZB48902")
    tree_view.add_node("软件学院", "ZB48903")
    tree_view.add_node("大学", "工商学院")
    tree_view.add_node("大学", "理工学院")
    tree_view.add_node("大学", "机电学院")

    tree_view.sort()    
    

    gtk.main()

    
