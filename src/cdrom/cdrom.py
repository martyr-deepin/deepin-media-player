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

OPEN_CDROM = 0x5309
CLOSE_CDROM = 0x5319

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
                               
