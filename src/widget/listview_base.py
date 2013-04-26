#! /usr/bin/env python
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

from utils import get_match_parent, get_offset_coordinate
import gtk
import pango

# 视图.
class View:
    LARGEICON, DETAILS, SMALLICON, LIST, TITLE = range(0, 5)

'''
largeicon =>> 每个项为一个最大化图标, 下面是一个标签.
smallicon =>> 每个项为一个小图标, 右边带一个标签.
list      =>> 每个项都显示一个小图标, 右边带一个标签, 各项排列在列中,没有列标头.
Details   =>> 包含列标头, 每列都可以显示一个图标和标签.
tile      =>> 
'''

class Text:
    LEFT, RIGHT, CENTER = (pango.ALIGN_LEFT, pango.ALIGN_RIGHT, pango.ALIGN_CENTER)

def type_check(type_name, type_str):
    return type(type_name).__name__ == type_str

class ListViewBase(gtk.Button):
    ''' ListViewBase 基类 '''
    def __init__(self):
        gtk.Button.__init__(self)
        # 初始化变量.
        self.__init_values()

    def __init_values(self):
        self.__expose_check = True # 防止大量数据加载的闪烁问题.
        self.columns = Columns() # 保存 ColumnHeader
        self.items   = Items()   # 保存 ListViewItem
        self.__view = View.DETAILS    # 设置视图, 默认为 Details.
        self.__grid_lines = False # Details视图, 显示网格线.
        self.__multi_select = False # 是否可以选择多个项.
        self.__alignment = None #各项对齐方式.
        # 初始化数据更新事件.
        self.columns.connect("update-data", self.__columns_update_data_event)
        self.items.connect("update-data", self.__items_update_data_event)

    def __columns_update_data_event(self, columns):
        #print "columns_update_data_event:", columns
        self.on_queue_draw_area()

    def __items_update_data_event(self, items):
        #print "items_update_date_event:", items
        self.on_queue_draw_area()

    def get_expose_check(self):
        return self.__expose_check

    def clear(self):
        self.columns = []
        self.items = []
        self.on_queue_draw_area()

    def begin_update(self):
        self.__expose_check = False
        self.on_queue_draw_area()

    def end_update(self):
        self.__expose_check = True
        self.on_queue_draw_area()

    def on_queue_draw_area(self):
        # 重绘区域.
        if self.__expose_check:
            scroll_win = get_match_parent(self, "ScrolledWindow")
            offset_x, offset_y , viewport = get_offset_coordinate(self)
            rect = self.allocation
            if scroll_win:
                rect = scroll_win.allocation
                x      = 0  + offset_x #rect.x + offset_x
                y      = 0  + offset_y #rect.y + offset_y
                w      = rect.width
                h      = rect.height
            else:
                x      = rect.x + offset_x
                y      = rect.y + offset_y
                w      = rect.width
                h      = rect.height
            self.queue_draw_area(x, y, w, h)

    ###################################
    ## grid_lines : 设置是否显示网格线.
    @property
    def grid_lines(self):
        return self.__grid_lines

    @grid_lines.setter
    def grid_lines(self, check):
        self.__grid_lines = check
        self.on_queue_draw_area()

    @grid_lines.getter
    def grid_lines(self):
        return self.__grid_lines

    @grid_lines.deleter
    def grid_lines(self):
        del self.__grid_lines

    ###################################
    ## multi_select : 是否可以选择多个项.
    @property
    def multi_select(self):
        return self.__multi_select

    @multi_select.setter
    def multi_select(self, check):
        self.__multi_select = check
        self.on_queue_draw_area()
        
    @multi_select.getter
    def multi_select(self):
        return self.__multi_select

    @multi_select.deleter
    def multi_select(self):
        del self.__multi_select

    ###################################
    ## view : 设置视图. 五种.
    @property
    def view(self):
        return self.__view

    @view.setter
    def view(self, view_name):
        self.__view = view_name
        self.on_queue_draw_area()

    @view.getter
    def view(self):
        return self.__view

    @view.deleter
    def view(self):
        del self.__view

