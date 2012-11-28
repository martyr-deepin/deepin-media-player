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

########################################################
#   Python Mplayer API(PMA).
#   .play(path)    .decvolume()
#   .pause()       .offmute()
#   .quit()        .nomute()
#   .next()        ... ...
#   .pre()
#   .fseek()
#   .bseek()
#   .addvolume()
########################################################
from dtk.ui.utils import remove_timeout_id
from locales import _
import random
import gtk
import os
import re
import fcntl
import gobject
import subprocess
from type_check import is_valid_video_file, is_valid_url_file, is_file_can_play 
from ini import Config
from cdrom.cdrom import cdrom_type, get_iso_type, CDROM_ERROR, CDROM_TYPE_DVD, CDROM_TYPE_VCD

# play list state.
# 0: single playing.      
SINGLE_PLAYING_STATE = 0
# 1: order playing.     
ORDER_PLAYING_STATE = 1
# 2: random player.      
RANDOM_PLAYER_STATE = 2
# 3: single cycle player. 
SINGLE_CYCLE_PLAYER = 3
# 4: list recycle play. 
LIST_RECYCLE_PLAY = 4
# channel state.
CHANNEL_NORMAL_STATE = 0
CHANNEL_LEFT_STATE = 1
CHANNEL_RIGHT_STATE = 2
# playing state.
STOPING_STATE = 0
STARTING_STATE = 1

# Get play widow ID.
def get_window_xid(widget):
    return widget.window.xid  

# Get ~ to play file path.
def get_home_path():
    return os.path.expanduser("~")

# Get play file length.
def get_length(file_path):
    '''Get media player length.'''
    cmd = "mplayer -vo null -ao null -frames 0 -identify '%s'" % (file_path)
    fp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    cmd_str = fp.communicate()[0]
    length_compile = re.compile(r"ID_LENGTH=([\d|\.]+)")
    try:
        length = length_compile.findall(cmd_str)[0]
    except:            
        length = 520                
    return length_to_time(length), str((length))

def get_vide_width_height(file_path):
    try:
        if is_valid_video_file(file_path):
            cmd = "mplayer -vo null -ao null -frames 0 -identify '%s' 2>&1" % (file_path)
            fp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)    
            cmd_str = fp.communicate()[0]
            length_compile = re.compile(r"VIDEO:.+") 
            length = length_compile.findall(cmd_str)
            length = length[0][16:]
            width_compile = re.compile(r"\d+x")
            height_compile = re.compile(r"x\d+")
    
            video_width = width_compile.findall(length)[0][:-1]
            video_height = height_compile.findall(length)[0][1:]

            return float(video_width), float(video_height)
        else:
            return float(0), float(0)
    except:
        return float(0), float(0)


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
        
