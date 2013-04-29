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

from dtk.ui.gio_utils import get_file_icon_pixbuf
from constant import DEFAULT_FONT, DEFAULT_FONT_SIZE
from constant import DEBUG
import threading
import gobject        
import glib
import gtk
import sys
import gio
import os
import cairo
import pangocairo
import pango


def add_sys_path(path):
    sys.path.append(path)


def get_text_size(text, text_size=DEFAULT_FONT_SIZE, text_font=DEFAULT_FONT):
    try:
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 0, 0)
        cr = cairo.Context(surface)
        context = pangocairo.CairoContext(cr)
        layout = context.create_layout()
        temp_font = pango.FontDescription("%s %s" % (text_font, text_size))
        layout.set_font_description(temp_font)
        layout.set_text(text)
        return layout.get_pixel_size()
    except:
        return (0, 0)


def get_match_parent(widget, match_types):
    parent = widget.get_parent()
    if parent == None:
        return None
    elif type(parent).__name__ in match_types:
        return parent
    else:
        return get_match_parent(parent, match_types)

def propagate_expose(widget, event):
    if hasattr(widget, "get_child") and widget.get_child() != None:
        widget.propagate_expose(widget.get_child(), event)

def get_offset_coordinate(widget):
    rect = widget.allocation
    viewport = get_match_parent(widget, ["Viewport"])
    if viewport:
        coordinate = widget.translate_coordinates(viewport, rect.x, rect.y)
        if len(coordinate) == 2:
            (offset_x, offset_y) = coordinate
            return (-offset_x, -offset_y, viewport)
        else:
            return (0, 0, viewport)
    else:
        return (0, 0, viewport)

def is_single_click(event): # 单击
    return event.button == 1 and event.type == gtk.gdk.BUTTON_PRESS

def is_double_click(event): # 双击
    return event.button == 1 and event.type == gtk.gdk._2BUTTON_PRESS

def is_left_button(event): # 左键.
    return event.button == 1

def is_right_button(event): # 右键.
    return event.button == 3
                   
def is_file_sub_type(file_name):
    file_type = get_file_type(str(file_name))
    return file_type in ["text/x-ssa", "application/x-subrip"]

########################################################
## 打开对话框
def show_open_dir_dialog_window(title):
    open_dialog = gtk.FileChooserDialog(title,
                                        None,
                                        gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                        (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                         gtk.STOCK_OPEN, gtk.RESPONSE_OK))
    open_dialog.set_current_folder(get_home_path())
    res = open_dialog.run()
    path_string = ""
    if res == gtk.RESPONSE_OK:
        path_string = open_dialog.get_filename()        
    open_dialog.destroy()
    return path_string

def show_open_file_dialog_window(title):
    open_dialog = gtk.FileChooserDialog(title,
                                        None,
                                        gtk.FILE_CHOOSER_ACTION_OPEN,
                                        (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                         gtk.STOCK_OPEN, gtk.RESPONSE_OK))
    open_dialog.set_current_folder(get_home_path())
    res = open_dialog.run()
    path_string = ""
    if res == gtk.RESPONSE_OK:
        path_string = open_dialog.get_filename()        
    open_dialog.destroy()
    return path_string                    
    
########################################################
## 获取文件信息.
def get_file_icon(video_path, icon_size=32): # 获取文件图标
    pixbuf = get_file_icon_pixbuf(video_path, icon_size)
    if pixbuf:
        pixbuf = gtk.image_new_from_pixbuf(pixbuf)
    return pixbuf

