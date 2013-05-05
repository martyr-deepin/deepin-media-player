#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import gtk
from widget.utils import is_file_audio, get_file_type

from format_conv.transmageddon import TransmageddonUI
from format_conv.conv_task_gui import ConvTAskGui
from widget.movie_menu import ScreenMidCombo


if __name__ == "__main__":
    #TransmageddonUI(["/home/long/视频/test.mp4"])
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    combo = ScreenMidCombo()
    win.add(combo)
    win.show_all()
    gtk.main()
