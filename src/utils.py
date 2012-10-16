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
import gio
import os
from type_check import is_file_can_play, is_valid_dmp_file

############################################################
### get widget : x, y, width, height.
def allocation(widget):
    cr = widget.window.cairo_create()
    rect = widget.get_allocation()
    return cr, rect.x, rect.y, rect.width, rect.height

############################################################
### threads.
def path_threads(path, mp):
    '''Thread path.'''
    os.chdir(path)
    
    if os.path.isdir(path):
        for i in os.listdir(path):
            if "." == i[0:1]:
                continue
            
            new_path = os.path.join(path, i)
                            
            if os.path.isdir(new_path):
                path_thread_id = threading.Thread(target=path_threads, args=(new_path, mp))
                path_thread_id.setDaemon(True)
                path_thread_id.start()
                
            if os.path.isfile(new_path):    
                new_file = new_path                
                # .dmp add play file..
                if is_valid_dmp_file(new_file):
                    mp.load_playlist(new_file)
                    
                # play file[.rmvb, .avi...].    
                if(is_file_can_play(new_file)):
                    old_file = new_file
                    file1, file2 = os.path.splitext(new_file)
                    new_file = file1 + file2.lower()                    
                    os.rename(old_file,new_file)
                    mp.add_play_file(new_file)                
                    
def get_paly_file_name(path):
    return os.path.splitext(os.path.split(path)[1])[0]

def get_paly_file_type(path):
    return os.path.splitext(os.path.split(path)[1])[1][1:]


def length_to_time(length):
    time_sec = int(float(length))
    time_hour = 0
    time_min = 0
    
    if time_sec >= 3600:
        time_hour = int(time_sec / 3600)
        time_sec -= int(time_hour * 3600)
        
    if time_sec >= 60:
        time_min = int(time_sec / 60)
        time_sec -= int(time_min * 60)         
        
    return str("%s:%s:%s"%(str(time_add_zero(time_hour)), 
                           str(time_add_zero(time_min)), 
                           str(time_add_zero(time_sec))))

def time_add_zero(time_to):    
    if 0 <= time_to <= 9:
        time_to = "0" + str(time_to)
    return str(time_to)

def get_file_size(path):        
    if os.path.exists(path):
        file_size = os.path.getsize(path)            
        return size_to_format(file_size)
    else:
        return 0
    
diskunit = ['Byte', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB']
def size_to_format(size, unit='Byte'):    
    if size < 1024:
        # print "size_to_format:", size
        return '%.2f %s' % (size, unit)
    else:
        return size_to_format(size/1024.0, diskunit[diskunit.index(unit) + 1])
    
    
    
    
