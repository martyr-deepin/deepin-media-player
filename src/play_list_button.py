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

from dtk.ui.button import ToggleButton
from skin import app_theme
from tooltip import tooltip_text
from locales import _

class PlayListButton(object):
    def __init__(self):
        self.button = ToggleButton(
            app_theme.get_pixbuf("bottom_buttons/play_list_button.png"),
            app_theme.get_pixbuf("bottom_buttons/list_button_background.png"),
            )
        self.button.set_active(False)
        tooltip_text(self.button, _("Playlist"))
        