def get_file_type(file_path): # 获取文件类型.
    try:
        gio_file = gio.File(file_path)
        file_atrr = ",".join([gio.FILE_ATTRIBUTE_STANDARD_CONTENT_TYPE,
                              gio.FILE_ATTRIBUTE_STANDARD_TYPE, 
                              gio.FILE_ATTRIBUTE_STANDARD_NAME,
                              gio.FILE_ATTRIBUTE_STANDARD_SIZE,
                              gio.FILE_ATTRIBUTE_STANDARD_DISPLAY_NAME,
                              gio.FILE_ATTRIBUTE_TIME_MODIFIED,
                              gio.FILE_ATTRIBUTE_STANDARD_ICON,
                              ])
        gio_file_info = gio_file.query_info(file_atrr)
        file_type = gio_file_info.get_attribute_as_string(gio.FILE_ATTRIBUTE_STANDARD_CONTENT_TYPE)
        return file_type
    except Exception, e:
        print e
        return None
    
def is_file_audio(file_name):    
    return get_file_type(file_name).startswith("audio")
    
def open_file(file_name, type_check=True):
    if type_check:
        os.system("xdg-open '%s'" % (os.path.split(file_name)[0]))
    else:
        os.system("nautilus '%s'" % (file_name))

########################################################                
## 转换时间的函数.                
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

# 获取当前用户的目录
def get_home_path():
    return os.path.expanduser("~")

def get_home_music():
    return glib.get_user_special_dir(glib.USER_DIRECTORY_MUSIC)

def get_home_video():
    return glib.get_user_special_dir(glib.USER_DIRECTORY_VIDEOS)

def get_home_image():
    return glib.get_user_special_dir(glib.USER_DIRECTORY_PICTURES)

def get_config_path():
    path = get_home_path() + "/.config/"
    return os.path.join(path, "deepin-media-player")

def get_user_plugin_path():
    # 用户插件目录.
    return os.path.join(get_config_path(), "plugins")

def get_ldmp_plugin_path():
    # 获取系统自带插件目录.
    path = os.path.split(os.path.dirname(os.path.realpath(__file__)))[0]
    ldmp_path = os.path.join(path, "plugins")
    return ldmp_path

def get_system_tooptil_icon(icon_name="logo.png"):
    # 获取气泡提示的图标.
    path = os.path.dirname(os.path.realpath(__file__))
    icon_path = os.path.join(path, icon_name)
    return icon_path

def allocation(widget): # 返回 cr, rect.
    cr = widget.window.cairo_create()
    rect = widget.get_allocation()
    return cr, rect
                    
def get_play_file_name(path): # 获取播放文件名.
    return os.path.splitext(os.path.split(path)[1])[0]

def get_play_file_type(path): # 获取播放后缀名.
    return os.path.splitext(os.path.split(path)[1])[1][1:]


def get_file_size(path): # 获取文件大小.
    if os.path.exists(path):
        file_size = os.path.getsize(path)            
        return size_to_format(file_size)
    else:
        return 0
    
diskunit = ['Byte', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB']

def size_to_format(size, unit='Byte'): # size 转换成k/b/g/t/p/e->B显示.
    if size < 1024:
        return '%.2f %s' % (size, unit)
    else:
        return size_to_format(size/1024.0, diskunit[diskunit.index(unit) + 1])                
    
        
##########################################
## 线程扫描播放列表.
##
class ScanTreeview(gobject.GObject):
    __gsignals__ = {
        "scan-file-event" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                             (gobject.TYPE_STRING,)),
        "scan-end-event" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                             (gobject.TYPE_PYOBJECT,)),        
        }            
    def __init__(self, youku_web, addr, check):
        gobject.GObject.__init__(self)
        self.event = threading.Event()
        self.youku_web_parse = youku_web
        self.addr = addr
        self.check = check
    
    def run(self):
        if self.check == True:
            scan_th = threading.Thread(target=self.__run_parse_web_func)
        elif self.check == 2:
            scan_th = threading.Thread(target=self.__run_to_addr_func)
        elif self.check == False:
            scan_th = threading.Thread(target=self.__run_scan_3_leave_func)
        scan_th.setDaemon(True) 
        scan_th.start()

    def __run_to_addr_func(self):
        flvcd = self.youku_web_parse
        addrs_list = []
        flvcd_addr_list = flvcd.parse(self.addr)
        addrs_list = flvcd_addr_list
        self.emit("scan-end-event", addrs_list)

    def __run_parse_web_func(self):
        info_list, page_num, all_sum = self.youku_web_parse.parse_web(self.addr)
        self.emit("scan-end-event", info_list)

    def __run_scan_3_leave_func(self):
        temp_list = self.youku_web_parse.scan_3_leave(self.addr)
        self.emit("scan-end-event", temp_list)    

