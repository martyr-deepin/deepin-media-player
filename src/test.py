#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import gtk
from widget.utils import is_file_audio, get_file_type

from format_conv.transmageddon import TransmageddonUI
from format_conv.conv_task_gui import ConvTAskGui
from widget.movie_menu import ScreenMidCombo
from screen_mid.open_url import OpenUrlDialog
from widget.net_search import Search


if __name__ == "__main__":
    #TransmageddonUI(["/home/long/视频/test.mp4"])
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    combo = ScreenMidCombo()
    search = Search()
    #win.add(combo)
    win.add(search)
    win.show_all()
    gtk.main()
    '''
    open_url_win = OpenUrlDialog()
    open_url_win.show_all()
    gtk.main()
    '''



