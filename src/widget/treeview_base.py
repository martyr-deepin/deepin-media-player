#! /usr/bin/ python
# -*- coding: utf-8 -*-

# Copyright (C) 2013 Deepin, Inc.
#               2013 Hailong Qiu
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



from utils import get_match_parent
#from utils import propagate_expose
from utils import get_text_size, is_left_button # 左键.
from draw  import draw_text, draw_pixbuf
from color import alpha_color_hex_to_cairo, color_hex_to_cairo
import gtk
from gtk import gdk
import gobject
import random


def type_check(type_name, type_str):
    return type(type_name).__name__ == type_str

class TreeViewBase(gtk.Button):
    def __init__(self):
        gtk.Button.__init__(self)
        self.__init_values()
        self.__init_events()

    def __init_events(self):
        self.connect("realize",              self.__treeview_realize_event)
        self.connect("button-press-event",   self.__treeview_button_press_event)
        self.connect("expose-event",         self.__treeview_expose_event)
        self.connect("motion-notify-event",  self.__treeview_motion_notify_event)

    def __treeview_realize_event(self, widget):
        widget.set_realized(True)
        self.__init_scroll_win()

    def __treeview_button_press_event(self, widget, event):
        node = self.__nodes_list[int(e.y/self.node_height)]
        node.is_expanded = not node.is_expanded
        self.tree_view_queue_draw_area()
        return False
    
    def __init_values(self):
        self.add_events(gtk.gdk.ALL_EVENTS_MASK)
        #
        self.header_height = 25
        self.node_height   = 25
        self.leave_width   = 20
        #
        self.children = []
        self.motion_items = []
        self.single_items = []
        #
        self.paint_nodes_event = self.__paint_nodes_event
        self.paint_nodes_background = self.__paint_nodes_background
        #
        self.__function_dict = {}
        self.__nodes_list = []
        self.nodes = Nodes()
        self.nodes.connect("update-data", self.__nodes_update_data_event)
        self.nodes.connect("added-data",  self.__nodes_added_data_event)
        self.nodes.connect("remove-data", self.__nodes_remove_data_event)
        self.nodes.connect("is-expanded", self.__nodes_is_expanded_event)
        #
        self.__init_values_columns()

    def __nodes_update_data_event(self, node):
        # 当有数据更新时,进行重绘.
        # 判断是否在重绘的区域内,如果不是,只设置数据.
        if self.tree_view_find_node_in_draw_area(node):
            self.tree_view_queue_draw_area()

    def __nodes_added_data_event(self, node):
        # 添加数据更新树型结构的映射列表.
        if node.parent == self.nodes:
            self.__nodes_list.append(node)
            self.__tree_view_set_add_size()
       
    def __nodes_is_expanded_event(self, node):
        #print "__nodes_is_expanded_event", node.text
        if node.is_expanded:
            if node.nodes: # 判断是否有子节点.
                if node.leave: # 判断是不是根节点.
                    if not node.parent.this.is_expanded: # 判断父亲节点是否已经展开了.
                        node.parent.this.is_expanded = True
                        for child_node in node.nodes:
                            self.__nodes_add_data(child_node)
                    else:
                        for child_node in node.nodes:
                            self.__nodes_add_data(child_node)
                else:
                    for child_node in node.nodes:
                        self.__nodes_add_data(child_node)
        elif not node.is_expanded:
            for flase_child_node in node.nodes:
                flase_child_node.is_expanded = False
                self.__nodes_remove_data(flase_child_node)

    def __nodes_add_data(self, node):
        parent = node.parent
        node_to_parent_index = parent.index(node)
        parent_to_list_index = self.__nodes_list.index(parent.this)
        index = parent_to_list_index + node_to_parent_index + 1
        self.__nodes_list.insert(index, node)
        self.__tree_view_set_add_size()

    def __nodes_remove_data(self, node):
        index = self.__nodes_list.index(node)
        self.__nodes_list.pop(index)
        self.__tree_view_set_remove_size()

    def __tree_view_set_add_size(self):
        size = self.get_size_request()
        self.set_size_request(size[0], size[1] + self.node_height)

    def __tree_view_set_remove_size(self):
        size = self.get_size_request()
        self.set_size_request(size[0], size[1] - self.node_height)

    def __nodes_remove_data_event(self, node):
        # 当有数据删除时,更新映射列表.
        print "remove............", node.text
        if node in self.__nodes_list:
            self.__nodes_list.remove(node)
        # 判断删除的数据是否在重绘区域,如果不是,不进行重绘.
        if self.tree_view_find_node_in_draw_area(node):
            self.tree_view_queue_draw_area()

    def __init_values_columns(self):
        self.columns = []

    def connect_event(self, event_name, function_potion):
        self.__function_dict[event_name] = function_point

    def emit(self, event_name, *arg):
        if self.__function_dict.has_key(event_name):
            self.__function_dict[event_name](*arg)

    def __init_scroll_win(self):
        self.scroll_win = get_match_parent(self, ["ScrolledWindow"])
        self.hadjustment = self.scroll_win.get_hadjustment()
        self.vadjustment = self.scroll_win.get_vadjustment()
        self.hadjustment.connect("value-changed", self.__list_view_adjustments_changed)
        self.vadjustment.connect("value-changed", self.__list_view_adjustments_changed)

    def __list_view_adjustments_changed(self, adjustments):
        self.tree_view_queue_draw_area()

    def __treeview_expose_event(self, w, e):
        cr = w.window.cairo_create()
        start_index  = max(int(self.scroll_win.get_vadjustment().get_value() / self.node_height), 0)
        end_index    = (start_index + (self.scroll_win.allocation.height) / self.node_height) + 1
        y_padding = 0 + start_index * self.node_height
        # draw background.
        x = 0
        y = 0 + start_index * self.node_height 
        w = self.scroll_win.allocation.width
        h = self.scroll_win.allocation.height + self.node_height * 2
        self.paint_nodes_background(cr, x, y, w, h)
        # draw node.
        for node in self.__nodes_list[start_index:end_index]:
            node_event = NodesEvent()
            node_event.cr = cr
            node_event.node = node
            node_event.x = 0
            node_event.y = y_padding
            node_event.w = self.scroll_win.allocation.width
            node_event.h = self.node_height #self.scroll_win.allocation.height
            #
            node_event.motion_items = self.motion_items
            node_event.single_items = self.single_items
            '''
            node_event.draw_text = draw_text # 写成 set/get , 忽略 cr参数.
            node_event.draw_pixbuf = draw_pixbuf # 写成 set/get , 忽略 cr参数.
            '''
            self.paint_nodes_event(node_event)
            y_padding += self.node_height
        #
        return True

    def __paint_nodes_background(self, cr, x, y, w, h):
        cr.set_source_rgba(*alpha_color_hex_to_cairo(("#272727",1.0)))
        cr.rectangle(x, y, w, h)
        cr.fill()

    def __paint_nodes_event(self, node_event):
        if node_event.node.leave == 0: # 根节点.
            x = node_event.x + 15
            if node_event.node.is_expanded:
                root_text = "-"
            else:
                root_text = "+"
            draw_text(node_event.cr, 
                      root_text, 
                      node_event.x + 5, 
                      node_event.y + get_text_size("+")[1]/2)
        else:
            x_padding = node_event.node.leave * self.leave_width
            x = node_event.x + 10 + x_padding
            if node_event.node.is_expanded:
                draw_text(node_event.cr, 
                          "*", 
                          node_event.x + x_padding, 
                          node_event.y + get_text_size("*")[1]/2)
            else:
                if node_event.node.leave < 2:
                    draw_text(node_event.cr, 
                              ">", 
                              node_event.x + x_padding, 
                              node_event.y + get_text_size(">")[1]/2)
        draw_text(node_event.cr, 
                  node_event.node.text, 
                  x,
                  node_event.y + get_text_size(node_event.node.text)[1]/2)

    def tree_view_queue_draw_area(self):
        self.scroll_win = get_match_parent(self, ["ScrolledWindow"])
        if self.scroll_win:
            start_index  = max(int(self.scroll_win.get_vadjustment().get_value() / self.node_height), 0)
            end_index    = (start_index + (self.scroll_win.allocation.height) / self.node_height) + 1
            w = self.scroll_win.allocation.width
            h = self.scroll_win.allocation.height
        else:
            start_index = 0
            end_index = self.allocation.height / self.allocation.height
            w = self.allocation.width
            h = self.allocation.height
        x = 0
        y = 0 + start_index * self.node_height 
        self.queue_draw_area(x, y, w, h)

    def tree_view_find_node_in_draw_area(self, node):
        if node in self.__nodes_list:
            index = self.__nodes_list.index(node)
            #
            self.scroll_win = get_match_parent(self, "ScrolledWindow")
            if self.scroll_win:
                start_index  = max(int(self.scroll_win.get_vadjustment().get_value() / self.node_height), 0)
                end_index    = (start_index + (self.scroll_win.allocation.height) / self.node_height) + 1
            else:
                start_index = 0
                end_index = 0
            if start_index <= index <= end_index:
                return True
        return False

    def __treeview_motion_notify_event(self, w, e):
        #print "do--mo--no--ev", e.x
        index = int(e.y) / self.node_height
        if index < len(self.__nodes_list):
            node = self.__nodes_list[index]
            self.motion_items = [node]
            self.tree_view_queue_draw_area()
            self.emit("treeview-motion-event", self, node)
        else:
            self.motion_items = []
            self.tree_view_queue_draw_area()
        return False

    def __treeview_button_press_event(self, w, e):
        index = int(e.y / self.node_height)
        if is_left_button(e):
            if index < len(self.__nodes_list):
                node = self.__nodes_list[index]
                node.is_expanded = not node.is_expanded
                self.single_items = [node]
                self.tree_view_queue_draw_area()
                self.emit("treeview-press-event", self, node)
                return False

    def connect_event(self, event_name, function_point):
        self.__function_dict[event_name] = function_point

    def emit(self, event_name, *arg):
        if self.__function_dict.has_key(event_name):
            self.__function_dict[event_name](*arg)

    ############################################################
    def delete(self, node): # 删除数据.
        node.parent.delete(node)

    def expanded_all(self): # 展开所有节点.
        pass


