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



import gtk
from gtk import gdk
import gobject
from draw  import draw_text
from color import alpha_color_hex_to_cairo

class NoteBook(gtk.Container):
    def __init__(self):
        gtk.Container.__init__(self)
        self.__init_values()

    def __init_values(self):
        self.add_events(gtk.gdk.ALL_EVENTS_MASK)
        self.title_child1 = gtk.Button("本地列表")
        self.title_child1.set_parent(self)
        self.title_child2 = gtk.Button("网络列表")
        self.title_child2.set_parent(self)
        self.title_w = 120
        self.title_h = 30
        self.save_title_h = self.title_h
        #
        self.title_child1.connect("clicked", self.__title_child1_clicked)
        self.title_child2.connect("clicked", self.__title_child2_clicked)
        self.title_child1.connect("expose-event", self.__title_child1_expose_event)
        self.title_child2.connect("expose-event", self.__title_child2_expose_event)
        #
        self.layout_show_check = True
        self.layout1 = None
        self.layout2 = None
        self.children = []
        # 添加子控件.
        self.children.append(self.title_child1)
        self.children.append(self.title_child2)

    def __title_child1_clicked(self, widget):
        if self.layout2 and self.layout1:
            self.layout_show_check = True

    def __title_child2_clicked(self, widget):
        if self.layout1 and self.layout2:
            self.layout_show_check = False

    def __title_child1_expose_event(self, widget, event):
        self.__title_expose_event(widget, event, self.layout_show_check)
        return True

    def __title_child2_expose_event(self, widget, event):
        self.__title_expose_event(widget, event, not self.layout_show_check)
        return True

    def __title_expose_event(self, widget, event, show_check):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        # draw background.   
        if show_check:
            bg_color = "#272727"
        else:
            bg_color = "#1b1b1b"
        cr.set_source_rgba(*alpha_color_hex_to_cairo((bg_color,1.0)))
        cr.rectangle(rect.x, rect.y, rect.width + 1, rect.height)
        cr.fill()
        # draw title name.
        text = widget.get_label()
        import pango
        if show_check:
            text_color = "#FFFFFF"
        else:
            text_color = "#A9A9A9"
        draw_text(cr, 
                  text, 
                  rect.x, rect.y, rect.width, rect.height, 
                  text_color=text_color,
                  text_size=9,
                  alignment=pango.ALIGN_CENTER)

    def add_layout1(self, layout1):
        self.layout1 = layout1
        self.layout1.set_parent(self)

    def add_layout2(self, layout2):
        self.layout2 = layout2
        self.layout2.set_parent(self)

    def do_realize(self):
        self.set_realized(True)
        self.__init_window()
        self.__init_children()
        self.queue_resize()

    def __init_window(self):
        self.window = gdk.Window(
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
            | gtk.gdk.VISIBILITY_NOTIFY
            | gdk.EXPOSURE_MASK
            | gdk.SCROLL_MASK
            | gdk.POINTER_MOTION_MASK
            | gdk.ENTER_NOTIFY_MASK
            | gdk.LEAVE_NOTIFY_MASK
            | gdk.BUTTON_PRESS_MASK
            | gdk.BUTTON_RELEASE_MASK
            | gdk.KEY_PRESS_MASK
            | gdk.KEY_RELEASE_MASK
            ))
        self.window.set_user_data(self)
        self.style.set_background(self.window, gtk.STATE_NORMAL)

    def __init_children(self):
        if self.title_child1:
            self.title_child1.set_parent_window(self.window)
        if self.title_child2:
            self.title_child2.set_parent_window(self.window)

        self.layout1.set_parent_window(self.window)
        self.layout2.set_parent_window(self.window)

    def do_unrealize(self):
        pass

    def do_map(self):
        gtk.Container.do_map(self)
        self.set_flags(gtk.MAPPED)
        #
        self.window.show()

    def do_umap(self):
        gtk.Container.do_umap(self)
        self.window.hide()

    def do_expose_event(self, e):
        #
        gtk.Container.do_expose_event(self, e)
        return False

    def do_size_request(self, req):
        self.title_child1.size_request()
        self.title_child2.size_request()
        self.layout1.size_request()
        self.layout2.size_request()

    def do_size_allocate(self, allocation):
        gtk.Container.do_size_allocate(self, allocation)
        self.allocation = allocation
        #
        title_w_padding = self.allocation.width/len(self.children)
        allocation = gdk.Rectangle()
        allocation.x  = 0
        allocation.y  = 0
        allocation.width  = title_w_padding
        allocation.height = self.title_h
        self.title_child1.size_allocate(allocation)
        allocation.x  = 0 + allocation.width
        self.title_child2.size_allocate(allocation)
        #
        if self.layout_show_check:
            layout2_x =  -self.allocation.width
        else:
            layout2_x = 0
            
        allocation.x = layout2_x
        allocation.y = 0 + self.title_h #self.layout2.allocation.y
        allocation.width = self.allocation.width
        allocation.height = self.allocation.height - self.title_h
        self.layout2.size_allocate(allocation)
        if not self.layout_show_check:
            layout1_x = - self.allocation.width
        else:
            layout1_x = 0
        allocation.x = layout1_x
        allocation.y = 0 + self.title_h #self.layout1.allocation.y
        self.layout1.size_allocate(allocation)
        #
        if self.get_realized():
            self.window.move_resize(
                    self.allocation.x,
                    self.allocation.y,
                    self.allocation.width,
                    self.allocation.height)

    def do_show(self):
        gtk.Container.do_show(self)

    def do_forall(self, include_internals, callback, data):
        callback(self.title_child1, data)
        callback(self.title_child2, data)
        callback(self.layout1, data)
        callback(self.layout2, data)

    def do_remove(self, widget):
        pass

    def hide_title(self):
        self.save_title_h = self.title_h
        self.title_h = 0

    def show_title(self):
        self.title_h = self.save_title_h

gobject.type_register(NoteBook)


if __name__ == "__main__":
    from treeview_base import TreeViewBase
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    scroll_win = gtk.ScrolledWindow()
    treeview_base = TreeViewBase()
    scroll_win.add_with_viewport(treeview_base)
    note_book = NoteBook()
    note_book.add_layout1(scroll_win)
    note_book.add_layout2(gtk.Button("测试一下"))
    win.add(note_book)
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
    win.show_all()
    gtk.main()

