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
import threading

class ThreadManage(object):
    '''Threading manage class.'''
    def __init__(self):
        self.thread_dict = {}
        
    def add_thread(self, thread_id, thread_name=None):
        if thread_name is not None:
            thread_id.setName(thread_name)
            self.thread_dict[thread_id.getName()] = thread_id
            
    def thread_name_to_string(self, thread_name):                            
        return str(thread_name)
    
    def thread_run_bool(self, thread_name):    
        thread_name = self.thread_name_to_string(thread_name)
        if self.thread_dict.has_key(str(thread_name)):
            return self.thread_dict[str(thread_name)].isAlive() 
        
    def thread_name_bool(self, thread_name):    
        thread_name = self.thread_name_to_string(thread_name)
        if self.thread_dict.has_key(str(thread_name)):
            return True
        
    def get_all_thread_name(self):
        return self.thread_dict
                        
    def clear_threads(self):
        self.thread_dict = {}

        
        
