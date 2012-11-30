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
import time

RAW_DOWN_EXE = "/NetVideo/down_video.exe"


def get_down_info(down_file, start_time=0, start_length=0):
    '''get down progress.'''
    return (get_down_progress(down_file), get_down_kb_s(down_file, start_time, start_length))
    
def get_down_progress(down_file):
    movie_length = get_sum_length(down_file)
    cur_length = get_current_length(down_file)
    # current length / max length
    down_progress = round(float(cur_length) / movie_length * 100, 2)
    return down_progress

def get_down_kb_s(down_file, start_time, start_length):
    ##############################
    # time.sleep(0.1)    
    ###############################
    start_time = get_current_time()
    start_length = get_current_length(down_file)
    end_time = get_current_time()
    end_length = get_current_length(down_file)
    print "start_time:", start_time
    print "start_length:", start_length
    # while True:
    #     end_length = get_current_length(down_file)
    #     end_time = get_current_time()
    #     if start_length != end_length and (start_time != end_time):
    #         print "end_length:", end_length
    #         print "end_time:", end_time
    #         break
    #     else:
    #         start_length = end_length
    #         start_time = end_time
        
    return int((end_length - start_length) / (end_time - start_time) / 1024)
              
def get_sum_length(down_file):
    p_ls = os.popen("ls -l " + down_file) # get max length.
    movie_length = int(p_ls.readline().strip().split(' ')[4])
    p_ls.close()
    return movie_length

def get_current_length(down_file):
    p_du = os.popen('du ' + down_file) # get current length.
    cur_length = int(p_du.readline().strip().split('\t')[0]) * 1024
    p_du.close()    
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


if __name__ == "__main__":
    # test_url = "qvod://1234261716|202C8A841C0715CD03CAEF631A8E73E9F4D156E2|将爱进行到底DVD.rmvb|"
    # if check_qvod_url(test_url):
    #     print get_movie_name(test_url) + "_" + get_hash_str(test_url) + ".exe"
    test_down_file = "/home/long/Desktop/将爱进行到底DVD.rmvb.!qd"
    info = get_down_info(test_down_file, get_current_time(), get_current_length(test_down_file))
    print "下载进度: " + str(info[0]) + "%" + " " + str(info[1]) + "kb/s"
    
    
