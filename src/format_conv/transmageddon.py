#!coding:utf-8
# Transmageddon
# Copyright (C) 2009 Christian Schaller <uraeus@gnome.org>
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

from skin import app_theme
from file_choose_button import FileChooserButton
from dtk.ui.button import Button
from dtk.ui.label import Label
from dtk.ui.menu import Menu
from new_combobox import NewComboBox
from conv_task_gui import ConvTAskGui, MediaItem
from gui import Form

import sys
import os

os.environ["GST_DEBUG_DUMP_DOT_DIR"] = "/tmp"
os.putenv('GST_DEBUG_DUMP_DIR_DIR', '/tmp')
import which
import time
import transcoder_engine
import gobject; gobject.threads_init()
from urlparse import urlparse
import codecfinder
import about
import presets
import utils
import datetime
from locales import _
# from gettext import gettext as _
import gettext

try:
   import pygtk
   pygtk.require("2.0")
   import glib
   import gtk
   import pygst
   pygst.require("0.10")
   import gst
   import gst.pbutils
except Exception, e:
   print "failed to import required modules"
   print e
   sys.exit(1)

major, minor, patch = gst.pygst_version
if (major == 0) and (patch < 22):
   print "You need version 0.10.22 or higher of gstreamer-python for Transmageddon" 
   sys.exit(1)

major, minor, patch = gobject.pygobject_version
if (major == 2) and (minor < 18):
   print "You need version 2.18.0 or higher of pygobject for Transmageddon"
   sys.exit(1)



TARGET_TYPE_URI_LIST = 80
dnd_list = [ ( 'text/uri-list', 0, TARGET_TYPE_URI_LIST ) ]


name_to_supported_containers_map = {
   "AVI" : "AVI",		#2           
   "3GP" : "3GPP",		#9   
   "MP4" : "MPEG4",	#8        
   "MPG" : "MPEG PS",	#3
   "TS"  : "MPEG TS",	#4        
   "OGG" : "Ogg",		#0
   "MKV" : "Matroska",	#1
   "M2TS": "AVCHD/BD",	#5
   "FLV" : "FLV",		#6
   "MOV" : "Quicktime",	#7
   "MXF" : "MXF",		#10
   "ASF" : "ASF", 		#11
   "WebM": "WebM",		#12
   _("Audio-only") : _("Audio-only")
   }

supported_containers = [
        "AVI",		#2           
        "3GP",		#9   
        "MP4",	#8        
        "MPG",	#3
        "TS",	#4        
        "OGG",		#0
        "MKV",	#1
        "M2TS",	#5
        "FLV",		#6
        "MOV",	#7
        "MXF",		#10
        "ASF", 		#11
        "I can not get this item to show for some reason",
        "WebM"		#12
]

# supported_containers = [
#         "AVI",		#2           
#         "3GPP",		#9   
#         "MPEG4",	#8        
#         "MPEG PS",	#3
#         "MPEG TS",	#4        
#         "Ogg",		#0
#         "Matroska",	#1
#         "AVCHD/BD",	#5
#         "FLV",		#6
#         "Quicktime",	#7
#         "MXF",		#10
#         "ASF", 		#11
#         "I can not get this item to show for some reason",
#         "WebM"		#12
# ]

supported_audio_codecs = [
       "vorbis",
       "flac",
       "mp3",
       "aac",
       "ac3",
       "speex",
       "celt",
       "amrnb",
       "wma2"
]

supported_video_codecs = [
       "theora",
       "dirac",
       "h264",
       "mpeg2",
       "mpeg4",
       "xvid",
       "h263p",
       "wmv2",
       "vp8"
]

# Maps containers to the codecs they support.  The first two elements are
# "special" in that they are the default audio/video selections for that
# container modify code. # 123456
supported_video_container_map = {
    'Ogg':        [ 'Theora', 'Dirac', 'On2 vp8' ],
    'MXF':        [ 'H264', 'MPEG2', 'MPEG4' ],
    'Matroska':   [ 'Dirac', 'Theora', 'H264', 'On2 vp8',
                    'MPEG4', 'MPEG2', 'xvid', 'H263+' ],
    # 'AVI':        [ 'H264', 'Dirac', 'MPEG2', 'MPEG4', 'xvid',
    #                 'WMV', 'On2 vp8' ], # Windows Media Video 2
    'AVI':        [ 'H264', 'MPEG4', 'xvid'],
    'Quicktime':  [ 'H264', 'Dirac', 'MPEG2', 'MPEG4', 'On2 vp8' ],
    # 'MPEG4':      [ 'H264', 'MPEG2', 'MPEG4' ],
    'MPEG4':      [ 'H264', 'MPEG4' ],
    'FLV':        [ 'H264'],
    # '3GPP':       [ 'H264', 'MPEG2', 'MPEG4', 'H263+' ],
    '3GPP':       [ 'MPEG4', 'H263+' ],    
    # 'MPEG PS':    [ 'MPEG2', 'MPEG1', 'H264', 'MPEG4' ],
    'MPEG PS':    [ 'MPEG2',  'H264'],
    'MPEG TS':    [ 'MPEG2', 'MPEG1', 'H264', 'MPEG4', 'Dirac' ],
    'AVCHD/BD':   [ 'H264' ],
    'ASF':        [ 'WMV' ], # Windows Media Video 2
    'WebM':       [ 'On2 vp8']
}

supported_audio_container_map = {
    'Ogg':         [ 'Vorbis', 'FLAC', 'Speex', 'Celt Ultra' ],
    'MXF':         [ 'MP3', 'AAC', 'AC3' ],
    'Matroska':    [ 'FLAC', 'AAC', 'AC3', 'Vorbis' ],
    # 'AVI':         [ 'mp3', 'AC3', 'WMA' ], # Windows Media Audio 2
    'AVI':         [ 'MP3', 'AC3', 'WMA' ],   
    'Quicktime':   [ 'AAC', 'AC3', 'MP3' ],
    'MPEG4':       [ 'AAC', 'MP3' ],
    # '3GPP':        [ 'AAC', 'mp3', 'AMR-NB' ],
    '3GPP':        [ 'AAC', 'AMR-NB' ],
    # 'MPEG PS':     [ 'mp3', 'AC3', 'AAC', 'mp2' ],
    'MPEG PS':     [ 'MP3', 'AC3' ],
    'MPEG TS':     [ 'MP3', 'AC3', 'AAC', 'MP2' ],
    'AVCHD/BD':    [ 'AC3' ],
    'FLV':         [ 'MP3' ],
    'ASF':         [ 'WMA', 'MP3'], # Windows Media Audio 2
    'WebM':        [ 'Vorbis']

    # "No container" is 13th option here (0-12)
    # if adding more containers make sure to update code for 'No container as it is placement tied'
}


