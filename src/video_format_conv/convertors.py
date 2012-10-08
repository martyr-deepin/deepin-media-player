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
import gst.pbutils
import os
import glib

containermap = { 'Ogg' : "application/ogg",
                 'Matroska' : "video/x-matroska",
                 'MXF' : "application/mxf",
                 'AVI' : "video/x-msvideo", 
                 'Quicktime' : "video/quicktime,variant=apple",
                 'MPEG4' : "video/quicktime,variant=iso",
                 'MPEG PS' : "video/mpeg,mpegversion=2,systemstream=true",
                 'MPEG TS' : "video/mpegts,systemstream=true,packetsize=188",
                 'AVCHD/BD' : "video/mpegts,systemstream=true,packetsize=192",
                 'FLV' : "video/x-flv",
                 '3GPP' : "video/quicktime,variant=3gpp",
                 'ASF' : "video/x-ms-asf, parsed=true",
                 'WebM' : "video/webm",
                 'No container' : False}

csuffixmap =   { 'Ogg' : ".ogg", 
                 'Matroska' : ".mkv", 
                 'MXF' : ".mxf", 
                 'AVI' : ".avi", 
                 'Quicktime' : ".mov", 
                 'MPEG4' : ".mp4", 
                 'MPEG PS' : ".mpg", 
                 'MPEG TS' : ".ts", 
                 'AVCHD/BD' : ".m2ts", 
                 'FLV' : ".flv", 
                 '3GPP' : ".3gp",
                 'ASF' : ".asf", 
                 'WebM' : ".webm", 
                 'No container' : ".null" }

audiosuffixmap =   { 'Ogg' : ".ogg", 
                     'Matroska' : ".mkv", 
                     'MXF' : ".mxf", 
                     'AVI' : ".avi", 
                     'Quicktime' : ".m4a",
                     'MPEG4' : ".mp4",     
                     'MPEG PS' : ".mpg", 
                     'MPEG TS' : ".ts", 
                     'FLV' : ".flv", 
                     '3GPP' : ".3gp", 
                     'ASF' : ".wma", 
                     'WebM' : ".webm" }

nocontainersuffixmap = {
    'audio/mpeg, mpegversion=(int)1, layer=(int)3' : ".mp3", 
    'audio/mpeg, mpegversion=(int)4, stream-format=(string)adts' : ".aac", 
    'audio/x-flac' : ".flac" }

codecmap = { 'Vorbis' : "audio/x-vorbis", 
             'FLAC' : "audio/x-flac", 
             'mp3' : "audio/mpeg, mpegversion=(int)1, layer=(int)3", 
             'AAC' : "audio/mpeg,mpegversion=4", 
             'AC3' : "audio/x-ac3", 
             'Speex' : "audio/x-speex",
             'Celt Ultra' : "audio/x-celt", 
             'ALAC' : "audio/x-alac", 
             'Windows Media Audio 2' : "audio/x-wma, wmaversion=(int)2", 
             'Theora' : "video/x-theora", 
             'Dirac' : "video/x-dirac", 
             'H264' : "video/x-h264", 
             'MPEG2' : "video/mpeg,mpegversion=2,systemstream=false", 
             'MPEG4' : "video/mpeg,mpegversion=4", 
             'xvid' : "video/x-xvid", 
             'Windows Media Video 2' : "video/x-wmv,wmvversion=2", 
             'dnxhd' : "video/x-dnxhd", 
             'divx5' : "video/x-divx,divxversion=5", 
             'divx4' : "video/x-divx,divxversion=4", 
             'AMR-NB' : "audio/AMR", 
             'H263+' : "video/x-h263,variant=itu,h263version=h263p", 
             'On2 vp8' : "video/x-vp8", 
             'mp2' : "audio/mpeg,mpegversion=(int)1, layer=(int)2", 
             'MPEG1' : "video/mpeg,mpegversion=(int)1,systemstream=false"}

gobject.threads_init()

NULL  = gst.STATE_NULL
PAUSE = gst.STATE_PAUSED
PLAYING = gst.STATE_PLAYING

