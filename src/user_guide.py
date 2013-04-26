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

from dtk.ui.slider import Wizard
from deepin_utils.file import get_parent_dir
import gtk
import locale
import os

def init_user_guide(callback=None):
    # Get language in current environment.
    (lang, _) = locale.getdefaultlocale()
    if lang == "zh_CN":
        slide_lang = lang
    elif lang in ["zh_HK", "zh_TW"]:
        slide_lang = "zh_HK"
    else:
        slide_lang = "en"
        
    # Get image directory.
    image_dir = os.path.join(get_parent_dir(__file__, 1), "user_guide")
    lang_dir  = os.path.join(image_dir, slide_lang)

    # Init user guide.
    user_guide = Wizard(
        [os.path.join(lang_dir, "%d.png" % i) for i in range(3)],
        (os.path.join(image_dir, "dot_normal.png"),
         os.path.join(image_dir, "dot_active.png"),             
         ),
        callback
        )
    
    # Show user guide.
    user_guide.show_all()

if __name__ == "__main__":
    gtk.gdk.threads_init()
    
    init_user_guide()

    gtk.main()
