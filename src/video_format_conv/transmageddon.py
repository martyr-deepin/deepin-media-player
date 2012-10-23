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
from gettext import gettext as _
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

supported_containers = [
        "Ogg",		#0
        "Matroska",	#1
        "AVI",		#2
        "MPEG PS",	#3
        "MPEG TS",	#4
        "AVCHD/BD",	#5
        "FLV",		#6
        "Quicktime",	#7
        "MPEG4",	#8
        "3GPP",		#9
        "MXF",		#10
        "ASF", 		#11
        "I can not get this item to show for some reason",
        "WebM"		#12
]

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
# container.
supported_video_container_map = {
    'Ogg':        [ 'Theora', 'Dirac', 'On2 vp8' ],
    'MXF':        [ 'H264', 'MPEG2', 'MPEG4' ],
    'Matroska':   [ 'Dirac', 'Theora', 'H264', 'On2 vp8',
                    'MPEG4', 'MPEG2', 'xvid', 'H263+' ],
    'AVI':        [ 'H264', 'Dirac', 'MPEG2', 'MPEG4', 'xvid',
                    'Windows Media Video 2', 'On2 vp8' ],
    'Quicktime':  [ 'H264', 'Dirac', 'MPEG2', 'MPEG4', 'On2 vp8' ],
    'MPEG4':      [ 'H264', 'MPEG2', 'MPEG4' ],
    'FLV':        [ 'H264'],
    '3GPP':       [ 'H264', 'MPEG2', 'MPEG4', 'H263+' ],
    'MPEG PS':    [ 'MPEG2', 'MPEG1', 'H264', 'MPEG4' ],
    'MPEG TS':    [ 'MPEG2', 'MPEG1', 'H264', 'MPEG4', 'Dirac' ],
    'AVCHD/BD':   [ 'H264' ],
    'ASF':        [ 'Windows Media Video 2' ],
    'WebM':       [ 'On2 vp8']
}

