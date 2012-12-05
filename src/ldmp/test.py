#! /usr/bin/env python
# -*- coding: utf-8 -*-

from dtk.ui.init_skin import init_skin
from dtk.ui.utils import get_parent_dir
import os
app_theme = init_skin(
    "deepin-ui-demo", 
    "1.0",
    "01",
    os.path.join(get_parent_dir(__file__), "skin"),
    os.path.join(get_parent_dir(__file__), "app_theme"),
    )

from dtk.ui.scrolled_window import ScrolledWindow
from ldmp import LDMP

import gtk

win = gtk.Window(gtk.WINDOW_TOPLEVEL)
win.connect("destroy", lambda w : gtk.main_quit())
win.set_size_request(500, 500)
main_vbox = gtk.VBox()
ldmp = LDMP() # 脚本运行.
win.connect("key-press-event", ldmp.key_press_event)
ldmp.open("test.ldmp")
main_vbox.pack_start(gtk.Entry(), False, False)
main_vbox.pack_start(ldmp, True, True)
win.add(main_vbox)
win.show_all()
gtk.main()
