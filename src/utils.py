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
import os

def allocation(widget):
    cr = widget.window.cairo_create()
    rect = widget.get_allocation()
    return cr, rect.x, rect.y, rect.width, rect.height

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
                 #path_threads(new_path, mp)
                
            if os.path.isfile(new_path):    
                new_file = new_path                
                # .dmp add play file..
                if(mp.find_dmp(new_file)):
                    mp.load_playlist(new_file)
                    
                # play file[.rmvb, .avi...].    
                if(mp.find_file(new_file)):
                    old_file = new_file
                    file1, file2 = os.path.splitext(new_file)
                    new_file = file1 + file2.lower()                    
                    os.rename(old_file,new_file)
                    mp.add_play_file(new_file)                
                    
