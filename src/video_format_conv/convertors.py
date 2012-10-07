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
import codecfinder
import glib
import presets
import os

NULL  = gst.STATE_NULL
PAUSE = gst.STATE_PAUSED
PLAYING = gst.STATE_PLAYING

# 保存视频格式转化的各个信息
class FormatInfo: 
    def __init__(self):
        self.filechosen = "" # FILECHOSEN = ""
        self.FILENAME = ""
        self.DESTDIR = ""
        self.CONTAINERCHOICE = ""
        self.AUDIOCODECVALUE = ""
        self.VIDEOCODECVALUE = ""
        self.PRESET = ""
        self.OHEIGHT = ""
        self.OWIDTH = ""
        self.FRATENUM = ""
        self.FRATEDEN = ""
        self.ACHANNELS = ""
        self.MULTIPASS = ""
        self.PASSCOUNTER = ""
        self.OUTPUTNAME = ""
        self.TIMESTAMP = ""
        self.ROTATIONVALUE = ""
        self.AUDIOPASSTOGGLE = ""
        self.VIDEOPASSTOGGLE = ""
        self.INTERLACED = ""
        self.INPUTVIDEOCAP = ""        
        #
        
class Convertors(gobject.GObject):
    __gsignals__ = {
        'convertors-update-progressbar' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        'convertors-eos' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        'convertors-error' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))
            }    
    def __init__(self, _format_info):
        gobject.GObject.__init__(self)
        #
        self.__format_info = _format_info
        # create pipeline.
        self.pipeline = gst.Pipeline("pipeline")
        self.pipeline.set_state(PAUSE)                    
        # uri file name.
        self.uridecoder = gst.element_factory_make("uridecodebin", "uridecoder")
        self.uridecoder.set_property("uri", self.__format_info.filechosen)
        
        
        self.pipeline.add(self.uridecoder)
        
        # connect bus message.
        bus = self.pipeline.get_bus()
        bus.add_watch(self.on_message)
        
    def on_message(self, bus, message):
        __type = message.type
        
        if gst.MESSAGE_EOS == __type: # 结束
            if self.passcounter == 0:
                if os.access(self.cachefile, os.F_OK):
                    os.remove(self.cachefile)
            self.emit("convertors-eos")
            self.player.set_state(NULL)
        elif gst.MESSAGE_ERROR == __type: # 错误信息
            (err, debug) = message.parse_error()
            # gst.DEBUG_BIN_TO_DOT_FILE (self.pipeline, gst.DEBUG_GRAPH_SHOW_ALL, 'transmageddon.dot')
            self.emit("convertors-error", err.message) # 发送错误信息给GUI界面.
        elif gst.MESSAGE_ASYNC_DONE == __type: # 更新进度条
            self.emit("convertors-update-progressbar") # 发送更新信号给GUI界面更新进度条.
        elif gst.MESSAGE_APPLICATION:    
            self.pipeline.set_state(NULL)
            self.pipeline.remove(self.uridecoder)
            
        return True    
        
