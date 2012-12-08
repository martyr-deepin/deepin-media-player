#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 Deepin, Inc.
#               2012 Hailong Qiu
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

import os
import gtk


from qvod_scan import QvodScan
from qvod_con import get_down_progress, get_movie_name, get_hash_str, check_qvod_url, cp_exe_to_down_dir, hide_down_qvod_exe, close_down_qvod_exe, run_down_qvod_exe

class QvodScanGui(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)        
        self.qvod_down_dict = {}
        self.qvod = QvodScan()
        self.set_title("QVOD电影搜索下载器")        
        self.set_size_request(250, 600)
        self.connect("destroy", self.main_win_quit)
        #
        self.main_vbox = gtk.VBox()
        self.scan_info_vbox = gtk.VBox()
        self.scan_page_hbox = gtk.HBox()
        self.scan_infO_scoll_win = gtk.ScrolledWindow()
        self.scan_infO_scoll_win.add_with_viewport(self.scan_info_vbox)
        #
        self.__init_scan_top()        
        self.__init_show_qvod_addr_window()
        #
        self.hide_down_win_btn = gtk.Button("下载管理器")
        self.hide_down_win_btn.connect("clicked", self.hide_down_win_btn_clicked)
        self.down_win = gtk.Window(gtk.WINDOW_POPUP)
        self.down_win.set_title("下载管理器")
        self.down_vbox = gtk.VBox()
        self.down_win.add(self.down_vbox)
        #        
        #
        self.main_vbox.pack_start(self.scan_hbox, False, False)
        self.main_vbox.pack_start(self.scan_infO_scoll_win, True, True)
        self.main_vbox.pack_start(self.scan_page_hbox, False, False)
        self.main_vbox.pack_start(self.hide_down_win_btn, False, False)
        self.add(self.main_vbox)
        self.show_all()        
        gtk.timeout_add(1000, self.update_down_progressbar)
        
    def main_win_quit(self, widget):    
        for key in self.qvod_down_dict.keys():
            close_down_qvod_exe(os.path.split(key)[1])
        gtk.main_quit()        
        
    def update_down_progressbar(self):    
        for key in self.qvod_down_dict.keys():
            # print "down progressbar:", get_down_progress(key + ".!qd")
            self.qvod_down_dict[key] = (self.qvod_down_dict[key][0], get_down_progress(key + ".!qd"))
        self.update_down_win()    
        return True    
    
    def hide_down_win_btn_clicked(self, widget):                            
        self.down_win.set_visible(not self.down_win.get_visible())
        self.update_down_win()
        
    def update_down_win(self):    
        for widget in self.down_vbox.get_children():
            self.down_vbox.remove(widget)
            
        for key in self.qvod_down_dict.keys():
            down_info = self.qvod_down_dict[key]
            self.down_vbox.pack_start(gtk.Button(os.path.split(key)[1] + "下载进度:" + str(down_info[1]) + "%"), False, False)
            
        self.down_vbox.show_all()
        main_x, main_y = self.get_position()
        main_w, main_h = self.get_size_request()
        self.down_win.set_size_request(self.down_win.get_size_request()[0], main_h - 60)
        self.down_win.move(main_x + main_w + 5, main_y + 60)        
        
    def __init_scan_top(self):    
        self.scan_hbox = gtk.HBox()
        self.scan_text = gtk.Entry()
        self.scan_btn  = gtk.Button("搜索")
        self.scan_label = gtk.Label("输入电影:")
        self.scan_hbox.pack_start(self.scan_label, False, False)
        self.scan_hbox.pack_start(self.scan_text, True, True)
        self.scan_hbox.pack_start(self.scan_btn, False, False)        
        self.scan_btn.connect("clicked", self.scan_btn_clicked)
        
    def __init_show_qvod_addr_window(self):
        self.qvod_addr_win = gtk.Window(gtk.WINDOW_TOPLEVEL)        
        self.qvod_addr_win.set_size_request(200, 250)
        self.qvod_addr_win.connect("destroy", self.__qvod_addr_win_destroy)
        self.qvod_addr_scoll_win = gtk.ScrolledWindow()
        self.qvod_addr_vbox = gtk.VBox()
        self.qvod_addr_scoll_win.add_with_viewport(self.qvod_addr_vbox)
        self.qvod_addr_win.add(self.qvod_addr_scoll_win)
                
    def __qvod_addr_win_destroy(self, widget):
        self.qvod_addr_win=None
        
    def scan_btn_clicked(self, widget):                    
        if self.qvod.scan(self.scan_text.get_text()):
            self.update_scan_page_hbox()
            self.update_scan_info_vbox(1)
        # print "总共有%d页" % (self.qvod.page_num)        
        
    def temp_page_btn_clicked(self, widget, index):
        self.update_scan_info_vbox(index)
        
    def update_scan_page_hbox(self):    
        for page_widget in self.scan_page_hbox.get_children():
            self.scan_page_hbox.remove(page_widget)
        #    
        for index in range(1, self.qvod.page_num + 1):
            temp_page_btn = gtk.Button(str(index))
            temp_page_btn.connect("clicked", self.temp_page_btn_clicked, index)
            self.scan_page_hbox.pack_start(temp_page_btn, False, False)
                
        self.scan_page_hbox.show_all()    
        
    def update_scan_info_vbox(self, index):
        scan_info_num = 0
        for widget in self.scan_info_vbox.get_children():
            self.scan_info_vbox.remove(widget)
            
        for info in self.qvod.get_qvod_info(index):
            scan_info_num += 1
            temp_btn_addr = gtk.Button(info.name)
            temp_btn_addr.connect("clicked", self.temp_btn_addr_clicked, info.addr, info.name)
            self.scan_info_vbox.pack_start(temp_btn_addr, False, False)
        self.scan_info_vbox.show_all()
        self.set_title(self.scan_text.get_text() + str(index) + "页"+ "总搜索" + str(scan_info_num) +"条")
        
    def temp_btn_addr_clicked(self, widget, go_addr, movie_name):
        if not self.qvod_addr_win:
            self.__init_show_qvod_addr_window()
        self.qvod_addr_win.set_title(movie_name + "qvod 下载地址")
        for widget in self.qvod_addr_vbox.get_children():
            self.qvod_addr_vbox.remove(widget)
        #    
        for qvod_addr in self.qvod.get_qvod_addr(go_addr)[0].split(","):
            if qvod_addr != "":
                temp_qvod_addr = gtk.Button(get_movie_name(qvod_addr))
                temp_qvod_addr.set_tooltip_text("点击便可下载,请到down_movie查看!!")
                temp_qvod_addr.connect("clicked", self.__temp_qvod_addr_down_clicked, qvod_addr)
                self.qvod_addr_vbox.pack_start(temp_qvod_addr, False, False)
            
        self.qvod_addr_win.show_all()
        
    def __temp_qvod_addr_down_clicked(self, widget, qvod_addr):
        movie_name = get_movie_name(qvod_addr)
        down_exe_addr = movie_name + "_" + get_hash_str(qvod_addr) + ".exe"
        cp_exe_to_down_dir(down_exe_addr, "./down_movie/")
        run_down_qvod_exe("./down_movie/" + down_exe_addr, movie_name)
        self.qvod_down_dict["./down_movie/" + movie_name] = ("./down_movie/" + down_exe_addr, 0)
        self.update_down_win()
        self.down_win.show_all()
if __name__ == "__main__":        
    QvodScanGui()
    gtk.main()
