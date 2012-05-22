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

import gtk
from dtk.ui.scrolled_window import ScrolledWindow                       

class TreeView(object):
    def __init__(self):
        self.tree_root = TREE()
        self.root_x = 10
        self.root_y = 10
        
        
        self.fixed = gtk.Fixed()        
        
        self.scrolled_window = ScrolledWindow()
        self.scrolled_window.add_child(self.fixed)
        
        
    def create_root_node(self, name, node):    
        if self.tree_root.add_root_node(name, node):
            node.x = self.root_x
            node.y = self.root_y
            self.root_y += 30
            # node.widget ad events expose-event.
            node.widget.connect("expose-event", self.draw_tree_view_line)
            # Fixe widget add child node.
            self.fixed.put(node.widget, node.x, node.y)
        
            
    def create_child_node(self father_name, child_name, child_node):        
        pass
        
        
    def draw_tree_view_line(self, widget, event):
       
        cr = widget.window.cairo_create()
        x, y, w, h = widget.allocation
                
        cr.set_line_width(0.5)
        cr.set_source_rgba(0, 0, 0, 1)
        
        # Draw h.
        cr.move_to(x-1, y + h / 2)
        cr.line_to(x+3 , y + h / 2)
        cr.stroke()
        # Draw v.
        cr.move_to(x-1, y + h / 2)
        cr.line_to(x-1, y + h / 2 + 30)
        cr.stroke()
        
        # cr.rectangle(x, y, w, h)
        # cr.fill()                
        
        if "get_child" in dir(widget) and widget.get_child() != None:
            widget.propagate_expose(widget.get_child(), event)
        
        return True
       
    
    
    
##################################################################        
#
#        
# nodes node.       
# tree  (nodes)->add root node. add child node... ..       
#
##################################################################        
class NODES(object):        
    '''Node value.'''
    def __init__(self, title):
        self.node_list = []  # node all nodes childs.                                              
        self.widget = gtk.Button(title) # save widget(gtk).
        self.title = title   # widget show title name.
        self.falgs = False   # Show and Hide all widget childs.
        self.x = 0           # widget position x.
        self.y = 0           # widget position y.
        self.width = 0       # widget width.
        self.height = 0      # widget height.
        
        
class TREE(object):        
    '''Tree struct.'''
    def __init__(self):        
        self.tree_list = []
        self.node_dict = {}
                
    def add_root_node(self, name, node):    
        '''Add tree node.'''
        if not self.node_dict.has_key(name):
            self.tree_list.append(node)
            self.node_dict[name] = node        
            return True
        else:    
            return False
        
    def add_node_child(self, name, node_name, node):            
        '''Add node child.'''
        if not self.node_dict.has_key(node_name) and self.node_dict.has_key(name):
            # print self.node_dict[name]
            self.node_dict[name].node_list.append(node)
            self.node_dict[node_name] = node 
            return True
        else:
            return False
                    
    def print_tree_list(self):         
        print self.tree_list                            
            
    def get_node_childs(self, node_name):    
        if self.node_dict.has_key(node_name):
            return self.node_dict[node_name].node_list
        else:
            return None
        
    def get_root_other_node(self, node_name):
        childs = []
        for node in self.tree_list:
            if not self.node_dict[node_name] == node:
                childs.append(node)                            
        return childs
    
    def get_tree_all_root_node(self):
        return self.tree_list
    
##########################################################################            
        
        
if __name__ == "__main__":        
    tree_view = TreeView()        
    tree_view.create_root_node("A", NODES("A"))
    tree_view.create_root_node("B", NODES("B"))
    tree_view.create_root_node("C", NODES("C"))
    tree_view.create_root_node("D", NODES("D"))
    tree_view.create_root_node("E", NODES("E"))
    tree_view.create_root_node("F", NODES("F"))
    tree_view.create_root_node("G", NODES("G"))
    tree_view.create_root_node("H", NODES("H"))
    tree_view.create_root_node("I", NODES("I"))
    tree_view.create_root_node("J", NODES("J"))
    tree_view.create_root_node("K", NODES("K"))
    tree_view.create_root_node("L", NODES("L"))
    
    
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    win.set_size_request(300, 300)
    win.connect("destroy", gtk.main_quit)
    win.add(tree_view.scrolled_window)
    win.show_all()
    gtk.main()
        
        
        
