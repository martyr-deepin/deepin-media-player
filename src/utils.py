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
import re

app_theme = Theme(os.path.join(
        (os.path.dirname(os.path.realpath(__file__))),"../app_theme"))

def get_home_path():
    return os.path.expanduser("~")
    
def get_length(file_path):
    '''Get media player length.'''
    cmd = "mplayer -vo null -ao null -frames 0 -identify '%s' 2>&1" % (file_path)
    fp = Popen(cmd, shell=True, stdout=PIPE)
    cmd_str = fp.communicate()[0]
    length_compile = re.compile(r"ID_LENGTH=([\d|\.]+)")
    length = length_compile.findall(cmd_str)[0]
    return float(length)


def allocation(widget):
    cr = widget.window.cairo_create()
    rect = widget.get_allocation()
    return cr, rect.x, rect.y, rect.width, rect.height

media_player = {"app":None, 
                "mp":None, 
                "screen":None,
                "panel":None,
                "panel2":None,
                "progressbar":None,
                "bottomhbox":None,
                "playlist":None,
                "play_state":0,
                "common_state":True,
                "fullscreen_state":False,
                "play_file_path":None,
                "show_time":None}


