#! /usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (C) 2013 XXX, Inc.
#               2013 XXX
#
# Author:   军委主席 <1295832215@qq.com>
# Maintainer:  军委主席 <1295832215@qq.com>
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



title = "pps插件"
class_name = "PluginPPS"
version = "1.0"
auto_check = False
author = "军委主席"
about = "PPS网络电视插件"


class PluginPPS(object):
    def __init__(self, this):
        self.this = this
        #self.this.add_net_to_play_list
        self.__init_values()

    def __init_values(self):
        self.show_check = auto_check
        self.tree_view = self.this.gui.play_list_view.tree_view
        #self.tree_view.connect_event("treeview-press-event", self.__treeview_press_event)
        #self.note_book = self.this.gui.play_list_view.note_book
        # 初始化网络播放列表.
        self.__init_tree_view()

    '''
    def start_plugin(self):
        pass
    
    def stop_plugin(self):
        pass
    '''