class Columns(list):
    def __init__(self):
        list.__init__(self)
        self.__init_values()

    def __init_values(self):
        self.__function_point = None # 函数指针.

    def connect(self, event_name, function_point):
        if event_name == "update-data":
            self.__function_point = function_point

    def emit(self):
        if self.__function_point:
            self.__function_point(self)

    @property
    def count(self):
        return len(self)
    
    @count.getter
    def count(self):
        return len(self)

    def clear(self):
        del self[:]
        self.emit()

    def add(self, text):
        if type_check(text, "str"):
            header = ColumnHeader(text)
            header.connect("update-data", self.__header_update_data_event)
            self.append(header)
            self.emit()

    def add_range(self, text_list):
        if type_check(text_list, "list"):
            for text in text_list:
                header = ColumnHeader(text)
                header.connect("update-data", self.__header_update_data_event)
                self.append(header)
            self.emit()

    def __header_update_data_event(self, column_header):
        self.emit()

class ColumnHeader(object):
    def __init__(self, text=""):
        self.__init_values()
        self.__text = text

    def __init_values(self):
        self.__text = ""  # 保存文本.
        self.__width = 80 # ColumnHeader 宽度.
        self.min_width = 50
        self.__text_color = "#000000"
        self.text_align = pango.ALIGN_LEFT # 文本对齐方式.
        self.image_key = None # 图片key.
        self.image_index = None # 图片索引.
        self.__function_point = None

    def connect(self, event_name, function_point):
        if event_name == "update-data":
            self.__function_point = function_point

    def emit(self):
        if self.__function_point:
            self.__function_point(self)

    @property
    def text(self):
        return self.__text

    @text.setter
    def text(self, text):
        self.__text = text
        self.emit()

    @text.getter
    def text(self):
        return self.__text

    @text.deleter
    def text(self):
        del self.__text

    @property
    def width(self):
        return self.__width

    @width.setter
    def width(self, width):
        self.__width = width
        self.emit()

    @width.getter
    def width(self):
        return self.__width

    @width.deleter
    def width(self):
        del self.__width

    @property
    def text_color(self):
        return self.__text_color

    @text_color.setter
    def text_color(self, text_color):
        self.__text_color = text_color
        self.emit()

    @text_color.getter
    def text_color(self):
        return self.__text_color

    @text_color.deleter
    def text_color(self):
        del self.__text_color

class Items(list):
    def __init__(self):
        list.__init__(self)
        # 初始化变量.
        self.__init_values()

    def __init_values(self):
        self.__function_point = None

    def connect(self, event_name, function_point): 
        if event_name == "update-data":
            self.__function_point = function_point

    def emit(self):
        # 回调函数.
        if self.__function_point:
            self.__function_point(self)

    def clear(self):
        del self[:]
        self.emit()

    def add(self, text_item):
        if type_check(text_item, "list"): # 判断是否为 str  类型.
            listview_item = ListViewItem()
            for text in text_item:
                listview_item.sub_items.add(text)
            listview_item.connect("update-data", self.__listview_item_update_data_event)
            self.append(listview_item)
            # 发送信号.
            self.emit()

    def add_range(self, text_items):
        if type_check(text_items, "list"):
            emit_check = False # 初始化发送信号的标志位.
            for item in text_items:
                if type_check(item, "list"):
                    if not emit_check: # 设置发送信号的标志位.
                        emit_check = True # 设置发送信号的标志位为真.
                    #
                    listview_item = ListViewItem(item)
                    listview_item.connect("update-data", self.__listview_item_update_data_event)
                    self.append(listview_item)

            if emit_check: # 判断是否发送信号.
                # 发送信号.
                self.emit()

    def add_insert(self, index, text_items):
        emit_check = False # 初始化发送信号的标志位.
        if type_check(text_items, "list"):
            for item in text_items:
                if type_check(item, "list"):
                    if not emit_check: # 设置发送信号的标志位.
                        emit_check = True # 设置发送信号的标志位为真.
                    #
                    listview_item = ListViewItem(item)
                    listview_item.connect("update-data", self.__listview_item_update_data_event)
                    self.insert(index, listview_item)

        elif type_check(text_items, "ListViewItem"):
            emit_check = True
            self.insert(index, text_items)

        if emit_check: # 判断是否发送信号.
            # 发送信号.
            self.emit()
    def __listview_item_update_data_event(self, listview_item):
        self.emit()