## 线程扫描目录.  
## scan_dir = ScanDir('/home')
## scan_dir.connect("scan-file-event",self.scan..  ..
## def scan_file_event(scan_dir, file_name):...        
class ScanDir(gobject.GObject):                
    __gsignals__ = {
        "scan-file-event" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                             (gobject.TYPE_STRING,)),
        "scan-end-event" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                             (gobject.TYPE_INT,)),        
        }            
    def __init__(self, path):
        gobject.GObject.__init__(self)
        self.event = threading.Event()
        self.path = path
        self.run()
        
    def pause(self): # 暂停线程
        self.event.clear()
        
    def start(self): # 开启线程
        self.event.set()
        
    def __wait(self):  
        self.event.wait()
        
    def enter(self):    
        gtk.gdk.threads_enter()
        
    def leave(self):    
        gtk.gdk.threads_leave()        
        
    def run(self):
        scan_th = threading.Thread(target=self.__run_func)
        scan_th.setDaemon(True) 
        scan_th.start()
        
    def __scan(self, path):
        self.__wait()
        try:
            if os.path.isdir(path):
                for file_ in os.listdir(path):
                    file_path = os.path.join(path, file_)
                    for sub_file in self.__scan(file_path):
                        yield sub_file
            else:    
                yield path
        except:
            print "read file error!!"
                            
    def __run_func(self):    
        num = 0
        for file_ in self.__scan(self.path):
            num += 1
            self.emit("scan-file-event", file_)
        self.emit("scan-end-event", num)    
        
if __name__ == "__main__":            
    gtk.gdk.threads_init()    
    def scan_file_event(scan_dir, file_name):
        gtk.gdk.threads_enter()
        #label.set_label(file_name)
        print file_name
        gtk.gdk.threads_leave()
        
    def scan_end_event(scan_dir):    
        gtk.gdk.threads_enter()
        label.set_label("%s扫描完毕"%(scan_dir.path))
        gtk.gdk.threads_leave()        
        
    def start_btn_clicked(widget):    
        scan_dir.start()
        #print show_open_file_dialog_window("测试")
        
    def pause_btn_clicked(widget):    
        scan_dir.pause()
        #print show_open_dir_dialog_window("测试")
        
    scan_dir = ScanDir("/media/文档")
    scan_dir.connect("scan-file-event", scan_file_event)                
    scan_dir.connect("scan-end-event", scan_end_event)
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    win.set_title("线程测试!!")
    vbox = gtk.VBox()
    hbox = gtk.HBox()
    start_btn=gtk.Button("开始")
    pause_btn=gtk.Button("暂停")    
    hbox.pack_start(start_btn, False, False)
    hbox.pack_start(pause_btn, False, False)
    label = gtk.Label("...")    
    vbox.pack_start(hbox, False, False)
    vbox.pack_start(label, False, False)
    # image = get_file_icon("/home/long/Desktop/test/test.rmvb", 32)
    # vbox.pack_start(image, False, False)
    win.add(vbox)    
    win.connect("destroy", lambda w : gtk.main_quit())    
    start_btn.connect("clicked", start_btn_clicked)
    pause_btn.connect("clicked", pause_btn_clicked)
    win.show_all()
    
    # gtk.gdk.threads_enter()
    gtk.main()
    # gtk.gdk.threads_leave()