supported_audio_container_map = {
    'Ogg':         [ 'Vorbis', 'FLAC', 'Speex', 'Celt Ultra' ],
    'MXF':         [ 'mp3', 'AAC', 'AC3' ],
    'Matroska':    [ 'FLAC', 'AAC', 'AC3', 'Vorbis' ],
    'AVI':         [ 'mp3', 'AC3', 'Windows Media Audio 2' ],
    'Quicktime':   [ 'AAC', 'AC3', 'mp3' ],
    'MPEG4':       [ 'AAC', 'mp3' ],
    '3GPP':        [ 'AAC', 'mp3', 'AMR-NB' ],
    'MPEG PS':     [ 'mp3', 'AC3', 'AAC', 'mp2' ],
    'MPEG TS':     [ 'mp3', 'AC3', 'AAC', 'mp2' ],
    'AVCHD/BD':    [ 'AC3' ],
    'FLV':         [ 'mp3' ],
    'ASF':         [ 'Windows Media Audio 2', 'mp3'],
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
       # conv task list.
       self.conv_list = conv_list
       # Transmageddon conv task list init.
       self.conv_task_gui = ConvTAskGui() # task list gui.
       self.conv_task_gui.start_btn.connect("clicked", self.conv_task_gui_start_btn_clicked)
       self.conv_task_gui.pause_btn.connect("clicked", self.conv_task_gui_pause_btn_clicked)
       self.task_list = []
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
           # streams=1 # this will become a variable once we support multiple streams
               vbox = gtk.VBox()
           
           # x=-1
           # while x < (streams-1):
               # x=x+1
               # print "x is " + str(x)
               # store = gtk.ListStore(gobject.TYPE_STRING, *extra)
               # combo = gtk.ComboBox(store)
               # text_cell = gtk.CellRendererText()
               # combo.pack_start(text_cell, True)
               # combo.add_attribute(text_cell, 'text', 0)
               # self.audiorows.append(combo)
               self.audiorows.append(self.form.bit_rate_combo)
               # vbox.add(self.audiorows[0])
               # return vbox
               return self.form.bit_rate_combo
       
       def dynamic_comboboxes_video(streams,extra = []):
           # streams=1
               vbox = gtk.VBox()
           
           # x=-1
           # while x < (streams-1):
               # x=x+1
               # store = gtk.ListStore(gobject.TYPE_STRING, *extra)
               # combo = gtk.ComboBox(store)
               # combo = NewComboBox()
               # text_cell = gtk.CellRendererText()
               # combo.pack_start(text_cell, True)
               # combo.add_attribute(text_cell, 'text', 0)
               # self.videorows.append(combo)
               self.videorows.append(self.form.frame_rate_combo)
               # vbox.add(self.videorows[0])
               # return vbox
               return self.form.frame_rate_combo
       
       #Define functionality of our button and main window
       # self.TopWindow = self.builder.get_object("TopWindow")
       self.TopWindow = gtk.Window(gtk.WINDOW_TOPLEVEL)
       self.vbox1 = gtk.VBox()       
       # self.FileChooser = self.builder.get_object("FileChooser")
       # self.FileChooser = gtk.FileChooserButton("选择文件")
       # self.FileChooser = FileChooserButton("选择文件")
       self.FileChooser = self.form.modify_chooser_btn     
       # self.videoinformation = self.builder.get_object("videoinformation") # GtkLabel
       # self.audioinformation = self.builder.get_object("audioinformation") # GtkLabel
       self.videoinformation = gtk.Label("Video height/width:")
       self.audioinformation = gtk.Label("Audio Channels:")
       # self.videocodec = self.builder.get_object("videocodec")
       # self.audiocodec = self.builder.get_object("audiocodec")
       self.videocodec = gtk.Label("Video codec:")
       self.audiocodec = gtk.Label("Audio codec:")
       
       self.audiobox = dynamic_comboboxes_audio([gobject.TYPE_PYOBJECT])
       self.videobox = dynamic_comboboxes_video([gobject.TYPE_PYOBJECT])
       # self.CodecBox = self.builder.get_object("CodecBox")
       self.CodecBox = gtk.Table() 
       # self.presetchoice = self.builder.get_object("presetchoice")
       self.presetsmodel = gtk.ListStore(gobject.TYPE_STRING)
       self.presetchoice = gtk.ComboBox(self.presetsmodel)
       # self.presetchoice = self.form.brand_combo # NewComboBox(110)
       self.cellrenderertext1 = gtk.CellRendererText()
       self.presetchoice.pack_start(self.cellrenderertext1, True)
       self.presetchoice.add_attribute(self.cellrenderertext1, 'text', 0)
       # self.containerchoice = self.builder.get_object("containerchoice")
       # self.containerchoice = gtk.ListStore(gobject.TYPE_STRING)       
       # self.containerchoice = gtk.ComboBox(self.containerchoice)
       self.containerchoice = self.form.format_combo # NewComboBox(110)
       # self.cellrenderertext2 = gtk.CellRendererText()
       # self.containerchoice.pack_start(self.cellrenderertext2, True)
       # self.containerchoice.add_attribute(self.cellrenderertext2, 'text', 0)
       # self.rotationchoice = self.builder.get_object("rotationchoice")
       # self.rotationmodel = gtk.ListStore(gobject.TYPE_STRING)
       # self.rotationchoice = gtk.ComboBox(self.rotationmodel)              
       self.rotationchoice = NewComboBox(110)
       # self.cellrenderertext3 = gtk.CellRendererText()
       # self.rotationchoice.pack_start(self.cellrenderertext3, True)
       # self.rotationchoice.add_attribute(self.cellrenderertext3, 'text', 0)

       self.hbox_button = gtk.HBox()
       # self.transcodebutton = self.builder.get_object("transcodebutton")
       self.transcodebutton = self.form.start_btn # Button("开始转换") #gtk.Button("transcodebutton")   
       # self.cancelbutton = self.builder.get_object("cancelbutton")
       self.cancelbutton = Button("停止转换") #gtk.Button("cancelbutton")
       # self.ProgressBar = self.builder.get_object("ProgressBar")
       self.ProgressBar = gtk.ProgressBar()
       # self.StatusBar = self.builder.get_object("StatusBar")
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
       # CodecBox.       
       # self.CodecBox.attach(self.audiobox, 0, 1, 1, 2, yoptions = gtk.FILL)
       # self.CodecBox.attach(self.videobox, 2, 3, 1, 2, yoptions = gtk.FILL)
       # self.CodecBox.show_all()
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
       self.ProgressBar.set_text(_("Transcoding Progress"))
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
       self.containerchoice.append_text(_("No container (Audio-only)"))

       # Populate the rotatation box
       self.rotationlist = [_("No rotation (default)"),\
                            _("Clockwise 90 degrees"), \
                            _("Rotate 180 degrees"),
                            _("Counterclockwise 90 degrees"), \
                            _("Horizontal flip"),
                            _("Vertical flip"), \
                            _("Upper left diagonal flip"),
                            _("Upper right diagnonal flip") ]

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
       self.presetchoice.prepend_text(_("No Presets"))

       self.waiting_for_signal="False"
       
       # self.TopWindow.show_all() # show TopWindow.
       
   # Get all preset values
   def reverse_lookup(self,v):
       for k in codecfinder.codecmap:
           if codecfinder.codecmap[k] == v:
               return k

   def provide_presets(self, devicename):  #
       print "provide_presets:"
       devices = presets.get() # presets.py return _presets
       print "devices:", devices
       device = devices[devicename]
       print "device:", device
       preset = device.presets["Normal"] # get { container, videc , audec, extension... } 
       print "preset:", preset.vcodec.width # test input.
       self.usingpreset=True
       self.containerchoice.set_active(-1) # resetting to -1 to ensure population of menu triggers
       self.presetaudiocodec = preset.acodec.name
       print "self.presetaudiocodec", self.presetaudiocodec
       self.presetvideocodec = preset.vcodec.name
       print "self.presetvideocodec:", self.presetvideocodec
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
               min = rem / 60
               sec = rem % 60
               time_rem = _("%(min)d:%(sec)02d") % {
                   "min": min,
                   "sec": sec,
                   }
               if percent_remain > 0.5:
                   if self.passcounter == int(0):
                       txt = "Estimated time remaining: %(time)s"
                       self.ProgressBar.set_text(_(txt) % \
                               {'time': str(time_rem)})
                   else:
                       txt = "Pass %(count)d time remaining: %(time)s"
                       self.ProgressBar.set_text(_(txt) % { \
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
       # print "ProgressBar timeout_add startet"
       
   def _on_eos(self, source):
       context_id = self.StatusBar.get_context_id("EOS")
       if (self.multipass ==  False) or (self.passcounter == int(0)):
           self.StatusBar.push(context_id, (_("File saved to %(dir)s") % \
                   {'dir': self.outputdirectory}))
           self.FileChooser.set_sensitive(True)
           self.containerchoice.set_sensitive(True)
           self.CodecBox.set_sensitive(True)
           self.presetchoice.set_sensitive(True)
           self.cancelbutton.set_sensitive(False)
           self.transcodebutton.set_sensitive(True)
           self.rotationchoice.set_sensitive(True)
           self.start_time = False
           self.ProgressBar.set_text("Done Transcoding")           
           # self.task_index = min(self.task_index + 1, len(self.task_list) - 1) # task 
           self.task_list[self.task_index].Pipeline("null") # close Pipeline.
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
           self.StatusBar.push(context_id, (_("Pass %(count)d Complete") % \
                   {'count': self.passcounter}))
           self.start_time = False
           self.ProgressBar.set_text(_("Start next pass"))
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
       container = streaminfo.get_caps()
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
               self.audioinformation.set_markup(''.join(('<small>', _("No Audio"), '</small>')))
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
       print "on_FileChooser_file_set:"
       # self.filename = self.builder.get_object ("FileChooser").get_filename()
       self.form.path_entry.set_text(filename) # 现实完整路径
       self.filename = self.FileChooser.get_filename()
       print "self.filename:", self.filename
       self.audiodata = {}
       if self.filename is not None: 
           self.haveaudio=False #make sure to reset these for each file
           self.havevideo=False #
           self.mediacheck(self.filename)
           self.ProgressBar.set_fraction(0.0)
           self.ProgressBar.set_text(_("Transcoding Progress"))
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

   def conv_task_gui_start_btn_clicked(self, widget):      
      # ??
      self.start_conv_function()
      
   def start_conv_function(self):   
      try:
         self.task_list[self.task_index].Pipeline("playing")
         self.task_list[self.task_index].Pipeline("pause")
         self.task_list[self.task_index].Pipeline("playing")
      
         self._transcoder = self.task_list[self.task_index]
         self._transcoder.connect("ready-for-querying", self.ProgressBarUpdate)
         self._transcoder.connect("got-eos", self._on_eos)
         self._transcoder.connect("got-error", self.show_error)

         self.conv_task_gui.list_view.items[self.task_index].set_status_icon("working")
         self.ProgressBar = self.conv_task_gui.list_view.items[self.task_index]      
      except Exception, e:   
         print "start_conv_function[error]:", e
      
   def conv_task_gui_pause_btn_clicked(self, widget):   
      self.task_list[self.task_index].Pipeline("pause")
      self.conv_task_gui.list_view.items[self.task_index].set_status_icon("wait")
      
   def _start_transcoding(self): 
       # filechoice = self.builder.get_object ("FileChooser").get_uri()
       # self.filename = self.builder.get_object ("FileChooser").get_filename()
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

       # print "transcoder values - filechoice: " + str(filechoice) + " - filename: " + str(self.filename) + " - outputdirectory: " + str(self.outputdirectory) + " - self.container: " + str(self.container) + " - audiocodec: " + str(audiocodec) + " - videocodec: " + str(videocodec), " -self.devicename: " + str(self.devicename) + "- vheight:" + str(vheight), " - vwidth: " + str(vwidth) + " - achannels: " + str(achannels) + " - self.multipass " + str(self.multipass) + " - self.passcounter: " + str(self.passcounter) + " -self.outputfilename: " + str(self.outputfilename) + " - self.timestamp: " + str(self.timestamp) + " - self.rotationvalue: " + str(self.rotationvalue) + " - self.audiopasstoggle: " + str(self.audiopasstoggle) + " - self.videopasstoggle: " + str(self.videopasstoggle) + " - self.interlaced: " + str(self.interlaced) + " - self.inputvideocaps: " + str(self.inputvideocaps)
       # print "*****************************************"
       # print "vheight:", vheight
       # print "vwidth:", vwidth
       # print "ratenum:", ratenum
       # print "ratednom:", ratednom
       # print "*****************************************"
       # self._transcoder
       new_width, new_height = (int(vwidth), int(vheight))
       model_text = self.form.model_combo.get_active_text()
       
       if model_text != "No Model":
          new_width, new_height = self.form.model_dict[model_text]
          
       print "new_width:", new_width   
       # VIDEOCODECVALUE -->> videocodec   
       transcoder = transcoder_engine.Transcoder(filechoice, self.filename,
                        self.outputdirectory, self.container, audiocodec, 
                        videocodec, self.devicename, 
                        vheight, vwidth, ratenum, ratednom, achannels, 
                        self.multipass, self.passcounter, self.outputfilename,
                        self.timestamp, self.rotationvalue, self.audiopasstoggle, 
                        self.videopasstoggle, self.interlaced, self.inputvideocaps, int(new_width), int(new_height))
        
       # transcoder.connect("ready-for-querying", self.ProgressBarUpdate)
       # transcoder.connect("got-eos", self._on_eos)
       # transcoder.connect("got-error", self.show_error)       
       
       self.task_list.append(transcoder)
       self.conv_task_gui.list_view.add_items([MediaItem()])
       self.conv_task_gui.show_all()
       
       return True

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
                   _("Plugins not found, choose different codecs."))
           self.FileChooser.set_sensitive(True)
           self.containerchoice.set_sensitive(True)
           self.CodecBox.set_sensitive(True)
           self.cancelbutton.set_sensitive(False)
           self.transcodebutton.set_sensitive(True)
       elif donemessage == gst.pbutils.INSTALL_PLUGINS_USER_ABORT:
           context_id = self.StatusBar.get_context_id("EOS")
           self.StatusBar.push(context_id, _("Codec installation aborted."))
           self.FileChooser.set_sensitive(True)
           self.containerchoice.set_sensitive(True)
           self.CodecBox.set_sensitive(True)
           self.cancelbutton.set_sensitive(False)
           self.transcodebutton.set_sensitive(True)
       else:
           context_id = self.StatusBar.get_context_id("EOS")
           self.StatusBar.push(context_id, _("Missing plugin installation failed: ")) + gst.pbutils.InstallPluginsReturn()

   def check_for_elements(self):
       if self.container==False:
           containerstatus=True
           videostatus=True
       else:
           # containerchoice = self.builder.get_object ("containerchoice").get_active_text ()
           containerchoice = self.containerchoice.get_active_text()
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
       # self.FileChooser.set_sensitive(False)
       # self.containerchoice.set_sensitive(False)
       # self.presetchoice.set_sensitive(False)
       # self.CodecBox.set_sensitive(False)
       # self.transcodebutton.set_sensitive(False)
       # self.rotationchoice.set_sensitive(False)
       self.cancelbutton.set_sensitive(True)
       # self.ProgressBar.set_fraction(0.0)
       # create a variable with a timestamp code
       timeget = datetime.datetime.now()
       self.timestamp = str(timeget.strftime("-%H%M%S-%d%m%Y"))
       # Remove suffix from inbound filename so we can reuse it together with suffix to create outbound filename
       self.nosuffix = os.path.splitext(os.path.basename(self.filename))[0]
       # pick output suffix
       # container = self.builder.get_object ("containerchoice").get_active_text ()
       container = self.containerchoice.get_active_text()
       if self.container==False: # deal with container less formats
           self.ContainerFormatSuffix = codecfinder.nocontainersuffixmap[gst.Caps.to_string(self.AudioCodec)]
       else:
           if self.havevideo == False:
               self.ContainerFormatSuffix = codecfinder.audiosuffixmap[container]
           else:
               self.ContainerFormatSuffix = codecfinder.csuffixmap[container]
       self.outputfilename = str(self.nosuffix+self.timestamp+self.ContainerFormatSuffix)
       context_id = self.StatusBar.get_context_id("EOS")
       self.StatusBar.push(context_id, (_("Writing %(filename)s") % {'filename': self.outputfilename}))
       if self.multipass == False:
           self.ProgressBar.set_text(_("Transcoding Progress"))
       else:
           self.passcounter=int(1)
           self.ProgressBar.set_text(_("Pass %(count)d Progress") % {'count': self.passcounter})
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
       self.ProgressBar.set_text(_("Transcoding Progress"))
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
               self.audiorows[0].append_text(str(gst.pbutils.get_codec_description("audio/mpeg, mpegversion=(int)1, layer=(int)3")))
               self.audiorows[0].append_text(str(gst.pbutils.get_codec_description("audio/mpeg, mpegversion=4, stream-format=adts")))
               self.audiorows[0].append_text(str(gst.pbutils.get_codec_description("audio/x-flac")))
               self.audiocodecs.append(gst.Caps("audio/mpeg, mpegversion=(int)1, layer=(int)3"))
               self.audiocodecs.append(gst.Caps("audio/mpeg, mpegversion=4, stream-format=adts"))
               self.audiocodecs.append(gst.Caps("audio/x-flac"))
               self.audiorows[0].set_active(0)
               self.audiorows[0].set_sensitive(True)
           else:
               audio_codecs = []
               audio_codecs = supported_audio_container_map[self.container]
               for c in audio_codecs:
                   self.audiocodecs.append(gst.Caps(codecfinder.codecmap[c]))
               for c in audio_codecs:
                   self.audiorows[0].append_text(c)
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
                       self.videorows[0].append_text(c)
                   self.videorows[0].set_sensitive(True)
                   self.videorows[0].set_active(0)

                   #add a 'No Video option'
                   self.videorows[0].append_text(_("No Video"))
                   self.videocodecs.append("novid")
                   self.videonovideomenuno=(len(self.videocodecs))-1
                      
                   # add the Passthrough option 
                   if self.videopass==True:
                       self.videorows[0].append_text(_("Video passthrough"))
                       self.videocodecs.append("pass")
                       self.videopassmenuno=(len(self.videocodecs))-1
                   
                   if self.audiopass==True:
                       self.audiorows[0].append_text(_("Audio passthrough"))
                       self.audiocodecs.append("pass")
                       self.audiopassmenuno=(len(self.audiocodecs))-1

   def on_containerchoice_changed(self, widget, text):
       self.CodecBox.set_sensitive(True)
       self.ProgressBar.set_fraction(0.0)
       self.ProgressBar.set_text(_("Transcoding Progress"))
       # if self.builder.get_object("containerchoice").get_active() == self.nocontainernumber: containerchoice
       if self.containerchoice.get_active() == self.nocontainernumber:
               self.container = False
               self.videorows[0].set_active(self.videonovideomenuno)
               self.videorows[0].set_sensitive(False)
       else:
           # if self.builder.get_object("containerchoice").get_active()!= -1:
           if self.containerchoice.get_active()!= -1:
               # self.container = self.builder.get_object ("containerchoice").get_active_text ()
               self.container = self.containerchoice.get_active_text ()
               if self.discover_done == True:
                   self.check_for_passthrough(self.container)
           self.transcodebutton.set_sensitive(True)
       self.populate_menu_choices()

   def on_presetchoice_changed(self, widget):
       # presetchoice = self.builder.get_object ("presetchoice").get_active_text ()
       presetchoice = self.presetchoice.get_active_text ()
       self.ProgressBar.set_fraction(0.0)
       if presetchoice == _("No Presets"):
           self.usingpreset=False
           self.devicename = "nopreset"
           self.containerchoice.set_sensitive(True)
           self.containerchoice.set_active(0)
           self.start_time = False
           self.multipass = False
           self.passcounter = False
           self.rotationchoice.set_sensitive(True)
           # if self.builder.get_object("containerchoice").get_active_text():
           if self.containerchoice.get_active_text():
               self.populate_menu_choices()
               self.CodecBox.set_sensitive(True)
               self.transcodebutton.set_sensitive(True)
       else: # 手机产品信息. 
           self.usingpreset=True
           self.ProgressBar.set_fraction(0.0)
           self.devicename = self.presetchoices[presetchoice]
           print "======================================"
           print "on_presetchoice_changed:"
           print "self.devicename", self.devicename
           self.provide_presets(self.devicename)
           self.containerchoice.set_sensitive(False)
           self.CodecBox.set_sensitive(False)
           self.rotationchoice.set_sensitive(False)
           # if self.builder.get_object("containerchoice").get_active_text():
           if self.containerchoice.get_active_text():
               self.transcodebutton.set_sensitive(True)
           print "======================================="    
           
   def on_rotationchoice_changed(self, widget, text):
       self.rotationvalue = self.rotationchoice.get_active()

   def on_audiocodec_changed(self, widget, text):
       if (self.houseclean == False and self.usingpreset==False):
           self.AudioCodec = self.audiocodecs[self.audiorows[0].get_active()]
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
           # self.ProgressBar.set_text(_("Transcoding Progress"))
           self.ProgressBar.set_text("show_error")
           if error_string=="noaudioparser":
               error_message = _("No audio parser, passthrough not available")
               codecs = supported_container_map[self.container]
               self.AudioCodec = codecs[0]
               self.audiopasstoggle = False
           elif error_string=="novideoparser":
               error_message= _("No video parser, passthrough not available")
               codecs = supported_container_map[self.container]
               self.VideoCodec = codecs[1]
               self.videopasstoggle = False
           else:
               error_message=_("Uknown error")
       else:
         error_message = error_string
       context_id = self.StatusBar.get_context_id("EOS")
       self.StatusBar.push(context_id, error_message)


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