gobject.type_register(TreeViewBase)


class NodesEvent(object):
    def __init__(self):
        self.cr = None
        self.x  = 0
        self.y  = 0
        self.w  = 0
        self.h  = 0
        self.node = None
        '''
        self.draw_pixbuf
        self.draw_text
        '''
        self.motion_items = None
        self.single_items = None


class Nodes(list):
    def __init__(self):
        list.__init__(self)
        self.this = None
        self.__function_dict = {}

    def add(self, text):
        node = Node()
        node.text = text
        node.parent = self
        if self.this:
            node.leave  = self.this.leave + 1
        node.connect("update-data", self.__node_update_data_event)
        node.connect("added-data",  self.__node_added_data_event)
        node.connect("remove-data", self.__node_remove_data_event)
        node.connect("is-expanded", self.__Node_is_expanded_event)
        self.append(node)
        self.emit("added-data", node)
        return node

    def delete(self, node):
        self.emit("remove-data", node)
        self.remove(node)
        for child_node in node.nodes[:]:
            node.nodes.delete(child_node)

    def __node_update_data_event(self, node):
        self.emit("update-data", node)

    def __node_added_data_event(self, node):
        self.emit("added-data", node)

    def __node_remove_data_event(self, node):
        self.emit("remove-data", node)

    def __Node_is_expanded_event(self, node):
        self.emit("is-expanded", node)

    def connect(self, event_name, function_point):
        self.__function_dict[event_name] = function_point

    def emit(self, event_name, *arg):
        if self.__function_dict.has_key(event_name):
            self.__function_dict[event_name](*arg)

