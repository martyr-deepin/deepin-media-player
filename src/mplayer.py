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
from locales import _
import random
import gtk
import os
import re
import fcntl
import gobject
import subprocess
from gio_format import format 
from ini import Config

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
    cmd = "mplayer -vo null -ao null -frames 0 -identify '%s' 2>&1" % (file_path)
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
        if get_vide_flags(file_path):
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
    timeSec = int(float(length))
    timeHour = 0
    timeMin = 0
    
    if timeSec >= 3600:
        timeHour = int(timeSec / 3600)
        timeSec -= int(timeHour * 3600)
        
    if timeSec >= 60:
        timeMin = int(timeSec / 60)
        timeSec -= int(timeMin * 60)         
        
    return str("%s:%s:%s"%(str(time_add_zero(timeHour)), 
                           str(time_add_zero(timeMin)), 
                           str(time_add_zero(timeSec))))
    
def time_add_zero(time_to):    
    if 0 <= time_to <= 9:
        time_to = "0" + str(time_to)
    return str(time_to)
        
def init_mplayer_config():
    # create .config.
    path = get_home_path() + "/.config"
    if not os.path.exists(path):
        os.mkdir(path)
    
    # create deepin-me...    
    path += "/deepin-media-player"    
    if not os.path.exists(path):
        os.mkdir(path)
    
    # create buffer file.
    if not os.path.exists(path + "/subtitle"):
        os.mkdir(path + "/subtitle")
    
    # create config.ini.    
    if not os.path.exists(path + "/config.ini"):
        fp = open(path + "/config.ini", "a")
        fp.close()
        
    if not os.path.exists(path + "/deepin_media_config.ini"):
        fp = open(path + "/deepin_media_config.ini", "a")
        fp.close()            
        # Init config.ini            
        config = Config(path + "/deepin_media_config.ini")
        # Init window.
        config.set("Window", "init_window", "True")
        
        #[FilePlay]
        for argv, value in ([
                ("video_file_open",                          2),
                ("open_new_file_clear_play_list",       "True"),
                ("memory_up_close_player_file_postion", "True"),
                ("find_play_file_relation_file",        "False"),
                ("mouse_progressbar_show_preview",      "False")
                ]):
            config.set("FilePlay", argv, value)
            
        #[SystemSet]
        for argv, value in ([
                ("minimize_pause_play", "False"),
                ("font",                "文泉驿微米黑"),
                ("font_size",           "16")
                ]):
            config.set("SystemSet", argv, value)
            
        #[PlayControl]
        for argv, value in ([
                ("play_control_bool", "True"),
                ("open_file_key",     "Ctrl + o"),
                ("open_file_dir_key", "Ctrl + f"),
                ("play_or_pause_key", "Space"),
                ("seek_key",          "Right"),
                ("back_key",          "Left"),
                ("full_key",          "Return"),
                ("pre_a_key",         "Page_Up"),
                ("next_a_key",        "Page_Down"),
                ("add_volume_key",    "Up"),
                ("sub_volume_key",    "Down"),
                ("mute_key",          "m"),
                ("concise_key",       "Shift + Return")
                ]):
            config.set("PlayControl", argv, value)
            
        #[OtherKey]
        for argv, value in ([
                ("other_key_bool",         "True"),
                ("add_brightness_key",     "="),
                ("sub_brightness_key",     "-"),
                ("inverse_rotation_key",   "w"),
                ("clockwise_key",          "e"),
                ("sort_image_key",         "Alt + a"),
                ("switch_audio_track_key", _("Disabled")),
                ("load_subtitle_key",      "Alt + o"),
                ("subtitle_delay_key",     "]"),
                ("subtitle_advance_key",   "["),
                ("mouse_left_single_clicked", _("Pause/Play")),
                ("mouse_left_double_clicked", _("Full Screen")),
                ("mouse_wheel_event", _("Volumn")),
                ]):
            config.set("OtherKey", argv, value)

        #[SubtitleSet]
        for argv, value in ([
                ("ai_load_subtitle", "True"),
                ("specific_location_search", "~/.config/deepin-media-player/subtitle")
                ]):
            config.set("SubtitleSet", argv, value)
        
        #[ScreenshotSet]
        for argv, value in ([
                ("save_clipboard", "False"),
                ("save_file", "True"),
                ("save_path", "~/.config/deepin-media-player/image"),
                ("save_type", ".png"),
                ("current_show_sort", "False")
                ]):



            config.set("ScreenshotSet", argv, value)
            
        # save ini config.
        config.save()
                   
    # create buffer file.
    if not os.path.exists(path + "/buffer"):
        os.mkdir(path + "/buffer")
        
    # create save image.    
    if not os.path.exists(path + "/image"):
        os.mkdir(path + "/image")
        
    '''preview scrot image'''    
    # create preview image buffer.    
    if not os.path.exists("/tmp/buffer"):
        os.mkdir("/tmp/buffer")    
        
    # create save preview window image.    
    if not os.path.exists("/tmp/preview"):
        os.mkdir("/tmp/preview") 

        
