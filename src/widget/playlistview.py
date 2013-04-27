#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 ~ 2013 Deepin, Inc.
#               2012 ~ 2013 Hailong Qiu
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


from dtk.ui.theme import ui_theme
from dtk.ui.scrolled_window import ScrolledWindow
from dtk.ui.draw import draw_vlinear
from skin import app_theme
from listview import ListView
from listview_base import Text
from treeview_base import TreeViewBase
from notebook import NoteBook
from color import alpha_color_hex_to_cairo, color_hex_to_cairo
from utils import get_text_size
from draw  import draw_text, draw_pixbuf
import gtk

class PlayListView(object):
    def __init__(self):
        self.tree_view_open = app_theme.get_pixbuf("treeview/open.png")
        self.tree_view_close = app_theme.get_pixbuf("treeview/close.png")
        #
        self.listview_color = ui_theme.get_color("scrolledbar")
        self.play_list_vbox = gtk.VBox()
        #
        self.list_scroll_win   = ScrolledWindow(0, 0)
        self.list_scroll_win.set_policy(gtk.POLICY_NEVER, gtk.POLICY_ALWAYS)
        self.list_view    = ListView()
        #
        self.tree_scroll_win   = ScrolledWindow(0, 0)
        self.tree_scroll_win.set_policy(gtk.POLICY_NEVER, gtk.POLICY_ALWAYS)
        self.tree_view     = TreeViewBase()
        self.note_book = NoteBook()
        #
        self.list_view.on_draw_sub_item =  self.__listview_on_draw_sub_item
        self.list_view.columns.add_range(["filename", "time"])
        self.list_view.columns[0].width = 100
        self.list_view.columns[1].width = 75
        #
        self.note_book.hide_title()
        self.tree_view.paint_nodes_event = self.__treeview_paint_nodes_event
        #
        self.list_scroll_win.add_with_viewport(self.list_view)
        self.tree_scroll_win.add_with_viewport(self.tree_view)
        self.note_book.add_layout1(self.list_scroll_win) 
        self.note_book.add_layout2(self.tree_scroll_win)
        #self.play_list_vbox.pack_start(self.scroll_win, True, True)
        self.play_list_vbox.pack_start(self.note_book, True, True)

    def __listview_on_draw_sub_item(self, e):
        color = self.listview_color.get_color()
        if e.double_items == e.item:
            e.text_color = "#000000"
            text_size=9
            color_info = [(0, (color, 0.8)), (1, (color, 0.8))] 
            draw_vlinear(e.cr,
                         e.x, e.y, e.w, e.h,
                         color_info
                         )
        elif e.item in e.single_items:
            e.text_color = "#FFFFFF"
            text_size=9
            color_info = [(0, (color, 0.5)), (1, (color, 0.5))] 
            draw_vlinear(e.cr,
                         e.x, e.y,
                         e.w, e.h,
                         color_info
                         )
        elif e.motion_items == e.item:
            e.text_color  = "#FFFFFF"
            text_size=9
            color_info = [(0, (color, 0.2)), (1, (color, 0.2))] 
            draw_vlinear(e.cr,
                         e.x, e.y,
                         e.w, e.h,
                         color_info
                         )
        else:
            e.text_color = "#FFFFFF"
            text_size=9


        text = e.text.decode("utf-8")
        if e.w == 100: # 显示播放名字的第一列.
            size = get_text_size(text, text_size=text_size)
            if size[0] >= 200:
                text = text[0:6] + "..."
            elif 80 < size[0] < 200:
                text = text[0:7] + "..."

        e.draw_text(e.cr, 
                str(text), 
                  e.x + 10, e.y, e.w, e.h,
                  text_color=e.text_color, 
                  text_size=text_size,
                  alignment=Text.LEFT)

    def __treeview_paint_nodes_event(self, node_event):
        leave_width = 20
        color = self.listview_color.get_color()
        text_color = "#FFFFFF"
        #
        if node_event.node in node_event.single_items:
            color_info = [(0, (color, 0.45)), (1, (color, 0.45))] 
            draw_vlinear(node_event.cr,
                         node_event.x, node_event.y, node_event.w, node_event.h,
                         color_info
                         )
            text_color = "#000000"
        elif node_event.node in node_event.motion_items:
            color_info = [(0, (color, 0.75)), (1, (color, 0.75))] 
            draw_vlinear(node_event.cr,
                         node_event.x, node_event.y, node_event.w, node_event.h,
                         color_info
                         )
        #
        if node_event.node.leave == 0: # 根节点.
            x = node_event.x + 20
            # 画root的图标.
            if node_event.node.is_expanded:
                pixbuf = self.tree_view_close.get_pixbuf()
            else:
                pixbuf = self.tree_view_open.get_pixbuf()
            draw_pixbuf(node_event.cr,
                        pixbuf,
                        node_event.x + 5,
                        node_event.y + pixbuf.get_height()/2 + 4)
        else:
            x_padding = node_event.node.leave * leave_width
            x = node_event.x + 10 + x_padding
            icon_x = node_event.x + x_padding
            icon_y = node_event.y + get_text_size(">")[1]/2
            #
            if node_event.node.is_expanded:
                text = "*"
            else:
                text = ">"

            if node_event.node.leave < 2:
                draw_text(node_event.cr, 
                          text, 
                          icon_x,
                          icon_y
                          )
        #
        draw_text(node_event.cr, 
                  node_event.node.text, 
                  x,
                  node_event.y + get_text_size(node_event.node.text)[1]/2,
                  text_color=text_color
                  )



