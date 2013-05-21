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
from dtk.ui.utils import propagate_expose
from dtk.ui.draw import draw_vlinear
from skin import app_theme
from listview import ListView
from listview_base import Text
from treeview_base import TreeViewBase
from net_search import Search
from notebook import NoteBook
from color import alpha_color_hex_to_cairo, color_hex_to_cairo
from utils import get_text_size
from draw  import draw_text, draw_pixbuf
import gtk

class PlayListView(object):
    def __init__(self):
        self.one_close = app_theme.get_pixbuf("treeview/1-close.png")
        self.one_open  = app_theme.get_pixbuf("treeview/1-open.png")
        self.two_close = app_theme.get_pixbuf("treeview/2-close.png")
        self.two_open  = app_theme.get_pixbuf("treeview/2-open.png")
        self.three_close = app_theme.get_pixbuf("treeview/3-close.png")
        self.three_open  = app_theme.get_pixbuf("treeview/3-open.png")
        #
        self.tree_view_open  = app_theme.get_pixbuf("treeview/open.png")
        self.tree_view_close = app_theme.get_pixbuf("treeview/close.png")
        self.tree_view_right = app_theme.get_pixbuf("treeview/right.png")
        self.tree_view_bottom = app_theme.get_pixbuf("treeview/bottom.png")
        #
        self.listview_color = ui_theme.get_color("scrolledbar")
        self.play_list_vbox = gtk.VBox()
        #
        self.list_view_vbox = gtk.VBox()
        self.list_scroll_win   = ScrolledWindow(0, 0)
        self.list_scroll_win.set_policy(gtk.POLICY_NEVER, gtk.POLICY_ALWAYS)
        self.list_view    = ListView()
        #
        self.play_list_con = PlayListControl()
        #
        self.list_view_vbox.pack_start(self.list_scroll_win, True, True)
        self.list_view_vbox.pack_start(self.play_list_con, False, False)
        # 网络列表，搜索框.
        self.tree_scroll_win   = ScrolledWindow(0, 0)
        self.tree_scroll_win.set_policy(gtk.POLICY_NEVER, gtk.POLICY_ALWAYS)
        self.tree_view_vbox = gtk.VBox()
        self.tree_view     = TreeViewBase()
        self.search_ali    = gtk.Alignment(0, 0, 1, 1)
        self.search        = Search()
        self.search_ali.add(self.search)
        #
        self.search_ali.set_padding(7, 5, 12, 12)
        self.tree_view_vbox.pack_start(self.search_ali, False, False)
        self.tree_view_vbox.pack_start(self.tree_scroll_win, True, True)
        self.search_ali.connect("expose-event", self.search_ali_expose_event)
        #
        self.note_book = NoteBook()
        #
        self.list_view.on_draw_sub_item =  self.__listview_on_draw_sub_item
        self.list_view.columns.add_range(["filename", "time"])
        self.list_view.columns[0].width = 120
        self.list_view.columns[1].width = 95
        #
        self.note_book.hide_title()
        self.tree_view.paint_nodes_event = self.__treeview_paint_nodes_event
        #
        self.list_scroll_win.add_with_viewport(self.list_view)
        self.tree_scroll_win.add_with_viewport(self.tree_view)
        #self.note_book.add_layout1(self.list_scroll_win) 
        self.note_book.add_layout1(self.list_view_vbox) 
        self.note_book.add_layout2(self.tree_view_vbox)
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
                         e.x, e.y, e.w, e.h,
                         color_info
                         )
        elif e.motion_items == e.item:
            e.text_color  = "#FFFFFF"
            text_size=9
            color_info = [(0, (color, 0.2)), (1, (color, 0.2))] 
            draw_vlinear(e.cr,
                         e.x, e.y, e.w, e.h,
                         color_info
                         )
        else:
            e.text_color = "#FFFFFF"
            text_size=9
        #
        text = e.text.decode("utf-8")
        one_width = self.list_view.columns[0].width
        two_width = self.list_view.columns[1].width
        #if e.w == one_width: # 显示播放名字的第一列.
        if e.column_index == 0:
            #
            t_width = 0
            t_index = 0
            add_point = False
            for t in text:
                t_width += get_text_size(t, text_size=text_size)[0]
                if t_width > one_width - 20:
                    add_point = True
                    break
                t_index += 1
            if add_point:
                text = text[:t_index] + "..."
            #
            alignment = Text.LEFT
            x = e.x + 15
        elif e.w == two_width:
            alignment = Text.RIGHT
            x = e.x - 15

        e.draw_text(e.cr, 
                str(text), 
                  x, e.y, e.w, e.h,
                  text_color=e.text_color, 
                  text_size=text_size,
                  alignment=alignment)

    def __treeview_paint_nodes_event(self, node_event):
        color = self.listview_color.get_color()
        text_color = "#FFFFFF"
        # 单击和移动, 双击.
        if node_event.node in node_event.single_items:
            color_info = [(0, (color, 0.45)), (1, (color, 0.45))] 
            draw_vlinear(node_event.cr,
                         node_event.x, node_event.y, node_event.w, node_event.h,
                         color_info
                         )
            #text_color = "#000000"
        elif node_event.node in node_event.motion_items:
            color_info = [(0, (color, 0.75)), (1, (color, 0.75))] 
            draw_vlinear(node_event.cr,
                         node_event.x, node_event.y, node_event.w, node_event.h,
                         color_info
                         )
        #
        x_padding = 12 # 因为要和搜索框对齐.
        if 0 == node_event.node.leave: # 根节点. :比如->> >我看过的. >优酷视频. >pps.
            if node_event.node.is_expanded:
                pixbuf = self.one_open.get_pixbuf()
            else:
                pixbuf = self.one_close.get_pixbuf()
        elif 1 == node_event.node.leave: # 
            if node_event.node.is_expanded:
                pixbuf = self.two_open.get_pixbuf()
            else:
                pixbuf = self.two_close.get_pixbuf()
        else:
            if node_event.node.is_expanded:
                pixbuf = self.three_open.get_pixbuf()
            else:
                pixbuf = self.three_close.get_pixbuf()
        #
        icon_x = node_event.x + x_padding
        icon_y = node_event.y + node_event.h/2 - pixbuf.get_height()/2 + 1
        if node_event.node.leave > 1:
            icon_x += (node_event.node.leave - 1) * pixbuf.get_width()
        if node_event.node.leave > 0:
            text_color = "#a8a8a8"
        ##########
        # 画图标.
        if node_event.node.nodes != []:
            draw_pixbuf(node_event.cr,
                        pixbuf,
                        icon_x,
                        icon_y) 
        # 画文本.
        text_x_padding = 15
        text_size = 9
        draw_text(node_event.cr, 
                  node_event.node.text, 
                  icon_x + text_x_padding,
                  node_event.y + node_event.h/2 - get_text_size(node_event.node.text, text_size=9)[1]/2,
                  text_color=text_color,
                  text_size=text_size
                  )

    def search_ali_expose_event(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        #
        bg_color = "#272727"
        cr.set_source_rgba(*alpha_color_hex_to_cairo((bg_color,1.0)))
        cr.rectangle(rect.x, rect.y, rect.width + 1, rect.height)
        cr.fill()
        #
        propagate_expose(widget, event)
        return True



class PlayListControl(gtk.HBox):
    def __init__(self):
        gtk.HBox.__init__(self)
        self.del_btn = gtk.Button("del")
        self.add_btn = gtk.Button("add")
        self.empty_btn = gtk.Button('')
        height = 22
        self.del_btn.set_size_request(-1, height)
        self.add_btn.set_size_request(-1, height)
        self.empty_btn.set_size_request(-1, height)
        # init pixbuf.        
        self.del_pixbuf = app_theme.get_pixbuf("bottom_buttons/play_list_del_file.png").get_pixbuf()
        self.add_pixbuf = app_theme.get_pixbuf("bottom_buttons/play_list_add_file.png").get_pixbuf()
        #
        self.del_btn.connect("expose-event", self.del_btn_expose_event)
        self.add_btn.connect("expose-event", self.add_btn_expose_event)
        self.empty_btn.connect("expose-event", self.empty_btn_expose_event)
        #
        self.pack_start(self.empty_btn, True, True)
        self.pack_start(self.add_btn, False, False)
        self.pack_start(self.del_btn, False, False)

    def del_btn_expose_event(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        self.paint_bg(cr, rect)
        x = rect.x + rect.width/2 - self.del_pixbuf.get_width()/2
        y = rect.y + rect.height/2  - self.del_pixbuf.get_height()/2
        if widget.state == gtk.STATE_ACTIVE:
            x += 1
            y += 1
        draw_pixbuf(cr, self.del_pixbuf, x, y)
        return True

    def add_btn_expose_event(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        self.paint_bg(cr, rect)
        x = rect.x + rect.width/2 - self.add_pixbuf.get_width()/2
        y = rect.y + rect.height/2  - self.add_pixbuf.get_height()/2
        if widget.state == gtk.STATE_ACTIVE:
            x += 1
            y += 1
        draw_pixbuf(cr, self.add_pixbuf, x, y)
        return True
    
    def empty_btn_expose_event(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        self.paint_bg(cr, rect)
        return True
    
    def paint_bg(self, cr, rect):
        cr.set_source_rgba(*alpha_color_hex_to_cairo(("#202020", 1.0)))
        cr.rectangle(*rect)
        cr.fill()