class Node(object):
    def __init__(self):
        self.__function_dict = {}
        self.text  = ""
        #self.sub_items = SubItems()
        self.__pixbuf      = None
        self.children = []
        #
        self.nodes = Nodes()
        self.nodes.this = self
        self.nodes.connect("update-data", self.__nodes_update_data_event)
        self.nodes.connect("added-data",  self.__nodes_added_data_event)
        self.nodes.connect("remove-data", self.__nodes_remove_data_event)
        self.nodes.connect("is-expanded", self.__nodes_is_expanded_event)
        #
        self.parent = None # 获取当前树节点的夫节点.
        self.leave  = 0    # 树的深度,不懂的看数据结构.
        self.__last_node  = []   # 获取最后一个子树节点.
        self.__first_node = []   # 获取树节点集合中的第一个子树节点.
        self.__next_node  = []   # 获取下一个同级节点.
        self.__prev_node  = []   # 获取上一个同级节点.
        self.__index      = None # 获取树节点在树节点集合中的位置.
        ####################
        self.__is_expanded = False # 是否展开状态.
        self.is_selected = False # 是否选中状态.
        self.is_editing  = False # 是否可编辑状态.
        ####################
        self.node_font   = None  # 字体.
        self.next_visible_node = None # 获取下一个可见树节点.
        self.is_visible  = True # 是否可见.

    def __nodes_update_data_event(self, nodes):
        self.emit("update-data", nodes)

    def __nodes_added_data_event(self, nodes):
        self.emit("added-data", nodes)

    def __nodes_remove_data_event(self, nodes):
        self.emit("remove-data", nodes)

    def __nodes_is_expanded_event(self, nodes):
        self.emit("is-expanded", nodes)

    def connect(self, event_name, function_point):
        self.__function_dict[event_name] = function_point

    def emit(self, event_name, *arg):
        if self.__function_dict.has_key(event_name):
            self.__function_dict[event_name](*arg)

    '''
    def add_widget(self, child_widget):
        self.children.append(child_widget)
    '''

    @property
    def is_expanded(self):
        return self.__is_expanded

    @is_expanded.setter
    def is_expanded(self, check):
        # 判断 is_expanded 不能相同 却 nodes不为空.
        if self.__is_expanded != check and self.nodes:
            self.__is_expanded = check
            self.emit("is-expanded", self)

    @is_expanded.getter
    def is_expanded(self):
        return self.__is_expanded

    @property
    def text(self):
        return self.__text

    @text.setter
    def text(self, text):
        self.__text = text
        self.emit("update-data", self)

    @text.getter
    def text(self):
        return self.__text

    @property
    def last_node(self):
    # 获取最后一个子树节点.
        return self.__last_node

    @last_node.getter
    def last_node(self):
        if self.nodes == []:
            return None
        else: 
            return self.nodes[len(self.nodes)-1]

    @property
    def first_node(self):
    # 获取树节点集合中的第一个子树节点.
        return self.__first_node

    @first_node.getter
    def first_node(self):
        if self.nodes == []:
            return None
        else: 
            return self.nodes[0]

    @property
    def prev_node(self):
        return self.__prev_node
    
    @prev_node.getter
    def prev_node(self):
        # 获取上一个同级节点.
        if self.parent:
            index = self.parent.index(self)
            if index:
                node = self.parent[index - 1]
                self.__prev_node = node
                return self.__prev_node
        return None

    @property
    def next_node(self):
        # 获取下一个同级节点.
        return self.__next_node

    @next_node.getter
    def next_node(self):
        if self.parent:
            index = self.parent.index(self)
            if index < len(self.parent) - 1:
                node = self.parent[index + 1]
                self.__next_node = node
                return self.__next_node
        return None

    @next_node.deleter
    def next_node(self):
        del self.__next_node

    @property
    def index(self):
        return self.__index

    @index.getter
    def index(self):
        if self.parent:
            _index = self.parent.index(self) 
            return _index
        return None

    @property
    def pixbuf(self):
        return self.__pixbuf

    @pixbuf.getter
    def pixbuf(self):
        return self.__pixbuf

    @pixbuf.setter
    def pixbuf(self, pixbuf):
        self.__pixbuf = pixbuf
        #self.emit()

    @pixbuf.deleter
    def pixbuf(self, pixbuf):
        del self.__pixbuf


