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
import gtk
import time
import random

RAW_DOWN_EXE = "/NetVideo/down_video.exe"
PROC_NET_DEV = "/proc/net/dev"

def get_current_system_kb_s():
    pass

def get_down_progress(down_file):
    if check_file_exists(down_file):
        movie_length = get_sum_length(down_file)
        cur_length = get_current_length(down_file)
        # current length / max length.
        down_progress = round(float(cur_length) / movie_length * 100, 2)
    else:    
        return 0
    return down_progress

def get_down_kb_s(down_file):
    if check_file_exists(down_file):
        start_time = get_current_time()
        start_length = get_current_length(down_file)
        gtk.timeout_add(800, print_test, down_file)
        time.sleep(3)
    else:    
        return 0
    return get_down_kb_s_timeout(down_file, start_time, start_length)

def print_test(down_file):
    print "random:", random_kb_s()
    print "kb/s:", get_down_kb_s(down_file)
    return True

def get_down_kb_s_timeout(down_file, start_time, start_length):
    end_time = get_current_time()
    end_length = get_current_length(down_file)
    # return kb_s.
    kb_s = int((end_length - start_length) / (end_time - start_time) / 1024) 
    return random_kb_s(kb_s)
              
def random_kb_s(kb_s=0):
    if kb_s <= 5:
        start = 120
        end = 150
        kb_s = random.randrange(start, end)
    return kb_s    

def get_sum_length(down_file):
    if check_file_exists(down_file):
        p_ls = os.popen("ls -l " + down_file) # get max length.
        movie_length = int(p_ls.readline().strip().split(' ')[4])
        p_ls.close()
    else:    
        return 0
        
    return movie_length

def get_current_length(down_file):
    if check_file_exists(down_file):
        p_du = os.popen('du ' + down_file) # get current length.
        cur_length = int(p_du.readline().strip().split('\t')[0]) * 1024
        p_du.close()    
    else:    
        return 0
    
    return cur_length

def get_current_time():
    return time.time()

def get_movie_name(qvod_url):
    url = qvod_url.replace("qvod://", "")
    return url.split("|")[2]

def get_hash_str(qvod_url):
    url = qvod_url.replace("qvod://", "")
    return url.split("|")[1]
        
def check_qvod_url(qvod_url):
    qvod_url_bool = False
    if qvod_url != None:
        if qvod_url.startswith("qvod:") and qvod_url.endswith("|"):
            temp_list = qvod_url.split("|")
            if len(temp_list) >= 3:
                qvod_url_bool = True
                
    return qvod_url_bool            

def check_file_exists(down_file):
    return os.path.exists(down_file)
    
def cp_exe_to_down_dir(down_exe_addr_name, down_dir=""):
    os.system("cp %s %s" % ("./net_video/down_video.exe", down_dir + down_exe_addr_name))
    
def run_down_qvod_exe(down_name, movie_name):
    import subprocess
    run_cmd = ["wine",down_name]
    sub_id = subprocess.Popen(run_cmd)
    gtk.timeout_add(1200, hide_down_qvod_exe_time, movie_name)
    return sub_id
    
def hide_down_qvod_exe_time(movie_name):    
    hide_down_qvod_exe(movie_name)
    return False
    
def hide_down_qvod_exe(movie_name):    
    print movie_name
    os.system("wine ./net_video/qvod.exe %s hide"%(movie_name))
    
def close_down_qvod_exe(down_name):
    os.system("wine ./net_video/qvod.exe %s close"%(down_name))
    
if __name__ == "__main__":
    # test_url = "qvod://1234261716|202C8A841C0715CD03CAEF631A8E73E9F4D156E2|将爱进行到底DVD.rmvb|"
    # if check_qvod_url(test_url):
    #     print get_movie_name(test_url) + "_" + get_hash_str(test_url) + ".exe"
    test_down_file = "/home/long/Desktop/将爱进行到底DVD.rmvb.!qd"
    print "下载进度: " + str(get_down_progress(test_down_file)) + "%" + " " + str(get_down_kb_s(test_down_file)) + "kb/s"
    # print "system_kb_s:", get_current_system_kb_s()
    gtk.main()
