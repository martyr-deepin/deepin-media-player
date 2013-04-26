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

# Media Player gui settings constant. 深度影音界面设置常量.
APP_WIDTH = 640 #  影音宽度
APP_HEIGHT = 480 # 影音高度
#
PROGRAM_NAME = "deepin-media-player" # appcation name. 应用程序名字.
PROGRAM_VERSION = "2.0" # version. 版本号.
#
DEBUG = True

def get_system_font():
    import gtk
    font_widget = gtk.Button()
    font_name = ' '.join(str(font_widget.get_pango_context().get_font_description()).split(" ")[0:-1])
    return font_name
DEFAULT_FONT = get_system_font()
DEFAULT_FONT_SIZE = 10

SEEK_VALUE = 10
VOLUME_VALUE = 5

# preview
PREVIEW_PV_WIDTH = 120
PREVIEW_PV_HEIGHT = 60
