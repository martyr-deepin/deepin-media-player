#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import gtk
from widget.utils import is_file_audio, get_file_type

from format_conv.transmageddon import TransmageddonUI
from format_conv.conv_task_gui import ConvTAskGui
from widget.movie_menu import Menu


if __name__ == "__main__":
    def test_btn_clicked(w):
        menu.popup(500, 500)
    #TransmageddonUI(["/home/long/视频/test.mp4"])
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    btn = gtk.Button("测试")
    btn.connect("clicked", test_btn_clicked)
    win.add(btn)
    menu = Menu()
    menu.set_title("测试1")
    c_menu = Menu()
    c_menu.set_title("测试1-1")
    c_menu.menu_parent = menu
    c_menu.child_check = True
    menu.menu_items[0].child_menus = c_menu
    c_menu = Menu()
    c_menu.menu_parent = menu
    c_menu.set_title("测试1-2")
    c_menu.child_check = True
    menu.menu_items[2].child_menus = c_menu
    cc_menu = Menu()
    #c_menu.menu_items[0].child_menus = cc_menu
    win.show_all()
    gtk.main()
