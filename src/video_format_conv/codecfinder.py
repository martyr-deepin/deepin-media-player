# Transmageddon
# Copyright (C) 2009 Christian Schaller <uraeus@gnome.org>
# Copyright (C) 2009 Edward Hervey <edward.hervey@collabora.co.uk>
# 
# Some code in this file came originally from the encode.py file in Pitivi
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

# THIS CODE CAN PROBABLY BE REDUCED A LOT IN SIZE SINCE ITS 3 BIG FUNCTIONS
# DOING ESSENTIALLY THE SAME, ESPECIALLY NOW THAT THE ONLY SPECIAL CASING
# REMAINING IS FFMUXERS AND WAVPACK


import pygst
pygst.require("0.10")
import gst

def list_compat(a1, b1):
   for x1 in a1:
       if not x1 in b1:
           return False
   return True

containermap = { 'Ogg' : "application/ogg", \
        'Matroska' : "video/x-matroska", \
        'MXF' : "application/mxf", \
        'AVI' : "video/x-msvideo", \
        'Quicktime' : "video/quicktime,variant=apple", \
        'MPEG4' : "video/quicktime,variant=iso", \
        'MPEG PS' : "video/mpeg,mpegversion=2,systemstream=true", \
        'MPEG TS' : "video/mpegts,systemstream=true,packetsize=188", \
        'AVCHD/BD' : "video/mpegts,systemstream=true,packetsize=192",\
        'FLV' : "video/x-flv", \
        '3GPP' : "video/quicktime,variant=3gpp", \
        'ASF' : "video/x-ms-asf, parsed=true", \
        'WebM' : "video/webm", 
        'No container' : False }

csuffixmap =   { 'Ogg' : ".ogg", \
        'Matroska' : ".mkv", \
        'MXF' : ".mxf", \
        'AVI' : ".avi", \
        'Quicktime' : ".mov", \
        'MPEG4' : ".mp4", \
        'MPEG PS' : ".mpg", \
        'MPEG TS' : ".ts", \
        'AVCHD/BD' : ".m2ts", \
        'FLV' : ".flv", \
        '3GPP' : ".3gp",
        'ASF' : ".asf", \
        'WebM' : ".webm", 
        'No container' : ".null" }

audiosuffixmap =   { 'Ogg' : ".ogg", \
        'Matroska' : ".mkv", \
        'MXF' : ".mxf", \
        'AVI' : ".avi", \
        'Quicktime' : ".m4a",
        'MPEG4' : ".mp4", \
        'MPEG PS' : ".mpg", \
        'MPEG TS' : ".ts", \
        'FLV' : ".flv", \
        '3GPP' : ".3gp", \
        'ASF' : ".wma", \
        'WebM' : ".webm"}

nocontainersuffixmap = {
         'audio/mpeg, mpegversion=(int)1, layer=(int)3' : ".mp3", \
         'audio/mpeg, mpegversion=(int)4, stream-format=(string)adts' : ".aac", \
         'audio/x-flac' : ".flac" }

codecmap = { 'Vorbis' : "audio/x-vorbis", \
        'FLAC' : "audio/x-flac", \
        'mp3' : "audio/mpeg, mpegversion=(int)1, layer=(int)3", \
        'AAC' : "audio/mpeg,mpegversion=4", \
        'AC3' : "audio/x-ac3", \
        'Speex' : "audio/x-speex",
        'Celt Ultra' : "audio/x-celt", \
        'ALAC' : "audio/x-alac", \
        'WMA' : "audio/x-wma, wmaversion=(int)2", # Windows Media Audio 2
        'Theora' : "video/x-theora", \
        'Dirac' : "video/x-dirac", \
        'H264' : "video/x-h264", \
        'MPEG2' : "video/mpeg,mpegversion=2,systemstream=false", \
        'MPEG4' : "video/mpeg,mpegversion=4", \
        'xvid' : "video/x-xvid", \
        'WMV' : "video/x-wmv,wmvversion=2", # Windows Media Video 2
        'dnxhd' : "video/x-dnxhd", \
        'divx5' : "video/x-divx,divxversion=5", \
        'divx4' : "video/x-divx,divxversion=4", \
        'AMR-NB' : "audio/AMR", \
        'H263+' : "video/x-h263,variant=itu,h263version=h263p", \
        'On2 vp8' : "video/x-vp8", \
        'mp2' : "audio/mpeg,mpegversion=(int)1, layer=(int)2", \
        'MPEG1' : "video/mpeg,mpegversion=(int)1,systemstream=false"}

#####
#This code checks for available muxers and return a unique caps string
#for each. It also creates a python dictionary mapping the caps strings 
#to concrete element names. 
#####

