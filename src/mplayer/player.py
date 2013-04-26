#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
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

from dtk.ui.utils import remove_timeout_id
from timer import Timer
import gobject
import subprocess        
import fcntl
import gtk
import os

DEBUG = 0
(STOPING_STATE, PAUSE_STATE, STARTING_STATE)= range(0, 3)
(CHANNEL_NORMAL_STATE, CHANNEL_LEFT_STATE, CHANNEL_RIGHT_STATE ) = range(0, 3)
(TYPE_FILE, TYPE_CD, TYPE_DVD, TYPE_VCD, TYPE_NETWORK, TYPE_DVB, TYPE_TV, TYPE_)= range(0, 8)

(ERROR_RETRY_WITH_MMSHTTP, ERROR_RESOLVE_AF_INET, ERROR_SOCKET_CONNECT,
 ERROR_FILE_FORMAT, ERROR_DVD_DEVICE, ERROR_RETRY_ALSA_BUSY,
 ERROR_RETRY_WITH_HTTP, ERROR_RETRY_WITH_HTTP_AND_PLAYLIST,
 ERROR_RETRY_WITH_PLAYLIST) = range(0, 9)

class Player(object):        
    def __init__(self):
        self.uri = ""
        self.debug = 1
        self.length = 0 # 总长度        
        self.ascept_state = ASCEPT_DEFULAT # 比例状态 默认:视频自己的比例.
        self.video_width = 0 # 视频的宽
        self.video_height = 0 # 视频的高
        self.video_present = False        
        self.type = TYPE_FILE # 播放文件类型.                                
        self.flip_screen = None # 旋转画面.
        self.force_cache = 0
        self.state = STOPING_STATE # 当前播放状态.{停止,暂停,正在播放}
        self.channel_state = CHANNEL_NORMAL_STATE # 声道选择状态 {左右,正常}    
        self.title_is_menu = False
        self.start_time = 0.0 # 开始时间.
        self.run_time = 0.0
        self.vo = None # -vo
        self.ao = None # -ao
        self.cache_size = 0 # 缓冲大小
        # 字幕添加.
        self.sub_index = -1
        self.subtitle  = []
        # 音轨选择.
        self.audio_index = 0
        self.audio_list = []
        #
        self.audio_select_index = None

        self.audio_track = None
        self.af_export_filename = "/tmp/mplayer_af_export" # af 临时保存文件.
        # 设置/调整视频参数.
        self.brightness = 0 #
        self.contrast   = 0 # 
        self.gamma      = 0 #    
        self.hue        = 0 # 色彩.
        self.osdlevel = 0
        self.saturation = 0        
        self.profile = None
        self.restart = False
        #
        self.video_format = None
        self.video_codec  = None
        self.video_bitrate = None
        self.video_fps = None
        self.audio_format = None
        self.audio_codec  = None
        self.audio_bitrate = None
        self.audio_rate = None
        self.audio_nch = None
        #
        self.media_device = None
        self.disable_binary = None
        self.extra_opts = None
        self.use_mplayer2 = False
        self.features_detected = False
        self.zoom = 1.0
        self.speed_multiplier = 1.0
        self.subtitle_scale = 1.0
        self.subtitle_delay = 0.0
        self.subtitle_position = 0
        self.subtitle_fuzziness = 0
        #
        self.audio_delay = 0.0
        # self.retry_on_full_cache = False
        self.alang = None #
        self.slang = None #
        
        self.deinterlace = None
        self.enable_hardware_codecs = None
        self.enable_divx = True
        self.disable_xvmc = False
        self.post_processing_level = 0
        #        
        self.alsa_mixer = None
        self.audio_channels = 0
        self.hardware_ac3 = None
        
        self.softvol = None
        #
        self.volumebool = False
        self.volume = 100
        self.volume_gain = 0
        #                
        self.frame_drop = None        
        self.audio_track_file = None
        self.subtitle_file = None
        self.enable_advanced_subtitles = None
        self.subtitle_margin = 0
        self.enable_embedded_fonts = None
        self.subtitle_font = None
        self.subtitle_outline = None
        self.subtitle_shadow = None
        self.subtitle_color = None
        self.subtitle_codepage = None        
        self.subtitle_source = None
        self.subtitle_is_file = None
        #                
        self.tv_device = None
        self.tv_driver = None
        self.tv_input = None
        self.tv_width = 0
        self.tv_height = 0
        self.tv_fps = 0
        
        self.seekable = False
        self.has_chapters = False        
        self.position = 0.0
        self.cache_percent = -1.0                        
        self.title = ""
        
