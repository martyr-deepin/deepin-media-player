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
import glib
import gobject
import shutil
import subprocess

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
                        gobject.TYPE_NONE,(gobject.TYPE_INT,))
        }
    def __init__(self, xid = None):
        
        gobject.GObject.__init__(self)
        
        self.xid         = xid 
        self.state       = 0
        self.lenState    = 0
        
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
            
            if self.xid:
                CMD = ['mplayer',
                       '-osdlevel',
                       '0',
                       '-double',
                       '-slave',
                       '-quiet',
                       '-wid',
                       str(self.xid), path]
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
            self.emit("play-start",False)
            (self.mplayerIn, self.mplayerOut) = (self.mpID.stdin, self.mpID.stdout)
            fcntl.fcntl(self.mplayerOut, 
                        fcntl.F_SETFL, 
                        os.O_NONBLOCK)
            # get lenght size.
            self.getPosID = gobject.timeout_add(100, self.get_time_pos) 
            
                    
            # IO_HUP[Monitor the pipeline is disconnected].
            self.eofID = gobject.io_add_watch(self.mplayerOut, gobject.IO_HUP, self.mplayerEOF)
            self.state = 1                
            self.get_time_length()
            
          
    ## Cmd control ##    
    def cmd(self, cmdStr):
        '''Mplayer command'''
        try:
            self.mplayerIn.write(cmdStr)
            self.mplayerIn.flush()
        except StandardError:
            print 'command error!!'
        
  
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
                    print self.lenNum
                    
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
                        self.getLenID = gobject.timeout_add(10, self.get_time_length)
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
            self.cmd('sub_select 1\n')
            
    def subremove(self):
        '''Remove subtitle'''
        if self.state:
            self.cmd('sub_remove\n')
                    
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
        self.cmd('mute 0\n')
    
    def nomute(self):
        '''Active mute'''
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
        if self.state:
            self.cmd('vo_fullscreen\n')
            
    def fseek(self, seekNum):
        '''Fast forward'''
        if self.state:
            self.cmd('seek +%d\n' % (seekNum))   
    
    def bseek(self, seekNum):
        '''backward'''
        if self.state:
            self.cmd('seek -%d\n' % (seekNum))
             
    def pause(self):
        if self.state: 
            self.cmd('pause\n')
      
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
        if self.playListSum >= 0:
            self.playListNum += 1
            # Start.
            self.playListNum = self.playListNum % self.playListSum
            self.next_or_pre_state()
            
    def pre(self):
        if self.playListSum >= 0:
            self.playListNum -= 1
            if self.playListNum < 0:
                self.playListNum = self.playListSum - 1
            self.next_or_pre_state()
                
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
    
    def scrot(self, scrotSec, scrotPath="/home/long/.mplayer"):
        if self.state and os.path.exists(scrotPath):
            os.system("mplayer -ss %s -noframedrop -nosound -vo png -frames 1 '%s'" % (scrotSec, self.path))
            # copy image file to The specified directory.
            file_list = os.listdir(".")
            for file in file_list:
                if os.path.isfile(file):
                    fp = open(file, "r")
                    f = fp.read(4)
                    if f[1:] == "PNG":
                        os.system("cp %s %s" % (file, scrotPath))
                    fp.close()                    
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
                                    
    def findFile(self, pathfile2):
        file1, file2 = os.path.splitext(pathfile2)
        if file2 in ['.mkv','.mp3','.mp4','.rmvb','.avi','.wmv','.3gp','rm']:
            return True
        else:
            return False
    
    def delPlayList(self, path): 
        '''Del a File'''
        self.playList.remove(path)
        self.playListSum -= 1
        
    def addPlayList(self, index, path):
        '''Add a File'''
        self.playList.intert(index, path)
        self.playListSum += 1
        
    def addPlayFile(self, path):    
        self.playList.append(path)
        self.playListSum += 1
        
    def loadPlayList(self, listFileName):
        f = open(listFileName)
        for i in f:
            self.playListSum += 1
            self.playList.append(i.strip("\n"))
        f.close()
       
    def savePlayList(self, listFileName):
        f = open(listFileName, 'w')
        for i in self.playList:
            f.write(i + "\n")
        f.close()
                
    def clearPlayList(self):
        for i in self.playList:
            self.playList.remove(i)
        for i in self.playList:
            self.playList.remove(i)
        
# get play widow ID.
def get_window_xid(widget):
    return widget.window.xid  

