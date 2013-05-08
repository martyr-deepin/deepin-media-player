#! /Usrh/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 - 2013 Deepin, Inc.
#               2012 - 2013 Hailong Qiu
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

################################################
###
# 获取光盘盘类型.
CDROM_ERROR      = -1 #
CDROM_TYPE_DVD   = 0  # dvd.
CDROM_TYPE_VCD   = 1  # vcd.
# dvd.
AUDIO_TS = "/AUDIO_TS"
VIDEO_TS = "/VIDEO_TS"
# vcd.
MPEGAV  = "/MPEGAV"
SEGMENT = "/SEGMENT"

def cdrom_type(cdrom_path, mount_path=True):
    try:
        if mount_path:
            cdrom_file_list = (cdrom_path).split("\n")
        else:    
            cdrom_file_list = os.listdir(cdrom_path)    
    except Exception, e:
        print "cdrom_type[error]:", e
        return CDROM_ERROR
    
    # cdrom type.
    if cdrom_dvd(cdrom_file_list):
        return CDROM_TYPE_DVD
    elif cdrom_vcd(cdrom_file_list):
        return CDROM_TYPE_VCD
    else:
        return CDROM_ERROR
    
def cdrom_dvd(file_list):
    audio_ts_bool = False
    video_ts_bool = False
    for file_ in file_list:
        if AUDIO_TS.endswith(file_.upper()):
            audio_ts_bool = True
        elif VIDEO_TS.endswith(file_.upper()):
            video_ts_bool = True            
    return (audio_ts_bool and video_ts_bool)

def cdrom_vcd(file_list):
    mpegav_bool = False
    segment_bool = False
    for file_ in file_list:
        if MPEGAV.endswith(file_.upper()):
            mpegav_bool = True
        elif SEGMENT.endswith(file_.upper()):
            segment_bool = True
    return (mpegav_bool or segment_bool)


###############################################################
###

OPEN_CDROM  = 0x5309
CLOSE_CDROM = 0x5319

def scan_cdrom():
    # 搜索 cdrom.
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
    # 打开cdrom.
    ioctl_cdrom(cdrom, OPEN_CDROM)
        
def close_cdrom(cdrom):
    # 关闭cdrom.
    ioctl_cdrom(cdrom, CLOSE_CDROM)
               
def get_iso_type(iso_path, iso_bool=True):
    # 获取iso类型.
    if iso_bool:
        iso_cmd = "isoinfo  -f -i %s" % (iso_path)
    else:    
        # 如果开打的是iso,挂载上去.
        iso_cmd = "isoinfo dev=%s -f" % ("/dev/sr0")    
        
    fp = os.popen(iso_cmd)
    return cdrom_type(fp.read())
    

if __name__ == "__main__":
    print scan_cdrom()
    for cdrom in scan_cdrom():
        print get_iso_type(cdrom)
    print get_iso_type("/home/long/test.iso", False)