if __name__ == "__main__":
    def test_paint_nodes_event(e):
        if e.node.leave == 0: # 根节点.
            draw_text(e.cr, 
                      e.node.text, 
                      e.x + e.w/2 - get_text_size(e.node.text)[0]/2, 
                      e.y + e.h/2 - get_text_size(e.node.text)[1]/2)
            e.cr.set_source_rgba(1, 1, 1, 1.0)
            e.cr.rectangle(e.x, e.y, e.w, e.h)
            e.cr.stroke()
        else:
            pixbuf = gtk.gdk.pixbuf_new_from_file("logo.png")
            pixbuf = pixbuf.scale_simple(e.h, e.h, gtk.gdk.INTERP_BILINEAR)
            draw_pixbuf(e.cr, pixbuf, e.x + e.w/2 - pixbuf.get_width()/2 + (e.node.leave - 1)* e.h, e.y)
            draw_text(e.cr, 
                      e.node.text, 
                      e.x + e.w/2 - get_text_size(e.node.text)[1]/2 + pixbuf.get_width() + e.node.leave * e.h,
                      e.y + e.h/2 - get_text_size(e.node.text)[1]/2)
        

    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    win.set_size_request(300, 300)
    treeview_base = TreeViewBase()
    #treeview_base.paint_nodes_event = test_paint_nodes_event
    scroll_win = gtk.ScrolledWindow()
    #
    node1 = treeview_base.nodes.add("优酷视频")
    dianshiju = node1.nodes.add("电视剧")
    node1.nodes.add("电影")
    node1.nodes.add("综艺")
    node1.nodes.add("音乐")
    node1.nodes.add("动漫")
    # 电视剧?
    xinshangying = dianshiju.nodes.add("新上映")
    dianshiju.nodes.add("明星")
    dianshiju.nodes.add("大陆剧")
    dianshiju.nodes.add("韩剧")
    dianshiju.nodes.add("TVB")
    #
    xinshangying.nodes.add("桐柏英雄")
    xinshangying.nodes.add("血雨母子情")
    #
    scroll_win.add_with_viewport(treeview_base)
    win.add(scroll_win)
    win.show_all()
    gtk.main()



