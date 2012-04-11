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

from dtk.ui.theme import *
from subprocess import *
from mplayer import *
import re

app_theme = Theme(os.path.join(
        (os.path.dirname(os.path.realpath(__file__))),"../app_theme"))


def allocation(widget):
    cr = widget.window.cairo_create()
    rect = widget.get_allocation()
    return cr, rect.x, rect.y, rect.width, rect.height


def pause_scrot(widget):
    x, y, w, h = widget.get_allocation()
    screenshot = gtk.gdk.Pixbuf.get_from_drawable(  
    gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, w, h),
            widget.window,
            gtk.gdk.colormap_get_system(),
            0, 0, 0, 0, w, h)
    save_path = get_home_path() + '/.config/deepin-media-player/image/pause.png'
    screenshot.save(save_path, 'png')    
