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

from dtk.ui.menu import Menu
from utils import app_theme

class PopupMenu(object):
    def __init__(self):
        self.menu = Menu([(None, "单个播放", None), # 0
                          (None, "顺序播放", None), # 1
                          (None, "随机播放", None), # 2
                          (None, "单个循环", None), # 3
                          (None, "列表循环", None)] # 4
                         ) 
        
        
        self.menu2 = Menu([(None, "按名称", None),
                           (None, "按类型", None)])
        
        self.root_menu = Menu([(None, "添加文件", None), 
                               (None, "添加文件夹", None),
                               (None),
                               (None, "删除选中项", None),
                               (None, "清空播放列表", None),
                               (None, "删除无效文件", None),
                               (None),
                               (None, "播放顺序", self.menu),                               
                               (None, "排序", self.menu2),
                               (None),
                               (None, "打开所在文件夹", None)
                               ], 
                              True)
        
        
        
        
######## Test demo ##################            

import gtk


def show_pop_menu(widget, event):
    if event.button == 3:
        menu.root_menu.show((int(event.x_root), int(event.y_root)),
                            (0, 0))
    
    
if __name__ == "__main__":        
    menu = PopupMenu()
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    win.connect("destroy", gtk.main_quit)
    btn = gtk.Button("点击菜单")
    btn.connect("button-press-event", show_pop_menu)
    win.add(btn)
    win.show_all()
    gtk.main()
        
    