def init_mplayer_config():
    # Create config directory if it not exists.
    path = os.path.join(get_home_path(), ".config/deepin-media-player")
    if not os.path.exists(path):
        os.makedirs(path)
        
    # Create subdirectories if it not exists.
    for subdir in ["subtitle", "buffer", "image"]:
        subpath = os.path.join(path, subdir)
        if not os.path.exists(subpath):
            os.makedirs(subpath)
            
    # Create preview directories if it not exists.
    for subdir in ["/tmp/buffer", "/tmp/preview"]:
        if not os.path.exists(subdir):
            os.makedirs(subdir)
        
    # Create config if it not exists.    
    config_path = os.path.join(path, "config.ini")
    if not os.path.exists(config_path):
        fp = open(config_path, "a")
        fp.close()
        
    # Create media config file if it not exists.
    media_config_path = os.path.join(path, "deepin_media_config.ini")
    if not os.path.exists(media_config_path):
        fp = open(media_config_path, "a")
        fp.close()            
        
        # Init config.ini            
        config = Config(media_config_path)
        
        # Init window.
        config.set("Window", "init_window", "True")
        
        #[FilePlay]
        for argv, value in ([
                ("video_file_open",                          2),
                ("open_new_file_clear_play_list", "True"),
                ("memory_up_close_player_file_postion", "True"),
                ("find_play_file_relation_file", "False"),
                ("mouse_progressbar_show_preview", "False")
                ]):
            config.set("FilePlay", argv, value)
            
        #[SystemSet]
        for argv, value in ([
                ("minimize_pause_play", "False"),
                ("font", "文泉驿微米黑"),
                ("font_size", "16")
                ]):
            config.set("SystemSet", argv, value)
            
        #[PlayControl]
        for argv, value in ([
                ("play_control_bool", "True"),
                ("open_file_key", "Ctrl + o"),
                ("open_file_dir_key", "Ctrl + f"),
                ("play_or_pause_key", "Space"),
                ("seek_key", "Right"),
                ("back_key", "Left"),
                ("full_key", "Return"),
                ("pre_a_key", "Page_Up"),
                ("next_a_key", "Page_Down"),
                ("add_volume_key", "Up"),
                ("sub_volume_key", "Down"),
                ("mute_key", "m"),
                ("concise_key", "Shift + Return")
                ]):
            config.set("PlayControl", argv, value)
            
        #[SubKey]    
        for argv, value in ([
                ("subkey_bool", "True"),
                ("subkey_add_delay_key", "["),
                ("subkey_sub_delay_key", "]"),
                ("subkey_load_key", "Alt + o"),
                ("subkey_add_scale_key", "Alt + Left"),
                ("subkey_sub_scale_key", "Alt + Right"),
                ]):
            config.set("SubKey", argv, value)
            
        #[OtherKey]
        for argv, value in ([
                ("other_key_bool", "True"),
                ("add_brightness_key", "="),
                ("sub_brightness_key", "-"),
                ("inverse_rotation_key", "w"),
                ("clockwise_key", "e"),
                ("sort_image_key", "Alt + a"),
                ("switch_audio_track_key", _("Disabled")),
                # ("load_subtitle_key", "Alt + o"),
                # ("subtitle_delay_key", "]"),
                # ("subtitle_advance_key", "["),
                ("mouse_left_single_clicked", _("Pause/Play")),
                ("mouse_left_double_clicked", _("Full Screen")),
                ("mouse_wheel_event", _("Volume")),
                ]):
            config.set("OtherKey", argv, value)

        #[SubtitleSet]
        for argv, value in ([
                ("ai_load_subtitle", "True"),
                # ("specific_location_search", os.path.join(get_home_path(), ".config/deepin-media-player/subtitle"))
                ("specific_location_search",  "~/.config/deepin-media-player/subtitle")
                ]):
            config.set("SubtitleSet", argv, value)
        
        #[ScreenshotSet]
        for argv, value in ([
                ("save_clipboard", "False"),
                ("save_file", "True"),
                # ("save_path", os.path.join(get_home_path(), ".config/deepin-media-player/image")),
                ("save_path", "~/.config/deepin-media-player/image"),
                ("save_type", ".png"),
                ("current_show_sort", "False")
                ]):
            config.set("ScreenshotSet", argv, value)
            
        # save ini config.
        config.save()
        
VIDEO_TYPE = 0        
DVD_TYPE = 1
VCD_TYPE = 2

