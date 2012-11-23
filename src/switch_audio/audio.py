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

import os
import gobject

VIDEO_TYPE = 0
DVD_TYPE = 1
VCD_TYPE = 2

class SwitchAudio(gobject.GObject):    
    __gsignals__ = {
        "add-switch-sid-file" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                                 (gobject.TYPE_PYOBJECT, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING)),
        "add-switch-aid-file" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                                 (gobject.TYPE_PYOBJECT, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING))
        }    
    def __init__(self):
        gobject.GObject.__init__(self)
        # Init value.
        self.switch_audio_list = []
        self.switch_subtitles_list = []
        # self.get_video_information(player_path)
        
    def get_video_information(self, video_path, video_type=VIDEO_TYPE):
        if video_type == VIDEO_TYPE:
            cmd = "mplayer -identify -frames 5 -endpos 0 -vo null '%s'" % (video_path)
        elif video_type == DVD_TYPE:
            cmd = "mplayer -vo null -ao null -frames 0 -identify "
            cmd += "dvd:// -dvd-device '%s'" % (video_path)

        pipe = os.popen(str(cmd))
        
        id_aid_id   = "ID_AUDIO_ID="
        id_aid_name = "ID_AID_%s_NAME="
        id_aid_lang = "ID_AID_%s_LANG="
        
        id_sid_id   = "ID_SUBTITLE_ID="
        id_sid_name = "ID_SID_%s_NAME="
        id_sid_lang = "ID_SID_%s_LANG="
        
        while True: 
            try:
                line_text = pipe.readline()
            except StandardError:
                break
        
            if not line_text:
                break
            # Get (number, name, lang)
            if line_text.startswith(id_aid_id):
                # Get aid id.
                number = line_text.replace(id_aid_id, "").split("\n")[0]
                # Get aid name.
                line_name_text = pipe.readline()
                name = "unknown"
                if line_name_text.startswith(id_aid_name % (number)):
                    name = line_name_text.replace(id_aid_name % (number), "").split("\n")[0]
                # Get aid lang.
                line_lang_text = pipe.readline()
                lang = "und"
                if line_lang_text.startswith(id_aid_lang % (number)):
                    lang = line_lang_text.replace(id_aid_lang % (number), "").split("\n")[0]
                # Save (number, name, lang).
                switch_audio_tuple = (number, name, lang)
                self.switch_audio_list.append(switch_audio_tuple)
                self.emit("add-switch-aid-file", self.switch_audio_list, number, name, lang)
                
            # Get subtitles.    
            if line_text.startswith(id_sid_id):    
                # Get sid id.
                number = line_text.replace(id_sid_id, "").split("\n")[0]
                # Get sid name.
                line_name_text = pipe.readline()                
                if line_name_text.startswith(id_sid_name % (number)):
                    name = line_name_text.replace(id_sid_name % (number), "").split("\n")[0]
                # Get sid lang.
                line_lang_text = pipe.readline()                    
                if line_lang_text.startswith(id_sid_lang % (number)):
                    lang = line_lang_text.replace(id_sid_lang % (number), "").split("\n")[0]
                # Save (number, name, lang)    
                switch_subtitles_tuple = (number, name, lang)
                self.switch_subtitles_list.append(switch_subtitles_tuple)
                self.emit("add-switch-sid-file", self.switch_subtitles_list, number, name, lang)
                
            # print line_text
                
        # Test print info.        
        # print "test print info[audio_tuple]:"
        # for  audio_tuple in self.switch_audio_list:
        #     print "%s(%s)-%s" % (audio_tuple[1], audio_tuple[2], audio_tuple[0])
        # print "test print info[subtitles_tuple]:"
        # for subtitles_tuple in self.switch_subtitles_list:
        #     print "%s(%s)-%s" % (subtitles_tuple[1], subtitles_tuple[2], subtitles_tuple[0])                         
            
            
if __name__ == "__main__":
    def add_switch_sid_file(SwitchAudio, switch_subtitles_list, number, name, lang):
        print "add_switch_sid_file:"
        print "%s(%s)-%s" % (name, lang, number)
    
    def add_switch_aid_file(SwitchAudio, switch_audio_list, number, name, lang):
        print "add_switch_aid_file:"
        print "%s(%s)-%s" % (name, lang, number)
    
    player_path = "/home/long/视频/select_switch/超级大坏蛋.Megamind.720p.梦幻天堂·龙网(killman.net).mkv"
    switch_audio = SwitchAudio()
    switch_audio.connect("add-switch-sid-file", add_switch_sid_file)
    switch_audio.connect("add-switch-aid-file", add_switch_aid_file)
    switch_audio.get_video_information(player_path)