def get_muxer_element(containercaps): 
   """
   Check all muxers for their caps and create a dictionary mapping caps 
   to element names. Then return elementname
   """

   flist = gst.registry_get_default().get_feature_list(gst.ElementFactory)
   muxers = []
   features = []
   elementname = False
   for fact in flist:
       # FIXME: the 'and not' part of this line should be removed, but it has to
       # stay in until Ranks have been set on most muxers in GStreamer. If
       # removed now we get lots of failures due to ending up with broken muxers
       if list_compat(["Codec", "Muxer"], fact.get_klass().split('/')) and not \
               fact.get_name().startswith('ffmux'):
           muxers.append(fact.get_name())
           features.append(fact)
   muxerfeature = dict(zip(muxers, features))
   incomingcaps = containercaps
   for x in muxers:
           element = x
           factory = gst.registry_get_default().lookup_feature(str(x))
           sinkcaps = [x.get_caps() for x in factory.get_static_pad_templates() \
                   if x.direction == gst.PAD_SRC]
           for caps in sinkcaps:
               if caps.intersect(incomingcaps):
                   if elementname == False:
                       elementname = element
                   else:
                       mostrecent = gst.PluginFeature.get_rank(muxerfeature[element])
                       original = gst.PluginFeature.get_rank(muxerfeature[elementname])
                       if mostrecent >= original:
                           elementname = element
   return elementname

######
#   This code checks for available audio encoders and return a unique caps
#   string for each.
#   It also creates a python dictionary mapping the caps strings to concrete
#   element names.
#####
def get_audio_encoder_element(audioencodercaps):
   """
   Check all audio encoders for their caps and create a dictionary 
   mapping caps to element names, only using the highest ranked element
   for each unique caps value. The input of the function is the unique caps
   and it returns the elementname. If the caps to not exist in dictionary it
   will return False.
   """

   flist = gst.registry_get_default().get_feature_list(gst.ElementFactory)
   encoders = []
   features = []
   elementname = False
   for fact in flist:
       if list_compat(["Codec", "Encoder", "Audio"], \
               fact.get_klass().split('/')):
           # excluding wavpackenc as the fact that it got two SRC pads mess up
           # the logic of this code
           if fact.get_name() != 'wavpackenc':
               encoders.append(fact.get_name())
               features.append(fact)
   encoderfeature = dict(zip(encoders, features))
   incomingcaps = audioencodercaps
   for x in encoders:
           element = x
           factory = gst.registry_get_default().lookup_feature(str(x))
           sinkcaps = [x.get_caps() for x in factory.get_static_pad_templates() \
                   if x.direction == gst.PAD_SRC]
           for caps in sinkcaps:
               if caps.intersect(incomingcaps):
                   if elementname == False:
                       elementname = element
                   else:
                       mostrecent = gst.PluginFeature.get_rank(encoderfeature[element])
                       original = gst.PluginFeature.get_rank(encoderfeature[elementname])
                       if mostrecent >= original:
                           elementname = element
   return elementname

#######
# This code checks for available video encoders and return a unique caps
# string for each. It also creates a python dictionary mapping the caps 
# strings to concrete element names.
#######

def get_video_encoder_element(videoencodercaps):
   """
   Check all video encoders for their caps and create a dictionary 
   mapping caps to element names, only using the highest ranked element
   for each unique caps value. The input of the function is the unique caps
   and it returns the elementname. If the caps to not exist in dictionary it
   will return False.
   """

   flist = gst.registry_get_default().get_feature_list(gst.ElementFactory)
   encoders = []
   features = []
   elementname = False
   for fact in flist:
       if list_compat(["Codec", "Encoder", "Video"], \
               fact.get_klass().split('/')):
           encoders.append(fact.get_name())
           features.append(fact) 
       elif list_compat(["Codec", "Encoder", "Image"], \
               fact.get_klass().split('/')):
           encoders.append(fact.get_name())
           features.append(fact)
   encoderfeature = dict(zip(encoders, features))
   incomingcaps = videoencodercaps
   for x in encoders:
           element = x
           factory = gst.registry_get_default().lookup_feature(str(x))
           sinkcaps = [x.get_caps() for x in factory.get_static_pad_templates() \
                   if x.direction == gst.PAD_SRC]
           for caps in sinkcaps:
               if caps.intersect(incomingcaps):
                   if elementname == False:
                       elementname = element
                   else:
                       mostrecent = gst.PluginFeature.get_rank(encoderfeature[element])
                       original = gst.PluginFeature.get_rank(encoderfeature[elementname])
                       if mostrecent >= original:
                           elementname = element
   return elementname
