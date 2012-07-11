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

import gtk
import os
from dtk.ui.slider import Wizard
from dtk.ui.utils import get_parent_dir

def init_user_guide():
    _file = os.path.join(get_parent_dir(__file__, 1), "user_guide")

    user_guide = Wizard(
        [os.path.join(_file, "network_play.png"),
         os.path.join(_file, "play_preview.png"),
         os.path.join(_file, "multi_mode_switch.png")],
        [(os.path.join(_file, "network_play_hover.png"), os.path.join(_file, "network_play_normal.png")),
         (os.path.join(_file, "play_preview_hover.png"), os.path.join(_file, "play_preview_normal.png")),
         (os.path.join(_file, "multi_mode_switch_hover.png"), os.path.join(_file, "multi_mode_switch_normal.png")),]
        )
    
    user_guide.show_all()
    


if __name__ == "__main__":
    gtk.gdk.threads_init()
    
    init_user_guide()

    gtk.main()
