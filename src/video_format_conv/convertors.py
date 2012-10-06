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

import gobject
import gst
import codecfinder
import glib
import presets
import os

NULL  = gst.STATE_NULL
PAUSE = gst.STATE_PAUSED
PLAYING = gst.STATE_PLAYING

# 保存视频格式转化的各个信息
class FormatInfo: 
    def __init__(self):
        self.FILECHOSEN = ""
        self.FILENAME = ""
        self.DESTDIR = ""
        self.CONTAINERCHOICE = ""
        self.AUDIOCODECVALUE = ""
        self.VIDEOCODECVALUE = ""
        self.PRESET = ""
        self.OHEIGHT = ""
        self.OWIDTH = ""
        self.FRATENUM = ""
        self.FRATEDEN = ""
        self.ACHANNELS = ""
        self.MULTIPASS = ""
        self.PASSCOUNTER = ""
        self.OUTPUTNAME = ""
        self.TIMESTAMP = ""
        self.ROTATIONVALUE = ""
        self.AUDIOPASSTOGGLE = ""
        self.VIDEOPASSTOGGLE = ""
        self.INTERLACED = ""
        self.INPUTVIDEOCAP = ""        
        #
        
class Convertors(gobject.GObject):
    __gsignals__ = {
        'convertors-update-progressbar' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        'convertors-eos' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        'convertors-error' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))
            }    
    def __init__(self, _format_info):
        gobject.GObject.__init__(self)
        #
        self.__format_info = _format_info
        self.container = self.__format_info.CONTAINERCHOICE
        self.audiocaps = self.__format_info.AUDIOCODECVALUE
        if False != self.container:
            self.containercaps = gst.Caps(codecfinder.containermap(self.__format_info.CONTAINERCHOICE))
        else:    
            if self.audiocaps.intersect(gst.Caps("audio/mpeg, mpegversion=1, layer=3")):
                self.containercaps = gst.Caps("application/x-id3")
                self.container = gst.Caps("application/x-id3")
        #    
        gst.preset_set_app_dir("./presets/")
        #
        self.stoptoggle = False
        self.videocaps = self.__format_info.VIDEOCODECVALUE
        
        self.audiopasstoggle = self.__format_info.AUDIOPASSTOGGLE
        self.interlaced = self.__format_info.INTERLACED
        self.videopasstoggle = self.__format_info.VIDEOPASSTOGGLE
        self.inputvideocaps = self.__format_info.INPUTVIDEOCAPS
        self.doaudio= False
        self.preset = self.__format_info.PRESET
        self.oheight = self.__format_info.OHEIGHT
        self.owidth = self.__format_info.OWIDTH
        self.fratenum = self.__format_info.FRATENUM
        self.frateden = self.__format_info.FRATEDEN
        self.achannels = self.__format_info.ACHANNELS
        self.blackborderflag = False
        self.multipass = self.__format_info.MULTIPASS
        self.passcounter = self.__format_info.PASSCOUNTER
        self.outputfilename = self.__format_info.OUTPUTNAME
        self.timestamp = self.__format_info.TIMESTAMP
        self.rotationvalue = int(self.__format_info.ROTATIONVALUE)
        self.vbox = {}
        
        if self.rotationvalue == 1 or self.rotationvalue == 3:
           nwidth = self.oheight
           nheight = self.owidth
           self.oheight = nheight
           self.owidth = nwidth 
           
        if self.multipass != False:
            self.cachefile = (str (glib.get_user_cache_dir()) + "/" + \
                                  "multipass-cache-file" + self.timestamp + ".log")   
                      
        if self.preset != "nopreset":
           height, width, num, denom, pixelaspectratio = self.provide_presets()
           for acap in self.audiocaps:
               acap["channels"] = self.channels
           for vcap in self.videocaps:
               vcap["height"] = int(height)
               vcap["width"] = int(width)
               vcap["framerate"] = gst.Fraction(num, denom)
               if pixelaspectratio != gst.Fraction(0, 0):
                   vcap["pixel-aspect-ratio"] = pixelaspectratio             
                                      
        self.pipeline = gst.Pipeline("Convertors")
        self.pipeline.set_state(PAUSE)
        
        self.uridecoder = gst.element_make_factor("uridecoder", "uridecoder")
        self.uridecoder.set_property("uri", self.__format_info.FILECHOSEN)        
        self.uridecoder.connect("pad-add", self.OnDynamicPad)
        
        audiopreset=None
        videopreset=None
        
        if "nopreset" != self.preset:
            audiopreset="Quality Normal"
            videopreset="Quality Normal"
            
        if False == self.container:
            if self.audiocaps.intersect(gst.Caps("audio/mpeg, mpegversion=4")):
                self.audiocaps=gst.Caps("audio/mpeg, mpegversion=4, stream-format=adts")
            elif self.audiocaps.intersect(gst.Caps("audio/x-flac")):
                self.audiocaps=gst.Caps("audio/x-flac")
        else:    
            self.encodebinprofile = gst.pbutils.EncodingContainerProfile ("containerformat", None , self.containercaps, None)
        if False != self.audiocaps:
           if False == self.container:
               self.encodebinprofile = gst.pbutils.EncodingAudioProfile (gst.Caps(self.audiocaps), audiopreset, gst.caps_new_any(), 0)
           else:
               self.audioprofile = gst.pbutils.EncodingAudioProfile (gst.Caps(self.audiocaps), audiopreset, gst.caps_new_any(), 0)
               self.encodebinprofile.add_profile(self.audioprofile)
               
        if "novid" != self.videocaps:
            if (False != self.videocaps):
                self.videoprofile = gst.pbutils.EncodingVideoProfile (gst.Caps(self.videocaps), videopreset, gst.caps_new_any(), 0)
                self.encodebinprofile.add_profile(self.videoprofile)
                
        self.encodebin = gst.element_factory_make ("encodebin", None)
        self.encodebin.set_property("profile", self.encodebinprofile)
        self.encodebin.set_property("avoid-reencoding", True)
        self.pipeline.add(self.encodebin)
        self.encodebin.set_state(gst.STATE_PAUSEDTE_AUSED)

        if False == self.videopasstoggle:
            if False != self.container:
                self.videoflipper = gst.element_factory_make("videoflip")
                self.videoflipper.set_property("method", self.rotationvalue)
                self.pipeline.add(self.videoflipper)

                self.deinterlacer = gst.element_factory_make("deinterlace")
                self.pipeline.add(self.deinterlacer)

                self.colorspaceconversion = gst.element_factory_make("ffmpegcolorspace")
                self.pipeline.add(self.colorspaceconversion)
                       
                self.deinterlacer.link(self.colorspaceconversion)
                self.colorspaceconversion.link(self.videoflipper)
                self.deinterlacer.set_state(PAUSE)
                self.colorspaceconversion.set_state(PAUSE)
                self.videoflipper.set_state(PAUSE)

        self.remuxcaps = gst.Caps()
        if self.audiopasstoggle:
            self.remuxcaps.append(self.audiocaps)
        if self.videopasstoggle:
            self.remuxcaps.append(self.videocaps)
        if self.audiopasstoggle and not self.videopasstoggle:
            self.remuxcaps.append_structure(gst.Structure("video/x-raw-rgb"))
            self.remuxcaps.append_structure(gst.Structure("video/x-raw-yuv"))
        if self.videopasstoggle and not self.audiopasstoggle:
            self.remuxcaps.append_structure(gst.Structure("audio/x-raw-float"))
            self.remuxcaps.append_structure(gst.Structure("audio/x-raw-int"))
        if "novid" == self.videocaps:
            if None != self.inputvideocaps:
                self.remuxcaps.append(self.inputvideocaps)
                self.remuxcaps.append_structure(gst.Structure("audio/x-raw-float"))
                self.remuxcaps.append_structure(gst.Structure("audio/x-raw-int"))

        if (self.audiopasstoggle) or (self.videopasstoggle) or (self.videocaps=="novid"):
            self.uridecoder.set_property("caps", self.remuxcaps)

        self.pipeline.add(self.uridecoder)

        self.transcodefileoutput = gst.element_factory_make("filesink", "fileoutput")
        temp_destdir = self.__format_info.DESTDIR + "/" + self.outputfilename
        self.transcodefileoutput.set_property("location", (temp_destdir))
        self.pipeline.add(self.transcodefileoutput)
        self.encodebin.link(self.transcodefileoutput)

        self.uridecoder.set_state(PAUSE)  
        self.BusMessages = self.BusWatcher()
        self.uridecoder.connect("no-more-pads", self.noMorePads)            
                    
    def reverse_lookup(self, v):    
        for k in codecfinder.codecmap:
            if codecfinder.codecmap[k] == v:
                return k
                    
    def provide_presets(self):
        devices = presets.get()
        device = devices[self.preset]
        preset = device.presets["Normal"]

        self.audiocaps=gst.Caps(preset.acodec.name)
        self.videocaps=gst.Caps(preset.vcodec.name)

        border = preset.vcodec.border
        if border == "Y":
            self.blackborderflag = True
        else:
            self.blackborderflag = False

        chanmin, chanmax = preset.acodec.channels
        if int(self.achannels) < int(chanmax):
            if int(self.achannels) > int(chanmin): 
                self.channels = int(self.achannels)
            else:
                self.channels = int(chanmin)
        else:
            self.channels = int(chanmax)

        wmin, wmax  =  preset.vcodec.width
        hmin, hmax = preset.vcodec.height
        width, height = self.owidth, self.oheight

        pixelaspectratio = preset.vcodec.aspectratio[0]

        if self.owidth > wmax:
            width = wmax
            height = int((float(wmax) / self.owidth) * self.oheight)
        if height > hmax:
            height = hmax
            width = int((float(hmax) / self.oheight) * self.owidth)

        if width % 2:
            width += 1
        if height % 2:
            height += 1

        if self.blackborderflag == True:
            width=wmax
            height=hmax
           
        rmin = preset.vcodec.rate[0].num / float(preset.vcodec.rate[0].denom)
        rmax = preset.vcodec.rate[1].num / float(preset.vcodec.rate[1].denom)
        rmaxtest = preset.vcodec.rate[1]
        orate = self.fratenum / self.frateden 
        
        if orate > rmax:
            num = preset.vcodec.rate[1].num
            denom = preset.vcodec.rate[1].denom
        elif orate < rmin:
            num = preset.vcodec.rate[0].num
            denom = preset.vcodec.rate[0].denom
        else:
            num = self.fratenum
            denom = self.frateden

        return height, width, num, denom, pixelaspectratio            

    def noMorePads(self, dbin):
        if (self.multipass == False) or (self.passcounter == int(0)):
            self.transcodefileoutput.set_state(gst.STATE_PAUSED)
        glib.idle_add(self.idlePlay)    
       
    def idlePlay(self):
        self.Pipeline("playing")
        return False        
   
    def BusWatcher(self):
       bus = self.pipeline.get_bus()
       bus.add_watch(self.on_message)    
       
    def on_message(self, bus, message): 
        __type = message.type
        if gst.MESSAGE_EOS == __type: # 结束
            if self.passcounter == 0:
                if os.access(self.cachefile, os.F_OK):
                    os.remove(self.cachefile)
            self.emit("convertors-eos")
            self.player.set_state(NULL)            
        elif gst.MESSAGE_ERROR == __type: # 错误信息
            (err, debug) = message.parse_error()
            gst.DEBUG_BIN_TO_DOT_FILE (self.pipeline, gst.DEBUG_GRAPH_SHOW_ALL, 'transmageddon.dot')
            self.emit("convertors-error", err.message) # 发送错误信息给GUI界面.
        elif gst.MESSAGE_ASYNC_DONE == __type: # 更新进度条
            self.emit("convertors-update-progressbar") # 发送更新信号给GUI界面更新进度条.         
        elif gst.MESSAGE_APPLICATION:    
            self.pipeline.set_state(NULL)
            self.pipeline.remove(self.uridecoder)
        return True    
    
    def OnDynamicPad(self, uridecodebin, src_pad):
       origin = src_pad.get_caps()
       if (False == self.container):
           a =  origin.to_string()
           if a.startswith("audio/"):
               sinkpad = self.encodebin.get_static_pad("audio_0")
               src_pad.link(sinkpad)
       else:
           if self.videocaps == "novid":
               c = origin.to_string()
               if c.startswith("audio/"):
                   sinkpad = self.encodebin.emit("request-pad", origin)
                   d = sinkpad.get_caps().to_string()
                   if d.startswith("audio/"):
                       src_pad.link(sinkpad)
           else:
               c = origin.to_string()
               if not c.startswith("text/"):
                   if not (c.startswith("video/") and (self.videocaps == False)):
                       sinkpad = self.encodebin.emit("request-pad", origin)
               if c.startswith("audio/"):
                   src_pad.link(sinkpad)
               elif ((c.startswith("video/") or c.startswith("image/")) and (self.videocaps != False)):
                   if self.videopasstoggle==False:
                       src_pad.link(self.deinterlacer.get_static_pad("sink"))
                       self.videoflipper.get_static_pad("src").link(sinkpad)
                       
                   else:
                       srccaps=src_pad.get_caps()
                       srcstring=srccaps.to_string()

                       sinkcaps=sinkpad.get_caps()
                       sinkstring=sinkcaps.to_string()

                       src_pad.link(sinkpad)

       GstTagSetterType = gobject.type_from_name("GstTagSetter")
       tag_setting_element=self.encodebin.get_by_interface(GstTagSetterType)
       if None != tag_setting_element:
           taglist=gst.TagList()
           taglist[gst.TAG_ENCODER] = "Transmageddon encoder"
           
           taglist[gst.TAG_APPLICATION_NAME] = "Transmageddon transcoder"
           tag_setting_element.merge_tags(taglist, gst.TAG_MERGE_APPEND)

    def Pipeline (self, state):
        if ("playing") == state:
            self.pipeline.set_state(PLAYING)
        elif ("null") == state:
            self.pipeline.set_state(NULL)            