def get_vide_flags(path):
    return format.get_video_bool(path)
            
        
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
        self.mplayer_pid = 0
        self.state = STOPING_STATE
        self.vide_bool = False
        self.pause_bool = False
        self.lenState = 0
        self.path = ""
        
        self.timeHour = 0
        self.timeMin = 0
        self.timeSec = 0
        
        self.lenNum = 0
        self.posNum = 0
        
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
        
    def play(self, path):
    
        self.path = path
        if not (self.state): # STOPING_STATE
            self.lenState = 1 
            # -input fil.. streme player.
            if self.xid:
                command = ['mplayer',
                           '-vo',
                           'gl,2,x11',
                           '-zoom',
                           '-nokeepaspect',
                           '-osdlevel',
                           '0',
                           '-double',
                           '-slave',
                           '-quiet']
                
                # If path is url, must be add option `-nocache`,
                # otherwise, mplayer cache process can't quit normally.
                if format.get_html_bool(self.path):
                    command += ['-nocache']
                       
                command.append('-wid')
                command.append('%s' % (str(self.xid)))
                command.append(path)
            else:
                command = ['mplayer',
                       '-double',
                       '-slave',
                       '-quiet', path]
                
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
            self.getLenID = gobject.timeout_add(60, self.get_time_length)
            # get pos size.
            self.getPosID = gobject.timeout_add(400, self.get_time_pos) 
                                
            # IO_HUP[Monitor the pipeline is disconnected].
            self.eofID = gobject.io_add_watch(self.mplayer_out, gobject.IO_HUP, self.mplayer_eof)
            self.state = STARTING_STATE
            self.vide_bool = get_vide_flags(self.path)
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
    def cmd(self, cmdStr):
        '''Mplayer command'''
        try:
            self.mplayer_in.write(cmdStr)
            self.mplayer_in.flush()
        except StandardError, e:
            print 'command error %s' % (e)
          
    def get_time_length(self):
        '''Get the total length'''
        self.cmd('get_time_length\n')
        while True:
            try:
                line = self.mplayer_out.readline()
            except StandardError:
                break
                            
            if not line:
                break   

            if line.startswith("ANS_LENGTH"):
                lenNum = int(float(line.replace("ANS_LENGTH=", "")))
                if lenNum > 0:
                    self.lenNum = lenNum               
                    self.emit("get-time-length",self.lenNum)
                    # print "mplayer:" + str(self.lenNum)
                    
        return True
                               
    def get_time_pos(self):
        '''Get the current playback progress'''
        # if not self.lenState:
        if self.getLenID:
            self.stop_get_len_id()
            
        self.cmd('get_time_pos\n')
        
        while True:
            try:
                line = self.mplayer_out.readline()
            except StandardError:
                break
                            
            if not line:
                break
        
            if line.startswith("ANS_TIME_POSITION"):
                posNum = int(float(line.replace("ANS_TIME_POSITION=", "")))
                
                if posNum > 0:
                    self.posNum = posNum                   
                    # Init Hour, Min, Sec.
                    self.timeHour = 0
                    self.timeMin = 0
                    self.timeSec = 0
                    self.time(self.posNum)  
                    self.emit("get-time-pos",int(self.posNum))
                    
        return True

    ## Subtitle Control ##
    def subload(self, subFile):
        '''Load subtitle'''
        if self.state == STARTING_STATE: # STARTING_STATE
            self.cmd('sub_load %s\n' % (subFile))
            self.cmd('sub_select 1\n')
            
    def subremove(self):
        '''Remove subtitle'''
        if self.state == STARTING_STATE:
            self.cmd('sub_remove\n')
            
    # subtitle alignment. # 0 top 1 center 2 bottom       
    # def sub_alignment_top(self):
    # def sub_alignment_center(self):
    # def sub_alignment_bottom(self):        
            
    # subtitle delay(+/-[abs]).
    # def sub_add_delay(self):       
    # def sub_sub_delay(self):    
            
    # subtitles load.
    # def sub_load(self, sub_file)
            
    # subtitle log.
    # def sub_log(self)
            
    # subtitle pos.    
    # def sub_pos(self)
            
    # subtitle remove(value).
    # def sub_remove(self, value)
            
    # subtitle select(value).  -1 close subtitle. 1 ... 2..3.select subtitle
    # def sub_select(self, value):
            
    # subtitle source(source).    
    # def sub_source(self):         
            
    # subtitle file(value).        
    # def sub_file(self, value):
            
    # subtitle vob(value).        
    # def sub_vob(self, value)        
            
    # subtitle demux(value).        
    # def sub_demux(self, value):        
            
    # subtitle scale(+/-[abs])
    # def sub_scale(self):                                
        
            
    ## Volume Control ##
    def addvolume(self, volumeNum):
        '''Add volume'''
        self.volume = volumeNum
        self.volume = min(self.volume, 100)
        
        if self.state == STARTING_STATE:
            self.cmd('volume +%s 1\n' % str(self.volume))
        
    def decvolume(self, volumeNum):
        '''Decrease volume'''
        self.volume = volumeNum
        self.volume = max(self.volume, 0)
        
        if self.state == STARTING_STATE:
            self.cmd('volume -%s 1\n' % str(self.volume))
            
    def setvolume(self, volumeNum):
        '''Add volume'''
        self.volume = volumeNum
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
        
        
    ## video Control ##
    # brightness.
    def addbri(self, briNum):
        '''Add brightness'''
        if self.state == STARTING_STATE:
            self.cmd('brightness +%s\n' % (briNum))
    
    def decbri(self, briNum):
        '''Decrease brightness'''
        if self.state == STARTING_STATE:
            self.cmd('brightness -%s\n' % (briNum))
    
    # saturation.
    def addsat(self, satNum):
        '''Add saturation'''
        if self.state == STARTING_STATE:
            self.cmd('saturation +%s\n' % (satNum))
            
    def decsat(self, satNum):
        '''Decrease saturation'''        
        if self.state == STARTING_STATE:
            self.cmd('saturation -%s\n' % (satNum))
    
    # contrast. 
    def addcon(self, conNum):
        '''Add contrast'''
        if self.state == STARTING_STATE:
            self.cmd('contrast +%s\n' % (conNum))    
            
    def deccon(self, conNum):
        '''Decrease contrast'''    
        if self.state == STARTING_STATE:
            self.cmd('contrast -%s\n' % (conNum))
    
    # hue.
    def addhue(self, hueNum):
        '''Add hue'''
        if self.state == STARTING_STATE:
            self.cmd('hue +%s\n' % (hueNum))        
    def dechue(self, hueNum):
        '''Decrease hue'''
        if self.state == STARTING_STATE:
            self.cmd('hue -%s\n' % (hueNum))
    
            
    ## Play control ##   
    def playwinmax(self):
        '''Filed play window.'''
        # if self.state:
        self.cmd('vo_fullscreen\n')
            
    def seek(self, seekNum):        
        '''Set rate of progress'''
        if self.state == STARTING_STATE:
            self.cmd('seek %d 2\n' % (seekNum))               
            
    def fseek(self, seekNum):
        '''Fast forward'''
        if self.state == STARTING_STATE:
            self.cmd('seek +%d\n' % (seekNum))   
            self.emit("play-fseek", seekNum)
            
    def bseek(self, seekNum):
        '''backward'''
        if self.state == STARTING_STATE:
            self.cmd('seek -%d\n' % (seekNum))
            self.emit("play-bseek", seekNum)
            
    def pause(self):
        if (self.state == STARTING_STATE) and (not self.pause_bool):             
            self.pause_bool = True
            self.cmd('pause \n')

    def start_play(self):        
        if (self.state == STARTING_STATE) and (self.pause_bool):
            self.pause_bool = False
            self.cmd('pause \n')        
                    
    def quit(self):
        '''quit deepin media player.'''
        if self.state == STARTING_STATE:
            
            self.stop_get_pos_id()
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
        if self.eofID:
            gobject.source_remove(self.eofID)
        self.eofID = 0
        
    def stop_get_pos_id(self):
        if self.getPosID:
            gobject.source_remove(self.getPosID)
        self.getPosID = 0
    
    def stop_get_len_id(self):
        if self.getLenID:
            gobject.source_remove(self.getLenID)
        self.getLenID = 0
            
    def mplayer_eof(self, error, mplayer):
        '''Monitoring disconnect'''
        self.stop_get_pos_id()
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
        self.timeSec = 0
        self.timeHour = 0
        self.timeMin = 0
        
        self.timeSec = int(sec)
        
        if self.timeSec >= 3600:
            self.timeHour = int(self.timeSec / 3600)
            self.timeSec -= int(self.timeHour * 3600)
        
        if self.timeSec >= 60:
            self.timeMin = int(self.timeSec / 60)
            self.timeSec -= int(self.timeMin * 60)         
            
        return self.timeHour, self.timeMin, self.timeSec    
    
    # Puase show image.
    def scrot(self, 
              scrot_pos, 
              scrot_save_path = get_home_path() + "/.config/deepin-media-player/image/scrot.png"):
        
        # ini config path.
        init_mplayer_config()
        #########################
        
        if self.state == STARTING_STATE:
            # scrot image.
            scrot_command = "cd ~/.config/deepin-media-player/buffer/ && mplayer -ss %s -noframedrop -nosound -vo png -frames 1 '%s'" % (scrot_pos, self.path)
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
            os.system("cd /tmp/buffer/ && mplayer -ss %s -noframedrop -nosound -vo png -frames 1 '%s'" % (scrot_pos, self.path))
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
                    
    def find_dmp(self, pathfile2):                                
        return pathfile2.lower().endswith(".dmp")
        
    def find_file(self, pathfile2):
        return format.get_play_bool(pathfile2)
    
    def del_playlist(self, path): 
        '''Del a File'''
        self.play_list.remove(path)            
        self.play_list_sum -= 1        
                
    def add_play_file(self, path):    
        if self.find_file(path): # play file.
            go = True           
            for i in self.play_list:
                if self.get_player_file_name(i) == self.get_player_file_name(path):
                    self.emit("same-name-event", i)
                    go = False
                    break
            if go:        
                self.play_list.append(path)
                self.emit("add-path", path)
                self.play_list_sum += 1
        
    def load_playlist(self, list_file_name):
        f = open(list_file_name)
        for i in f:            
            self.add_play_file(i.strip("\n"))
        f.close()
       
    def save_playlist(self, list_file_name):
        f = open(list_file_name, 'w')
        for file in self.play_list:
            f.write(file + "\n")
        f.close()
                
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
    
