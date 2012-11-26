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
import gtk
import subprocess

################################################
###
class CdromType(object):
    def __init__(self):        
        self.id_label = None                    
        self.mount_path = None
        self.type = None
        self.device_file = None
        self.device_model = None
        self.id_type = None        
        self.cdrom_type = None        

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
        self.cdrom_dict = {}
        self.srx_list = []
        try:
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
                    self.get_cdrom_info(dev)
        except Exception, e:            
            print "Service[Error]:", e
                
        # print test.
        # for key in self.cdrom_dict.keys():
        #     print "========================="
        #     print "device_file:", self.cdrom_dict[key].device_file
        #     print "mount_path:", self.cdrom_dict[key].mount_path
        #     print "id_label:", self.cdrom_dict[key].id_label
        #     print "id_type:", self.cdrom_dict[key].id_type
        #     print "type:", self.cdrom_dict[key].type
            
    def get_vcd_info(self, dev):        
        cmd = "mplayer -vo null -ao null -frames 0 -identify vcd://2 -dvd-device '%s'" % (dev)
        pipe = os.popen(str(cmd))
        
    def get_dvd_info(self, dev):                
        cmd = "mplayer -vo null -ao null -frames 0 -identify dvdnav:// -dvd-device '%s'" % (dev)
        pipe = os.popen(str(cmd))
        while True: 
            try:
                line_text = pipe.readline()
            except StandardError:
                break
        
            if not line_text:
                break        

            if line_text.startswith("TITLE"):
                print "TITLE:", line_text
            elif line_text.startswith("[mkv] Track ID"):
                print "[mkv] Track ID:", line_text
                    
    def get_cdrom_info(self, dev):        
        self.cdrom_dict[str(dev)] = CdromType()            
        obj = self.bus.get_object(DESKTOP_UDISKS, dev)
        device_props = dbus.Interface(obj, DBUS_PROPERTIES)
        # save device file.
        device_file = device_props.Get(UDISKS_DEVICE, "DeviceFile")
        self.cdrom_dict[str(dev)].device_file = device_file
        try:
            # read cdrom type info.
            # mount_path = device_props.Get(UDISKS_DEVICE, 'DeviceMountPaths')
            # id_label = device_props.Get(UDISKS_DEVICE, "IdLabel")            
            drive_model = device_props.Get(UDISKS_DEVICE, "DriveModel")
            # id_type = device_props.Get(UDISKS_DEVICE, "IdType")
            # type_ = cdrom_type(mount_path[0]) # save cdrom type.            
            # save cdrom type info.            
            # self.cdrom_dict[str(dev)].id_label = id_label
            # self.cdrom_dict[str(dev)].mount_path = mount_path[0] # save mount path.
            # self.cdrom_dict[str(dev)].type = type_            
            self.cdrom_dict[str(dev)].device_model = drive_model
            # self.cdrom_dict[str(dev)].id_type = id_type # iso9660
            # self.cdrom_dict[str(dev)].cdrom_type = get_iso_type(drive_model, False)
            return True
        except Exception, e:
            print "get_cdrom_info[Error]:", e
            return False
        
    def changed_drive(self, device):
        if device.split("/")[-1].startswith("sr"):
            if(self.get_cdrom_info(device)):
                # send signal.
                self.emit("changed-cdrom", 
                          device,
                          self.cdrom_dict[device].mount_path
                          )
        
################################################
###
# 光盘类型.
CDROM_ERROR      = -1 #
CDROM_TYPE_DVD   = 0  # dvd.
CDROM_TYPE_VCD   = 1  # vcd.
# dvd.
AUDIO_TS = "/AUDIO_TS"
VIDEO_TS = "/VIDEO_TS"
# vcd.
MPEGAV  = "/MPEGAV"
SEGMENT = "/SEGMENT"

def cdrom_type(cdrom_path):
    try:
        cdrom_file_list = (cdrom_path).split("\n")
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
               
