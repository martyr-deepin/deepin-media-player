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
import pyinotify

class MediaConfig(gobject.GObject):
    __gsignals__ = {
        "get-items":(gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_NONE,(gobject.TYPE_INT,)),
        "get-option":(gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_NONE,(gobject.TYPE_INT,)),
        
        }
    def __init__(self):
        
        self.config_path = ""        
        self.cf = ConfigParser.ConfigParser()
        
    def init_read(self, config_path):    
        self.config_path = config_path
        self.cf.read(config_path)    
        
    def get_options(self, section):
        return self.cf.options(section)
    
    def get_items(self, section):
        return self.cf.items(section)
        
    def get_sections(self):
        return self.cf.sections()
    
    def add_section(self, section):
        self.cf.add_section(section)
        
    def set_value(self, section, option, value):    
        self.cf.set(section, option , value)
        
    def quit(self):    
        fp = open(self.config_path, "w")
        self.cf.write(fp)
        fp.close()
        
        
class EventHandler(ProcessEvent):
    def process_IN_CREATE(self, event):
        print   "Create file: %s "  %   os.path.join(event.path,
event.name)

    def process_IN_DELETE(self, event):
        print   "Delete file: %s "  %   os.path.join(event.path,
event.name)
    
    def process_IN_MODIFY(self, event):
            print   "Modify file: %s "  %   os.path.join(event.path,
event.name)
    

def FSMonitor(path='/home/long/.config/deepin-media-player'):
        wm = WatchManager() 
        mask = IN_DELETE | IN_CREATE |IN_MODIFY
        notifier = Notifier(wm, EventHandler())
        wm.add_watch(path, mask,rec=True)
        print 'now starting monitor %s'%(path)
        while True:
                try:
                        notifier.process_events()
                        if notifier.check_events():
                                notifier.read_events()
                except KeyboardInterrupt:
                        notifier.stop()
                        break


            
Test = 1    
if __name__ == "__main__":
    if Test == 1:
        FSMonitor()
    if Test == 3:    
        mc = MediaConfig()        
        mc.init_read("/home/long/project/deepin-media-player/src/test.ini")
        print mc.get_sections()
        print mc.get_items("db")
        print mc.get_options("db")

        mc.add_section("playlist")
        mc.set_value("playlist", "video1", "/home/long/meida/dfdf")
        mc.set_value("playlist", "video2", "/home/fdsfdsfsdf")
        mc.quit()