####################################################################        
### Mplayer后端控制.
class LDMP(gobject.GObject):
    '''Linux Deepin Mplayer 后端.'''
    __gsignals__ = {
        "get-time-pos":(gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_NONE,(gobject.TYPE_INT,gobject.TYPE_STRING,)),
        "get-time-length":(gobject.SIGNAL_RUN_LAST,
                           gobject.TYPE_NONE,(gobject.TYPE_INT, gobject.TYPE_STRING,)),
        "get-subtitle":(gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_NONE,(gobject.TYPE_STRING, gobject.TYPE_INT,)),
        "get-audio-info":(gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_NONE,(gobject.TYPE_STRING, gobject.TYPE_INT,)),
        "end-media-player":(gobject.SIGNAL_RUN_LAST,
                            gobject.TYPE_NONE,()),
        "start-media-player":(gobject.SIGNAL_RUN_LAST,
                            gobject.TYPE_NONE,()),    
        "screen-changed":(gobject.SIGNAL_RUN_LAST,
                            gobject.TYPE_NONE,(gobject.TYPE_INT, gobject.TYPE_INT)),        
        "pause-play":(gobject.SIGNAL_RUN_LAST,
                     gobject.TYPE_NONE,(gobject.TYPE_INT,)),
        "mute-play":(gobject.SIGNAL_RUN_LAST,
                     gobject.TYPE_NONE,(gobject.TYPE_INT,)),
        "volume-play":(gobject.SIGNAL_RUN_LAST,
                     gobject.TYPE_NONE,(gobject.TYPE_INT,)),
        "error-msg":(gobject.SIGNAL_RUN_LAST,
                     gobject.TYPE_NONE,(gobject.TYPE_INT,)),
        }
    def __init__(self, xid=None):
        gobject.GObject.__init__(self)        
        # init values.
        self.xid = xid
        self.player = Player()
        # 加入读取配置文件, 设置-vo等选项.
        
    def play(self):                
        self.player.type = self.get_play_file_type() # 设置文件类型
        codecs_vdpau = None
        codecs_crystalhd = None
        
        self.command = ["mplayer"]
        self.command.append("-noidle")
        self.command.append("-softvol")
        self.command.append("-volume")
        self.command.append(str(self.player.volume))
        self.emit("volume-play", self.player.volume)
        self.command.append("-nostop-xscreensaver")
        if self.player.profile:
            self.command.append("-profile")
            self.command.append(self.player.profile)
            
        if self.player.vo: # mplayer -vo help | grep xv 
            # 视频输出选项. 
            self.command.append("-vo")
            if self.player.vo.startswith('vdpau'):
                #
                if self.player.deinterlace:
                    self.command.append("vdpau:deint=2,%s,gl,x11" % (self.player.vo))
                else:
                    self.command.append("%s,gl,x11" % (self.player.vo))
                #
                if self.player.enable_hardware_codecs:
                    if self.player.enable_divx:
                        codecs_vdpau = "ffmpeg12vdpau,ffh264vdpau,ffwmv3vdpau,ffvc1vdpau,ffodivxvdpau,"
                    else:
                        codecs_vdpau = "ffmpeg12vdpau,ffh264vdpau,ffwmv3vdpau,ffvc1vdpau,"
            elif self.player.vo.startswith("vaapi"): 
                self.command.append(self.player.vo)
                self.command.append("-va")
                self.command.append("vaapi")
            elif self.player.vo.startswith("xvmc"):
                if self.player.disable_xvmc:
                    self.command.append("xv,")
                else:    
                    self.command.append("%s,xv," % (self.player.vo))
            else:            
                if self.player.vo.startswith("gl"):
                    self.command("gl_nosw")
                elif self.player.vo.startswith("gl2"):
                    self.command.append("gl_nosw")
                else:    
                    self.command.append("%s" % (self.player.vo))
                
                if self.player.deinterlace:
                    self.command.append("-vf-pre")
                    self.command.append("yadif,softskip,scale")
                    
                if self.player.post_processing_level > 0:
                    self.command.append("-vf-add")
                    self.command.append("pp=ac/tn:a")
                    self.command.append("-autoq")
                    self.command.append("%d" % (self.player.post_processing_level))
                    
                self.command.append("-vf-add")
                self.command.append("screenshot")
                
                
        if self.player.enable_hardware_codecs:
            codecs_crystalhd = "ffmpeg2crystalhd,ffdivxcrystalhd,ffwmv3crystalhd,ffvc1crystalhd,ffh264crystalhd,ffodivxcrystalhd,"
            
        codecs = None    
        if codecs_vdpau and codecs_crystalhd:    
            codecs = codecs_vdpau + codecs_crystalhd
        elif codecs_vdpau:    
            codecs = codecs_vdpau
        elif codecs_crystalhd:    
            codecs = codecs_crystalhd
            
        if codecs:    
            self.command.append("-vc")
            self.command.append("%s" % (codecs))
            
        if self.player.ao: # 音频输出选项.   
            self.command.append("-ao")
            self.command.append("%s" % (self.player.ao))
            
            if self.player.alsa_mixer:
                self.command.append("-mixer-channel")
                self.command.append("%s" % (self.player.alsa_mixer))
                
        # 初始化声道.    
        self.command.append("-channels")            
        # if self.player.audio_channels:
        case = self.player.audio_channels
        if case == 1:
            self.command.append("4")
        elif case == 2:    
            self.command.append("6")
        elif case == 3:    
            self.command.append("8")
        else:    
            self.command.append("2")
                    
        if self.player.hardware_ac3:        
            self.command.append("-afm")
            self.command.append("hwac3,")
        else:    
            self.command.append("-af-add")
            self.command.append("export=%s:512" % (self.player.af_export_filename))

        if self.player.flip_screen: # 旋转画面. 
            # 水平翻转 mirror, 垂直翻转-flip, rotate=(0-7), 
            self.command.append("-vf")
            self.command.append(self.player.flip_screen)

        # 添加初始化设置.        
        self.command.append("-quiet")    
        self.command.append("-slave")    
        #self.command.append("-noidle")    
        self.command.append("-noconsolecontrols")    
        #self.command.append("-nostop-xscreensaver")    
        self.command.append("-identify")    
        
        if self.player.softvol:
            if self.player.volume != 0:
                self.command.append("-volume")
                self.command.append("%i" % (self.player.volume))
            if self.player.volume_gain != 0:
                self.command.append("-af-add")
                self.command.append("volume=%lf:0" % (self.playervolume_gain))
            self.command.append("-softvol")
            
        if self.player.start_time > 0:
            self.command.append("-ss")
            self.command.append("%d" % (self.player.start_time))
            
        if self.player.run_time > 0:    
            self.command.append("-endpos")
            self.command.append("%d", self.player.run_time)
            
        if self.player.frame_drop:    
            self.command.append("-framedrop")
            
        self.command.append("-msglevel")    
        self.command.append("all=5")    
        
        self.command.append("-osdlevel")
        self.command.append("%i" % (self.player.osdlevel))
        
        self.command.append("-delay")
        self.command.append("%f" % (self.player.audio_delay))
        
        self.command.append("-subdelay")
        self.command.append("%f" % (self.player.subtitle_delay))
        
        self.command.append("-subpos")
        self.command.append("%d" % (self.player.subtitle_position))
                        
        self.command.append("-wid")
        self.command.append(str(self.xid))
        
        self.command.append("-brightness")
        self.command.append(str(self.player.brightness))
        
        self.command.append("-contrast")
        self.command.append(str(self.player.contrast))
        self.command.append("-hue")
        self.command.append(str(self.player.hue))
        self.command.append("-saturation")                   
        self.command.append(str(self.player.saturation))
        
        if self.player.alang:
            self.command.append("-alang")
            self.command.append("%s" % (self.player.alang))
            
        if self.player.slang:    
            self.command.append("-slang")
            self.command.append("%s" % (self.player.slang))
            
        self.command.append("-nomsgcolor")    
        self.command.append("-nomsgmodule")
            
        self.command.append("-nokeepaspect")
        
        if (self.player.audio_track_file 
            and len(self.player.audio_track_file) > 0):
            self.command.append("-audiofile")
            self.command.append("%s" % (self.player.audio_track_file))
            
        if (self.player.subtitle_file
            and len(self.player.subtitle_file) > 0):
            self.command.append("-sub")
            self.command.append("%s" % (self.player.subtitle_file))
            
        if self.player.enable_advanced_subtitles:
            self.command.append("-ass")
            if self.player.subtitle_margin > 0:
                self.command.append("-ass-bottom-margin")
                self.command.append("%d"%(self.player.subtitle_margin))
                self.command.append("-ass-use-margins")
                
            if self.player.enable_embedded_fonts:                    
                self.command.append("-embeddedfonts")
            else:    
                self.command.append("-noembeddedfonts")
                #
                if (self.player.subtitle_font
                    and len(self.player.subtitle_font) > 0):                    
                    fontname = self.player.subtitle_font
                    size = fontname.find(" ")
                    if size:
                        size[0] = '\0'
                    size +=  " Bold" 
                    if size:
                        size[0] = '\0'
                    size += " Italic"    
                    if size:    
                        size[0] = '\0'
                        
                    if self.player.subtitle_font.startswith("Italic"):
                        italic = ",Italic=1" 
                    else:    
                        italic = ",Italic=0"
                    if self.player.subtitle_font.startswith("Bold"):
                        bold = ",Bold=1"
                    else:                            
                        bold = ",Bold=0"
                    if self.player.subtitle_outline:
                        outline = ",Outline=1" 
                    else:
                        outline = ",Outline=0"
                    if self.player.subtitle_shadow:    
                        shadow = ",Shadow=2" 
                    else:
                        shadow = ",Shadow=0"    
                    font_str = "FontName=" + fontname + italic + bold + outline + shadow
                    self.command.append("-ass-force-style")
                    self.command.append(font_str)
                    
                    
                    self.command.append("-ass-font-scale")
                    self.command.append("%f" % self.player.subtitle_scale);
                    
                    if (self.player.subtitle_color and len(self.player.subtitle_color) > 0):
                        self.command.append("-ass-color");
                        self.command.append("%s" % self.player.subtitle_color);
        else:        
             if self.player.subtitle_scale:
                 self.command.append("-subfont-text-scale")
                 self.command.append("%d" % (self.player.subtitle_scale * 3))
                        
             if (self.player.subtitle_font 
                 and len(self.player.subtitle_font)):
                 fontname = self.player.subtitle_font
                 size = fontname.find(" ")
                 if size:
                     size[0] = '\0'
                     self.command.append("-subfont")    
                     self.command.append("%s" % (fontname))    
                        
        if (self.player.subtitle_codepage 
            and len(self.player.subtitle_codepage)):
            self.command.append("-subcp")
            
        if self.player.extra_opts:
            opts = self.player.extra_opts
            i = 0
            while opts[i]:
                self.command.append(opts[i])
                i += 1
                
        ############## 判断播放类型        
        if self.player.type == TYPE_FILE: # 普通播放类型.
            # if filename:
                if self.player.force_cache and self.player.cache_size >= 32:
                    self.command.append("-cache")
                    self.command.append("%d" % (self.player.cache_size))
                # self.command.append(str(filename))    
                self.command.append(str(self.player.uri))    
        elif self.player.type == TYPE_CD: # CD类型.
            self.command.append("-cache")
            self.command.append("%d" % (self.cache_size))
            self.command.append("%s" % (self.uri))
            if self.player.media_device:
                self.command.append("-dvd-device")
                self.command.append("%s" % (self.media_device))
        elif self.player.type == TYPE_DVD: # DVD类型.
            self.command.append("-mouse-movements")
            self.command.append("-nocache")
            self.command.append("dvdnav://")
            if self.player.media_device:
                self.command.append("-dvd-device")
                self.command.append("%s" % (self.player.media_device))
        elif self.player.type == TYPE_VCD: # VCD播放.    
            self.command.append("-nocache")
            self.command.append("%s" % (self.player.uri))
            if self.player.media_device:
                self.command.append("-dvd-device")
                self.command.append("%s" % (self.player.media_device))
        elif self.player.type == TYPE_NETWORK: # 网络媒体播放.
            if self.player.uri.startswith("apple.com"):
                self.command.append("-user-agent")
                self.command.append("QuickTime/7.6.9")
            elif self.player.cache_size >= 32:
                self.command.append("-cache")
                self.command.append("%d" % (self.player.cache_size))
            else:    
                self.command.append("-nocache")
            self.command.append("%s" % (self.player.uri))
        elif self.player.type == TYPE_DVB and self.player.type == TYPE_TV: # TV播放.
            if self.player.tv_device:
                self.command.append("-tv:device")
                self.command.append("%s" % (self.player.tv_device))
            if self.player.tv_driver:    
                self.command.append("-tv:driver")
                self.command.append("%s" % (self.player.tv_driver))
            if self.player.tv_input:
                self.command.append("-tv:input")
                self.command.append("%s" % (self.player.tv_input))
            if self.player.tv_width > 0:
                self.command.append("-tv:width")
                self.command.append("%d" % (self.tv_width))
            if self.player.tv_height > 0:
                self.command.append("-tv:height")
                self.command.append("%d" % (self.tv_height))
            if self.player.tv_fps > 0:    
                self.command.append("-tv:fps")
                self.command.append("%d" % (self.tv_fps))
            self.command.append("-nocache")    
            
            self.command.append("%s" % (self.player.uri))    
            
        #print self.command
        # 链接管道.
        self.mp_id = subprocess.Popen(self.command, 
                                      stdin = subprocess.PIPE,
                                      stdout = subprocess.PIPE,
                                      stderr = subprocess.PIPE,
                                      shell = False)
            
        self.mplayer_pid = self.mp_id.pid
        (self.mplayer_in, self.mplayer_out, self.mplayer_err) = (self.mp_id.stdin, self.mp_id.stdout, self.mp_id.stderr)
        fcntl.fcntl(self.mplayer_out, 
                        fcntl.F_SETFL, 
                        os.O_NONBLOCK)            
                
        # IO_HUP[Monitor the pipeline is disconnected].
        self.watch_in_id = gobject.io_add_watch(self.mplayer_out, 
                                                gobject.IO_IN, 
                                                self.player_thread_reader)
        self.watch_err_id = gobject.io_add_watch(self.mplayer_err, 
                                                 gobject.IO_IN, 
                                                 self.player_thread_reader_error)
        self.watch_in_hup_id = gobject.io_add_watch(self.mplayer_out, 
                                                    gobject.IO_HUP, 
                                                    self.player_thread_complete)
        #
        self.timer = Timer(1000)
        self.timer.connect("Tick", self.thread_query)
        self.timer.Enabled = True 
        self.player.state = STARTING_STATE
        if self.player.volumebool: #判断是否静音.
            self.nomute()
        #
        # gobject.timeout_add_seconds(1, self.thread_query, 1)        
        #
            
    def thread_query(self, tick):
        self.get_time_pos()
        
    '''获取Mplayer时间.''' # t12345
    def get_percent_pos(self): # 获取当前位置为整数的百分比 
        self.cmd('get_percent_pos\n')

    def get_sub_visibility(self):    
        self.cmd("get_sub_visibility\n")
        
    def get_time_length(self):    
        self.cmd('get_time_length\n')
    
    def get_time_pos(self): # 当前位置用秒表示，采用浮点数.
        self.cmd('get_time_pos\n')
                                        
    '''字幕控制''' 
    def sub_add(self, sub_file):
        '''Load subtitle'''
        if self.player.state == STARTING_STATE: # STARTING_STATE
            self.cmd("sub_load '%s'\n" % (sub_file))
            self.player.sub_index += 1
            self.emit("get-subtitle", sub_file, self.player.sub_index)
            
    def sub_select(self, index):        
        # 字幕选择.
        if self.player.state: # STARTING_STATE
            self.cmd('sub_select %s\n' % str(index))

    def sub_clear(self, end_index): # clear all subtitl file.
        if self.player.state == STARTING_STATE:
            for index in range(0, end_index):
                self.sub_del(index)
                
    def sub_del(self, index):        
        if self.player.state == STARTING_STATE: # STARTING_STATE
            self.cmd('sub_remove %s\n' % index)
                        
    def sub_stop(self):        
        if self.player.state == STARTING_STATE:
            self.cmd("sub_select -1\n")
            
    # subtitle alignment. # 0 top 1 center 2 bottom  
    def sub_alignment_top(self):
        self.sub_alignment(0)
        
    def sub_alignment_center(self):
        self.sub_alignment(1)
        
    def sub_alignment_bottom(self):
        self.sub_alignment(2)
        
    def sub_alignment(self, alignment_state):
        if self.player.state == STARTING_STATE:
            self.cmd("sub_alignment %s\n"%(alignment_state))

    # subtitle delay(+/-[abs]).
    def sub_up_delay(self): # sub_delay 0.1\n sub_delay -0.1\n
        self.sub_delay(0.1)
        
    def sub_down_delay(self):
        self.sub_delay(-0.1)
    
    def sub_delay(self, value):                    
        if self.player.state == STARTING_STATE:
            self.cmd("sub_delay %s\n" % (value))
        
    # subtitle log.
    # def sub_log(self)
            
    # subtitle pos.    
    # def sub_pos(self)
            
    # subtitle source(source).    
    # def sub_source(self):         
            
    # subtitle file(value).        
    # def sub_file(self, value):
            
    # subtitle vob(value).        
    # def sub_vob(self, value)        
            
    # subtitle demux(value).        
    # def sub_demux(self, value):        
            
    # subtitle scale(+/-[abs])
    # sub_scale %f 1\n. 默认 1.0
    def sub_up_scale(self):
        self.subtitle_scale_value += 0.1
        self.sub_scale(self.subtitle_scale_value)
        
    def sub_down_scale(self):
        self.subtitle_scale_value -= 0.1
        self.sub_scale(self.subtitle_scale_value)
    
    def sub_scale(self, value): # value -> %f
        if self.player.state == STARTING_STATE:
            self.cmd("sub_scale %s 1\n" % (value));
            
    '''声音控制''' 
    def addvolume(self, volume_num):
        '''Add volume'''
        self.player.volume += volume_num
        self.player.volume = min(self.player.volume, 100)
        self.cmd('volume %d 1\n' % (self.player.volume))
        self.emit("volume-play", self.player.volume)
        
    def decvolume(self, volume_num):
        '''Decrease volume'''
        self.player.volume -= volume_num
        self.player.volume = max(self.player.volume, 0)
        self.cmd('volume %d 1\n' % (self.player.volume))
        self.emit("volume-play", self.player.volume)
            
    def setvolume(self, volume_num):
        '''Set volume'''
        value = min(max(volume_num, 0), 100)
        self.player.volume = value
        self.cmd('volume %d 1\n' % (self.player.volume))
        self.emit("volume-play", self.player.volume)
            
    def leftchannel(self):
        '''The left channel'''
        self.cmd('af channels=2:2:0:0:0:0\n')
        self.player.channel_state = CHANNEL_LEFT_STATE #1
    
    def rightchannel(self):
        '''The right channel'''
        self.cmd('af channels=2:2:0:1:1:1\n')             
        self.player.channel_state = CHANNEL_RIGHT_STATE #2
            
    def normalchannel(self):
        '''Normal channel'''
        self.cmd('af channels=2:2:0:0:1:1\n')
        self.player.channel_state = CHANNEL_NORMAL_STATE #0
            
    def offmute(self): 
        self.player.volumebool = False
        self.cmd('mute 0\n')
        self.emit("mute-play", self.player.volumebool)
                
    def nomute(self):
        '''Active mute'''
        self.player.volumebool = True
        self.cmd('mute 1\n')
        self.emit("mute-play", self.player.volumebool)
                
    def off_switch_audio(self):
        self.switch_audio(-1)
        
    def switch_audio(self, number):        
        self.cmd('switch_audio %s\n'% str(number))
            
    '''视频控制''' # video123456
    # brightness.
    def addbri(self, bri_num):
        '''Add brightness'''
        if self.player.state == STARTING_STATE:
            self.cmd('brightness +%s\n' % (bri_num))
    
    def decbri(self, bri_num):
        '''Decrease brightness'''
        if self.player.state == STARTING_STATE:
            self.cmd('brightness -%s\n' % (bri_num))
    
    # saturation.
    def addsat(self, sat_num):
        '''Add saturation'''
        if self.player.state == STARTING_STATE:
            self.cmd('saturation +%s\n' % (sat_num))
            
    def decsat(self, sat_num):
        '''Decrease saturation'''        
        if self.player.state == STARTING_STATE:
            self.cmd('saturation -%s\n' % (sat_num))
    
    # contrast. 
    def addcon(self, con_num):
        '''Add contrast'''
        if self.player.state == STARTING_STATE:
            self.cmd('contrast +%s\n' % (con_num))    
            
    def deccon(self, con_num):
        '''Decrease contrast'''    
        if self.player.state == STARTING_STATE:
            self.cmd('contrast -%s\n' % (con_num))
    
    # hue.
    def addhue(self, hue_num):
        '''Add hue'''
        if self.player.state == STARTING_STATE:
            self.cmd('hue +%s\n' % (hue_num))        
    def dechue(self, hue_num):
        '''Decrease hue'''
        if self.player.state == STARTING_STATE:
            self.cmd('hue -%s\n' % (hue_num))
        
    '''dvd控制''' #dvd123456
    # cdrom [dvd, vcd, cd].        
    def dvd_mouse_pos(self, x, y):        
        if self.player.state == STARTING_STATE:
            self.cmd('set_mouse_pos %d %d\n' % (int(x), int(y)))
        
    def dvd_up(self):
        self.cmd('dvdnav up\n')
        
    def dvd_down(self):    
        self.cmd('dvdnav down\n')
            
    def dvd_left(self):        
        self.cmd('dvdnav left\n')
        
    def dvd_right(self):
        self.cmd('dvdnav right\n')
        
    def dvd_menu(self):    
        self.cmd('dvdnav menu\n')
        
    def dvd_select(self):
        self.cmd("dvdnav select\n")
    
    def dvd_prev(self):    
        self.cmd("dvdnav prev\n")
        
    def dvd_mouse(self):    
        if self.player.state == STARTING_STATE:
            self.cmd('dvdnav mouse\n')
        
    def switch_angle(self, value):    
        self.cmd("switch_angle '%s'\n" % (value))
        
    def next_title(self, value):    
        self.switch_title(value)
        
    def prev_title(self, value):    
        self.switch_title(value)
        
    def switch_title(self, value):
        self.cmd("switch_title %d\n" % (int(value)))
        
    def switch_chaptet(self, value, type_):
        self.cmd("switch_chaptet '%s' '%s'" % (value, type_))
            
    '''播放器控制[快进，倒退，暂停]'''    
    def seek(self, seek_num):        
        '''Set rate of progress'''
        if self.player.state == STARTING_STATE or self.player.state == PAUSE_STATE:
            self.cmd('seek %d 2\n' % (seek_num))               
            
    def fseek(self, seek_num):
        '''Fast forward'''
        if self.player.state == STARTING_STATE or self.player.state == PAUSE_STATE:
            self.cmd('seek +%d\n' % (seek_num))   
            
    def bseek(self, seek_num):
        '''backward'''
        if self.player.state == STARTING_STATE or self.player.state == PAUSE_STATE:
            self.cmd('seek -%d\n' % (seek_num))
            
    def pause(self):
        if (self.player.state == STARTING_STATE or self.player.state == PAUSE_STATE):
            if self.player.state == PAUSE_STATE:
                self.player.state = STARTING_STATE
                self.emit("pause-play", True)
            else:    
                self.player.state = PAUSE_STATE
                self.emit("pause-play", False)
            self.cmd('pause \n')
            
    def stop(self):    
        if self.player.state in [STARTING_STATE, PAUSE_STATE]:
            self.quit()
            
    '''截图'''
    # def screenshot(self, value=0):
    #    self.cmd("screenshot %d /home/long \n" % (value))
    
    def screenshot(self, path=None, outdir=".", type="jpeg"):
        if not path:
            path = self.path
        os.system("mplayer -ss 1 -noframedrop -nosound -vo %s:outdir=%s -frames 1 %s >/dev/null 2>&1" % (type, outdir, path))
        
    '''显示消息'''    
    def show_text(self, text, duration=1000, level=0):
        self.cmd("osd_show_text %s %d %s\n" % (text, duration, level))
        
    '''给Mplayer发送命令''' #cmd123456
    def cmd(self, cmd_str):
        '''Mplayer command'''
        try:            
            # print self.mplayer_in, cmd_str
            self.mplayer_in.write(str(cmd_str))
            self.mplayer_in.flush()
        except StandardError, e:
            if DEBUG:
                print 'command error %s' % (e)            

    '''mplayer 管道控制'''
    def player_thread_reader(self, source, condition):    
        if source == None:
            return False        
        
        if not self.player.state: # 如果播放结束,直接退出.
            return False

        try:
            buffer = source.readline()
        except:
            return False # 白屏BUG，所以返回假.
        '''
        if buffer == gobject.IO_STATUS_ERROR:
            if DEBUG:
                print "GIO IO Error:", buffer
            return True
        else:
            if DEBUG:
                if buffer.find("ANS") == None:
                    print buffer
        '''
        if buffer:
            if buffer.startswith("Cache fill"):
                print "Cache fill:", buffer
                # percent = buffer.replace("Cache fill:")
            #    
            if buffer.startswith("AO:"):                
                self.cmd("get_property switch_audio\n")
                
            if buffer.startswith("VO:"):
                # VO: [xv] 1280x720 => 1280x720 Planar YV12
                split_text = buffer.split(" ")
                # 获取
                size = split_text[2].split('x')
                width = int(size[0].strip())
                height = int(size[1].strip())
                # 获取视频的宽和高.
                video_size = split_text[4].split("x")
                self.player.video_width = int(video_size[0].strip())
                self.player.video_height = int(video_size[1].strip())
                self.emit("screen-changed", self.player.video_width, self.player.video_height)
                
            if buffer.startswith("Video: no video"):
                self.player.video_width = 0
                self.player.video_height = 0
                self.emit("screen-changed", self.player.video_width, self.player.video_height)
            # 
            if buffer.startswith("ANS_TIME_POSITION"):
                pos =  float(buffer.replace("ANS_TIME_POSITION=", "").split("\n")[0])
                old_position = self.player.position # 1234567
                self.player.position = pos
                if old_position != self.player.position:
                    #print "postion:", self.player.position
                    if pos:
                        self.emit("get-time-pos", pos, length_to_time(pos))
                '''
                if pos >= int(self.player.length): # 结束播放.
                    self.quit()
                '''
            #   
            if buffer.startswith("ID_START_TIME"):
                self.player.start_time = float(buffer.replace("ID_START_TIME=", "").split("\n")[0] )
                # print "ID_START_TIME:", self.player.start_time
            #    
            if buffer.startswith("ID_LENGTH"):
                length = float(buffer.replace("ID_LENGTH=", "").split("\n")[0])
                self.player.length = length
                # print "ID_LENGTH:", length
                self.emit("get-time-length", length, length_to_time(length))
                
            #    
            if buffer.startswith("ANS_LENGTH"):
                length = float(buffer.replace("ANS_LENGTH=", "").split("\n")[0])
                # print "ANS_LENGTH:", length
                self.player.length = length
                self.emit("get-time-length", length, length_to_time(length))
            #    
            if buffer.startswith("ID_AUDIO_TRACK"):
                self.audio_track = buffer.replace("ID_AUDIO_TRACK=", "").split("\n")[0]
                # print "ID_AUDIO_TRACK:", self.audio_track
                
            if buffer.startswith("ANS_switch_audio"): 
                # 字幕选择的那个!!
                switch_audio_index = buffer.replace("ANS_switch_audio=", "").split("\n")[0]
                self.player.audio_select_index = switch_audio_index
                
               
            if buffer.startswith("ANS_sub_source"):                    
                self.player.subtitle_source = buffer.replace("ANS_sub_source=", "").split("\n")[0]
                if self.player.subtitle_source == 0:
                    self.player.subtitle_is_file = True
                    self.cmd("get_property sub_file\n")                                
                elif self.player.subtitle_source == 1:    
                    self.player.subtitle_is_file = False
                    self.cmd("get_property sub_vob\n")                                
                elif self.player.subtitle_source == 2:    
                    self.player.subtitle_is_file = False
                    self.cmd("get_property sub_demux\n")
                                        
            if buffer.startswith("ANS_sub_file"):
                print "ANS_sub_file:", buffer.replace("ANS_sub_file", "").split("\n")[0]
                # self.emit()
                
            if buffer.startswith("ANS_sub_demux"):
                print buffer.replace("ANS_sub_demux", "").split("\n")[0]
                # self.emit()
                
            if buffer.startswith("DVDNAV_TITLE_IS_MENU"):
                self.player.title_is_menu = True
                self.get_time_length()
                
            if buffer.startswith("DVDNAV_TITLE_IS_MOVIE"):
                self.player.title_is_menu = False
                self.get_time_length()
                
            if buffer.startswith("ID_SUBTITLE_ID="): 
                id = buffer.replace("ID_SUBTITLE_ID=", "").split("\n")[0]
                self.player.sub_index = int(id)
                self.player.subtitle.append(id)                
                
            if buffer.startswith("ID_SID_"):
                text = buffer.split("_")[3]
                if text.startswith("NAME="):
                    name = text.replace("NAME=", "").split("\n")[0]
                    text = self.player.subtitle[self.player.sub_index]
                    text += ':' + name
                    self.player.subtitle[self.player.sub_index] = text
                elif text.startswith("LANG="):
                    lang = text.replace("LANG=", "").split("\n")[0]
                    text = self.player.subtitle[self.player.sub_index]
                    text_list = text.split(":")
                    id = text_list[0]
                    name = text_list[1]
                    text = name + "（" + lang + "）" + "-" + id
                    self.player.subtitle[self.player.sub_index] = text
                    # 发送字幕字符串.
                    self.emit("get-subtitle", text, self.player.sub_index)
                    
            if buffer.startswith("ID_FILE_SUB_ID="):
                id = buffer.replace("ID_FILE_SUB_ID=", "")
                print "ID_FILE_SUB_ID:", id
                
            if buffer.startswith("ID_AUDIO_ID="):
                self.emit("start-media-player")
                id = buffer.replace("ID_AUDIO_ID=", "").split("\n")[0]
                self.player.audio_index = int(id)
                self.player.audio_list.append(id)

            if buffer.startswith("ID_AID_"):    
                text = buffer.split("\n")[0]
                scan_aid_name = "ID_AID_%s_NAME=" % str(self.player.audio_index)
                scan_aid_lang = "ID_AID_%s_LANG=" % str(self.player.audio_index)
                if text.find(scan_aid_name) != -1:
                    name = text.replace(scan_aid_name, "")
                    text = self.player.audio_list[self.player.audio_index]
                    text += ":" + name
                    self.player.audio_list[self.player.audio_index] = text
                elif text.find(scan_aid_lang) != -1:
                    lang = text.replace(scan_aid_lang, "")
                    text_list = self.player.audio_list[self.player.audio_index].split(":")
                    if text_list:
                        try:
                            id = text_list[0]
                            name = text_list[1]
                            text = name + "（" + lang + "）" + "-" + id 
                            self.player.audio_list[self.player.audio_index] = text
                        except:
                            text = "Unknown" + "（" + lang + "）" + "-" + str(self.player.audio_index)
                        self.emit("get-audio-info", text, self.player.audio_index)

            if  buffer.startswith("ID_CHAPTERS="):   
                print "ID_CHAPTERS:", buffer.replace("ID_CHAPTERS=", "")
                
            if (buffer.startswith("ID_SEEKABLE=")
                and buffer.startswith("ID_SEEKABLE=0")):    
                print "ID_SEEKABLE and ID_SEEKABLE=0:", buffer
                print "True"
                
            if buffer.startswith("ID_VIDEO_FORMAT"): 
                self.player.video_format = buffer.replace("ID_VIDEO_FORMAT=", "").split("\n")[0]
                # print "ID_VIDEO_FORMAT:", self.player.video_format
                # buffer.startswith("ID_VIDEO_FORMAT")
                # len("ID_VIDEO_FORMAT=")
                # self.file_info.width == 0 and self.file_info.height == 0
                
            if buffer.startswith("ID_VIDEO_CODEC"):
                self.player.video_codec = buffer.replace("ID_VIDEO_CODEC=", "").split("\n")[0]
                # print "ID_VIDEO_CODEC:", self.player.video_codec
                
            if buffer.startswith("ID_VIDEO_FPS"):    
                self.player.video_fps = buffer.replace("ID_VIDEO_FPS=", "").split("\n")[0]
                # print "ID_VIDEO_FPS:", self.player.video_fps
                
            if buffer.startswith("ID_VIDEO_BITRATE"):    
                self.player.video_bitrate = buffer.replace("ID_VIDEO_BITRATE=", "").split("\n")[0]
                # print "ID_VIDEO_BITRATE:", self.player.video_bitrate                
            #    
            if buffer.startswith("ID_AUDIO_FORMAT"):
                self.player.audio_format = buffer.replace("ID_AUDIO_FORMAT=", "").split("\n")[0]
                # print 'ID_AUDIO_FORMAT:', self.player.audio_format

            if buffer.startswith("ID_AUDIO_CODEC"):
                self.player.audio_codec = buffer.replace("ID_AUDIO_CODEC=", "").split("\n")[0]
                # print "ID_AUDIO_CODEC:", self.player.audio_codec
                
            if buffer.startswith("ID_AUDIO_BITRATE"):    
                self.player.audio_bitrate = buffer.replace("ID_AUDIO_BITRATE=", "").split("\n")[0]
                # print "ID_AUDIO_BITRATE:", self.player.audio_bitrate
                
            if buffer.startswith("ID_AUDIO_RATE"):    
                self.player.audio_rate = buffer.replace("ID_AUDIO_RATE=", "").split("\n")[0]
                # print "ID_AUDIO_RATE:", self.player.audio_rate
                
            if buffer.startswith("ID_AUDIO_NCH"):                    
                self.player.audio_nch = buffer.replace("ID_AUDIO_NCH=", "").split("\n")[0]
                # print "ID_AUDIO_NCH:", self.player.audio_nch
                
            if buffer.startswith("*** screenshot"):    
                #... ...
                print buffer
            
            if buffer.startswith("Name   : "):
                print "name:", buffer
                
            if buffer.startswith("Genre  : "):
                print "Genre:", buffer
                
            if buffer.startswith("Title: "):    
                print "Title:", buffer
                
            if buffer.startswith("Artist: "):    
                print "Artist:", buffer
                
            if buffer.startswith("Album: "):    
                print "Album:", buffer                
                
            if buffer.startswith("ICY Info"):
                print "ICY info:", buffer
                # ... ...
                
            if buffer.startswith("ID_FILENAME"):   
                file_name = buffer.replace("ID_FILENAME=", "").split("\n")[0] + "\0"
                self.player.title = os.path.split(file_name)[1]
                
        return True
    
    def player_thread_reader_error(self, source, condition): # 错误处理.
        error_code = None
        
        if not source or not self.player.state:
            return False
                
        try:
            buffer = source.readline()
            #print "error:--->>", buffer
        except Exception , e:
            buffer = ""
            return False # 白屏BUG，所以返回假.（假死)

            
        if self.player.type == TYPE_FILE:    
            if buffer.startswith("Failed to recognize file format"):
                error_code = ERROR_FILE_FORMAT
        elif self.player.type == TYPE_DVD:
            # if buffer.startswith("Couldn't open DVD device"):
            #     error_code = ERROR_DVD_DEVICE
            pass
        elif self.player.type == TYPE_NETWORK:    
            if buffer.startswith("mplayer: could not connect to socket"):
                error_code = ERROR_SOCKET_CONNECT                
            elif (buffer.startswith("Couldn't resolve name for AF_INET") 
                  or buffer.startswith("Couldn't resolve name for AF_INET6")):
                error_code = ERROR_RESOLVE_AF_INET
                
        # if buffer.startswith("X11 error"):
        #     error_code = ERROR_X11
            
        # if buffer.startswith("Failed creating VDPAU decoder"):
            # if (self.player.enable_divx 
                # and self.player.vo.startswith("vdpau")):
                # error_code = ERROR_RETRY_WITHOUT_DIVX_VDPAU
            
        # if buffer.startswith("decoding to PIX_FMT_NONE is not supported"):
        #     if self.player.enable_divx:
        #         error_code = ERROR_RETRY_WITHOUT_HARDWARE_CODECS
                
        # if buffer.startswith("The selected video_out device is incompatible with this codec"):
        #     if (self.player.disable_xvmc 
        #         and self.player.startswith("xvmc")):
        #         error_code = ERROR_RETRY_WITHOUT_XVMC
                
        if buffer.startswith("[AO_ALSA] Playback open error: Device or resource busy"):
            error_code = ERROR_RETRY_ALSA_BUSY
                        
        if buffer.startswith("Failed to open"):
            if buffer.find("mms://") and self.player.type == TYPE_NETWORK:
                error_code = ERROR_RETRY_WITH_MMSHTTP
                
        if buffer.startswith("No stream found to handle url mmshttp://"):
            error_code = ERROR_RETRY_WITH_HTTP
            
        if (buffer.startswith("Server returned 404:File Not Found")
            and self.player.uri.startswith("mmshttp://")):    
                error_code = ERROR_RETRY_WITH_HTTP
                
        if buffer.startswith("unknown ASF streaming type") and self.player.uri.startswith("mmshttp://"):
            error_code = ERROR_RETRY_WITH_HTTP
            
        if buffer.startswith("Error while parsing chunk header"):
            error_code = ERROR_RETRY_WITH_HTTP_AND_PLAYLIST
    
        if buffer.startswith("Failed to initiate \"video/X-ASF-PF\" RTP subsession"):
            error_code = ERROR_RETRY_WITH_PLAYLIST
                        
        if buffer.startswith("moov atom not found"):
            self.playerretry_on_full_cache = True;
            
        if buffer.startswith("MOV: missing header (moov/cmov) chunk"): 
            self.playerretry_on_full_cache = True;

        if buffer.startswith("Seek failed"):    
            self.quit()
                        
        if error_code:
            self.emit("error-msg", error_code)
            
        return True
    
    def player_thread_complete(self, source, condition): 
        #print "player_thread_complete..."
        if DEBUG:
            print "player_thread_complete:", "断开管道!!"
        try:            
            # modify state.
            self.player.state = STOPING_STATE
            #print "mplayer_pid:", self.mplayer_pid
            # close fd.
            self.mplayer_in.close()
            self.mplayer_out.close()
            self.mplayer_err.close()
            remove_timeout_id(self.watch_in_id)
            remove_timeout_id(self.watch_err_id)
            remove_timeout_id(self.watch_in_hup_id)
            # kill mplayer.
            self.mp_id.kill() 
            os.kill(self.mplayer_pid, 0)
            #os.system("kill %s" % (self.mplayer_pid)) # 杀死 mplayer pid.
            self.timer.Enabled = False # 关闭发送get-time-pos命令的时钟.   
            self.emit("end-media-player")        
        except StandardError, e:
            print "player_thread_complete:", e
        return False
    
    def get_play_file_type(self):
        if self.player.uri.startswith(('mmshttp', 'http', 'mms', 'https')):
            return TYPE_NETWORK        
        elif self.player.uri.startswith(('dvdnav', 'dvd')):
            return TYPE_DVD
        elif self.player.uri.startswith(('cdda', 'cddb')):
            return TYPE_CD
        elif self.player.uri.startswith(("vcd")):
            return TYPE_VCD
        elif self.player.uri.startswith(('tv')):
            return TYPE_TV
        elif self.player.uri.startswith(('dvb')):
            return TYPE_DVB
        elif self.player.uri.startswith(('file')):
            return TYPE_FILE
        else:
            return TYPE_FILE
            
    def quit(self): # 退出.
        try: # BUG: 由于结束的进度太慢,所以需要在这里直接免杀进程.
            self.cmd('quit \n')       
            self.player.state = STOPING_STATE

            self.mplayer_in.close()
            self.mplayer_out.close()
            self.mplayer_err.close()

            self.emit("end-media-player")        
        except:
            pass
                