def get_iso_type(iso_path, iso_bool=True):
    if iso_bool:
        iso_cmd = "isoinfo  -f -i %s" % (iso_path)
    else:    
        iso_cmd = "isoinfo dev=%s -f" % ("/dev/sr0")    
        
    fp = os.popen(iso_cmd)
    return cdrom_type(fp.read())
        
import re
def get_dvd_title_info(dvd_path):
    # [title_index, title_length, chapters_number, title_chapters[tuple]]
    dvd_info_list = []

    cmd = "mplayer -vo null -ao null -frames 0 -identify "
    cmd += "dvdnav:// -dvd-device '%s'" % (dvd_path)
    fp = os.popen(cmd)
    
    ID_DVD_TITLE = "ID_DVD_TITLE_"
    LENGTH = "_LENGTH="
    CHAPTERS = "_CHAPTERS="
    # print fp.readline()
    while True: 
        try:
            line_text = fp.readline()
        except StandardError:
            break
        
        if not line_text:
            break
        
        # print line_text
        try:
            if line_text.startswith(ID_DVD_TITLE):
                compile_str = re.compile(r"\d+")
                # get title index and length.
                index_str = line_text.replace(ID_DVD_TITLE, "").split("\n")[0]
                title_index = compile_str.findall(index_str)[0]
            
                title_length = line_text.replace("%s%s%s" % (ID_DVD_TITLE, title_index, LENGTH), "")
                # get chaters.            
                line_text = fp.readline()
                if len(title_index.strip()) > 0:
                    if int(title_index.strip()) > 0:                    
                        # get chaters number.
                        ID_DVD_TITLE_INDEX_CHAPTERS = "%s%s%s" % (ID_DVD_TITLE, title_index, CHAPTERS)
                        # print ID_DVD_TITLE_INDEX_CHAPTERS
                        if line_text.startswith(ID_DVD_TITLE_INDEX_CHAPTERS):
                            title_chapters_number = compile_str.findall(line_text.replace(ID_DVD_TITLE_INDEX_CHAPTERS, ""))[0]
                        
                # get chaters time.
                line_text = fp.readline()
                TITLE_INDEX_CHAPTERS = "TITLE %s, CHAPTERS:" % (title_index)
                if line_text.startswith(TITLE_INDEX_CHAPTERS):
                    title_chapters = line_text.replace(TITLE_INDEX_CHAPTERS, "").split(",")
                
                        
            
                dvd_info_list.append(__save_dvd_info(title_index, int(float(title_length)), title_chapters_number, title_chapters))
            
        except Exception, e:
            print "[Error]cdrom.py--->>get_dvd_info:", e
            
    return dvd_info_list     

def __save_dvd_info(title_index, title_length, title_chapters_number, title_chapters):
    to_time = __length_to_time(title_length)
    to_tuple = __chapters_time_to_tuple(title_chapters)
    # print "--------------------------------"
    # print "index:", title_index
    # print "to_time:", to_time
    # print "number:", title_chapters_number
    # print "to_tuple:", to_tuple
    # print "--------------------------------"
    dvd_info = (title_index,
                to_time,
                title_chapters_number,
                to_tuple)
    return dvd_info

def __chapters_time_to_tuple(title_chapters):
    temp_list = []
    for chapters in title_chapters:
        if chapters != "\n":
            temp_list.append(chapters.strip())
    return tuple(temp_list)

def __length_to_time(title_length):
    time_sec = title_length
    time_hour = 0
    time_min = 0
    
    if time_sec >= 3600:
        time_hour = int(time_sec / 3600)
        time_sec -= int(time_hour * 3600)
        
    if time_sec >= 60:
        time_min = int(time_sec / 60)
        time_sec -= int(time_min * 60)         
        
    return str("%s:%s:%s"%(str(__time_add_zero(time_hour)), 
                           str(__time_add_zero(time_min)), 
                           str(__time_add_zero(time_sec))))

def __time_add_zero(time):
    if 9 >= time >= 0:
        return "0" + str(time)
    else:
        return time
    
if __name__ == "__main__":
    print get_iso_type("/dev/sr0", False)
    # for info in get_dvd_title_info("/dev/sr0"):
        # print info

    
'''
switch_title [value]

'''    
