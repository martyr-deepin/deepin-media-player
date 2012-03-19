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


from dtk.ui.listview import *
from dtk.ui.scrolled_window import *

from constant import *
from utils import *

class List(object):
    def __init__(self):
        self.vbox = gtk.VBox()
        self.scrolled_window, self.list_view, self.items = self.list_init()
        self.vbox.pack_start(self.scrolled_window, True, True)
        
    def list_init(self):    
        scrolled_window = ScrolledWindow()
        items = map(lambda index: ListItem(
                "豆浆油条 %04d" % index,
                "林俊杰 %04d" % index,
                "10:%02d" % (index % 60),
                ), range(0, 100))
        list_view = ListView()
        list_view.add_titles(["歌名", "歌手", "时间"])
        list_view.add_items(items)
    
        scrolled_window.add_child(list_view)
        return scrolled_window, items, list_view