# 保存视频格式转化的各个信息
class FormatInfo: 
    def __init__(self):
        self.filechosen = "" # FILECHOSEN
        self.outputfilename = "" # OUTPUTNAME
        self.containerchoice = "" #CONTAINERCHOICE // 视频格式(.avi | .ogg | .rmvb | .flv)
        self.videocaps = ""
        
        self.FILENAME = ""
        # self.DESTDIR = ""
        
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
        # create pipeline.
        self.pipeline = gst.Pipeline("pipeline")
        
        audiopreset=None
        videopreset=None
        # get video format to containercaps.
        self.containercaps = gst.Caps(containermap[self.__format_info.containerchoice])
        self.encodebinprofile = gst.pbutils.EncodingContainerProfile("containerformat", None , self.containercaps, None)
        self.audiocaps = gst.Caps("audio/x-flac")
        self.audioprofile = gst.pbutils.EncodingAudioProfile(gst.Caps(self.audiocaps), audiopreset, gst.caps_new_any(), 0)
        self.videoprofile = gst.pbutils.EncodingVideoProfile(gst.Caps(self.__format_info.videocaps), videopreset, gst.caps_new_any(), 0)
        self.encodebinprofile.add_profile(self.audioprofile)
        self.encodebinprofile.add_profile(self.videoprofile)
        
        # create element factory.
        self.uridecoder = gst.element_factory_make("uridecodebin", "uridecoder")
        self.encodebin = gst.element_factory_make("encodebin", None)
        self.videoflipper = gst.element_factory_make("videoflip")                
        self.deinterlacer = gst.element_factory_make("deinterlace")                
        self.colorspaceconversion = gst.element_factory_make("ffmpegcolorspace")        
        self.fileoutput = gst.element_factory_make("filesink", "fileoutput")
               
        # set property.
        self.uridecoder.set_property("uri", self.__format_info.filechosen)
        self.encodebin.set_property("profile", self.encodebinprofile) # set profile encodebinprofile.
        self.encodebin.set_property("avoid-reencoding", True)
        self.fileoutput.set_property("location", self.__format_info.outputfilename)
        
        # create Caps.
        self.remuxcaps = gst.Caps()        
        # self.remuxcaps append append_structure        
        
        self.uridecoder.set_property("caps", self.remuxcaps)
                
        # pipeline add element factory.
        self.pipeline.add(self.uridecoder)
        self.pipeline.add(self.encodebin)
        self.pipeline.add(self.videoflipper)
        self.pipeline.add(self.deinterlacer)
        self.pipeline.add(self.colorspaceconversion) 
        self.pipeline.add(self.fileoutput)
        
        # link.
        self.encodebin.link(self.fileoutput)
        self.deinterlacer.link(self.colorspaceconversion)
        self.colorspaceconversion.link(self.videoflipper)
        
        self.pipeline.set_state(gst.STATE_PAUSED)
        self.encodebin.set_state(gst.STATE_PAUSED)
        self.deinterlacer.set_state(gst.STATE_PAUSED)
        self.colorspaceconversion.set_state(gst.STATE_PAUSED)
        self.videoflipper.set_state(gst.STATE_PAUSED)
        self.uridecoder.set_state(gst.STATE_PAUSED)
        
        # connect bus message.
        bus = self.pipeline.get_bus()
        bus.add_watch(self.on_message)        
                
        self.uridecoder.connect("pad-added", self.OnDynamicPad)
        self.uridecoder.connect("no-more-pads", self.noMorePads)
        
    def on_message(self, bus, message):
        __type = message.type
        
        print "on_message function.................", __type
        
        if gst.MESSAGE_EOS == __type: # 结束
            if self.passcounter == 0:
                if os.access(self.cachefile, os.F_OK):
                    os.remove(self.cachefile)
            self.emit("convertors-eos")
            self.player.set_state(NULL)
        elif gst.MESSAGE_ERROR == __type: # 错误信息
            (err, debug) = message.parse_error()
            # gst.DEBUG_BIN_TO_DOT_FILE (self.pipeline, gst.DEBUG_GRAPH_SHOW_ALL, 'convertors.dot')
            self.emit("convertors-error", err.message) # 发送错误信息给GUI界面.
        elif gst.MESSAGE_ASYNC_DONE == __type: # 更新进度条
            self.emit("convertors-update-progressbar") # 发送更新信号给GUI界面更新进度条.
        elif gst.MESSAGE_APPLICATION:
            self.pipeline.set_state(NULL)
            self.pipeline.remove(self.uridecoder)
            
        return True
        
    def OnDynamicPad(self, uridecodebin, src_pad):
        print "OnDynamicPad function ................."
        origin = src_pad.get_caps()
        # sinkpad = self.encodebin.emit("request-pad", origin)
        # src_pad.link(sinkpad)
    
    def noMorePads(self, dbin):    
        print "noMorePads function .................."
        # if (self.multipass == False) or (self.passcounter == int(0)):
           # self.transcodefileoutput.set_state(gst.STATE_PAUSED)           
           # print "******************"
        glib.idle_add(self.idlePlay)

    def idlePlay(self, state):       
        self.Pipeline("playing")
        return False
        
    def Pipeline (self, state):
        if state == ("playing"):
            self.pipeline.set_state(gst.STATE_PLAYING)
        elif state == ("null"):
            self.pipeline.set_state(gst.STATE_NULL)
    
    
if __name__ == "__main__":    
    import gtk
    def convertors_error(NONE, error_string):
        print "convertors_error:" , error_string
        
    def convertors_eof(source):    
        print "source:", source
        
    def ProgressBarUpdate(source):    
        print "ProgressBarUpdate function :", source
        
    format_info = FormatInfo()
    format_info.filechosen = "file:///home/long/视频/123.rmvb"
    format_info.outputfilename = "/home/long/视频/234.rmvb"    
    format_info.containerchoice = "Ogg"
    format_info.videocaps = "video/x-theora"
    convertors = Convertors(format_info)
    convertors.connect('convertors-error', convertors_error)
    convertors.connect("convertors-eos", convertors_eof)
    convertors.connect("convertors-update-progressbar", ProgressBarUpdate)
    gtk.main()
