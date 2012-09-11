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


from dtk.ui.dialog import DialogBox, DIALOG_MASK_MULTIPLE_PAGE
from skin          import app_theme
from locales       import _
import os
import gtk
import gobject
import threading
         
# Video section.
class VideoSection(object):
    def __init__(self):     
        self.flags = False   
        self.code_format      = None        
        self.video_bit_rate   = None
        self.video_frame_rate = None
        self.resolution       = None
        self.display_         = None
        
# Audio section.
class AudioSection(object):
    def __init__(self):
        self.flags = False
        self.code_format      = None
        self.audio_bit_rate   = None
        self.channels_number  = None
        self.sampling_number  = None
        self.audio_digit      = None
        
# code information.        
class CodeInFormation(object):
    def __init__(self):
        self.flags = False
        # Video section.
        self.video_section = VideoSection()
        # Audio section.
        self.audio_section = AudioSection()

# video information.
class VideoInFormation(object):
    def __init__(self):
        self.flags = False
        # Player file icon.
        self.icon = None
        # File type.
        self.file_type = None
        # Resolution.
        self.resolution = None
        # File size.
        self.file_size = None
        # File length(time).
        self.length = None
        # Code information.
        self.code_information = CodeInFormation()

def get_video_information(video_path):
    cmd = "mplayer -identify -frames 5 -endpos 0 -vo null  '%s'" % (video_path)
    pipe = os.popen(str(cmd))
    return video_string_to_information(pipe)
    
def video_string_to_information(pipe):
    video_information = VideoInFormation()
    video_information.code_information.video_section.code_format = "RMVB"
    print pipe.read()
    return video_information
            
###########################################################
### video information GUI.

class VideoInformGui(gobject.GObject):
    def __init__(self):
        gobject.GObject.__init__(self)
        self.app = DialogBox("文件信息查看", 480, 350,
                             mask_type=DIALOG_MASK_MULTIPLE_PAGE,
                             modal=False,
                             window_hint=gtk.gdk.WINDOW_TYPE_HINT_DIALOG,
                             window_pos=gtk.WIN_POS_CENTER,
                             resizable=True)        
        # Init . 
        
        # Set app size.
        self.app.set_size_request(480, 350)
        
        self.app.connect("destroy", lambda w : self.app.destroy())
                
        # self.app.body_box.pack_start()
        # self.app.left_button_box.set_buttons([self.scan_sub_sum_label])
        # self.app.right_button_box.set_buttons([self.down_button, self.close_button])
    def show_window(self):    
        self.app.show_all()
        
    def init_(self): 
        self.file_type_label = ""
        self.resolution_label = ""
        self.file_size_label = ""
        self.length_label = "" # format(hour:min:sec)
        
