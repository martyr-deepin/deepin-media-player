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
import dbus
import gobject
from pprint import pprint
import gtk

################################################
###
class CdromType(object):
    def __init__(self):
        self.id_label = None
        self.mount_path = None        
        self.type = None
        self.
################################################
###

DESKTOP_UDISKS = "org.freedesktop.UDisks"
DESKTOP_UDISKS_PATH = "/org/freedesktop/UDisks"
DBUS_PROPERTIES = "org.freedesktop.DBus.Properties"
UDISKS_DEVICE = 'org.freedesktop.UDisks.Device'

from dbus.mainloop.glib import DBusGMainLoop
    
class Service(gobject.GObject):    
    __gsignals__ = {
        "changed-cdrom" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                          (gobject.TYPE_PYOBJECT, gobject.TYPE_STRING, ))
        }    
    def __init__(self):
        gobject.GObject.__init__(self)
        self.srx_list = []
        DBusGMainLoop(set_as_default=True)
        self.bus = dbus.SystemBus()
        self.obj = self.bus.get_object(DESKTOP_UDISKS, DESKTOP_UDISKS_PATH)
        devs = dbus.Interface(self.obj, DESKTOP_UDISKS)
        # Init event.
        devs.connect_to_signal("DeviceChanged", self.changed_drive)
        # save sr?[0-x] [cdrom].
        for dev in devs.EnumerateDevices():
            if dev.split("/")[-1].startswith("sr"):
                self.srx_list.append(str(dev))                
                print "dev:", dev
        # test input.        
        # for srx_path in self.srx_list:        
        #     obj = self.bus.get_object(DESKTOP_UDISKS, srx_path)
        #     device_props = dbus.Interface(obj, DBUS_PROPERTIES)
        #     label = device_props.Get(UDISKS_DEVICE, 'IdLabel')
        #     if label != "":
        #         print device_props.Get(UDISKS_DEVICE, "DeviceMountPaths")[0]
            
    def load_drive(self, device):
        print "load_drive:", device
        
    def changed_drive(self, device):
        mount_path = None
        # print "changed_drive:", device
        if device.split("/")[-1].startswith("sr"):
            obj = self.bus.get_object(DESKTOP_UDISKS, device)
            device_props = dbus.Interface(obj, DBUS_PROPERTIES)
            try:
                mount_path = device_props.Get(UDISKS_DEVICE, 'DeviceMountPaths')
                print device_props.Get(UDISKS_DEVICE, 'DeviceMountPaths')
                # print "mount_path:", mount_path
                mount_path = mount_path[0]
                # print os.listdir(mount_path)
                cd_type = cdrom_type(mount_path)    
            
                if cd_type == CDROM_TYPE_DVD:
                    print "你插入的是DVD光盘"
                elif cd_type == CDROM_TYPE_VCD:
                    print "你插入的是VCD光盘"
                elif cd_type == CDROM_ERROR:
                    print "发生错误，不是DVD，VCD光盘！！"

                # send signal.
                self.emit("changed-cdrom", device, mount_path)
            except Exception, e:
                # print "changed_drive[error]:", e
                pass
        
################################################
###
# 光盘类型.
CDROM_ERROR      = -1 #
CDROM_TYPE_DVD   = 0  # dvd.
CDROM_TYPE_VCD   = 1  # vcd.
# dvd.
AUDIO_TS = "AUDIO_TS"
VIDEO_TS = "VIDEO_TS"
# vcd.
MPEGAV  = "MPEGAV"
SEGMENT = "SEGMENT"

def cdrom_type(cdrom_path):
    try:
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
    return (mpegav_bool or segment_bool)

###############################################################
###

OPEN_CDROM  = 0x5309
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
    def changed_drive_cdrom(service, dev, mount_path):
        print "发送一个信号来了...."
        print "changed_drive_cdrom:",
        print "dev:", dev
        print "mount_path:", mount_path
        
    # cdrom_list = scan_cdrom()
    # for cdrom in cdrom_list:
    #     print "cdrom:", cdrom
    #     open_cdrom(cdrom)
        
    # for cdrom in cdrom_list:
    #     close_cdrom(cdrom)
    ser = Service()
    ser.connect("changed-cdrom", changed_drive_cdrom)
    # mainloop = gobject.MainLoop()
    # mainloop.run()    
    gtk.main()
    # cd_type = cdrom_type("/media/DVD Video")
    
    # if cd_type == CDROM_TYPE_DVD:
    #     print "你插入的是DVD光盘"
    # elif cd_type == CDROM_TYPE_VCD:
    #     print "你插入的是VCD光盘"
    # elif cd_type == CDROM_ERROR:
    #     print "发生错误，不是DVD，VCD光盘！！"