class TransmageddonUI:
   """This class loads the GtkBuilder file of the UI"""
   def __init__(self, conv_list=[]):
       self.form = Form()              
       self.form.show_all()       
       self.form.hide_setting()      
       # self.form.show_and_hide_task_btn.connect("clicked", self.conv_task_gui_show_and_hide_task_btn_clicked)
       # conv task list.
       self.conv_list = conv_list
       self.conv_dict = {} # save conv state{filename, self.audiodata...}.
       # Transmageddon conv task list init.
       self.conv_task_gui = ConvTAskGui() # task list gui.
       # self.conv_task_gui.start_btn.connect("clicked", self.conv_task_gui_start_btn_clicked)
       self.conv_task_gui.pause_btn.connect("clicked", self.conv_task_gui_pause_btn_clicked)       
       self.conv_task_gui.close_btn.connect("clicked", lambda w : self.conv_task_gui.hide_all())
       self.conv_task_gui.list_view.connect("button-press-event", self.show_popup_menu)
       self.conv_task_gui.list_view.connect("single-click-item",  self.save_open_selsect_file_name)
       self.conv_task_gui.list_view.connect("delete-select-items", self.delete_task_list)
               
       self.task_list = []
       self.conv_task_list = []
       self.task_index = 0
       #Set up i18n
       gettext.bindtextdomain("transmageddon","../../share/locale")
       gettext.textdomain("transmageddon")
       #initialize discoverer
       self.discovered = gst.pbutils.Discoverer(5000000000)
       self.discovered.connect('discovered', self.succeed)
       self.discovered.start()

       self.audiorows=[] # set up the lists for holding the codec combobuttons
       self.videorows=[]
       self.audiocodecs=[] # create lists to store the ordered lists of codecs
       self.videocodecs=[]
	
       # set flag so we remove bogus value from menu only once
       self.bogus=0

       # these dynamic comboboxes allow us to support files with multiple streams eventually
       def dynamic_comboboxes_audio(streams,extra = []):
               vbox = gtk.VBox()
               self.audiorows.append(self.form.bit_rate_combo)
               return self.form.bit_rate_combo
       
       def dynamic_comboboxes_video(streams,extra = []):
               vbox = gtk.VBox()
               self.videorows.append(self.form.frame_rate_combo)
               return self.form.frame_rate_combo
       
       #Define functionality of our button and main window
       # self.TopWindow = self.builder.get_object("TopWindow")
       self.TopWindow = gtk.Window(gtk.WINDOW_TOPLEVEL)
       self.vbox1 = gtk.VBox()       
       # self.FileChooser = gtk.FileChooserButton("选择文件")
       # self.FileChooser = FileChooserButton("选择文件")
       self.FileChooser = self.form.modify_chooser_btn     
       self.videoinformation = gtk.Label("Video height/width:")
       self.audioinformation = gtk.Label("Audio Channels:")
       self.videocodec = gtk.Label("Video codec:")
       self.audiocodec = gtk.Label("Audio codec:")
       
       self.audiobox = dynamic_comboboxes_audio([gobject.TYPE_PYOBJECT])
       self.videobox = dynamic_comboboxes_video([gobject.TYPE_PYOBJECT])
       self.CodecBox = gtk.Table() 
       self.presetsmodel = gtk.ListStore(gobject.TYPE_STRING)
       self.presetchoice = gtk.ComboBox(self.presetsmodel)
       # self.presetchoice = self.form.brand_combo # NewComboBox(110)
       self.cellrenderertext1 = gtk.CellRendererText()
       self.presetchoice.pack_start(self.cellrenderertext1, True)
       self.presetchoice.add_attribute(self.cellrenderertext1, 'text', 0)
       self.containerchoice = self.form.format_combo # NewComboBox(110)
       self.rotationchoice = NewComboBox(110)

       self.hbox_button = gtk.HBox()
       self.transcodebutton = self.form.start_btn # Button("开始转换") #gtk.Button("transcodebutton")   
       self.cancelbutton = Button("停止转换") #gtk.Button("cancelbutton")
       self.ProgressBar = gtk.ProgressBar()
       self.StatusBar = gtk.Statusbar()
       self.audiorows[0].connect("changed", self.on_audiocodec_changed)
       self.videorows[0].connect("changed", self.on_videocodec_changed)
       # TopWindow.
       # self.TopWindow.set_title("视频格式转换")
       # self.TopWindow.set_size_request(350, 400)
       # self.TopWindow.connect("destroy", lambda w : gtk.main_quit())
       # FileChooser.
       # self.FileChooser.connect("file-set", self.on_FileChooser_file_set)
       self.FileChooser.connect("changed", self.on_FileChooser_file_set)
       # self.FileChooser.connect("selection-changed", self.on_FileChooser_file_set)
       self.FileChooser.connect("changed", self.on_FileChooser_file_set)
       # self.FileChooser.dialog.connect("file-set", self.on_FileChooser_file_set)       
       # self.FileChooser.dialog.connect("selection-changed", self.on_FileChooser_file_set)
       # presetchoice.       
       self.presetchoice.set_active(0)
       self.presetchoice.connect("changed", self.on_presetchoice_changed)
       # containerchoice.
       self.containerchoice.connect("changed", self.on_containerchoice_changed)
       # rotationchoice.
       self.rotationchoice.connect("changed", self.on_rotationchoice_changed)       
       # 
       # transcodebutton.
       self.transcodebutton.connect("clicked", self.on_transcodebutton_clicked)
       # cancelbutton.
       self.cancelbutton.connect("clicked", self.on_cancelbutton_clicked)
       
       #
       # add child widgets.
       #
       # self.hbox_button.pack_start(self.cancelbutton, True, True)
       # self.hbox_button.pack_start(self.transcodebutton, True, True)       
       # self.vbox1.pack_start(self.FileChooser, False, False)
       # self.vbox1.pack_start(self.videoinformation, True, True) # 视频高度/宽度
       # self.vbox1.pack_start(self.audioinformation, True, True) # 音频通道
       # self.vbox1.pack_start(self.videocodec, False, False) # 视频信息
       # self.vbox1.pack_start(self.audiocodec, False, False) # 音频信息
       # self.vbox1.pack_start(self.presetchoice, False, False)
       # self.vbox1.pack_start(self.containerchoice, False, False)
       # self.vbox1.pack_start(self.CodecBox, False, False)
       # self.vbox1.pack_start(self.rotationchoice, False, False)
       # self.vbox1.pack_start(self.ProgressBar, False, False)
       # self.vbox1.pack_start(self.hbox_button, False, False)
       # self.vbox1.pack_start(self.StatusBar, False, False)
       # self.TopWindow.add(self.vbox1)
       
       def get_file_path_from_dnd_dropped_uri(self, uri):
           # get the path to file
           path = ""
           if uri.startswith('file:\\\\\\'): # windows
               path = uri[8:] # 8 is len('file:///')
           elif uri.startswith('file://'): # nautilus, rox
               path = uri[7:] # 7 is len('file://')
           elif uri.startswith('file:'): # xffm
               path = uri[5:] # 5 is len('file:')
           return path

       def on_drag_data_received(widget, context, x, y, selection, target_type, \
               timestamp):
           if target_type == TARGET_TYPE_URI_LIST:
               uri = selection.data.strip('\r\n\x00')
               # self.builder.get_object ("FileChooser").set_uri(uri)

       self.TopWindow.connect('drag_data_received', on_drag_data_received)
       self.TopWindow.drag_dest_set( gtk.DEST_DEFAULT_MOTION |
               gtk.DEST_DEFAULT_HIGHLIGHT | gtk.DEST_DEFAULT_DROP, dnd_list, \
               gtk.gdk.ACTION_COPY)

       self.start_time = False
       self.multipass = False
       self.passcounter = False
       
       # Set the Videos XDG UserDir as the default directory for the filechooser
       # also make sure directory exists
       if 'get_user_special_dir' in glib.__dict__:
           self.videodirectory = \
                   glib.get_user_special_dir(glib.USER_DIRECTORY_VIDEOS)
           self.audiodirectory = \
                   glib.get_user_special_dir(glib.USER_DIRECTORY_MUSIC)
       else:
           print "XDG video or audio directory not available"
           self.videodirectory = os.getenv('HOME')
           self.audiodirectory = os.getenv('HOME')
       if self.videodirectory is None:
           print "XDG video or audio directory not available"
           self.videodirectory = os.getenv('HOME')
           self.audiodirectory = os.getenv('HOME')
       CheckDir = os.path.isdir(self.videodirectory)
       if CheckDir == (False):
           os.mkdir(self.videodirectory)
       CheckDir = os.path.isdir(self.audiodirectory)
       if CheckDir == (False):
           os.mkdir(self.audiodirectory)
       self.FileChooser.set_current_folder(self.videodirectory)

       # Setting AppIcon
       FileExist = os.path.isfile("../../share/pixmaps/transmageddon.svg")
       if FileExist:
           self.TopWindow.set_icon_from_file( \
                   "../../share/pixmaps/transmageddon.svg")

       else:
           try:
               self.TopWindow.set_icon_from_file("transmageddon.svg")
           except:
               print "failed to find appicon"

       # default all but top box to insensitive by default
       # self.containerchoice.set_sensitive(False)
       self.CodecBox.set_sensitive(False)
       self.transcodebutton.set_sensitive(False)
       self.cancelbutton.set_sensitive(False)
       self.presetchoice.set_sensitive(False)
       self.containerchoice.set_sensitive(False)
       self.rotationchoice.set_sensitive(False)
       
       # set default values for various variables
       self.AudioCodec = "vorbis"
       self.VideoCodec = "theora"
       self.ProgressBar.set_text("Transcoding Progress")
       self.container = False
       self.vsourcecaps = False
       self.asourcecaps = False
       self.videopasstoggle=False # toggle for passthrough mode chosen
       self.audiopasstoggle=False
       self.videopass=False # toggle for enabling adding of video passthrough on menu
       self.audiopass=False
       self.containertoggle=False # used to not check for encoders with pbutils
       self.discover_done=False # lets us know that discover is finished
       self.missingtoggle=False
       self.interlaced=False
       self.havevideo=False # tracks if input file got video
       self.haveaudio=False
       self.devicename = "nopreset"
       self.nocontaineroptiontoggle=False
       self.outputdirectory=False # directory for holding output directory value
       # create variables to store passthrough options slot in the menu
       self.audiopassmenuno=1
       self.videopassmenuno=1
       self.videonovideomenuno=-2
       # create toggle so I can split codepath depending on if I using a preset
       # or not
       self.usingpreset=False
       self.presetaudiocodec="None"
       self.presetvideocodec="None"
       self.inputvideocaps=None # using this value to store videocodec name to feed uridecodebin to avoid decoding video when not keeping video
       self.nocontainernumber = int(13) # this needs to be set to the number of the no container option in the menu (from 0)
       self.p_duration = gst.CLOCK_TIME_NONE
       self.p_time = gst.FORMAT_TIME

       # Populate the Container format combobox
       for i in supported_containers:
           self.containerchoice.append_text(str(i))
           
       # add i18n "No container"option
       # self.containerchoice.append_text("No container (Audio-only)") # 不输出视频，只有音频
       self.containerchoice.append_text(_("Audio-only"))

       # Populate the rotatation box
       self.rotationlist = ["No rotation (default)",\
                            "Clockwise 90 degrees", \
                            "Rotate 180 degrees",
                            "Counterclockwise 90 degrees", \
                            "Horizontal flip",
                            "Vertical flip", \
                            "Upper left diagonal flip",
                            "Upper right diagnonal flip" ]

       for y in self.rotationlist: 
           self.rotationchoice.append_text(y)
           
       self.rotationchoice.set_active(0)
       self.rotationvalue = int(0) 
      
       # Populate Device Presets combobox
       devicelist = []
       shortname = []
       preset_list = sorted(presets.get().items(),
                            key = (lambda x: x[1].make + x[1].model))
       for x, (name, device) in enumerate(preset_list):
           # print "device:", device
           self.presetchoice.append_text(str(device))
           devicelist.append(str(device))
           shortname.append(str(name))

       for (name, device) in (presets.get().items()):
          shortname.append(str(name))
          
       self.presetchoices = dict(zip(devicelist, shortname))          
       self.presetchoice.prepend_text("No Presets")

       self.waiting_for_signal="False"
       
       # self.TopWindow.show_all() # show TopWindow.
       
       for conv in self.conv_list:
          self.FileChooser.set_filename(conv)
          self.push_all(conv)
          
       # for key in self.conv_dict.keys():
          # print "key:", self.conv_dict[key]
          
   # Get all preset values
   def reverse_lookup(self,v):
       for k in codecfinder.codecmap:
           if codecfinder.codecmap[k] == v:
               return k

   def provide_presets(self, devicename):  #
       # print "provide_presets:"
       devices = presets.get() # presets.py return _presets
       # print "devices:", devices
       device = devices[devicename]
       # print "device:", device
       preset = device.presets["Normal"] # get { container, videc , audec, extension... } 
       # print "preset:", preset.vcodec.width # test input.
       self.usingpreset=True
       self.containerchoice.set_active(-1) # resetting to -1 to ensure population of menu triggers
       self.presetaudiocodec = preset.acodec.name
       # print "self.presetaudiocodec", self.presetaudiocodec
       self.presetvideocodec = preset.vcodec.name
       # print "self.presetvideocodec:", self.presetvideocodec
       if preset.container == "application/ogg":
           self.containerchoice.set_active(0)
       elif preset.container == "video/x-matroska":
           self.containerchoice.set_active(1)
       elif preset.container == "video/x-msvideo":
           self.containerchoice.set_active(2)
       elif preset.container == "video/mpeg,mpegversion=2,systemstream=true":
           self.containerchoice.set_active(3)
       elif preset.container == "video/mpegts,systemstream=true,packetsize=188":
           self.containerchoice.set_active(4)
       elif preset.container == "video/mpegts,systemstream=true,packetsize=192":
           self.containerchoice.set_active(5)
       elif preset.container == "video/x-flv":
           self.containerchoice.set_active(6)
       elif preset.container == "video/quicktime,variant=apple":
           self.containerchoice.set_active(7)
       elif preset.container == "video/quicktime,variant=iso":
           self.containerchoice.set_active(8)
       elif preset.container == "video/quicktime,variant=3gpp":
           self.containerchoice.set_active(9)
       elif preset.container == "application/mxf":
           self.containerchoice.set_active(10)
       elif preset.container == "video/x-ms-asf":
           self.containerchoice.set_active(11)
       elif preset.container == "video/webm":
           self.containerchoice.set_active(12)
       else:
            print "failed to set container format from preset data"


       # Check for number of passes
       # passes = preset.vcodec.passes
       #if passes == "0":
       self.multipass = False
       #else:
       #   self.multipass = int(passes)
       #   self.passcounter = int(0)

   # Create query on uridecoder to get values to populate progressbar 
   # Notes:
   # Query interface only available on uridecoder, not decodebin2)
   # FORMAT_TIME only value implemented by all plugins used
   # a lot of original code from gst-python synchronizer.py example
   def Increment_Progressbar(self):      
       # self.conv_task_gui.show_time_label.set_text(_("..."))
       if self.start_time == False:  
           self.start_time = time.time()
       try:
           position, format = \
                   self._transcoder.uridecoder.query_position(gst.FORMAT_TIME)
           # print "position is " + str(position)
       except:
           position = gst.CLOCK_TIME_NONE

       try:
           duration, format = \
                   self._transcoder.uridecoder.query_duration(gst.FORMAT_TIME)
           # print "duration is " + str(duration)
       except:
           duration = gst.CLOCK_TIME_NONE
       if position != gst.CLOCK_TIME_NONE:
           value = float(position) / duration
           # print "value is " + str(value)
           if float(value) < (1.0) and float(value) >= 0:
               self.ProgressBar.set_fraction(value)
               percent = (value*100)
               timespent = time.time() - self.start_time
               percent_remain = (100-percent)
               # print "percent remain " + str(percent_remain)
               # print "percentage is " + str(percent)
               if percent != 0:
                   rem = (timespent / percent) * percent_remain
               else: 
                   rem = 0.1
               hour = rem / 3600               
               min = (rem % 3600) / 60
               sec = rem % 60
               time_rem = "%(hour)02d:%(min)02d:%(sec)02d" % {
                   "hour": hour,
                   "min": min,
                   "sec": sec,
                   }
               #
               # print "time_rem:", time_rem # add progress info to task gui.
               if self.conv_task_gui.pause_btn.label == _("Pause"):
                  self.conv_task_gui.show_time_label.set_text(_("Time remaining : ") + time_rem)
               else:   
                  self.conv_task_gui.show_time_label.set_text("")
               #               
               if percent_remain > 0.5:
                   if self.passcounter == int(0):
                       txt = "Estimated time remaining: %(time)s"
                       self.ProgressBar.set_text(txt % \
                               {'time': str(time_rem)})
                   else:
                       txt = "Pass %(count)d time remaining: %(time)s"
                       self.ProgressBar.set_text(txt % { \
                               'count': self.passcounter, \
                               'time': str(time_rem), })
               return True
           else:               
               self.ProgressBar.set_fraction(0.0)
               return False
       else:
           return False

   # Call gobject.timeout_add with a value of 500millisecond to regularly poll
   # for position so we can
   # use it for the progressbar
   def ProgressBarUpdate(self, source):
       gobject.timeout_add(500, self.Increment_Progressbar)
       
   def _on_eos(self, source):
       context_id = self.StatusBar.get_context_id("EOS")
       if (self.multipass ==  False) or (self.passcounter == int(0)):
           self.StatusBar.push(context_id, ("File saved to %(dir)s" % \
                   {'dir': self.outputdirectory}))
           self.FileChooser.set_sensitive(True)
           self.containerchoice.set_sensitive(True)
           self.CodecBox.set_sensitive(True)
           self.presetchoice.set_sensitive(True)
           self.cancelbutton.set_sensitive(False)
           self.transcodebutton.set_sensitive(True)
           self.rotationchoice.set_sensitive(True)
           self.start_time = False
           self.conv_task_gui.show_time_label.set_text("")
           self.ProgressBar.set_text("Done Transcoding")          
           # self.task_index = min(self.task_index + 1, len(self.task_list) - 1) # task 
           self.task_list[self.task_index].Pipeline("null") # close Pipeline.
           self.task_list[self.task_index].conv_flags = 1 # conv done.
           try:
              self.conv_task_gui.list_view.items[self.task_index].set_status_icon("success") # set status icon.
           except Exception, e:   
              print "_on_eos[error]:", e
              
           self.task_index += 1
           self.ProgressBar.set_fraction(1.0)
           self.ProgressBar = gtk.ProgressBar() # restart .
           if self.task_index < len(self.task_list):
              self.start_conv_function()
           self.start_time = False
           self.multipass = False
           self.passcounter = False
           self.audiopasstoggle=False
           self.videopasstoggle=False
           self.houseclean=False # due to not knowing which APIs to use I need
                                 # this toggle to avoid errors when cleaning
                                 # the codec comboboxes
       else:
           self.StatusBar.push(context_id, ("Pass %(count)d Complete" % \
                   {'count': self.passcounter}))
           self.start_time = False
           self.ProgressBar.set_text("Start next pass")
           if self.passcounter == (self.multipass-1):
               self.passcounter = int(0)
               self._start_transcoding()
           else:
               self.passcounter = self.passcounter+1
               self._start_transcoding()


   # Use the pygst extension 'discoverer' to get information about the incoming
   # media. Probably need to get codec data in another way.
   # this code is probably more complex than it needs to be currently
 
   def succeed(self, discoverer, info, error):
       result=gst.pbutils.DiscovererInfo.get_result(info)
       streaminfo=info.get_stream_info()
       try:
          container = streaminfo.get_caps()
       except Exception, e:   
          print "succeed[error]:", e
          # self.form.bit_rate_combo.prepend_text("No A")
          self.form.frame_rate_combo.prepend_text(_("No Video"))
          
       seekbool = info.get_seekable()
       clipduration=info.get_duration()

       # result=gst.pbutils.DiscovererInfo.get_result(info)
       # streaminfo=info.get_stream_info()
       # container = streaminfo.get_caps()
       # seekbool = info.get_seekable()
       # clipduration=info.get_duration()

       audiostreamcounter=-1
       audiostreams=[]
       audiotags=[]
       audiochannels=[]
       samplerate=[]
       inputaudiocaps=[]
       markupaudioinfo=[]
       videowidth = None
       videoheight = None
       for i in info.get_stream_list():
           if isinstance(i, gst.pbutils.DiscovererAudioInfo):
               audiostreamcounter=audiostreamcounter+1
               inputaudiocaps.append(i.get_caps())
               audiostreams.append( \
                       gst.pbutils.get_codec_description(inputaudiocaps[audiostreamcounter]))
               audiotags.append(i.get_tags())
               test=i.get_channels()
               audiochannels.append(i.get_channels())
               samplerate.append(i.get_sample_rate())
               self.haveaudio=True
               self.audiodata = { 'audiochannels' : audiochannels[audiostreamcounter], \
                       'samplerate' : samplerate[audiostreamcounter], 'audiotype' : inputaudiocaps[audiostreamcounter], \
                       'clipduration' : clipduration }
               markupaudioinfo.append((''.join(('<small>', \
                       'Audio channels: ', str(audiochannels[audiostreamcounter]) ,'</small>'))))

               self.containerchoice.set_active(-1) # set this here to ensure it happens even with quick audio-only
               self.containerchoice.set_active(0)
           if self.haveaudio==False:
               self.audioinformation.set_markup(''.join(('<small>', "No Audio", '</small>')))
               self.audiocodec.set_markup(''.join(('<small>', "",'</small>')))

           if isinstance(i, gst.pbutils.DiscovererVideoInfo):
               self.inputvideocaps=i.get_caps()
               videotags=i.get_tags()
               interlacedbool = i.is_interlaced()
               if interlacedbool is True:
                   self.interlaced=True
               self.havevideo=True
               self.populate_menu_choices() # run this to ensure video menu gets filled
               videoheight=i.get_height()
               videowidth=i.get_width()
               videodenom=i.get_framerate_denom()
               videonum=i.get_framerate_num()

               self.videodata = { 'videowidth' : videowidth, 'videoheight' : videoheight, 'videotype' : self.inputvideocaps,
                              'fratenum' : videonum, 'frateden' :  videodenom }

           self.discover_done=True
           if self.havevideo==False:
               self.videoinformation.set_markup(''.join(('<small>', _("No Video"), '</small>')))
               self.videocodec.set_markup(''.join(('<small>', "",
                                      '</small>')))
           if self.waiting_for_signal == True:
               if self.containertoggle == True:
                   if self.container != False:
                       self.check_for_passthrough(self.container)
               else:
                   self.check_for_elements()
                   if self.missingtoggle==False:
                       self._start_transcoding()
           if self.container != False:
               self.check_for_passthrough(self.container)
       # set markup

       if audiostreamcounter >= 0:
           self.audioinformation.set_markup(''.join(('<small>', \
                       'Audio channels: ', str(audiochannels[0]), '</small>')))
           self.audiocodec.set_markup(''.join(('<small>','Audio codec: ', \
                       str(gst.pbutils.get_codec_description(inputaudiocaps[audiostreamcounter])), \
                       '</small>')))
       if videowidth and videoheight:
           self.videoinformation.set_markup(''.join(('<small>', 'Video width&#47;height: ', str(videowidth),
                                            "x", str(videoheight), '</small>')))
           self.videocodec.set_markup(''.join(('<small>', 'Video codec: ',
                                       str(gst.pbutils.get_codec_description(self.inputvideocaps)),
                                      '</small>')))

   def discover(self, path):
       self.discovered.discover_uri_async("file://"+path)

   def mediacheck(self, FileChosen):
       uri = urlparse (FileChosen)
       path = uri.path
       self.discover(path)
   
   def check_for_passthrough(self, containerchoice):
       videointersect = ("EMPTY")
       audiointersect = ("EMPTY")
       if (containerchoice != False or self.usingpreset==False):
           container = codecfinder.containermap[containerchoice]
           containerelement = codecfinder.get_muxer_element(container)
           if containerelement == False:
               self.containertoggle = True
               self.check_for_elements()
           else:
               factory = gst.registry_get_default().lookup_feature(containerelement)
               for x in factory.get_static_pad_templates():
                   if (x.direction == gst.PAD_SINK):
                       sourcecaps = x.get_caps()
                       if self.havevideo == True:
                          if videointersect == ("EMPTY"):
                              # clean accepted caps to 'pure' value without parsing requirements
                              # might be redudant and caused by encodebin bug
                              textdata=gst.Caps.to_string(self.videodata['videotype'])
                              sep= ','
                              minitext = textdata.split(sep, 1)[0]
                              cleaned_videodata=gst.Caps(minitext)

                              videointersect = sourcecaps.intersect(cleaned_videodata)

                              if videointersect != ("EMPTY"):
                                  self.vsourcecaps = videointersect
                       if self.haveaudio == True:
                           if audiointersect == ("EMPTY"):
                               audiointersect = sourcecaps.intersect(self.audiodata['audiotype'])
                               if audiointersect != ("EMPTY"):
                                   self.asourcecaps = audiointersect
               if videointersect != ("EMPTY"):
                   self.videopass=True
               else:
                   self.videopass=False

               if audiointersect != ("EMPTY"):
                   self.audiopass=True
               else:
                   self.audiopass=False
               
   # define the behaviour of the other buttons
   def on_FileChooser_file_set(self, widget, filename, uri):
       # print "on_FileChooser_file_set:"
       self.form.path_entry.set_text(filename) # 现实完整路径
       self.filename = self.FileChooser.get_filename()
       # print "self.filename:", self.filename
       self.audiodata = {}
       if self.filename is not None: 
           self.haveaudio=False #make sure to reset these for each file
           self.havevideo=False #
           self.mediacheck(self.filename)
           self.ProgressBar.set_fraction(0.0)
           self.ProgressBar.set_text("Transcoding Progress")
           if (self.havevideo==False and self.nocontaineroptiontoggle==False):
               self.nocontaineroptiontoggle=True
           else:
               self.presetchoice.set_sensitive(True)
               self.presetchoice.set_active(0)

               # removing bogus text from supported_containers
               if self.bogus==0:
                   self.containerchoice.remove_text(12)
                   self.bogus=1
               self.nocontaineroptiontoggle=False
           self.containerchoice.set_sensitive(True)

   def push_all(self, key):        
      self.conv_dict[key] = (self.filename, 
                             self.audiodata,
                             self.haveaudio,
                             self.havevideo,
                             self.discovered,
                             self.nocontaineroptiontoggle,
                             self.bogus
                             )
               
   def pop_all(self, key):   
      self.filename = self.conv_dict[key][0]
      self.audiodata = self.conv_dict[key][1]
      self.haveaudio = self.conv_dict[key][2]
      self.havevideo = self.conv_dict[key][3]
      self.discovered = self.conv_dict[key][4]
      self.nocontaineroptiontoggle = self.conv_dict[key][5]
      self.bogus = self.conv_dict[key][6]
      
   def conv_task_gui_show_and_hide_task_btn_clicked(self, widget): 
      if not self.conv_task_gui.get_visible(): 
         self.conv_task_gui.show_all() 
      else:   
         self.conv_task_gui.hide_all() 
      
   def conv_task_gui_pause_play(self):      
      self.task_list[self.task_index].Pipeline("pause")
      self.conv_task_gui.list_view.items[self.task_index].set_status_icon("wait")
      
   def conv_task_gui_staring_play(self):
      self.task_list[self.task_index].Pipeline("playing")
      self.conv_task_gui.list_view.items[self.task_index].set_status_icon("working")
      
   def start_conv_function(self):   
      try:
         self.task_list[self.task_index].Pipeline("playing")      
         self.conv_task_gui.show_time_label.set_text(_("Converting"))
         self._transcoder = self.task_list[self.task_index]
         self._transcoder.connect("ready-for-querying", self.ProgressBarUpdate)
         self._transcoder.connect("got-eos", self._on_eos)
         self._transcoder.connect("got-error", self.show_error)

         self.conv_task_gui.list_view.items[self.task_index].set_status_icon("working")
         self.ProgressBar = self.conv_task_gui.list_view.items[self.task_index]      
         self.conv_task_gui.queue_draw()
      except Exception, e:   
         print "start_conv_function[error]:", e
      
   def conv_task_gui_pause_btn_clicked(self, widget):
      try:
         if self.task_list[self.task_index].state_label != "null":
            if widget.label == _("Pause"):
               widget.set_label(_("continue"))
               self.conv_task_gui_pause_play()
            else:            
               widget.set_label(_("Pause"))
               self.conv_task_gui_staring_play()
      except Exception, e:         
         print "conv_task_gui_pause_btn_clicked:", e
               
   def show_popup_menu(self, widget, event):
      if 3 == event.button:
         self.root_menu = Menu([(None, _("Open a directory"), self.open_conv_file_dir),
                                 None,
                                (None, _("Delete"), self.delete_conv_task_file),
                                (None, _("Remove complete tasks"),self.clear_succeed_conv_task_file)
                                ], True)

         self.root_menu.show((int(event.x_root), int(event.y_root)), (0, 0))
         
   def clear_succeed_conv_task_file(self):
      temp_task_list = []
      task_i = 0
      for task in self.task_list:
         if task.conv_flags:
            del self.conv_task_gui.list_view.items[task_i]
            temp_task_list.append(task)
         else:   
            task_i += 1
            task.Pipeline("pause") # pause task.                                                
      # delete transcoder task.      
      for temp_task in temp_task_list:
         self.task_list.remove(temp_task)
      # restart start task.
      if temp_task_list != [] and self.task_list != []:
         self.task_index = 0
         self.conv_task_gui.show_all()
         self.start_conv_function()
         gtk.timeout_add(1200, self.restart_start_btn)
      else:         
         try:
            if not self.task_list[self.task_index].conv_flags:
               self.task_list[self.task_index].Pipeline("playing")
         except Exception, e:      
            print "clear_succeed_conv_task_file[error]:", e
         
   def delete_conv_task_file(self):
      self.select_rows = self.conv_task_gui.list_view.select_rows
      self.items = self.conv_task_gui.list_view.items
      temp_task_list = []
      for row in self.select_rows:
         if not self.task_list[row].conv_flags:
            self.task_list[row].Pipeline("null") # set pipiline null.
         temp_task_list.append(self.task_list[row]) # add to temp task list.

      for temp_task in temp_task_list:
         self.task_list.remove(temp_task)
         
      # delete select.   
      self.conv_task_gui.list_view.delete_select_items()
      
   def delete_task_list(self, list_view, list_item):      
      # clear items.
      self.conv_task_gui.list_view.items = []  
      # find task index.
      self.task_index = 0
      for task in self.task_list:
         if task.conv_flags:
            self.task_index += 1
            break
      # restart draw media item list view.   
      for transcoder in self.task_list:
         media_item = MediaItem()
         media_item.set_name(transcoder.name)
         media_item.path = transcoder.outputdirectory
         media_item.set_format(transcoder.container)
         # set state icon.
         if transcoder.conv_flags:
            media_item.set_status_icon("success")
         self.conv_task_gui.list_view.add_items([media_item])
         
      if self.conv_task_gui.list_view.items != []:
         # start run task. 
         self.conv_task_gui.show_all()
         self.start_conv_function()
         gtk.timeout_add(1200, self.restart_start_btn)
      
   def open_conv_file_dir(self):
      # os.system("nautilus %s" % (self.list_view_select_file_dir))
      os.system("xdg-open '%s'" % (self.list_view_select_file_dir))
                
   def save_open_selsect_file_name(self, list_view, list_item, column, offset_x, offset_y):  
      self.list_view_select_file_dir = list_item.get_path()
      
   def _start_transcoding(self): 
       filechoice = self.FileChooser.get_uri()
       self.filename = self.FileChooser.get_filename()
       
       if (self.havevideo and (self.VideoCodec != "novid")):
           vheight = self.videodata['videoheight']
           vwidth = self.videodata['videowidth']
           ratenum = self.videodata['fratenum']
           ratednom = self.videodata['frateden']
           if self.videopasstoggle == False:
               videocodec = self.VideoCodec
           else: # this is probably redundant and caused by encodebin 
               textdata=gst.Caps.to_string(self.vsourcecaps)
               sep= ','
               minitext  = textdata.split(sep, 1)[0]
               videocodec = minitext
           self.outputdirectory=self.videodirectory
       else:
           self.outputdirectory=self.audiodirectory
           videocodec=False
           vheight=False
           vwidth=False
           ratenum=False
           ratednom=False
       if self.haveaudio:
           achannels = self.audiodata['audiochannels']
           if self.audiopasstoggle == False:
               audiocodec = self.AudioCodec
           else:
               audiocodec = gst.Caps.to_string(self.asourcecaps)
       else:
           audiocodec=False
           achannels=False

       new_width, new_height = (int(vwidth), int(vheight))
       model_text = self.form.model_combo.get_active_text()
       
       if model_text != _("No Model"):
          new_width, new_height = self.form.model_dict[model_text]
       else:   
          if type(videocodec) != bool:
             ratio_text = self.form.ratio_combo.get_active_text().replace(" x ", "-").split("-")
             new_width = ratio_text[0]
             new_height = ratio_text[1]
          # print "active_text:", ratio_text
          # print "new_width:", new_width
          # print "new_height:", new_height
          
       import urllib
       # get set output path.
       out_path = self.form.save_path_entry.get_text()       
       if not len(out_path):
          out_path = os.path.expanduser("~")
       # print "out_path:", out_path
       self.outputdirectory = out_path # output path.   
       # _format = self.outputfilename[-3:]
       # add conv task.
       for conv in self.conv_list:             
          filechoice = "file://" + urllib.quote(conv)
          self.filename = conv                    
          name = os.path.splitext(os.path.split(conv)[1])[0]
          name_time = datetime.datetime.now()             
          container_fromat = self.ContainerFormatSuffix
             
          self.outputfilename =  name + "-LD-%s%s" % (name_time,  container_fromat)
          
          transcoder = transcoder_engine.Transcoder(
                           filechoice, self.filename,
                           self.outputdirectory, self.container, audiocodec, 
                           videocodec, self.devicename, 
                           vheight, vwidth, ratenum, ratednom, achannels, 
                           self.multipass, self.passcounter, self.outputfilename,
                           self.timestamp, self.rotationvalue, self.audiopasstoggle, 
                           self.videopasstoggle, self.interlaced, self.inputvideocaps, 
                           int(new_width), int(new_height))
          
          transcoder.name = name
          transcoder.outputdirectory = self.outputdirectory
          transcoder.container = self.container
          
          self.task_list.append(transcoder)
          media_item = MediaItem()
          media_item.set_name(transcoder.name)
          media_item.path = transcoder.outputdirectory
          media_item.set_format(container_fromat[1:])
          self.conv_task_gui.list_view.add_items([media_item])
          self.conv_task_list.append(media_item)
       
       self.conv_task_gui.show_all()       
       self.start_conv_function()   
       gtk.timeout_add(1000, self.restart_start_btn)
       
       return True

   def restart_start_btn(self): # .
      self.task_list[self.task_index].Pipeline("playing")
      
   def donemessage(self, donemessage, null):
       if donemessage == gst.pbutils.INSTALL_PLUGINS_SUCCESS:
           # print "success " + str(donemessage)
           if gst.update_registry():
               print "Plugin registry updated, trying again"
           else:
               print "GStreamer registry update failed"
           if self.containertoggle == False:
               # print "done installing plugins, starting transcode"
               # FIXME - might want some test here to check plugins needed are
               # actually installed
               # but it is a rather narrow corner case when it fails
               self._start_transcoding()
       elif donemessage == gst.pbutils.INSTALL_PLUGINS_PARTIAL_SUCCESS:
           self.check_for_elements()
       elif donemessage == gst.pbutils.INSTALL_PLUGINS_NOT_FOUND:
           context_id = self.StatusBar.get_context_id("EOS")
           self.StatusBar.push(context_id, \
                   "Plugins not found, choose different codecs.")
           self.FileChooser.set_sensitive(True)
           self.containerchoice.set_sensitive(True)
           self.CodecBox.set_sensitive(True)
           self.cancelbutton.set_sensitive(False)
           self.transcodebutton.set_sensitive(True)
       elif donemessage == gst.pbutils.INSTALL_PLUGINS_USER_ABORT:
           context_id = self.StatusBar.get_context_id("EOS")
           self.StatusBar.push(context_id, "Codec installation aborted.")
           self.FileChooser.set_sensitive(True)
           self.containerchoice.set_sensitive(True)
           self.CodecBox.set_sensitive(True)
           self.cancelbutton.set_sensitive(False)
           self.transcodebutton.set_sensitive(True)
       else:
           context_id = self.StatusBar.get_context_id("EOS")
           self.StatusBar.push(context_id, "Missing plugin installation failed: ") + gst.pbutils.InstallPluginsReturn()

   def check_for_elements(self):
       if self.container==False:
           containerstatus=True
           videostatus=True
       else:
           # containerchoice = self.builder.get_object ("containerchoice").get_active_text ()
           containerchoice = name_to_supported_containers_map[self.containerchoice.get_active_text()]
           containerstatus = codecfinder.get_muxer_element(codecfinder.containermap[containerchoice])
           if self.havevideo:
               if self.videopasstoggle != True:
                   if self.VideoCodec == "novid":
                       videostatus=True
                   else:
                       videostatus = codecfinder.get_video_encoder_element(self.VideoCodec)
               else:
                   videostatus=True
       if self.haveaudio:
           if self.audiopasstoggle != True:
               audiostatus = codecfinder.get_audio_encoder_element(self.AudioCodec)
           else:
               audiostatus=True
       else:
           audiostatus=True
       if self.havevideo == False: # this flags help check if input is audio-only file
           videostatus=True
       if not containerstatus or not videostatus or not audiostatus:
           self.missingtoggle=True
           fail_info = []
           if self.containertoggle==True:
               audiostatus=True
               videostatus=True
           if containerstatus == False: 
               fail_info.append(gst.caps_from_string(codecfinder.containermap[containerchoice]))
           if audiostatus == False:
               fail_info.append(self.AudioCodec)
           if videostatus == False:
               fail_info.append(self.VideoCodec)
           missing = []
           for x in fail_info:
               missing.append(gst.pbutils.missing_encoder_installer_detail_new(x))
           context = gst.pbutils.InstallPluginsContext ()
           context.set_xid(self.TopWindow.get_window().xid)
           strmissing = str(missing)
           gst.pbutils.install_plugins_async (missing, context, \
                   self.donemessage, "NULL")

   # The transcodebutton is the one that calls the Transcoder class and thus
   # starts the transcoding
   def on_transcodebutton_clicked(self, widget): # 确定按钮 事件.
       self.containertoggle = False
       self.cancelbutton.set_sensitive(True)
       # self.ProgressBar.set_fraction(0.0)
       # create a variable with a timestamp code
       timeget = datetime.datetime.now()
       self.timestamp = str(timeget.strftime("-%H%M%S-%d%m%Y"))
       # Remove suffix from inbound filename so we can reuse it together with suffix to create outbound filename
       self.nosuffix = os.path.splitext(os.path.basename(self.filename))[0]
       # pick output suffix
       # container = self.builder.get_object ("containerchoice").get_active_text ()
       container = name_to_supported_containers_map[self.containerchoice.get_active_text()]
       if self.container==False: # deal with container less formats
           self.ContainerFormatSuffix = codecfinder.nocontainersuffixmap[gst.Caps.to_string(self.AudioCodec)]
       else:
           if self.havevideo == False:
               self.ContainerFormatSuffix = codecfinder.audiosuffixmap[container]
           else:
               self.ContainerFormatSuffix = codecfinder.csuffixmap[container]
       self.outputfilename = str(self.nosuffix+self.timestamp+self.ContainerFormatSuffix)
       context_id = self.StatusBar.get_context_id("EOS")
       self.StatusBar.push(context_id, ("Writing %(filename)s" % {'filename': self.outputfilename}))
       if self.multipass == False:
           self.ProgressBar.set_text("Transcoding Progress")
       else:
           self.passcounter=int(1)
           self.ProgressBar.set_text("Pass %(count)d Progress" % {'count': self.passcounter})
       if self.haveaudio:
           if self.audiodata.has_key("samplerate"):
               self.check_for_elements()
               if self.missingtoggle==False:
                   self._start_transcoding()
           else:
               self.waiting_for_signal="True"
       elif self.havevideo:
           if self.videodata.has_key("videoheight"):
               self.check_for_elements()
               if self.missingtoggle==False:
                   self._start_transcoding()
           else:
               self.waiting_for_signal="True"
       #hide format conv from.
       self.form.hide_all()        
       
   def on_cancelbutton_clicked(self, widget): # 取消按钮 事件.
       self.FileChooser.set_sensitive(True)
       self.containerchoice.set_sensitive(True)
       self.CodecBox.set_sensitive(True)
       self.presetchoice.set_sensitive(True)
       self.rotationchoice.set_sensitive(True)
       self.presetchoice.set_active(0)
       self.cancelbutton.set_sensitive(False)
       self.transcodebutton.set_sensitive(True)
       self._cancel_encoding = \
               transcoder_engine.Transcoder.Pipeline(self._transcoder,"null")
       self.ProgressBar.set_fraction(0.0)
       self.ProgressBar.set_text("Transcoding Progress")
       context_id = self.StatusBar.get_context_id("EOS")
       self.StatusBar.pop(context_id)
       self.audiopasstoggle=False

   def populate_menu_choices(self):
       # self.audiocodecs - contains list of whats in self.audiorows
       # self.videocodecs - contains listof whats in self.videorows
       # audio_codecs, video_codecs - temporary lists

       # clean up stuff from previous run
       self.houseclean=True # set this to avoid triggering events when cleaning out menus
       self.audiorows[0].clear_items()
       # self.audiorows[0].append_text("")
       # for c in self.audiocodecs: # 
       #     self.audiorows[0].remove_text(0)
       self.audiocodecs =[]
       if self.havevideo==True:
           if self.container != False:
               self.videorows[0].clear_items()
               # self.videorows[0].append_text("")
               # for c in self.videocodecs:
               #     self.videorows[0].remove_text(0)
               self.videocodecs=[]
       self.houseclean=False
      # end of housecleaning

       # start filling audio
       if self.haveaudio==True:
           
           if self.usingpreset==True: # First fill menu based on presetvalue
               self.audiorows[0].append_text(str(gst.pbutils.get_codec_description(self.presetaudiocodec)))
               self.audiorows[0].set_active(0)
               self.audiocodecs.append(self.presetaudiocodec)
           elif self.container==False: # special setup for container less case, looks ugly, but good enough for now
               # self.audiorows[0].append_text(str(gst.pbutils.get_codec_description("audio/mpeg, mpegversion=(int)1, layer=(int)3")))
               # self.audiorows[0].append_text(str(gst.pbutils.get_codec_description("audio/mpeg, mpegversion=4, stream-format=adts")))
               audio_only_select_code = str(gst.pbutils.get_codec_description("audio/x-flac"))               
               self.audiorows[0].append_text(audio_only_select_code)
               self.audiocodecs.append(gst.Caps("audio/mpeg, mpegversion=(int)1, layer=(int)3"))
               self.audiocodecs.append(gst.Caps("audio/mpeg, mpegversion=4, stream-format=adts"))
               self.audiocodecs.append(gst.Caps("audio/x-flac"))
               self.audiorows[0].set_active(0)
               self.audiorows[0].set_sensitive(True)
           else:
               audio_codecs = []
               audio_codecs = supported_audio_container_map[self.container]
               import copy
               temp_audio_codecs = copy.copy(audio_codecs)
               
               c_i = 0
               for c in temp_audio_codecs:  
                  if c == "MP3":                     
                     temp_audio_codecs[c_i] = "mp3"
                  elif c == "MP2":   
                     temp_audio_codecs[c_i] = "mp2"
                  c_i += 1                     
               
               for c in audio_codecs:
                   self.audiorows[0].append_text(c)
                  
               for c in temp_audio_codecs:
                   self.audiocodecs.append(gst.Caps(codecfinder.codecmap[c]))
                   
           self.audiorows[0].set_sensitive(True)
           self.audiorows[0].set_active(0)
       else:
               self.audiorows[0].set_sensitive(False)

       # fill in with video
       if self.havevideo==True:
           if self.container != False:
               if self.usingpreset==True:
                   self.videorows[0].append_text(str(gst.pbutils.get_codec_description(self.presetvideocodec)))
                   self.videorows[0].set_active(0)
                   self.videocodecs.append(self.presetvideocodec)
               else:
                   video_codecs=[]
                   video_codecs = supported_video_container_map[self.container]
                   self.rotationchoice.set_sensitive(True)
                   for c in video_codecs:
                       self.videocodecs.append(gst.Caps(codecfinder.codecmap[c]))
                   for c in video_codecs: # I can't update the menu with loop append
                       # print "c:", c
                       self.videorows[0].append_text(c)
                       
                   self.form.frame_rate_label.set_sensitive(True)    
                   self.videorows[0].set_sensitive(True)
                   self.videorows[0].set_active(0)

                   #add a 'No Video option'
                   self.videorows[0].append_text(_("No Video"))
                   self.videocodecs.append("novid")
                   self.videonovideomenuno=(len(self.videocodecs))-1
                      
                   # add the Passthrough option.
                   # if self.videopass==True:
                   #     self.videorows[0].append_text("Video passthrough")
                   #     self.videocodecs.append("pass")
                   #     self.videopassmenuno=(len(self.videocodecs))-1
                   
                   # if self.audiopass==True:
                   #     self.audiorows[0].append_text("Audio passthrough")
                   #     self.audiocodecs.append("pass")
                   #     self.audiopassmenuno=(len(self.audiocodecs))-1
       else:
          self.form.frame_rate_label.set_sensitive(False)
          self.videorows[0].set_sensitive(False)
          self.videorows[0].prepend_text(_("No Video"))

   def on_containerchoice_changed(self, widget, text):
       self.CodecBox.set_sensitive(True)
       self.ProgressBar.set_fraction(0.0)
       self.ProgressBar.set_text("Transcoding Progress")
       
       if self.containerchoice.get_active() == self.nocontainernumber:
               self.container = False
               self.videorows[0].set_active(self.videonovideomenuno)
               self.videorows[0].set_sensitive(False)
               self.form.frame_rate_label.set_sensitive(False)
       else:          
           if self.containerchoice.get_active()!= -1:
               self.container = name_to_supported_containers_map[self.containerchoice.get_active_text ()]
               if self.discover_done == True:
                   self.check_for_passthrough(self.container)
           self.transcodebutton.set_sensitive(True)
           
       self.populate_menu_choices()

   def on_presetchoice_changed(self, widget):
       # presetchoice = self.builder.get_object ("presetchoice").get_active_text ()
       presetchoice = self.presetchoice.get_active_text ()
       self.ProgressBar.set_fraction(0.0)
       if presetchoice == "No Presets":
           self.usingpreset=False
           self.devicename = "nopreset"
           self.containerchoice.set_sensitive(True)
           self.containerchoice.set_active(0)
           self.start_time = False
           self.multipass = False
           self.passcounter = False
           self.rotationchoice.set_sensitive(True)
           # if self.builder.get_object("containerchoice").get_active_text():
           if name_to_supported_containers_map[self.containerchoice.get_active_text()]:
               self.populate_menu_choices()
               self.CodecBox.set_sensitive(True)
               self.transcodebutton.set_sensitive(True)
       else: # 手机产品信息. 
           self.usingpreset=True
           self.ProgressBar.set_fraction(0.0)
           self.devicename = self.presetchoices[presetchoice]
           # print "======================================"
           # print "on_presetchoice_changed:"
           # print "self.devicename", self.devicename
           self.provide_presets(self.devicename)
           self.containerchoice.set_sensitive(False)
           self.CodecBox.set_sensitive(False)
           self.rotationchoice.set_sensitive(False)
           # if self.builder.get_object("containerchoice").get_active_text():
           if name_to_supported_containers_map[self.containerchoice.get_active_text()]:
               self.transcodebutton.set_sensitive(True)
           # print "======================================="    
           
   def on_rotationchoice_changed(self, widget, text):
       self.rotationvalue = self.rotationchoice.get_active()

   def on_audiocodec_changed(self, widget, text):
       if (self.houseclean == False and self.usingpreset==False):
           audio_codec = self.audiorows[0].get_active()
           # print "audio_codec:", audio_codec
           # if audio_codec == "MP3":
           #    audio_codec = "mp3"
           self.AudioCodec = self.audiocodecs[audio_codec]
           if self.container != False:
               if self.audiorows[0].get_active() ==  self.audiopassmenuno:
                   self.audiopasstoggle=True
       elif self.usingpreset==True:
           self.AudioCodec = gst.Caps(self.presetaudiocodec)    

   def on_videocodec_changed(self, widget, text):
       if (self.houseclean == False and self.usingpreset==False):
           if self.container != False:
               self.VideoCodec = self.videocodecs[self.videorows[0].get_active()]
           else:
                   self.VideoCodec = "novid"
           if self.videorows[0].get_active() == self.videopassmenuno:
               self.videopasstoggle=True
       elif self.usingpreset==True:
           self.VideoCodec = gst.Caps(self.presetvideocodec)

   def on_about_dialog_activate(self, widget):
       """
           Show the about dialog.
       """
       about.AboutDialog()


   def show_error(self, NONE, error_string):
       if (error_string=="noaudioparser") or (error_string=="novideoparser"):
           self.FileChooser.set_sensitive(True)
           self.containerchoice.set_sensitive(True)
           self.CodecBox.set_sensitive(True)
           self.presetchoice.set_sensitive(True)
           self.rotationchoice.set_sensitive(True)
           self.presetchoice.set_active(0)
           self.cancelbutton.set_sensitive(False)
           self.transcodebutton.set_sensitive(True)
           self.ProgressBar.set_fraction(0.0)
           # self.ProgressBar.set_text("Transcoding Progress")
           self.ProgressBar.set_text("show_error")
           if error_string=="noaudioparser":
               error_message = "No audio parser, passthrough not available"
               codecs = supported_container_map[self.container]
               self.AudioCodec = codecs[0]
               self.audiopasstoggle = False
           elif error_string=="novideoparser":
               error_message= "No video parser, passthrough not available"
               codecs = supported_container_map[self.container]
               self.VideoCodec = codecs[1]
               self.videopasstoggle = False
           else:
               error_message="Uknown error"
       else:
         error_message = error_string
         
       self.conv_task_gui.show_time_label.set_text(_(error_message))  
       self.conv_task_gui.list_view.items[self.task_index].set_status_icon("error")
       self.task_list[self.task_index].Pipeline("null")
       self.task_index = 0
       gtk.timeout_add(3000, self.clear_error_label_show)
       
       context_id = self.StatusBar.get_context_id("EOS")
       self.StatusBar.push(context_id, error_message)

   def clear_error_label_show(self):
      self.conv_task_gui.show_time_label.set_text("")  
      return False
   
   def on_debug_activate(self, widget):
       dotfile = "/tmp/transmageddon-debug-graph.dot"
       pngfile = "/tmp/transmageddon-pipeline.png"
       if os.access(dotfile, os.F_OK):
           os.remove(dotfile)
       if os.access(pngfile, os.F_OK):
           os.remove(pngfile)
       gst.DEBUG_BIN_TO_DOT_FILE (self._transcoder.pipeline, \
               gst.DEBUG_GRAPH_SHOW_ALL, 'transmageddon-debug-graph')
       # check if graphviz is installed with a simple test
       try:
           dot = which.which("dot")
           os.system(dot + " -Tpng -o " + pngfile + " " + dotfile)
           gtk.show_uri(gtk.gdk.Screen(), "file://"+pngfile, 0)
       except which.WhichError:
              print "The debug feature requires graphviz (dot) to be installed."
              print "Transmageddon can not find the (dot) binary."
   
if __name__ == "__main__":
        hwg = TransmageddonUI()
        gtk.main()