class ListViewItem(object):
    def __init__(self, item=[]):
        self.__init_values()
        self.sub_items.add_range(item)

    def __init_values(self):
        self.sub_items = SubItems()
        self.sub_items.connect("update-data", self.__sub_items_update_data_event)

    def __sub_items_update_data_event(self, sub_items):
        self.emit()

    def connect(self, event_name, function_point):
        if event_name == "update-data":
            self.__function_point = function_point

    def emit(self):
        if self.__function_point:
            self.__function_point(self)

class SubItems(list):
    def __init__(self):
        list.__init__(self)
        self.__init_values()

    def __init_values(self):
        self.__function_point = None

    def connect(self, event_name, function_point):
        if event_name == "update-data":
            self.__function_point = function_point

    def emit(self):
        if self.__function_point:
            self.__function_point(self)

    def add(self, text):
        if type_check(text, "tuple"):
            sub_item = SubItem()
            sub_item.text   = text[0]
            sub_item.pixbuf = text[1]
        elif type_check(text, "str"):
            sub_item = SubItem(text)
        sub_item.connect("update-data", self.__sub_item_update_data_event)
        self.append(sub_item)

    def add_range(self, items_text):
        for text in items_text:
            self.add(text)
            '''
            sub_item = SubItem(text)
            sub_item.connect("update-data", self.__sub_item_update_data_event)
            self.append(sub_item)
            '''

    def __sub_item_update_data_event(self, sub_item):
        self.emit()
    

class SubItem(object):
    def __init__(self, text=""):
        self.__init_values()
        self.__text = text

    def __init_values(self):
        self.__text = ""
        self.__pixbuf = None
        self.__text_color = "#000000"
        self.__text_align = pango.ALIGN_LEFT
        self.__function_point = None

    def connect(self, event_name, function_point):
        if event_name == "update-data":
            self.__function_point = function_point

    def emit(self):
        if self.__function_point:
            self.__function_point(self)
    
    # text.
    @property
    def text(self):
        return self.__text

    @text.setter
    def text(self, text):
        self.__text = text
        self.emit()

    @text.getter
    def text(self):
        return self.__text

    @text.deleter
    def text(self):
        del self.__text

    # text color.
    @property
    def text_color(self):
        return self.__text_color

    @text_color.setter
    def text_color(self, text_color):
        self.__text_color = text_color
        self.emit()

    @text_color.getter
    def text_color(self):
        return self.__text_color

    @text_color.deleter
    def text_color(self):
        del self.__text_color

    # pixbuf
    @property
    def pixbuf(self):
        return self.__pixbuf

    @pixbuf.setter
    def pixbuf(self, pixbuf):
        self.__pixbuf = pixbuf
        self.emit()

    @pixbuf.getter
    def pixbuf(self):
        return self.__pixbuf

    @pixbuf.deleter
    def pixbuf(self):
        del self.__pixbuf

    @property
    def text_color(self):
        return self.__text_color

    @text_color.setter
    def text_color(self, text_color):
        self.__text_color = text_color
        self.emit()

'''
columns[列表] <= ColumnHeader
items[列表]   <= ListViewItem
ColumnHeader---{属性:text, width...}
ListViewItem[列表] <= SubItems <= SubItem---{属性:text...}

界面层.
控制层.
数据层.
'''

if __name__ == "__main__":
    listview1 = ListViewBase()
    listview1.items.add_range([[("文本", "gtk.gdk.pixbuf")],
                               [("文件管理七", "gtk.gdk.pixbuf")],
                               [("文件管理七", "gtk.gdk.pixbuf")],
                               [("文件管理七", "gtk.gdk.pixbuf")],
                               [("文件管理七", "gtk.gdk.pixbuf")],
                               [("文件管理七", "gtk.gdk.pixbuf")],
                               [("文件管理七", "gtk.gdk.pixbuf")],
                               [("文件管理七", "gtk.gdk.pixbuf")],
                               [("文件管理七", "gtk.gdk.pixbuf")],
                               [("文件管理七", "gtk.gdk.pixbuf")],
                               [("文件管理七", "gtk.gdk.pixbuf")],
                              ])
    #
    for item in listview1.items:
        for sub_item in item.sub_items:
            print "sub_item:", sub_item.text, sub_item.pixbuf



