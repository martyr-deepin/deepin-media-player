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

import random
import gtk
import os
import re
import fcntl
# import glib
import gobject
# import shutil
import subprocess
# from utils import *
from gio_format import format 
from ini import Config

# Get play widow ID.
def get_window_xid(widget):
    return widget.window.xid  

# Get ~ to play file path.
def get_home_path():
    return os.path.expanduser("~")

# Get play file length.
def get_length(file_path):
    '''Get media player length.'''    
    # cmd = "ffmpeg -i '%s' 2>&1 | grep 'Duration' | cut -d ' ' -f 4 | sed s/,//" % (file_path)
    cmd = "mplayer -vo null -ao null -frames 0 -identify '%s' 2>&1" % (file_path)
    fp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)    
    cmd_str = fp.communicate()[0]
    length_compile = re.compile(r"ID_LENGTH=([\d|\.]+)")
    try:
        length = length_compile.findall(cmd_str)[0]
    except:    
        
        length = 520
    # return (fp.stdout.read().split()[0])
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
            return None, None
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
        timeMin  = int(timeSec / 60)
        timeSec -= int(timeMin * 60)         
        
    if timeHour > 0:    
        # return str("%s时%s分%s秒"%(str(time_add_zero(timeHour)), 
        #                            str(time_add_zero(timeMin)), 
        #                            str(time_add_zero(timeSec))))
        return str("%s时%s分"%(str(time_add_zero(timeHour)), 
                                   str(time_add_zero(timeMin))))

    if timeMin > 0:
        return str("%s分%s秒"%(str(time_add_zero(timeMin)), 
                               str(time_add_zero(timeSec))))
    if timeSec > 0:
        return str("%s秒"%(str(time_add_zero(timeSec))))
    
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
            #[FilePlay]
            config.set("FilePlay", "video_file_open",                     1)
            config.set("FilePlay", "open_new_file_clear_play_list",       "True")
            config.set("FilePlay", "memory_up_close_player_file_postion", "True")
            config.set("FilePlay", "find_play_file_relation_file",        "False")
            config.set("FilePlay", "mouse_progressbar_show_preview",      "False")
            #[SystemSet]
            config.set("SystemSet", "minimize_pause_play", "False")            
            config.set("SystemSet", "font",                "文泉驿微米黑")
            config.set("SystemSet", "font_size",           "8")
            # config.set()
            # config.set()
            # config.set()
            #[PlayControl]
            config.set("PlayControl", "open_file_key",     "Ctrl + o")
            config.set("PlayControl", "open_file_dir_key", "Ctrl + f")
            config.set("PlayControl", "play_or_pause_key", "Space")
            config.set("PlayControl", "seek_key",          "Right")
            config.set("PlayControl", "back_key",          "Left")
            config.set("PlayControl", "full_key",          "Return")
            config.set("PlayControl", "pre_a_key",         "Page_Up")
            config.set("PlayControl", "next_a_key",        "Page_Down")
            config.set("PlayControl", "add_volume_key",    "Up")
            config.set("PlayControl", "sub_volume_key",    "Down")
            config.set("PlayControl", "mute_key",          "m")
            config.set("PlayControl", "concise_key",       "Shift + Return")
            #[OtherKey]
            config.set("OtherKey", "add_brightness_key",     "=")
            config.set("OtherKey", "sub_brightness_key",     "-")
            config.set("OtherKey", "inverse_rotation_key",   "w")
            config.set("OtherKey", "clockwise_key",          "e")
            config.set("OtherKey", "sort_image_key",         "Alt + a")
            config.set("OtherKey", "switch_audio_track_key", "Ctrl + Alt + o")
            config.set("OtherKey", "load_subtitle_key",      "Alt + o")
            config.set("OtherKey", "subtitle_delay_key",     "]")
            config.set("OtherKey", "subtitle_advance_key",   "[")
            config.set("OtherKey", "mouse_left_single_clicked", "暂停/播放")
            config.set("OtherKey", "mouse_left_double_clicked", "全屏")
            config.set("OtherKey", "mouse_wheel_event", "音量")
            #[SubtitleSet]
            config.set("SubtitleSet", "ai_load_subtitle", "True")
            config.set("SubtitleSet", "specific_location_search", "~/.config/deepin-media-player/subtitle")
            #[ScreenshotSet]
            config.set("ScreenshotSet", "save_clipboard", "False")
            config.set("ScreenshotSet", "save_file", "True")
            config.set("ScreenshotSet", "save_path", "~/.config/deepin-media-player/image")
            config.set("ScreenshotSet", "save_type", ".png")
            config.set("ScreenshotSet", "current_show_sort", "False")
            # save ini config.
            config.save()
            
        # Test config input.
        # config = Config(path + "/deepin_media_config.ini")    
        # print config.get("PlayControl", "open_file_key")
            
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
                    gobject.TYPE_NONE,(gobject.TYPE_INT,))
        }
    def __init__(self, xid = None):
        
        gobject.GObject.__init__(self)
        
        self.xid         = xid 
        self.mplayer_pid = 0
        self.state       = 0
        self.vide_bool   = False
        self.pause_bool  = False
        self.lenState    = 0
        self.path = ""
        
        self.timeHour    = 0
        self.timeMin     = 0
        self.timeSec     = 0
        
        self.lenNum      = 0
        self.posNum      = 0
        
        # player list.
        self.playList      = [] 
        # player list sum. 
        self.playListSum   = 0 
        # player list number. 
        self.playListNum   = -1
        # random player num.
        self.random_num = 0;
        
        self.volumebool = False
        self.volume     = 100
        # player state.
        # 0: single playing.      
        # 1: order playing.     
        # 2: random player.      
        # 3: single cycle player. 
        # 4: list recycle play. 
        self.playListState = 0 

        
    def play(self, path):
    
        self.path = path
        if not self.state:
            self.lenState = 1 
            # -input fil.. streme player.
            if self.xid:
                CMD = ['mplayer',
                       # '-input',
                       # 'file=/tmp/cmd',
                       '-vo',
                       'gl,2,x11',
                       # 'x11',
                       # 'vdpau:deint=2,vdpau,gl,x11',
                       # '-va',
                       # '',
                       '-zoom',
                       '-nokeepaspect',
                       '-osdlevel',
                       '0',
                       '-double',
                       '-slave',
                       '-quiet']
                       
                CMD.append('-wid')
                CMD.append('%s'%(str(self.xid)))
                CMD.append(path)
            else:
                CMD = ['mplayer',
                       '-double',
                       '-slave',
                       '-quiet', path]
                
            self.mpID = subprocess.Popen(CMD, 
                                         stdin  = subprocess.PIPE,
                                         stdout = subprocess.PIPE,
                                         stderr = subprocess.PIPE,
                                         shell  = False)
            
            self.mplayer_pid = self.mpID.pid
            (self.mplayerIn, self.mplayerOut) = (self.mpID.stdin, self.mpID.stdout)
            
            
                        
            fcntl.fcntl(self.mplayerOut, 
                        fcntl.F_SETFL, 
                        os.O_NONBLOCK)
            
            # get lenght size.
            self.getPosID = gobject.timeout_add(400, self.get_time_pos) 
            
                    
            # IO_HUP[Monitor the pipeline is disconnected].
            self.eofID = gobject.io_add_watch(self.mplayerOut, gobject.IO_HUP, self.mplayerEOF)
            self.state = 1                
            self.get_time_length()
            self.vide_bool = get_vide_flags(self.path)
            # emit play-start.
            gobject.timeout_add(250, self.emit_play_start_event)
            
    def emit_play_start_event(self):        
        self.setvolume(self.volume)
        if self.volumebool:
            self.nomute()
        self.emit("play-start", self.mplayer_pid)
        
        return False
    
    ## Cmd control ##    
    def cmd(self, cmdStr):
        '''Mplayer command'''
        try:
            self.mplayerIn.write(cmdStr)
            self.mplayerIn.flush()
        except StandardError, e:
            print 'command error %s' % (e)
        
  
    def get_time_length(self):
        '''Get the total length'''
        self.cmd('get_time_length\n')
        while True:
            try:
                line = self.mplayerOut.readline()
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
        if not self.lenState:
            if self.getLenID:
                self.stopGetLenID()
            
        self.cmd('get_time_pos\n')
        
        while True:
            try:
                line = self.mplayerOut.readline()
            except StandardError:
                break
                            
            if not line:
                break
        
            if line.startswith("ANS_TIME_POSITION"):
                posNum = int(float(line.replace("ANS_TIME_POSITION=", "")))
                if self.lenState:
                        self.getLenID = gobject.timeout_add(60, self.get_time_length)
                        self.lenState = 0
                if posNum > 0:
                    self.posNum = posNum                   
                    # Init Hour, Min, Sec.
                    self.timeHour = 0
                    self.timeMin  = 0
                    self.timeSec  = 0
                    self.time(self.posNum)  
                    # Test time output.
                    #print '%s:%s:%s' % (self.timeHour,self.timeMin,self.timeSec) 
                    self.emit("get-time-pos",int(self.posNum))
                    
        return True

    ## Subtitle Control ##
    def subload(self, subFile):
        '''Load subtitle'''
        if self.state:
            self.cmd('sub_load %s\n' % (subFile))
            # self.cmd('sub_select 1\n')
            
    def subremove(self):
        '''Remove subtitle'''
        if self.state:
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
        if self.volume > 100:
            self.volume = 100

        if self.state:
            self.cmd('volume +%s 1\n' % str(self.volume))
        
    def decvolume(self, volumeNum):
        '''Decrease volume'''
        self.volume = volumeNum
        if self.volume < 0:
            self.volume = 0            
        if self.state:
            self.cmd('volume -%s 1\n' % str(self.volume))
            
    def setvolume(self, volumeNum):
        '''Add volume'''
        self.volume = volumeNum
        if self.volume > 100:
            self.volume = 100
        if self.volume < 0:    
            self.volume = 0
            
        if self.state:
            self.cmd('volume %s 1\n' % str(self.volume))
            
    def leftchannel(self):
        '''The left channel'''
        if self.state:
            self.cmd('af channels=2:2:0:1:1:1\n') 
    
    def rightchannel(self):
        '''The right channel'''
        if self.state:
            self.cmd('af channels=2:2:0:0:0:0\n')
    
    def normalchannel(self):
        '''Normal channel'''
        if self.state:
            self.cmd('af channels=2:2:0:0:1:1\n')
    
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
        if self.state:
            self.cmd('brightness +%s\n' % (briNum))
    
    def decbri(self, briNum):
        '''Decrease brightness'''
        if self.state:
            self.cmd('brightness -%s\n' % (briNum))
    
    # saturation.
    def addsat(self, satNum):
        '''Add saturation'''
        if self.state:
            self.cmd('saturation +%s\n' % (satNum))
            
    def decsat(self, satNum):
        '''Decrease saturation'''        
        if self.state:
            self.cmd('saturation -%s\n' % (satNum))
    
    # contrast. 
    def addcon(self, conNum):
        '''Add contrast'''
        if self.state:
            self.cmd('contrast +%s\n' % (conNum))    
            
    def deccon(self, conNum):
        '''Decrease contrast'''    
        if self.state:
            self.cmd('contrast -%s\n' % (conNum))
    
    # hue.
    def addhue(self, hueNum):
        '''Add hue'''
        if self.state:
            self.cmd('hue +%s\n' % (hueNum))        
    def dechue(self, hueNum):
        '''Decrease hue'''
        if self.state:
            self.cmd('hue -%s\n' % (hueNum))
    
            
    ## Play control ##   
    def playwinmax(self):
        '''Filed play window.'''
        # if self.state:
        self.cmd('vo_fullscreen\n')
            
    def seek(self, seekNum):        
        '''Set rate of progress'''
        if self.state:
            self.cmd('seek %d 2\n' % (seekNum))               
            
    def fseek(self, seekNum):
        '''Fast forward'''
        if self.state:
            self.cmd('seek +%d\n' % (seekNum))   
            self.emit("play-fseek", seekNum)
            
    def bseek(self, seekNum):
        '''backward'''
        if self.state:
            self.cmd('seek -%d\n' % (seekNum))
            self.emit("play-bseek", seekNum)
            
    def pause(self):
        if self.state  and not self.pause_bool:             
            self.pause_bool = True
            self.cmd('pause \n')

    def start_play(self):        
        if self.state and self.pause_bool:
            self.pause_bool = False
            self.cmd('pause \n')        
                    
    def quit(self):
        '''quit deepin media player.'''
        if self.state:
            
            self.stopGetPosID()
            self.stopEofID()
            # Send play end signal.
            self.emit("play-end", True)
            self.cmd('quit \n')
            self.state = 0
            try:
                self.mplayerIn.close()
                self.mplayerOut.close()
                self.mpID.kill()
            except StandardError:
                pass
                
    def stopEofID(self):
        if self.eofID:
            gobject.source_remove(self.eofID)
        self.eofID = 0
        
    def stopGetPosID(self):
        if self.getPosID:
            gobject.source_remove(self.getPosID)
        self.getPosID = 0
    
    def stopGetLenID(self):
        if self.getLenID:
            gobject.source_remove(self.getLenID)
        self.getLenID = 0
            
    def mplayerEOF(self, error, mplayer):
        '''Monitoring disconnect'''
        self.stopGetPosID()
        self.state = 0 
        self.mplayerIn, self.mplayerOut = None, None
        # Send play end signal.
        self.emit("play-end", True)
        if self.playListState == 0: 
            self.quit()
            return False
        
        self.playListNum += 1
        # Order play
        if self.playListState == 1:
            self.quit()
            if self.playListNum < self.playListSum:
                self.play(self.playList[self.playListNum])    
            else:
                self.playListNum -= 1
                return False
        # signal loop.    
        elif self.playListState == 3:            
            self.playListNum -= 1
            self.play(self.playList[self.playListNum])                
            
            
        self.playListNum = self.playListNum % self.playListSum
        
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
        self.playListNum = random.randint(0, self.playListSum - 1)
        for i in range(0,self.playListSum + self.playListSum):
            if self.playListNum == self.random_num:
                self.playListNum = random.randint(0, self.playListSum - 1)
            else:
                break           
        self.random_num = self.playListNum    
        self.quit()
        self.play(self.playList[self.playListNum])
            
    def list_recycle_paly(self):
        '''state : 4'''
        self.quit()
        self.play(self.playList[self.playListNum])
    
    def next_or_pre_state(self):    
        if self.playListState == 2: #Random player
            self.random_player()     
        elif self.playListState == 4 or self.playListState == 0 or self.playListState == 1 or self.playListState == 3:
            self.list_recycle_paly() 
            
    def next(self):
        if self.playListSum > 0:
            self.playListNum += 1
            # Start.
            self.playListNum = self.playListNum % self.playListSum
            self.next_or_pre_state()
            self.emit("play-next", 1)
        else:    
            self.emit("play-next", 0)
            
    def pre(self):
        if self.playListSum > 0:
            self.playListNum -= 1
            if self.playListNum < 0:
                self.playListNum = self.playListSum - 1
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
            self.timeMin  = int(self.timeSec / 60)
            self.timeSec -= int(self.timeMin * 60)         
            
        return self.timeHour, self.timeMin, self.timeSec    
    
    # Puase show image.
    def scrot(self, 
              scrot_pos, 
              scrot_save_path = get_home_path() + "/.config/deepin-media-player/image/scrot.png"):
        
        # ini config path.
        init_mplayer_config()
        #########################
        
        if self.state:
            # scrot image.
            os.system("cd ~/.config/deepin-media-player/buffer/ && mplayer -ss %s -noframedrop -nosound -vo png -frames 1 '%s'" % (scrot_pos, self.path))
            # modify image name or get image file.
            save_image_path = get_home_path() + "/.config/deepin-media-player/buffer/"        # save image buffer dir.    
            image_list = os.listdir(get_home_path() + "/.config/deepin-media-player/buffer/") # get dir all image.
            # print image_list
            for image_name in image_list:
                if "png" == image_name[-3:]:
                    # preview window show image.
                    os.system("cp '%s' '%s'" % (save_image_path + image_name, 
                                                scrot_save_path))
                    
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
            
        if self.state:
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
                        # image = pixbuf.scale_simple(120, 60, gtk.gdk.INTERP_BILINEAR)
                        pixbuf.save(scrot_save_path, "png")
                    except:    
                        break
                    break
                
            return True
        else:
            return False
        
        
        
    def findCurrentDir(self, path):
        '''Get all the files in the folder'''
        pathdir = os.listdir(path)       
        for pathfile in pathdir:
            pathfile2 = path + '/' + pathfile
            if os.path.isfile(pathfile2):
                if self.findFile(pathfile2):
                    self.playListSum += 1
                    self.playList.append(pathfile2)
                    
    def findDmp(self, pathfile2):                                
        file1, file2 = os.path.splitext(pathfile2)
        if file2.lower() in ['.dmp']:
            return True
        else:
            return False
        
    def findFile(self, pathfile2):
        return format.get_play_bool(pathfile2)
    
    def delPlayList(self, path): 
        '''Del a File'''
        self.playList.remove(path)            
        self.playListSum -= 1        
        
    def addPlayList(self, index, path):
        '''Add a File'''
        self.playList.intert(index, path)        
        self.playListSum += 1
        
    def addPlayFile(self, path):    
        if self.findFile(path): # play file.
            go = True           
            for i in self.playList:
                if self.get_player_file_name(i) == self.get_player_file_name(path):
                    go = False
                    break
            if path[0:4].lower() == "http":
                go = True
            if go:        
                self.playList.append(path)
                self.emit("add-path", path)
                self.playListSum += 1
        
    def loadPlayList(self, listFileName):
        f = open(listFileName)
        for i in f:            
            if self.findFile(i.strip("\n")):
                # self.playListSum += 1
                # self.playList.append(i.strip("\n"))
                self.addPlayFile(i.strip("\n"))
        f.close()
       
    def savePlayList(self, listFileName):
        f = open(listFileName, 'w')
        for i in self.playList:
            f.write(i + "\n")
        f.close()
                
    def clearPlayList(self):
        # for i in self.playList:
        #     self.playList.remove(i)
        # for i in self.playList:
        #     self.playList.remove(i)
        # clear play list.
        self.playList      = [] 
        # player list sum. 
        self.playListSum   = 0 
        # player list number. 
        self.playListNum   = -1
        # random player num.
        self.random_num = 0        
        self.emit("clear-play-list", 1)
        

    def get_player_file_name(self, pathfile2):     
        file1, file2 = os.path.split(pathfile2)
        return os.path.splitext(file2)[0]
       
