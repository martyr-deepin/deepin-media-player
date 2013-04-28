#! /usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (C) 2013 XXX, Inc.
#               2013 红铭曼,王芳
#
# Author:     红铭曼,王芳 <hongmingman@sina.com>
# Maintainer: 红铭曼,王芳 <hongmingman@sina.com>
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


from youku.youku_scan import scan_page
from youku.youku_to_flvcd import YouToFlvcd
from youku.youku_web_parse import YoukuWebParse
from youku.youku_web import music_type_dict, comic_type_dict, youku_root
from youku.youku_web import zy_type_dict, movie_type_dict, tv_type_dict
from widget.utils import ScanTreeview
import gtk

class_name = "PluginYouku"
version = "1.0"
auto_check = True

class PluginYouku(object):
    def __init__(self, this):
        self.this = this
        self.this.add_net_to_play_list
        self.__init_values()
        #self.__init_gui()

    def __init_values(self):
        #
        self.youku_web_parse = YoukuWebParse()
        #
        self.show_check = auto_check
        self.tree_view = self.this.gui.play_list_view.tree_view
        self.tree_view.connect_event("treeview-press-event", self.__treeview_press_event)
        self.note_book = self.this.gui.play_list_view.note_book
        # 初始化网络播放列表.
        self.__init_tree_view()

    def __init_tree_view(self):
        self.youku_root = self.tree_view.nodes.add("优酷视频")
        self.youku_root.addr = "http://www.youku.com"
        # 初始化根节点的 表单.
        for key, addr in youku_root.items():
            node = self.youku_root.nodes.add(key)
            node.addr = addr
        self.tv_node    = self.youku_root.nodes[0]
        self.movie_node = self.youku_root.nodes[1]
        self.zy_node    = self.youku_root.nodes[2]
        self.music_node = self.youku_root.nodes[3]
        self.comic_node = self.youku_root.nodes[4]
         
        #
        self.__init_type_lists()

    def __init_type_lists(self):
        for key in tv_type_dict.keys():
            node = self.tv_node.nodes.add(key)
            node.addr = tv_type_dict[key]

        for key in movie_type_dict.keys():
            node = self.movie_node.nodes.add(key)
            node.addr = movie_type_dict[key]

        for key in zy_type_dict.keys():
            node = self.zy_node.nodes.add(key)
            node.addr = zy_type_dict[key]

        for key in music_type_dict.keys():
            node = self.music_node.nodes.add(key)
            node.addr = music_type_dict[key]

        for key in comic_type_dict.keys():
            node = self.comic_node.nodes.add(key)
            node.addr = comic_type_dict[key]

        '''
        #info_list, page_num, all_sum = self.youku_web_parse.parse_web(v_olist_dict["热血"])
        for info in info_list:
            node = re_xue_node.nodes.add(info[0])
            node.addr = info[1]
        '''

    def __treeview_press_event(self, treeview, node):
        if node.leave == 2 and node.nodes == []:
            scan_treeview = ScanTreeview(self.youku_web_parse, node.addr, True)
            scan_treeview.connect("scan-end-event", self.scan_treeview_end_event, node)
            scan_treeview.run()
        elif node.leave == 3 and node.nodes == []:
            if node.parent.this.parent.this.text in ["音乐"]:
                self.add_to_play_list(node)
            elif node.parent.this.parent.this.text in ["电影"]:
                #print node.addr
                movie_info = self.youku_web_parse.scan_movie_leave(node.addr)
                if movie_info:
                    save_addr = node.addr
                    node.addr = movie_info[0]
                    self.add_to_play_list(node)
                    node.addr = save_addr
                else:
                    self.this.show_messagebox("优酷收费视频，无法播放...")
            else:
                scan_treeview = ScanTreeview(self.youku_web_parse, node.addr, False)
                scan_treeview.connect("scan-end-event", self.scan_treeview_end_event, node)
                scan_treeview.run()
        elif node.leave == 4:
            self.add_to_play_list(node)

    def scan_treeview_end_event(self, scan_tv, temp_list, node):
        for addr, name in temp_list:
            temp_node = node.nodes.add(name)
            temp_node.addr = addr
        if temp_list:
            node.is_expanded = True

    def add_to_play_list(self, node):
        flvcd = YouToFlvcd()
        scan_treeview = ScanTreeview(flvcd, node.addr, 2)
        scan_treeview.connect("scan-end-event", self.scan_end_add_to_list_event, node)
        scan_treeview.run()
        #flvcd_addr_list = flvcd.parse(node.addr)

    def scan_end_add_to_list_event(self, scan_tv, temp_list, node):
        flvcd_addr_list = temp_list
        index = 0
        for addr in flvcd_addr_list:
            check = False
            if not index:
                check = True
            if len(flvcd_addr_list) > 1:
                text = node.text + "-" + str(index)
            else:
                text = node.text
            self.this.add_net_to_play_list(
                    text,
                    addr,
                    "优酷视频", check)
            index += 1

    def __init_gui(self):
        self.scan_win = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.scrol_win = gtk.ScrolledWindow()
        self.scan_entry_hbox = gtk.HBox()
        self.scan_entry = gtk.Entry()
        self.scan_btn  = gtk.Button("搜索")
        self.scan_btn.connect("clicked", self.scan_btn_clicked)
        self.scan_entry_hbox.pack_start(self.scan_entry, False, False)
        self.scan_entry_hbox.pack_start(self.scan_btn, False, False)
        #
        self.vbox = gtk.VBox()
        self.vbox.pack_start(self.scan_entry_hbox, False, False)
        self.scrol_win.add_with_viewport(self.vbox)
        self.scan_win.add(self.scrol_win)

        #
        w, h = 300, 300
        self.scan_win.set_size_request(w, h)

    def scan_btn_clicked(self, widget):
        scan_text = self.scan_entry.get_text()
        scan_info = scan_page(1, scan_text)
        info_list = scan_info[0] # 信息列表.
        for info_list in scan_info[0]:
            btn = gtk.Button(info_list[0] + info_list[1] + "时间" + info_list[2] + info_list[3])
            btn.connect("clicked", self.btn_connect_addr_to, info_list)
            self.vbox.pack_start(btn, False, False)
            self.vbox.show_all()
        #######################################
        page_num  = scan_info[1] # 一页的总页数.
        sum       = scan_info[2] # 全部搜索的数.
        page_sum  = min(sum/page_num, 100)
        #print "总的页数:", page_sum

    def btn_connect_addr_to(self, widget, info):
        flvcd = YouToFlvcd()
        flvcd_addr_list = flvcd.parse(info[1])
        index = 0
        for addr in flvcd_addr_list:
            check = False
            if not index:
                check = True
            self.this.add_net_to_play_list(info[0]+ str(index),
                    addr,
                    info[3], check)
            index += 1

    def show_scan_win(self):
        if self.show_check:
            self.scan_win.show_all()

    def hide_scan_win(self):
        self.scan_win.hide_all()

    def start_plugin(self):
        #print "获取dbus_id", self.this.dbus_id
        #print "start_plugin."
        self.show_check = True
        #self.show_scan_win()
        # 加入网络列表.
        self.note_book.show_title() # 修复BUG， 当为网络列表的时候 隐藏，就看不到本地列表拉.

    def stop_plugin(self):
        #print "end_plugin..."
        self.show_check = False
        # 删除网络列表的node.
        # 并影藏网络列表.
        self.note_book.hide_title()
        
        
        
