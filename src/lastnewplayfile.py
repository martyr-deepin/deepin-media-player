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

from ini import Config

import os
import time
import gobject

class LastNewPlayFile(gobject.GObject):
    __gsignals__ = {
        "get-file-name":(gobject.SIGNAL_RUN_LAST,
                           gobject.TYPE_NONE,(gobject.TYPE_STRING,))
        }
    def __init__(self):
        gobject.GObject.__init__(self)
        self.ini = Config(self.get_home_path() + "/.config/deepin-media-player/config.ini")
        
        # Init time.
        self.year = 0
        self.mon  = 0
        self.mday = 0
        self.hour = 0
        self.min  = 0
        self.sec  = 0
        self.time = "%s%s%s%s%s%s"%(self.year, self.mon, self.mday, self.hour, self.min, self.sec)
        # Init argvs list.
        self.argvs_list = self.ini.get_argvs("LastNewPlayFile")
        self.argvs_num  = 0
        if self.argvs_list:            
            self.argvs_num  = len(self.argvs_list.keys())
        self.table_list = []
        
    def get_current_time(self):
        time_struct = time.localtime(time.time())
        self.year = time_struct.tm_year
        self.mon  = time_struct.tm_mon
        self.mday = time_struct.tm_mday
        self.hour = time_struct.tm_hour
        self.min  = time_struct.tm_min
        self.sec  = time_struct.tm_sec
        return "%s%s%s%s%s%s"%(self.year, self.mon, self.mday, self.hour, self.min, self.sec)
        
    def set_file_time(self, play_file):
        if len(play_file) > 0:
            if self.ini.get_argv_bool("LastNewPlayFile", '"%s"'%(play_file)):            
                self.ini.set("LastNewPlayFile", '"%s"'%(play_file), self.get_current_time())            
            else:
                if self.argvs_num < 10:
                    # print self.argvs_num
                    self.ini.set("LastNewPlayFile", '"%s"'%(play_file), self.get_current_time())
                else:                    
                    modify_argv = self.get_modify_argv().argv
                    # print "modify_argv...."
                    self.ini.modify_argv("LastNewPlayFile", '%s'%(modify_argv), '"%s"'%(play_file), self.get_current_time())
                
        # Save and get argv kyes.    
        self.argvs_list = self.ini.get_argvs("LastNewPlayFile")
        # print self.argvs_list
        if self.argvs_list:
            self.argvs_num = len(self.argvs_list.keys())
        self.ini.save()
        
        return self.argvs_to_menu()
    
    def argvs_to_menu(self):
        temp_last_list = []
        try:
            for argv in self.ini.get_argvs("LastNewPlayFile"):
                argv_name = (argv[1:])[:-1]
                # print argv_name
                temp_last_list.append((None, argv_name, lambda :self.emit("get-file-name","%s" % (argv_name))))
        except:        
            pass
                        
        return temp_last_list
            
        
    def get_modify_argv(self):    
        return self.create_table()
    
    def get_home_path(self):
        return os.path.expanduser("~")
        
    def create_table(self):
        temp_table = Table()
        temp_table.section = "LastNewPlayFile"
        temp_table.argv    = self.argvs_list.keys()[0]
        temp_table.value   = self.argvs_list[self.argvs_list.keys()[0]]
        
        for key in self.argvs_list.keys():
            if self.argvs_list[key] <= temp_table.value:
                temp_table.argv  = key
                temp_table.value = self.argvs_list[key]
                
        return temp_table        
    
class Table(object):    
    def __init__(self):
        self.section  = None
        self.argv     = None
        self.value    = None
        
if __name__ == "__main__":        
    last_new_play_file = LastNewPlayFile()
    last_new_play_file.set_file_time("/media/文档/电影/守望者~罪恶迷途-MP4/守望者~罪恶迷途B123123.mp4")
    






