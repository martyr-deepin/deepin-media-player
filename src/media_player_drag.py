#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2013 Deepin, Inc.
#               2013 Hailong Qiu
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


import gobject
import urllib
import glib
import gtk
import os

DRAG_NAME_0  = "text/plain"
DRAG_INFO_0  = 0

DRAG_NAME_1  = "text/uri-list"
DRAG_INFO_1  = 1

DRAG_NAME_2  = "STRING"
DRAG_INFO_2  = 2


class MediaPlayDrag(object):
    def __init__(self, this):
        self.__init_values(this)
        self.__init_events()

    def __init_values(self, this):
        self.this = this
        self.app  = self.this.gui.app
        self.play_list = self.this.gui.play_list_view.list_view
        #
        self.target = [
                (DRAG_NAME_0, 0, DRAG_INFO_0),
                (DRAG_NAME_1, 0, DRAG_INFO_1),
                (DRAG_NAME_2, 0, DRAG_INFO_2)
                ]

    def __init_events(self):
        # 初始化拖动 文件，文件夹，文本字符.
        self.__init_drag_files(self.this.gui.screen_frame)
        self.__init_drag_files(self.play_list, type_check=False)

    def __init_drag_files(self, widget, type_check=True):
        # 拖动文件，文件夹，文字.
        widget.drag_dest_set(
                gtk.DEST_DEFAULT_MOTION |
                #gtk.DEST_DEFAULT_HIGHLIGHT |
                gtk.DEST_DEFAULT_DROP,
                self.target,
                gtk.gdk.ACTION_COPY
                )
        #
        widget.connect("drag-data-received", self.widget_drag_data_received_event, type_check)

    def widget_drag_data_received_event(self, w, context, x, y, data, info, time, type_check):
        if not data:
            return False
        if data.get_length() < 0:
            return False

        if (info == DRAG_INFO_0 or
            info == DRAG_INFO_1 or 
            info == DRAG_INFO_2):
            try:
                files = glib.uri_list_extract_uris(str(data.data).strip())
            except:
                files = str(data.data).split("\n")[:-1]
            files_list = []
            paths_list = []
            for file in files:
                if len(file) > 0:
                    file = urllib.unquote(file)
                    # 转换字符格式.
                    if file.startswith("file:///"):
                        file = file[7:]
                    else:
                        file = file.decode("unicode-escape")
                    # 判断这个目录是否存在.
                    if os.path.exists(file):
                        # 判断是否为目录.
                        if os.path.isdir(file):
                            file = urllib.unquote(file)
                            path = file
                            paths_list.append(str(path))
                        else:
                            # 判断是字幕文件还是播放文件.
                            file = urllib.unquote(file)
                            files_list.append(str(file))
            if files_list:
                self.this.files_to_play_list(files_list, type_check)
            if paths_list:
                self.this.dirs_to_play_list(paths_list, type_check)

        return True



