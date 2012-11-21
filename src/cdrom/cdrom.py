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
                
        # print test.
        for key in self.cdrom_dict.keys():
            print "========================="
            print "device_file:", self.cdrom_dict[key].device_file
            print "mount_path:", self.cdrom_dict[key].mount_path
            print "id_label:", self.cdrom_dict[key].id_label
            print "id_type:", self.cdrom_dict[key].id_type
            print "type:", self.cdrom_dict[key].type
            
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
            mount_path = device_props.Get(UDISKS_DEVICE, 'DeviceMountPaths')
            id_label = device_props.Get(UDISKS_DEVICE, "IdLabel")            
            drive_model = device_props.Get(UDISKS_DEVICE, "DriveModel")
            id_type = device_props.Get(UDISKS_DEVICE, "IdType")
            type_ = cdrom_type(mount_path[0]) # save cdrom type.            
            # save cdrom type info.            
            self.cdrom_dict[str(dev)].id_label = id_label
            self.cdrom_dict[str(dev)].mount_path = mount_path[0] # save mount path.
            self.cdrom_dict[str(dev)].type = type_            
            self.cdrom_dict[str(dev)].device_model = drive_model
            self.cdrom_dict[str(dev)].id_type = id_type # iso9660
            
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
    import gtk    
    def changed_cdrom(cdrom, device, mount_path):
        print "发来一个信号!!"
        print device, mount_path
        
    # clicked -->>> menu.    
    def cdrom_btn_clicked(widget):
        command = "mplayer -slave -quiet -input file=/tmp/cmd "
        for key in ser.cdrom_dict.keys():
            if widget.get_label() == ser.cdrom_dict[key].device_file:
                if ser.cdrom_dict[key].type == CDROM_TYPE_DVD: # DVD.
                    print "播放DVD光盘!!"
                    if ser.cdrom_dict[key].mount_path:                        
                        ser.get_dvd_info(ser.cdrom_dict[key].device_file)
                        command += "-mouse-movements -nocache  dvdnav:// -dvd-device %s " % (ser.cdrom_dict[key].device_file)
                        command += "-wid %s" % (play_win.window.xid)
                        os.system(command)        
                elif ser.cdrom_dict[key].type == CDROM_TYPE_VCD: # VCD.
                    if ser.cdrom_dict[key].mount_path:
                        command += "-nocache vcd://2 -dvd-device %s " % (ser.cdrom_dict[key].device_file)
                        command += "-wid %s" % (play_win.window.xid)
                        os.system(command)
                    
    main_win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    main_win.add_events(gtk.gdk.ALL_EVENTS_MASK)
    ser = Service()
    ser.connect("changed-cdrom", changed_cdrom)
    main_win.set_title("主界面!!")
    btn_hbox = gtk.HBox()
    for key in ser.cdrom_dict.keys():
        temp_button = gtk.Button(ser.cdrom_dict[key].device_file)
        temp_button.connect("clicked", cdrom_btn_clicked)
        btn_hbox.pack_start(temp_button)
    main_win.connect("destroy", lambda w : gtk.main_quit())
    main_win.add(btn_hbox)
    main_win.show_all()
    
    play_win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    play_win.add_events(gtk.gdk.ALL_EVENTS_MASK)
    play_win.set_size_request(350, 350)
    play_win.set_title("多光驱测试!!")
    play_win.connect('destroy', lambda w : gtk.main_quit())
    play_win.show_all()    
    gtk.main()
    

    
    
    
'''    
dvdnav <button_name>
up      dvdnav up\n
down    dvdnav down\n
left    dvdnav left\n
right   dvdnav right\n
menu    dvdnav menu\n
select  dvdnav select\n
prev    dvdnav prev\n
mouse   dvdnav mouse\n

switch_angle [value] 切换DVD的角度.
switch_title [value] 切换dvd标题.
switch_chaptet [value][type] 切换章节.
sub_demux [value] 显示字幕

cmd = "mplayer -vo null -ao null -frames 0 -identify '%s'" % (file_path)
fp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)

get_audio_bitrate   音频比特率
get_audio_codec     音频编码器名称
get_audio_samples   声道数
get_file_name       专辑的元数据
get_meta_artist     艺术家的元数据
get_meta_comment    评论....
get_meta_genre      流派
get_meta_title      标题
get_meta_track      音轨数量
get_meta_year       年份
get_video_bitrate   比特率
get_video_codec     视频编码器名称
get_video_resolution 视频分辨率

多光驱检测.
 -------------------  ----------
|Play DISC [播放光盘] | /dev/sr0 |
 -------------------  ----------
                     | /dev/sr1 |
                      ----------
                     | /dev/sr2 |
                      ----------
当用户点击下去的时候,自行判断光驱内有无光盘.
如果有光盘 : 判断是  dvd , vcd, 数据光盘, cd...

 ---------------------------- -------------
| DVD navigation [dvd 导航]  |  上一章节     |
 ---------------------------- -------------
                             | 下一章节     |
                              -------------
                             |   跳至      |
                              -------------
                             | dvd 内置菜单 |  
                              -------------
                             |   配音      |
                              ------------- 
                             |   字幕      |    
                              -------------
                             |  弹出光驱    |
                              ------------- 
                             |  关闭光驱    |
                              -------------
                     

                   
跳至-->> 标题 [ 章节1, 章节2, 章节n ]

dvd内置菜单 []
                     
配音 [ 英语, ac3 48000HZ 16位 6, 
      中文, ac3 48000HZ  16...,
      英语 1(Director Comments 1), Ac3 480000HZ 16....]  
                                     
字幕 [ 关闭字幕, 中文 ]
'''
