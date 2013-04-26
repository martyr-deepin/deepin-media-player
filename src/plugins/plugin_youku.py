#! /usr/bin/python
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


from youku.youku_scan import scan_page
from youku.youku_to_flvcd import YouToFlvcd
import gtk

class_name = "PluginYouku"
version = "1.0"
auto_check = True

class PluginYouku(object):
    def __init__(self, this):
        self.this = this
        self.this.add_net_to_play_list
        self.__init_values()
        self.__init_gui()

    def __init_values(self):
        self.show_check = auto_check

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
        print "总的页数:", page_sum

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
        print "获取dbus_id", self.this.dbus_id
        print "start_plugin."
        self.show_check = True
        self.show_scan_win()

        
    def stop_plugin(self):
        print "end_plugin..."
        self.show_check = False
        
        
        