class  Mplayer(gobject.GObject):
    '''deepin media player control layer'''
    __gsignals__ = {
        "get-time-pos":(gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_NONE,(gobject.TYPE_INT,)),
        "get-time-length":(gobject.SIGNAL_RUN_LAST,
                           gobject.TYPE_NONE,(gobject.TYPE_INT,)),
        "volume":(gobject.SIGNAL_RUN_LAST,
                  gobject.TYPE_NONE,(gobject.TYPE_INT,)),
        "play-init":(gobject.SIGNAL_RUN_LAST,
                      gobject.TYPE_NONE,(gobject.TYPE_INT,)),
        "play-start":(gobject.SIGNAL_RUN_LAST,
                      gobject.TYPE_NONE,(gobject.TYPE_INT,)),
        "play-end":(gobject.SIGNAL_RUN_LAST,
                    gobject.TYPE_NONE,(gobject.TYPE_INT,)),
        "play-next":(gobject.SIGNAL_RUN_LAST,
                     gobject.TYPE_NONE,(gobject.TYPE_INT,)),
        "play-pre":(gobject.SIGNAL_RUN_LAST,
                    gobject.TYPE_NONE,(gobject.TYPE_INT,)),
        "play-fseek":(gobject.SIGNAL_RUN_LAST,
                      gobject.TYPE_NONE,(gobject.TYPE_INT,)),
        "play-bseek":(gobject.SIGNAL_RUN_LAST,
                      gobject.TYPE_NONE,(gobject.TYPE_INT,)),
        "add-path":(gobject.SIGNAL_RUN_LAST,
                    gobject.TYPE_NONE,(gobject.TYPE_STRING,)),
        "clear-play-list":(gobject.SIGNAL_RUN_LAST,
                    gobject.TYPE_NONE,(gobject.TYPE_INT,)),
        "same-name-event":(gobject.SIGNAL_RUN_LAST,
                    gobject.TYPE_NONE,(gobject.TYPE_STRING,))
        }
    def __init__(self, xid = None):
        
        gobject.GObject.__init__(self)
        
        self.xid = xid 
        self.aid_number  = 0
        self.mplayer_pid = 0
        self.state = STOPING_STATE
        self.vide_bool = False
        self.dvd_bool = False
        self.video_type = VIDEO_TYPE
        self.pause_bool = False
        self.dvd_menu_bool = False # test dvdnav menu.
        self.lenState = 0
        self.path = ""
        
        self.time_hour = 0
        self.time_min = 0
        self.time_sec = 0
        
        self.len_num = 0
        self.pos_num = 0
        
        # select channel state.
        self.channel_state = CHANNEL_NORMAL_STATE
        
        # player list.
        self.play_list = [] 
        # player list sum. 
        self.play_list_sum = 0 
        # player list number. 
        self.play_list_num = -1
        # random player num.
        self.random_num = 0;
        
        self.volumebool = False
        self.volume = 100
        # player state.
        # 0: single playing.      
        # 1: order playing.     
        # 2: random player.      
        # 3: single cycle player. 
        # 4: list recycle play. 
        self.play_list_state = SINGLE_PLAYING_STATE
        self.subtitle_scale_value = 1.0        
        
    def play(self, path, cdrom_type=None):            
        self.video_type = VIDEO_TYPE
        self.path = path
        if not (self.state): # STOPING_STATE
            self.lenState = 1 
            # -input file.. streme player.
            command = ['mplayer',
                       '-vo',
                       'gl,2,x11,xv',
                       '-zoom',
                       '-nokeepaspect',
                       '-osdlevel',
                       '0',
                       '-double',
                       '-slave',
                       '-quiet']            
            
            # control deepin-media-player.
            # command.append("-input")
            # command.append("file=/tmp/deepin_media_player_cmd")

            # If path is url, must be add option `-nocache`,
            # otherwise, mplayer cache process can't quit normally.
            if is_valid_url_file(self.path):
                command += ['-nocache']
                
            if  self.path.endswith(".iso") or cdrom_type != None: # mount .iso
                # type.
                if cdrom_type == None:
                    type_ = get_iso_type(self.path)
                else:    
                    type_ = cdrom_type
                    
                if type_ == CDROM_TYPE_DVD: # add dvd iso.
                    command.append("-mouse-movements")
                    command.append("-nocache")
                    command.append("dvdnav://")
                    command.append("-dvd-device")
                    self.dvd_bool = True
                    self.dvd_menu_bool = True
                    self.video_type = DVD_TYPE
                elif type_ == CDROM_TYPE_VCD: # add vcd iso.
                    command.append("-nocache")
                    command.append("vcd://2")
                    command.append("-dvd-device")

            # add path.                
            command.append(path)
            # add wid.
            command.append('-wid')
            command.append('%s' % (str(self.xid)))
            
            self.mp_id = subprocess.Popen(command, 
                                         stdin = subprocess.PIPE,
                                         stdout = subprocess.PIPE,
                                         stderr = subprocess.PIPE,
                                         shell = False)
            
            self.mplayer_pid = self.mp_id.pid
            (self.mplayer_in, self.mplayer_out) = (self.mp_id.stdin, self.mp_id.stdout)
                                                
            fcntl.fcntl(self.mplayer_out, 
                        fcntl.F_SETFL, 
                        os.O_NONBLOCK)
            
            self.emit("play-init", True)
            
            # get length size.
            self.get_time_length(path)
            # get pos size.
            self.get_position_id = gobject.timeout_add(400, self.get_time_pos) 
                                
            # IO_HUP[Monitor the pipeline is disconnected].
            self.eof_id = gobject.io_add_watch(self.mplayer_out, gobject.IO_HUP, self.mplayer_eof)
            self.state = STARTING_STATE
            if cdrom_type == None:
                self.vide_bool = is_valid_video_file(self.path)
            else:    
                self.vide_bool = 1 # dvd
            # Set volume.
            if self.volumebool:
                self.nomute()
            else:    
                self.setvolume(self.volume)
                
            # emit play-start.
            gobject.timeout_add(250, self.emit_play_start_event)
            
    def emit_play_start_event(self):
        self.channel_state = CHANNEL_NORMAL_STATE # 0
        self.emit("play-start", self.mplayer_pid)
        return False
    
    ## Cmd control ##    
    def cmd(self, cmd_str):
        '''Mplayer command'''
        try:
            self.mplayer_in.write(cmd_str)
            self.mplayer_in.flush()
        except StandardError, e:
            print 'command error %s' % (e)
          
    def get_time_length(self, path):
        '''Get the total length'''
        self.len_num = int(float(get_length(path)[1]))
        self.emit("get-time-length", self.len_num)
                               
    def get_time_pos(self):
        '''Get the current playback progress'''
        self.cmd('get_time_pos\n')
        
        while True:
            try:
                line = self.mplayer_out.readline()
            except StandardError:
                break
                            
            if not line:
                break
        
            if line.startswith("ANS_TIME_POSITION"):
                pos_num = int(float(line.replace("ANS_TIME_POSITION=", "")))
                
                if pos_num > 0:
                    self.pos_num = pos_num                   
                    # Init Hour, Min, Sec.
                    self.time_hour = 0
                    self.time_min = 0
                    self.time_sec = 0
                    self.time(self.pos_num)  
                    self.emit("get-time-pos", int(self.pos_num))
                    
        return True

    ## Subtitle Control ##
    def sub_add(self, sub_file):
        '''Load subtitle'''
        if self.state == STARTING_STATE: # STARTING_STATE
            self.cmd("sub_load '%s'\n" % (sub_file))
            
    def sub_select(self, index):        
        if self.state == STARTING_STATE: # STARTING_STATE
            self.cmd('sub_select %s\n' % str(index))
            
    def sub_clear(self, end_index): # clear all subtitl file.
        if self.state == STARTING_STATE:
            for index in range(0, end_index):
                self.sub_del(index)
                
    def sub_del(self, index):        
        if self.state == STARTING_STATE: # STARTING_STATE
            self.cmd('sub_remove %s\n' % index)
                        
    def sub_stop(self):        
        if self.state == STARTING_STATE:
            self.cmd("sub_select -1\n")
            
    # subtitle alignment. # 0 top 1 center 2 bottom  
    def sub_alignment_top(self):
        self.sub_alignment(0)
        
    def sub_alignment_center(self):
        self.sub_alignment(1)
        
    def sub_alignment_bottom(self):
        self.sub_alignment(2)
        
    def sub_alignment(self, alignment_state):
        if self.state == STARTING_STATE:
            self.cmd("sub_alignment %s\n"%(alignment_state))

    # subtitle delay(+/-[abs]).
    def sub_up_delay(self): # sub_delay 0.1\n sub_delay -0.1\n
        self.sub_delay(0.1)
        
    def sub_down_delay(self):
        self.sub_delay(-0.1)
    
    def sub_delay(self, value):                    
        if self.state == STARTING_STATE:
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
        if self.state == STARTING_STATE:
            self.cmd("sub_scale %s 1\n" % (value));
                    
    ## Volume Control ##
    def addvolume(self, volume_num):
        '''Add volume'''
        self.volume = volume_num
        self.volume = min(self.volume, 100)
        
        if self.state == STARTING_STATE:
            self.cmd('volume +%s 1\n' % str(self.volume))
        
    def decvolume(self, volume_num):
        '''Decrease volume'''
        self.volume = volume_num
        self.volume = max(self.volume, 0)
        
        if self.state == STARTING_STATE:
            self.cmd('volume -%s 1\n' % str(self.volume))
            
    def setvolume(self, volume_num):
        '''Add volume'''
        self.volume = volume_num
        self.volume = max(min(self.volume, 100), 0)
        
        if self.state == STARTING_STATE:
            self.cmd('volume %s 1\n' % str(self.volume))
            
    def leftchannel(self):
        '''The left channel'''
        if self.state == STARTING_STATE:
            self.cmd('af channels=2:2:0:0:0:0\n')
            self.channel_state = CHANNEL_LEFT_STATE #1
    
    def rightchannel(self):
        '''The right channel'''
        if self.state == STARTING_STATE:
            self.cmd('af channels=2:2:0:1:1:1\n')             
            self.channel_state = CHANNEL_RIGHT_STATE #2
            
    def normalchannel(self):
        '''Normal channel'''
        if self.state == STARTING_STATE:
            self.cmd('af channels=2:2:0:0:1:1\n')
            self.channel_state = CHANNEL_NORMAL_STATE #0
            
    def offmute(self): 
        self.volumebool = False
        self.cmd('mute 0\n')
        
        
    def nomute(self):
        '''Active mute'''
        self.volumebool = True
        self.cmd('mute 1\n')
                
    def off_switch_audio(self):
        self.switch_audio(-1)
        
    def switch_audio(self, number):        
        self.cmd('switch_audio %s\n'% str(number))
        self.aid_number = number
        
    ## video Control ##
    # brightness.
    def addbri(self, bri_num):
        '''Add brightness'''
        if self.state == STARTING_STATE:
            self.cmd('brightness +%s\n' % (bri_num))
    
    def decbri(self, bri_num):
        '''Decrease brightness'''
        if self.state == STARTING_STATE:
            self.cmd('brightness -%s\n' % (bri_num))
    
    # saturation.
    def addsat(self, sat_num):
        '''Add saturation'''
        if self.state == STARTING_STATE:
            self.cmd('saturation +%s\n' % (sat_num))
            
    def decsat(self, sat_num):
        '''Decrease saturation'''        
        if self.state == STARTING_STATE:
            self.cmd('saturation -%s\n' % (sat_num))
    
    # contrast. 
    def addcon(self, con_num):
        '''Add contrast'''
        if self.state == STARTING_STATE:
            self.cmd('contrast +%s\n' % (con_num))    
            
    def deccon(self, con_num):
        '''Decrease contrast'''    
        if self.state == STARTING_STATE:
            self.cmd('contrast -%s\n' % (con_num))
    
    # hue.
    def addhue(self, hue_num):
        '''Add hue'''
        if self.state == STARTING_STATE:
            self.cmd('hue +%s\n' % (hue_num))        
    def dechue(self, hue_num):
        '''Decrease hue'''
        if self.state == STARTING_STATE:
            self.cmd('hue -%s\n' % (hue_num))
    
    # get play file info.        
    def get_audio_bitrate(self): # 音频比特率
        self.cmd("get_audio_bitrate\n")
        return self.get_info("ANS_AUDIO_BITRATE=")
                
    def get_audio_codec(self): # 音频编码器名称
        self.cmd("get_audio_codec\n")
        return self.get_info("ANS_AUDIO_CODEC=")
    
    def get_audio_samples(self): # 采样数 声道数 
        self.cmd("get_audio_samples\n")
        return self.get_info("ANS_AUDIO_SAMPLES=")
    
    def get_file_name(self): # 专辑的元数据
        self.cmd("get_file_name\n")
        return self.get_info("ANS_FILENAME=")
    
    def get_meta_artist(self): # 艺术家的元数据
        self.cmd("get_meta_artist\n")
        return self.get_info("ANS_META_ARTIST=")
        
    def get_meta_comment(self): # 评论....
        self.cmd("get_meta_comment\n")
        return self.get_info("ANS_META_COMMENT=")
    
    def get_meta_genre(self): # 流派
        self.cmd("get_meta_genre\n")
        return self.get_info("ANS_META_GENRE=")
        
    def get_meta_title(self): # 标题
        self.cmd("get_meta_title\n")
        return self.get_info("ANS_META_TITLE=")
    
    def get_meta_track(self): # 音轨数量
        self.cmd("get_meta_track\n")
        return self.get_info("ANS_META_TRACK=")
    
    def get_meta_year(self): # 年份
        self.cmd("get_meta_year\n")
        return self.get_info("ANS_META_YEAR=")
    
    def get_video_bitrate(self): # 视频比特率
        self.cmd("get_video_bitrate\n")
        return self.get_info("ANS_VIDEO_BITRATE=")
    
    def get_video_codec(self): # 视频编码器名称
        self.cmd("get_video_codec\n")
        return self.get_info("ANS_VIDEO_CODEC=")
        
    def get_video_resolution(self): # 视频分辨率
        self.cmd("get_video_resolution\n")
        return self.get_info("ANS_VIDEO_RESOLUTION=")
    
    def get_info(self, info_flags): # get information
        while True:
            try:
                line = self.mplayer_out.readline()
            except StandardError:
                break
                            
            if not line:
                break
            
            if line.startswith(info_flags):
                return line.replace(info_flags, "")
            else:
                return line
                            
    # cdrom [dvd, vcd, cd].        
    def dvd_mouse_pos(self, x, y):        
        if self.state == STARTING_STATE:
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
        if self.state == STARTING_STATE:
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
                
    ## Play control ##   
    def playwinmax(self):
        '''Filed play window.'''
        if not self.dvd_bool:
            self.cmd('vo_fullscreen\n')
            
    def seek(self, seek_num):        
        '''Set rate of progress'''
        if self.state == STARTING_STATE:
            self.cmd('seek %d 2\n' % (seek_num))               
            
    def fseek(self, seek_num):
        '''Fast forward'''
        if self.state == STARTING_STATE:
            self.cmd('seek +%d\n' % (seek_num))   
            self.emit("play-fseek", seek_num)
            
    def bseek(self, seek_num):
        '''backward'''
        if self.state == STARTING_STATE:
            self.cmd('seek -%d\n' % (seek_num))
            self.emit("play-bseek", seek_num)
            
    def pause(self):
        if (self.state == STARTING_STATE) and (not self.pause_bool) and (not self.dvd_menu_bool):             
            self.pause_bool = True
            self.cmd('pause \n')

    def start_play(self):        
        if (self.state == STARTING_STATE) and (self.pause_bool):
            self.pause_bool = False
            self.cmd('pause \n')        
                    
    def quit(self):
        '''quit deepin media player.'''
        if self.state == STARTING_STATE:
            # dvd bool.
            self.dvd_bool = False
            self.dvd_menu_bool = False
            
            self.stop_get_position_id()
            self.stop_eof_id()
            # Send play end signal.
            self.emit("play-end", True)
            self.cmd('quit \n')
            self.state = STOPING_STATE
            try:
                self.mplayer_in.close()
                self.mplayer_out.close()
                self.mp_id.kill()
            except StandardError:
                pass
                
    def stop_eof_id(self):
        remove_timeout_id(self.eof_id)
        
    def stop_get_position_id(self):
        remove_timeout_id(self.get_position_id)
    
    def stop_get_len_id(self):
        remove_timeout_id(self.get_length_id)
            
    def mplayer_eof(self, error, mplayer):
        '''Monitoring disconnect'''
        self.stop_get_position_id()
        self.state = STOPING_STATE
        self.mplayer_in, self.mplayer_out = None, None
        # Send play end signal.
        self.emit("play-end", True)
        if self.play_list_state == SINGLE_PLAYING_STATE: 
            self.quit()
            return False
        
        self.play_list_num += 1
        # Order play
        if self.play_list_state == ORDER_PLAYING_STATE:
            self.quit()
            if self.play_list_num < self.play_list_sum:
                self.play(self.play_list[self.play_list_num])    
            else:
                self.play_list_num -= 1
                return False
        # signal loop.    
        elif self.play_list_state == SINGLE_CYCLE_PLAYER:            
            self.play_list_num -= 1
            self.play(self.play_list[self.play_list_num])                
            
            
        self.play_list_num = self.play_list_num % self.play_list_sum
        
        self.next_or_pre_state()    
        
        return False
                
    # player state.
    # 0: single playing.      
    # 1: order playing.       
    # 2: random player.       
    # 3: single cycle player. 
    # 4: list recycle play.                          
    
    def random_player(self): 
        '''Random player'''
        self.play_list_num = random.randint(0, self.play_list_sum - 1)
        for i in range(0,self.play_list_sum + self.play_list_sum):
            if self.play_list_num == self.random_num:
                self.play_list_num = random.randint(0, self.play_list_sum - 1)
            else:
                break           
        self.random_num = self.play_list_num    
        self.quit()
        self.play(self.play_list[self.play_list_num])
            
    def list_recycle_paly(self):
        '''state : 4'''
        self.quit()
        self.play(self.play_list[self.play_list_num])
    
    def next_or_pre_state(self):    
        if self.play_list_state == RANDOM_PLAYER_STATE: #Random player
            self.random_player()     
        elif self.play_list_state == LIST_RECYCLE_PLAY or self.play_list_state == SINGLE_PLAYING_STATE or self.play_list_state == ORDER_PLAYING_STATE or self.play_list_state == SINGLE_CYCLE_PLAYER:
            self.list_recycle_paly() 
            
    def next(self):
        if self.play_list_sum > 0:
            self.play_list_num += 1
            # Start.
            self.play_list_num = self.play_list_num % self.play_list_sum
            self.next_or_pre_state()
            self.emit("play-next", 1)
        else:    
            self.emit("play-next", 0)
            
    def pre(self):
        if self.play_list_sum > 0:
            self.play_list_num -= 1
            if self.play_list_num < 0:
                self.play_list_num = self.play_list_sum - 1
            self.next_or_pre_state()
            self.emit("play-pre", 1)
                
    ## time Control ##
    def time(self, sec):
        # Clear.
        self.time_sec = 0
        self.time_hour = 0
        self.time_min = 0
        
        self.time_sec = int(sec)
        
        if self.time_sec >= 3600:
            self.time_hour = int(self.time_sec / 3600)
            self.time_sec -= int(self.time_hour * 3600)
        
        if self.time_sec >= 60:
            self.time_min = int(self.time_sec / 60)
            self.time_sec -= int(self.time_min * 60)         
            
        return self.time_hour, self.time_min, self.time_sec    
    
    # Puase show image.
    def scrot(self, 
              scrot_pos, 
              scrot_save_path = get_home_path() + "/.config/deepin-media-player/image/scrot.png"):
        
        # ini config path.
        init_mplayer_config()
        #########################
        
        if self.state == STARTING_STATE:
            # scrot image.
            scrot_command = "cd ~/.config/deepin-media-player/buffer/ && mplayer -ss %s -noframedrop -nosound -vo png -frames 1 '%s' >/dev/null 2>&1" % (scrot_pos, self.path)
            os.system(scrot_command)
            # modify image name or get image file.
            save_image_path = get_home_path() + "/.config/deepin-media-player/buffer/"        # save image buffer dir.
            image_list = os.listdir(get_home_path() + "/.config/deepin-media-player/buffer/") # get dir all image.
            # print image_list
            for image_name in image_list:
                if "png" == image_name[-3:]:
                    # preview window show image.
                    os.system("cp '%s' '%s'" % (save_image_path + image_name, scrot_save_path))                    
                    break                
            return True
        else:
            return False
        
        
    def preview_scrot(self, 
                      scrot_pos, 
                      scrot_save_path = "/tmp/preview/preview.jpeg"):                      
        # ini config path.
        init_mplayer_config()
        #########################
        
        if not os.path.exists(os.path.split(scrot_save_path)[0]):
            os.mkdir(os.path.split(scrot_save_path)[0])
            
        if self.state == STARTING_STATE:
            # scrot image.
            os.system("cd /tmp/buffer/ && mplayer -ss %s -noframedrop -nosound -vo png -frames 1 '%s' >/dev/null 2>&1" % (scrot_pos, self.path))
            # modify image name or get image file.
            save_image_path = "/tmp/buffer/"        # save preview image buffer dir.    
            image_list = os.listdir(save_image_path) # get dir all image.
            # print image_list
            for image_name in image_list:
                if "png" == image_name[-3:]:
                    # preview window show image.
                    try:
                        pixbuf = gtk.gdk.pixbuf_new_from_file(save_image_path + "00000001.png")
                        pixbuf.save(scrot_save_path, "png")
                    except:    
                        break
                    break
                
            return True
        else:
            return False               
        
    def find_current_dir(self, path):
        '''Get all the files in the folder'''
        pathdir = os.listdir(path)       
        for pathfile in pathdir:
            pathfile2 = os.path.join(path, pathfile)
            if os.path.isfile(pathfile2):
                self.add_play_file(pathfile2)
                    
    def del_playlist(self, path): 
        '''Del a File'''
        self.play_list.remove(path)            
        self.play_list_sum -= 1        
                
    def add_play_file(self, path):    
        if is_file_can_play(path): # play file.
            if self.get_player_file_name(path) in map(self.get_player_file_name, self.play_list):
                self.emit("same-name-event", path)
            else:
                self.play_list.append(path)
                self.emit("add-path", path)
                self.play_list_sum += 1
                
    def load_playlist(self, list_file_name):
        with open(list_file_name) as f:
            for i in f:
                self.add_play_file(i.strip("\n"))
       
    def save_playlist(self, list_file_name):
        with open(list_file_name, 'w') as f:
            for file in self.play_list:
                f.write(file + '\n')
                
    def clear_playlist(self):
        # clear play list.
        self.play_list = [] 
        # player list sum. 
        self.play_list_sum = 0 
        # player list number. 
        self.play_list_num = -1
        # random player num.
        self.random_num = 0        
        self.emit("clear-play-list", 1)
        
    def get_player_file_name(self, pathfile2):     
        file1, file2 = os.path.split(pathfile2)
        return os.path.splitext(file2)[0]
        
    def starting_state_bool(self):
        return self.state == STARTING_STATE
    
