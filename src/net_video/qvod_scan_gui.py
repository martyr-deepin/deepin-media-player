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


import gtk


from qvod_scan import QvodScan
from qvod_con import get_down_progress

class QvodScanGui(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)        
        self.qvod = QvodScan()
        self.set_title("QVOD电影搜索下载器")        
        self.connect("destroy", lambda w : gtk.main_quit())
        #
        self.main_vbox = gtk.VBox()
        self.__init_scan_top()        
        self.main_vbox.pack_start(self.scan_hbox, False, False)
        self.main_vbox.pack_start(gtk.Entry(), True, True)
        self.add(self.main_vbox)
        self.show_all()        
        
    def __init_scan_top(self):    
        self.scan_hbox = gtk.HBox()
        self.scan_text = gtk.Entry()
        self.scan_btn  = gtk.Button("搜索")
        self.scan_label = gtk.Label("输入电影:")
        self.scan_hbox.pack_start(self.scan_label, False, False)
        self.scan_hbox.pack_start(self.scan_text, True, True)
        self.scan_hbox.pack_start(self.scan_btn, False, False)
        
        self.scan_btn.connect("clicked", self.scan_btn_clicked)
        
    def scan_btn_clicked(self, widget):    
        print self.qvod.scan(self.scan_text.get_text())
        for info in self.qvod.get_qvod_info(1):
            print "=========================="
            print "地址:", info.addr
            print "名称:", info.name
            print "地区:", info.area
            print "类型:", info.type
            print "日期:", info.date
        #######################################
        print "总共有%d页" % (self.qvod.page_num)

if __name__ == "__main__":        
    QvodScanGui()
    gtk.main()
