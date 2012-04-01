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
from  pyinotify import  WatchManager, Notifier, ProcessEvent, IN_DELETE, IN_CREATE,IN_MODIFY
import ConfigParser
import string, os, sys
import gobject



class MediaConfig(gobject.GObject):
    __gsignals__ = {
        "media-config":(gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_NONE,())
        # "media-modify":(gobject.SIGNAL_RUN_LAST,
        #                 gobject.TYPE_NONE,())
        }
    def __init__(self):
        gobject.GObject.__init__(self)
        self.config_path = ""        
        self.cf = ConfigParser.ConfigParser()
        self.emit("media-config")
        
    def init_read(self, config_path):    
        self.config_path = config_path
        self.cf.read(config_path)    
        self.emit("media-config")        
        
    def get_value(self, section, option):    
        try:
            return self.cf.get(section, option)
        except:
            return -1
            
    def get_options(self, section):
        try:
            return self.cf.options(section)
        except:
            return -1
    
    def get_items(self, section):
        try:
            return self.cf.items(section)
        except:
            return -1
        
    def get_sections(self):
        try:
            return self.cf.sections()
        except:
            return -1
            
    def add_section(self, section):
        self.cf.add_section(section)
        
    def set_value(self, section, option, value):    
        self.cf.set(section, option , value)
        
    def save_config(self):    
        fp = open(self.config_path, "w")
        self.cf.write(fp)
        fp.close()
        
    # def FSMonitor(self):
    #     if "" != self.config_path:
    #         wm = WatchManager() 
    #         mask = IN_MODIFY
    #         notifier = Notifier(wm, self.process_IN_MODIFY)
    #         wm.add_watch(self.config_path, mask, rec=True)
    #         print 'now starting monitor %s'%(self.config_path)
    #         while True:
    #             try:
    #                 notifier.process_events()
    #                 if notifier.check_events():
    #                     notifier.read_events()
    #             except KeyboardInterrupt:
    #                 notifier.stop()
    #                 break
    
    # def process_IN_MODIFY(self, event):
    #     '''File modify emit signal.'''
    #     print   "Modify file: %s "  %   os.path.join(event.path, event.name)
    #     self.emit("media-modify")
        
media_config = MediaConfig()        

def Test(config):
    print "fdsf"
        
if __name__ == "__main__":
    mc = MediaConfig()        
    #mc.connect("media-config", Test)
    mc.init_read(get_home_path() + "/.config/deepin-media-player/config.ini")
    # mc.add_section("window_mode")
    # mc.set_value("window_mode", "ss", "50")
    # mc.set_value("window_mode", "vv", "150")
    print mc.get_options("window")
    print mc.get_items("window_mode")
    print mc.get_sections()
    
    print mc.get_items("window")
    print mc.get_value("window_mode", "ss")
    #mc.write()
    #mc.FSMonitor()


   
