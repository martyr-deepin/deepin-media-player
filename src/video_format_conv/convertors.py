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

import gobject
import gst

NULL  = gst.STATE_NULL
PAUSE = gst.STATE_PAUSED

# 保存视频格式转化的各个信息
class Format:
    def __init__(self):
        self.source_file = ""
        self.output_file = ""
        self.codecaps = None
    
        
class Convertors(gobject.GObject):
    __gsignals__ = {
        'convertors-update-progressbar' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        'convertors-eos' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        'convertors-error' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))
            }    
    def __init__(self, _format):
        gobject.GObject.__init__(self)
        #
        self.__format = _format
        #
        self.pipeline = gst.Pipeline("Convertors")
        self.pipeline.set_state(PAUSE)
        self.uridecoder = gst.element_make_factor("uridecoder", "uridecoder")
        self.player_name.set_property("uri", "file://%s" % (self.__format.source_file))
        #
        # gst.Caps("audio/mpeg")
        #
        self.pipeline.add(self.uridecoder)
        self.pipeline.set_state(PAUSE)
        
        #
        bus = self.player.get_bug()
        bus.add_signal_watch()
        bus.connect("message", self.on_message)
        
    def on_message(self, bus, message): 
        __type = message.type
        if gst.MESSAGE_EOS == __type: # 结束
            self.player.set_state(NULL)
            self.emit("convertors-eos")
        elif gst.MESSAGE_ERROR == __type: # 错误信息
            self.player.set_state(NULL)
            (err, debug) = message.parse_error()
            self.emit("convertors-error", err.message) # 发送错误信息给GUI界面.
        elif gst.MESSAGE_ASYNC_DONE == __type: # 更新进度条
            self.emit("convertors-update-progressbar") # 发送更新信号给GUI界面更新进度条.            
            
            
            
        
