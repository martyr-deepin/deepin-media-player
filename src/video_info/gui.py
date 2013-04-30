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

from skin          import app_theme
from locales       import _
from dtk.ui.gio_utils import get_file_icon_pixbuf
from dtk.ui.dialog import DialogBox, DIALOG_MASK_MULTIPLE_PAGE
from dtk.ui.label  import Label
from dtk.ui.button import Button
from dtk.ui.tab_window import TabBox
from dtk.ui.entry import InputEntry
from dtk.ui.line import HSeparator
from widget.utils    import get_play_file_type, length_to_time, get_play_file_name
from widget.utils import get_file_size
from widget.utils import open_file
import os
import gtk
import gobject


### video information GUI.
APP_TITLE = _("Properties")
APP_WIDTH = 490
APP_HEIGHT = 390
ICON_H     = 30
ICON_W     = 30

class VideoInformGui(gobject.GObject):
    def __init__(self, ldmp):
        gobject.GObject.__init__(self)
        # Init.
        self.player = ldmp.player
        # Init video widgets.
        self.init_video_widgets()
        # init code widgets.
        self.init_code_widgets()
        #
        self.app = DialogBox(APP_TITLE, 
                             APP_WIDTH, 
                             APP_HEIGHT,
                             mask_type = DIALOG_MASK_MULTIPLE_PAGE,
                             modal = False,
                             window_hint = gtk.gdk.WINDOW_TYPE_HINT_DIALOG,
                             window_pos = gtk.WIN_POS_CENTER,
                             resizable = False)
        self.tab_box = TabBox()
        self.close_button = Button(_("Close"))
        #
        # app.
        #
        self.app.connect("destroy", lambda w : self.app.destroy())
        #
        # tabbox.
        #        
        items = [(_("video information"), self.fixed_video), (_("decoding information"), self.fixed_code)] #
        self.tab_box.add_items(items)
        #
        # close_button.
        #
        self.close_button.connect("clicked", lambda w : self.app.destroy())        
        #
        self.app.right_button_box.set_buttons([self.close_button])
        self.app.body_box.pack_start(self.tab_box)        
        
    def show_window(self):
        self.app.show_all()
        # set file path entry start.
        self.file_path_text.entry.move_to_start()

    def get_information(self, path):    
        self.init_video_widgets(path)
        
    def init_video_widgets(self):        
        try:
            # ini vlaue.
            tabs = "   "
            describe = _("File path:") + "%s" % (tabs)
            self.widget_offset_x = 30
            self.widget_offset_y = 20
            #
            self.fixed_video      = gtk.Fixed()
            pixbuf = get_file_icon_pixbuf(self.player.uri, ICON_H)
            self.file_icon_image  = gtk.image_new_from_pixbuf(pixbuf)
            self.first_hseparator = HSeparator(app_theme.get_shadow_color("hSeparator").get_color_info(),
       0, 35)
            self.first_hseparator_hbox = gtk.HBox()
            self.file_name_label  = Label("   ", label_width = 350)
            self.file_type_label  = Label(_("File type:") + "%s%s" % (tabs, get_play_file_type(self.player.uri)))
            self.resolution_label = Label(_("Resolution:") + "%s%sx%s" % (tabs, self.player.video_width, self.player.video_height))
            self.file_size_label  = Label(_("File size:") + "%s%s" % (tabs, get_file_size(self.player.uri)))
            self.length_label     = Label(_("Duration:") + "%s%s" % (tabs, self.player.length))
            self.second_hseparator = HSeparator(app_theme.get_shadow_color("hSeparator").get_color_info(), 0, 35)
            self.second_hseparator_hbox = gtk.HBox()            
            self.file_path_label  = Label(describe, enable_select=False, wrap_width=420)
            self.file_path_text = InputEntry(str(self.player.uri))
            self.open_file_path_btn = Button(_("Open directory"))
            #
            # first_heparator_hbox.
            #
            self.first_hseparator_hbox.set_size_request(APP_WIDTH-15, 1)
            self.first_hseparator_hbox.pack_start(self.first_hseparator)
            #
            # second_hseparator_hbox.
            #
            self.second_hseparator_hbox.set_size_request(APP_WIDTH-15, 1)
            self.second_hseparator_hbox.pack_start(self.second_hseparator)
            #
            # file_path_text.
            #
            # self.file_path_text.set_sensitive(False)
            self.file_path_text.set_size(260, 25)            
            #
            # open_file_path_btn.
            #            
            self.open_file_path_btn.connect("clicked", self.open_file_path_btn_clicked)
            icon_width = 30
            #
            self.widgets_list = [
                (self.file_icon_image, self.widget_offset_x, self.widget_offset_y),
                (self.file_name_label, self.widget_offset_x + icon_width + 10, self.widget_offset_y + 10),
                (self.first_hseparator_hbox, 0, self.widget_offset_y + 15),
                (self.file_type_label, self.widget_offset_x, self.widget_offset_y + 65),
                (self.resolution_label, self.widget_offset_x + 130, self.widget_offset_y + 65),
                (self.file_size_label, self.widget_offset_x , self.widget_offset_y + 85),
                (self.length_label, self.widget_offset_x + 130, self.widget_offset_y + 85),
                (self.second_hseparator_hbox, 0, self.widget_offset_y + 85),
                (self.file_path_label, self.widget_offset_x, self.widget_offset_y + 140),
                (self.file_path_text, self.widget_offset_x + 60, self.widget_offset_y + 136),
                (self.open_file_path_btn, self.widget_offset_x + 325, self.widget_offset_y + 136)
            ]                       
            #
            for widget, x, y in self.widgets_list:
                self.fixed_video.put(widget, x, y)
        except Exception, e:
            print "video info...init_video_widgets-->>>[error],", e
                
            
    def open_file_path_btn_clicked(self, widget):
        open_file(str(self.player.uri), True)
            
    def init_code_widgets(self):
        try:
            # Init value.
            self.copy_clipboard = gtk.Clipboard()
            self.widget_x = 20
            self.widget_y = 20
            tabs = "   "
            #
            try:
                scaling = str(round(float(self.player.video_width) / self.player.video_height, 3))
            except:
                scaling = 0
            try:
                bit_rate = str(int(self.player.video_bitrate) / 1000) + " kbps"
            except:
                bit_rate = 0
            self.fixed_code = gtk.Fixed()
            self.video_strem_info_label = Label(_("Video stream info:"))
            self.code_format_label      = Label(_('.Codec format:') + "%s%s" % (tabs, self.player.video_format))
            self.video_fps_label        = Label(_(".Frame rate:") + "%s%s" % (tabs, self.player.video_fps))
            self.video_display_asscept_label = Label(_(".Scaling:") + "%s%s" % (tabs, scaling))
            self.video_malv_label = Label(_(".Video bit rate:") + "%s%s " % (tabs, bit_rate))
            self.video_resolution_label = Label(_(".Resolution:") + "%s%s" % (tabs, str(self.player.video_width) + "x" + str(self.player.video_height)))
            self.hseparator = HSeparator(app_theme.get_shadow_color("hSeparator").get_color_info(), 0, 35)
            self.hseparator_hbox = gtk.HBox()
            self.audio_strem_info_label = Label(_("Audio stream info:"))
            self.audio_format_label     = Label(_(".codec format:") + "%s%s" % (tabs, self.player.audio_format))
            self.audio_channels_number_label = Label(_(".track number:") + "%s%s " % (tabs, self.player.audio_nch + " channels"))
            self.audio_weishu_label = Label(_(".Audio digit:") + "%s%s " % (tabs, str(int(self.player.audio_nch) * 8) + " bits"))
            self.audio_malv_label = Label(_(".Audio bit rate:") + "%s%s" % (tabs, str(int(self.player.audio_bitrate) / 1000) + " kbps"))
            self.audio_sampling_label = Label(_(".Sampling:") + "%s%s " % (tabs, self.player.audio_rate + " Hz"))
            self.copy_info_btn = Button(_("Copy info"))
            # Init widgets top left.
            self.widgets_top_left = [
                self.video_strem_info_label,
                self.code_format_label,
                self.video_fps_label,
                self.video_display_asscept_label,                
                ]            
            # Init widgets bottom left.    
            self.widgets_bottom_left = [
                self.audio_strem_info_label,
                self.audio_format_label,
                self.audio_channels_number_label,
                self.audio_weishu_label,
                ]
            #
            # hseparator
            #
            self.hseparator_hbox.set_size_request(APP_WIDTH - 15, 1)
            self.hseparator_hbox.pack_start(self.hseparator)            
            #
            # copy_info_btn
            #
            self.copy_info_btn.connect("clicked", self.copy_info_btn_clicked)
            # Init widgets top right.
            self.widgets_top_right = [
                self.video_malv_label,
                self.video_resolution_label,                
                ]            
            # Init widgets bottom right.
            self.widgets_bottom_right = [
                self.audio_malv_label,
                self.audio_sampling_label
                ]            
                        
            # fixed_code add top left widgets.
            widget_top_left_y = self.widget_y
            for widget_top_left in self.widgets_top_left:
                self.fixed_code.put(widget_top_left, self.widget_x, widget_top_left_y)
                widget_top_left_y += 20
            # fixed_code add bottom left widgets.    
            widget_bottom_left_y = self.widget_y + widget_top_left_y + 10
            for widget_bottom_left in self.widgets_bottom_left:
                self.fixed_code.put(widget_bottom_left, self.widget_x, widget_bottom_left_y)
                widget_bottom_left_y += 20            
            # fixed_code add top right widgets.    
            widget_right_x = self.widget_x + 200
            widget_top_right_y = self.widget_y  + 20              
            for widget_top_right in self.widgets_top_right:
                self.fixed_code.put(widget_top_right, widget_right_x, widget_top_right_y)
                widget_top_right_y += 20
            # fixed_code add bottom right widgets.    
            widget_bottom_right_y = self.widget_y + widget_top_right_y + 50
            for widget_bottom_right in self.widgets_bottom_right:
                self.fixed_code.put(widget_bottom_right, widget_right_x, widget_bottom_right_y)
                widget_bottom_right_y += 20
            #    
            self.fixed_code.put(self.hseparator_hbox, 0, widget_top_left_y-22)
            self.fixed_code.put(self.copy_info_btn, 370, 245)
        except Exception, e:
            print "video_info.. gui.py..init_code_widgets[error]", e
        
    def copy_info_btn_clicked(self, widget):        
        copy_info_text = "%s\n\n%s\t%s\n\n%s\t%s\n\n%s\n\n------------------------------------------------\n\n%s\n\n%s\t\t%s\n\n%s\t%s\n\n%s\n\n" % (self.video_strem_info_label.get_text(), 
                           self.code_format_label.get_text(),
                           self.video_malv_label.get_text(),
                          self.video_fps_label.get_text(),
                          self.video_resolution_label.get_text(),
                          self.video_display_asscept_label.get_text(),
                          self.audio_strem_info_label.get_text(),
                          self.audio_format_label.get_text(),
                          self.audio_malv_label.get_text(),
                          self.audio_channels_number_label.get_text(),
                          self.audio_sampling_label.get_text(),
                          self.audio_weishu_label.get_text(),
                          )
        self.copy_clipboard.set_text(copy_info_text)
        
        
