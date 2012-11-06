#! /Usrh/bin/env python
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

import fcntl
import os

OPEN_CDROM  = 0x5309
CLOSE_CDROM = 0x5319
# 光盘类型.
CDROM_ERROR      = -1
CDROM_TYPE_DVD   = 0
CDROM_TYPE_VCD   = 1
CDROM_TYPE_CD    = 2
CDROM_TYPE_ISO   = 3
CDROM_TYPE_DATA  = 4
CDROM_TYPE_EMPTY = 5
# dvd.
AUDIO_TS = "AUDIO_TS"
VIDEO_TS = "VIDEO_TS"
# vcd.
MPEGAV  = "MPEGAV"
SEGMENT = "SEGMENT"
# cd.

################################################
###
def cdrom_type(cdrom_path):
    try:
        cdrom_file_list = os.listdir(cdrom_path)
        if len(cdrom_file_list) == 0:
            return CDROM_TYPE_EMPTY
    except Exception, e:
        print "cdrom_type[error]:", e
        return CDROM_ERROR
    # cdrom type.
    if cdrom_dvd(cdrom_file_list):
        return CDROM_TYPE_DVD
    elif cdrom_vcd(cdrom_file_list):
        return CDROM_TYPE_VCD
    elif cdrom_cd(cdrom_file_list):
        return CDROM_TYPE_CD
    elif cdrom_iso(cdrom_file_list):
        return CDROM_TYPE_ISO
    elif cdrom_data(cdrom_file_list):
        return CDROM_TYPE_DATA
    else:
        return CDROM_ERROR
    
def cdrom_dvd(file_list):
    audio_ts_bool = False
    video_ts_bool = False
    for file_ in file_list:
        if file_.upper().startswith(AUDIO_TS):
            audio_ts_bool = True
        elif file_.upper().startswith(VIDEO_TS):
            video_ts_bool = True            
    return (audio_ts_bool and video_ts_bool)

def cdrom_vcd(file_list):
    mpegav_bool = False
    segment_bool = False
    for file_ in file_list:
        if file_.upper().startswith(MPEGAV):
            mpegav_bool = True
        elif file_.upper().startswith(SEGMENT):
            segment_bool = True
    return (mpegav_bool and segment_bool)

def cdrom_cd(file_list):
    pass

def cdrom_iso(file_list):
    pass

def cdrom_data(file_list):
    return True

###############################################################
def scan_cdrom():
    cdrom_list = []
    dev_name_list = os.listdir("/dev")
    for name in dev_name_list:
        if name.startswith("cdrom"):
            cdrom_list.append(os.path.join("/dev", name))
    return cdrom_list        

def ioctl_cdrom(cdrom, CDROM_MASK):    
    try:
        cd_device = cdrom
        if os.path.islink(cd_device):
            base_path = os.path.dirname(cd_device)
            if not cd_device[0] == '/':
                cd_device = os.path.join(base_path, cd_device)
            # cdrom mask: { OPEN_CDROM-> open. | CLOSE_CDROM-> close. }
            cdrom = os.open(cd_device, os.O_RDONLY | os.O_NONBLOCK)
            fcntl.ioctl(cdrom, CDROM_MASK, 0)
            os.close(cdrom)
    except Exception, e:     
        print "close cdrom {ioctl_cdrom | function}[error]:", e

def open_cdrom(cdrom):
    ioctl_cdrom(cdrom, OPEN_CDROM)
        
def close_cdrom(cdrom):
    ioctl_cdrom(cdrom, CLOSE_CDROM)
           
if __name__ == "__main__":     
    cdrom_list = scan_cdrom()
    for cdrom in cdrom_list:
        print "cdrom:", cdrom
        open_cdrom(cdrom)
        
    for cdrom in cdrom_list:
        close_cdrom(cdrom)
        
    cd_type = cdrom_type("/media/DVD Video")
    if cd_type == CDROM_TYPE_EMPTY:
        print "你插入的数据光盘是空的"
    elif cd_type == CDROM_TYPE_DVD:
        print "你插入的是DVD光盘"
    elif cd_type == CDROM_TYPE_VCD:
        print "你插入的是VCD光盘"
    elif cd_type == CDROM_TYPE_CD:    
        print "你插入的是CD光盘"
    elif cd_type == CDROM_TYPE_ISO:    
        print "你挂载的是ISO"
    elif cd_type == CDROM_TYPE_DATA:    
        print "你插入的是数据光盘"
    elif cd_type == CDROM_ERROR:    
        print "你没有插入光盘"