def remove_timeout_id(callback_id):
    if callback_id:
        gobject.source_remove(callback_id)
        callback_id = None
                                               
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
        

############################################################
### 画面比例

ASCEPT_4X3_STATE = "4:3"
ASCEPT_16X9_STATE = "16:9"
ASCEPT_5X4_STATE = "5:4"
ASCEPT_16X10_STATE = "16:10"
ASCEPT_1_85X1_STATE = "1.85:1"
ASCEPT_2_35X1_STATE = "2.35:1"
ASCEPT_FULL_STATE = None
ASCEPT_DEFULAT = "defulat" # 视频的宽[video_width]/视频的高[video_height]

def set_ascept_function(screen_frame, video_aspect):
    x, y, w, h = screen_frame.allocation
    screen_frame_aspect = round(float(w) / h, 2)
    #
    if screen_frame_aspect == video_aspect or video_aspect == None:
        screen_frame.set(0.0, 0.0, 1.0, 1.0)
    elif screen_frame_aspect > video_aspect:
        x = (float(h)* video_aspect) / w
        if x > 0.0:
            screen_frame.set(0.5, 0.0, _max(x, 0.1, 1.0), 1.0)
        else:
            screen_frame.set(0.5, 0.0, 1.0, 1.0)
    elif screen_frame_aspect < video_aspect:
        y = (float(w) / video_aspect) / h;
        if y > 0.0:
            screen_frame.set(0.0, 0.5, 1.0, _max(y, 0.1, 1.0))
        else:
            screen_frame.set(0.0, 0.5, 1.0, 1.0)

def _max(x, low, high):
    if low <= x <= high:
        return x
    if low > x:
        return low
    if high < x:
        return high
    
# 获取播放窗口的XID.
def get_window_xid(widget):
    return widget.window.xid
    
'''关闭和打开双缓冲.'''
def unset_flags(screen):
    '''Set double buffer.'''
    screen.unset_flags(gtk.DOUBLE_BUFFERED)

def set_flags(screen):
    '''Set double buffer.'''
    screen.set_flags(gtk.DOUBLE_BUFFERED)
    
    
