#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Wang Yong
# 
# Author:     Wang Yong <lazycat.manatee@gmail.com>
# Maintainer: Wang Yong <lazycat.manatee@gmail.com>
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


from skin import app_theme
from dtk.ui.draw import draw_vlinear
from dtk.ui.dialog import DialogBox, DIALOG_MASK_SINGLE_PAGE
from dtk.ui.entry import InputEntry
from dtk.ui.draw import draw_vlinear
from file_choose_button import FileChooserButton
from dtk.ui.button import Button
from dtk.ui.label import Label
from dtk.ui.combo import ComboBox
from dtk.ui.utils import container_remove_all
from new_combobox import NewComboBox
from new_button import LabelButton
from read_xml import ReadXml

import gtk
import os

from locales import _

form_size = eval(_("('form_size', 500, 180)"))

FORM_WIDTH = int(form_size[1])
# FORM_HEIGHT = 280
FORM_HEIGHT = int(form_size[2])


class Form(DialogBox):
    def __init__(self):
        DialogBox.__init__(self, 
                           _("Convert"), 
                           FORM_WIDTH, FORM_HEIGHT, 
                           mask_type=DIALOG_MASK_SINGLE_PAGE,
                           close_callback=self.hide_all,
                           modal=True,                           
                           window_hint=gtk.gdk.WINDOW_TYPE_HINT_DIALOG,
                           window_pos=gtk.WIN_POS_CENTER,
                           # skip_taskbar_hint=False,
                           resizable=False,
                           )                        
        # Init value.
        self.init_value()
        # Init all widgets.
        self.InitializeComponent()
        
    def init_value(self): 
        read_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "xml")
        self.read_xml = ReadXml(read_path)
        self.model_dict = {}

        # init brand EN list.
        self.brand_dict = {
            "intel" : _("intel"), "zte"   : _("zte"), "hasee" : _("hasee"),
            "apple" : _("apple"), "nokia" : _("nokia"), "alcatel" : _("alcatel"), 
            "google" : _("google"), "asus" : _("asus"), "hp" : _("hp"), 
            "sony" : _("sony"), "hedy" : _("hedy"), 
            "archos" : _("archos"), "boway" : _("boway"), "bird" : _("bird"), 
            "vivo" : _("vivo"), "great wall" : _("great wall"), "changhong" : _("changhong"), 
            "skyworth" : _("skyworth"), "dell" : _("dell"), "philips" : _("philips"), 
            "toshiba" : _("toshiba"), "amazon" : _("amazon"), "sdo" : _("sdo"), 
            "disney" : _("disney"), "haier" : _("haier"), "fujitsu" : _("fujitsu"), 
            "acer" : _("acer"), "lenovo" : _("lenovo"), "gigabyte" : _("gigabyte"), 
            "xiaomi" : _("xiaomi"), "huawei" : _("huawei"), "blackberry" : _("blackberry"), 
            "motorola" : _("motorola"), "sangsung" : _("sangsung"), "meizu " : _("meizu "), 
            "benq" : _("benq"), "panasonic" : _("panasonic"), "sony ericsson" : _("sony ericsson"), 
            "pioneer" : _("pioneer"), "hyundai" : _("hyundai"), "newman" : _("newman"), 
            "coolpad" : _("coolpad"), "malata" : _("malata"), "malata" : _("malata"), 
            "sharp" : _("sharp"), "gionee" : _("gionee"), "k-touch" : _("k-touch"), 
            "Pantech" : _("Pantech"), "hisense" : _("hisense"), "teclast" : _("teclast"), 
            "cube" : _("cube"), "amoi" : _("amoi"), "doov" : _("doov"), 
            "minte" : _("minte"), "dopod" : _("dopod"), "eton" : _("eton"), 
            "cherr" : _("cherr"), "gaoxinqi" : _("gaoxinqi"), "konka" : _("konka"), 
            "viewsonic" : _("viewsonic"), "xibo" : _("xibo"), "hosin" : _("hosin"), 
            "apanda" : _("apanda"), "iocean" : _("iocean"), "mastone" : _("mastone")
            }        
        
    def InitializeComponent(self):
        # Init form event.
        # self.connect("destroy", lambda w : self.destroy())
        self.connect("destroy", lambda w : self.hide_all())
        # Init widgets.
        self.brand_label = Label(_("phone brand : "))
        self.format_label = Label(_("Output format : "))        
        self.bit_rate_label = Label(_("Audio encoder : "))
        self.frame_rate_label = Label(_("Video encoder : "))
        self.path_label = Label(_("Output directory : "))
        self.model_label = Label(_("Phone model : "))
        self.ratio_label = Label('    ' + _("Resolution : "))        
        
        self.path_entry = InputEntry()
        self.save_path_entry = InputEntry()
        fixed_width = 108       
        self.brand_combo = NewComboBox(fixed_width)
        self.format_combo = NewComboBox(fixed_width)
        self.bit_rate_combo = NewComboBox(fixed_width)
        self.frame_rate_combo = NewComboBox(fixed_width)
        self.model_combo = NewComboBox(fixed_width)
        self.ratio_combo = NewComboBox(fixed_width) 
        
        self.modify_chooser_btn = FileChooserButton("选择") # connect self.FileChooser
        self.save_chooser_btn = Button(_("Change"))
        self.start_btn = Button(_("Start"))
        self.close_btn = Button(_("Close"))
        self.higt_set_bool = False
        self.higt_set_btn = LabelButton()#Button(_("Advanced"))
        
        self.show_and_hide_task_btn = Button(_("Task Manager"))
        
        self.higt_hbox = gtk.HBox()
        self.higt_hbox.pack_start(self.higt_set_btn)
        
        self.higt_align = gtk.Alignment()
        self.higt_align.add(self.higt_hbox)
        self.higt_align.set_padding(0, 0, 7, 0)
        self.higt_align.set(1, 0, 1, 0)
        
        self.left_button_box.set_buttons([self.higt_align])
        self.right_button_box.set_buttons([self.start_btn, self.close_btn])
        
        # ratio_combo.
        self.__ratio_list = ["176 x 220", "240 x 320", "320 x 240", 
                             "320 x 480", "400 x 240", "480 x 800", 
                             "540 x 960", "600 x 1024", "640 x 480", 
                             "720 x 1280", "800 x 480", "800 x 600", 
                             "1024 x 600", "1024 x 768", "1152 x 864",
                             ]    
        self.ratio_items = []
        for ratio in self.__ratio_list:
            self.ratio_combo.append_text(ratio)
            self.ratio_items.append((ratio, ratio))
        self.ratio_combo.set_active(5)            
        # brand_combo.
        brand_items = []
        for brand in self.read_xml.brand_dict.keys():
            brand_po = brand
            if self.brand_dict.has_key(brand):
                brand_po = self.brand_dict[brand]
            brand_items.append((brand_po, brand))
        
        self.brand_combo.set_items(brand_items, 0) 
        #self.brand_combo.add_items(brand_items, 0)
        
        self.brand_combo.prepend_text(_("No Presets"))
        self.brand_combo.connect("changed", self.brand_combo_item_selected)
        # model_combo.
        self.model_label.set_sensitive(False)
        self.model_combo.set_sensitive(False)
        self.model_combo.prepend_text(_("No Model"))
        self.model_combo.connect("changed", self.model_combo_item_selected)
        # 
        self.save_chooser_btn.set_size_request(75, 21)
        self.save_chooser_btn.connect("clicked", self.save_chooser_btn_clicked)
        
        # path_entry.
        PATH_ENTRY_WIDTH = 240
        PATH_ENTRY_HEIGHT = 22
        self.save_path_entry.set_sensitive(False)
        self.save_path_entry.set_text(self.get_home_path())
        self.save_path_entry.set_size(PATH_ENTRY_WIDTH, PATH_ENTRY_HEIGHT)
        self.close_btn.connect("clicked", lambda w : self.hide_all())
        # higt_set_btn.
        self.higt_set_btn.connect("clicked", self.higt_set_btn_clicked)
        
        # form body box add main fixed.
        self.body_table_ali = gtk.Alignment()
        self.body_table_ali.set_padding(6, 0, 0, 0)
        self.body_table = gtk.Table(rows=6, columns=4, homogeneous=False)
        self.body_table_ali.add(self.body_table)
        
        self.brand_model_hbox = gtk.HBox()    
        top, bottom = 5, 5
        brand_position = eval(_("('brand_position', 20)"))
        model_position = eval(_("('model_position', 20)"))
        self.brand_hbox_ali, self.brand_hbox = self.create_hbox(bottom, top, 15 + int(brand_position[1]), 0, self.brand_label, self.brand_combo)
        self.model_hbox_ali, self.model_hbox = self.create_hbox(bottom, top, 50 - int(model_position[1]), 0, self.model_label, self.model_combo)
        
        self.brand_model_hbox.pack_start(self.brand_hbox_ali, False, False)
        self.brand_model_hbox.pack_start(self.model_hbox_ali, False, False)
        format_position = eval(_("('format_position', 12)"))
        ratio_position = eval(_("('ratio_position', 18)"))
        self.format_hbox_ali, self.format_hbox = self.create_hbox(bottom, top, 15 + int(format_position[1]), 0, self.format_label, self.format_combo)
        self.ratio_hbox_ali, ratio_hbox = self.create_hbox(bottom, top, 50 - int(ratio_position[1]), 0, self.ratio_label, self.ratio_combo)
        
        self.format_ratio_hbox = gtk.HBox()
        self.format_ratio_hbox.pack_start(self.format_hbox_ali, False, False)
        self.format_ratio_hbox.pack_start(self.ratio_hbox_ali, False, False)
                
        frame_rate_position = eval(_("('frame_position', 13)"))
        bit_rate_position = eval(_("('bit_rate_position', 28)"))
        self.frame_rate_hbox_ali, self.frame_rate_hbox = self.create_hbox(bottom, top, 15 + int(frame_rate_position[1]), 0, self.frame_rate_label, self.frame_rate_combo)
        self.bit_rate_hbox_ali, self.bit_rate_hbox = self.create_hbox(bottom, top, 50 - int(bit_rate_position[1]), 0, self.bit_rate_label, self.bit_rate_combo)
        
        self.bit_frame_hbox = gtk.HBox()        
        self.bit_frame_hbox.pack_start(self.frame_rate_hbox_ali, False, False)
        self.bit_frame_hbox.pack_start(self.bit_rate_hbox_ali, False, False)
        
        # self.path_label, self.save_path_entry, self.save_chooser_btn
        self.save_path_hbox_ali = gtk.Alignment()
        self.save_path_hbox = gtk.HBox()
        self.save_path_hbox_ali.set_padding(5, 5, 16, 0)
        self.save_path_hbox_ali.add(self.save_path_hbox)
                
        self.save_path_entry_ali = gtk.Alignment()
        self.save_path_entry_ali.set_padding(1, 0, 0, 0)
        self.save_path_entry_ali.add(self.save_path_entry)
        
        self.save_chooser_btn_ali = gtk.Alignment()
        self.save_chooser_btn_ali.set_padding(0, 0, 10, 0)
        self.save_chooser_btn_ali.add(self.save_chooser_btn)
        
        self.save_path_hbox.pack_start(self.path_label, False, False)
        self.save_path_hbox.pack_start(self.save_path_entry_ali, False, False)
        self.save_path_hbox.pack_start(self.save_chooser_btn_ali, False, False)
        
        # left right top, bottom.
        '''brand_model_hbox.'''
        # self.body_table.attach(self.brand_model_hbox, 0, 1, 0, 1, gtk.EXPAND, gtk.EXPAND)
        self.body_table.attach(self.brand_model_hbox, 0, 1, 0, 1, gtk.FILL, gtk.FILL)
        # self.body_table.attach(self.model_hbox, 1, 2, 0, 1, gtk.EXPAND, gtk.EXPAND)
        # self.body_table.attach(self.model_hbox, 2, 3, 0, 1, gtk.EXPAND, gtk.EXPAND)
        # self.body_table.attach(self.model_hbox, 3, 4, 0, 1, gtk.EXPAND, gtk.EXPAND)
        '''format_ratio_hbox.'''
        # self.body_table.attach(self.format_ratio_hbox, 0, 1, 1, 2, gtk.EXPAND, gtk.EXPAND)
        self.body_table.attach(self.format_ratio_hbox, 0, 1, 1, 2, gtk.FILL, gtk.FILL)
        # self.body_table.attach(self.format_combo, 1, 2, 1, 2, gtk.EXPAND, gtk.EXPAND)
        # self.body_table.attach(self.ratio_hbox, 2, 3, 1, 2, gtk.EXPAND, gtk.EXPAND)
        # self.body_table.attach(self.ratio_combo, 3, 4, 1, 2, gtk.EXPAND, gtk.EXPAND)
        '''bit_frame_hbox.'''
        # self.body_table.attach(self.bit_frame_hbox, 0, 1, 2, 3, gtk.EXPAND, gtk.EXPAND)
        self.body_table.attach(self.bit_frame_hbox, 0, 1, 2, 3, gtk.FILL, gtk.FILL)
        '''save_path_hbox.'''
        # self.body_table.attach(self.save_path_hbox_ali, 0, 1, 3, 4, gtk.EXPAND, gtk.EXPAND)
        self.body_table.attach(self.save_path_hbox_ali, 0, 1, 3, 4, gtk.FILL, gtk.FILL)
                
        self.body_box.pack_start(self.body_table_ali, True, True)
        self.hide_setting()
        
    def create_hbox(self, top, bottom, left, right, child1, child2):
        hbox_ali = gtk.Alignment()
        hbox_ali.set_padding(top, bottom, left, right)
        hbox = gtk.HBox()        
        hbox_ali.add(hbox)
        hbox.pack_start(child1, False, False)
        hbox.pack_start(child2, False, False)
        return hbox_ali, hbox
        
    def get_home_path(self):
        return os.path.expanduser("~")
        
    def save_chooser_btn_clicked(self, widget):
        '''保存目录... ...'''
        self.show_open_dir_dialog_window()
        
    def show_open_dir_dialog_window(self):
        open_dialog = gtk.FileChooserDialog(
                         _("Choose a directory"),
                         None,
                         gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                         (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                          gtk.STOCK_OPEN, gtk.RESPONSE_OK)
                         )
        # current floader set.
        open_dialog.set_current_folder(self.get_home_path())
        # run dir dialog window.
        res = open_dialog.run()
        
        if res == gtk.RESPONSE_OK:
            path_string = open_dialog.get_filename()
            if path_string:
                self.save_path_entry.set_text(path_string)
        # destroy dialog window.        
        open_dialog.destroy()       
    
    def brand_combo_item_selected(self, combo, item_content):
        self.model_combo.clear_items()
        self.ratio_combo.clear_items()
        #
        try:
            self.model_dict = self.read_xml.load(self.read_xml.brand_dict[item_content])
        except Exception, e:    
            print "brand_combo_item_selected[error]:", e
            self.model_dict = {}
        #    
        if item_content != _("No Presets") and self.model_dict != {}:
            model_items = []
            for model in self.model_dict:
                model_items.append((model, model))
            self.model_combo.set_items(model_items, 0)    
            
            # self.model_combo.droplist.set_size_request(-1, self.model_combo.droplist_height)
            self.model_combo.set_active(0)            
            self.model_combo.set_sensitive(True)
            self.model_label.set_sensitive(True)
        else:        
            # clear model and ratio all text.
            self.model_combo.append_text(_("No Model"))
            self.model_combo.set_sensitive(False)            
            self.model_label.set_sensitive(False)
            # add ratios.
            for ratio in self.ratio_items:
                self.ratio_combo.append_text(ratio[0])
            self.ratio_combo.set_active(5)    
            
    def model_combo_item_selected(self, combo, item_content):        
        if len(item_content):
            width, height = self.model_dict[item_content]
            self.ratio_combo.clear_items()
            self.ratio_combo.prepend_text("%s x %s"%(width, height))
            
    def higt_set_btn_clicked(self, widget):    
        if not self.higt_set_bool:
            self.hide_all_new()            
        else:    
            self.show_all_new()
            
        self.higt_set_bool = not self.higt_set_bool                 
               
    def show_all_new(self):    
        self.show_all()
        self.hide_setting()
        self.higt_set_btn.show_all()        
        
    def hide_all_new(self):    
        self.higt_set_btn.hide_all()
        self.show_setting()
        
    def hide_setting(self):
        self.bit_frame_hbox.hide_all()
        self.set_geometry_hints(None, FORM_WIDTH, FORM_HEIGHT, 
                                FORM_WIDTH, FORM_HEIGHT, -1, -1, -1, -1, -1, -1)
        self.set_size_request(FORM_WIDTH, FORM_HEIGHT)
        
    def show_setting(self):
        self.bit_frame_hbox.show_all()
        add_width = 30
        self.set_geometry_hints(None, FORM_WIDTH, FORM_HEIGHT + add_width, 
                                FORM_WIDTH, FORM_HEIGHT + add_width, -1, -1, -1, -1, -1, -1)
        self.set_size_request(FORM_WIDTH, FORM_HEIGHT + add_width)        
    
if __name__ == "__main__":
    form = Form()
    form.show_all()
    form.hide_setting()
    # form.hide_setting()
    # form.show_setting()
    gtk.main()
    
    
