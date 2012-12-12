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

'''
addr     跳转地址.
name     影片名称
area     地区.
actor    影片演员.
direct   影片导演.
type     类型.
date     上映日期.
image    图片
state    影片状态.
qvod_addr qvod 地址.
other     备注信息.
'''

class ShowInfoWidget(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self)
        self.movie_image = MovieImage()
        
class MovieImage(gtk.Button):
    def __init__(self):
        gtk.Button.__init__(self)
        self.add_events(gtk.gdk.ALL_EVENTS_MASK)
        
if __name__ == "__main__":
    show_info = ShowInfoWidget()
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    win.add(show_info)
    win.show_all()
    gtk.main()
