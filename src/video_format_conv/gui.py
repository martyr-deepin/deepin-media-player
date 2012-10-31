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
from new_combobox import NewComboBox
from read_xml import ReadXml

import gtk
import os

from locales import _

FORM_WIDTH = 425
FORM_HEIGHT = 280


class Form(DialogBox):
    def __init__(self):
        DialogBox.__init__(self, 
                           _("Format converter"), 
                           FORM_WIDTH, FORM_HEIGHT- 80, 
                           mask_type=DIALOG_MASK_SINGLE_PAGE,
                           close_callback=self.hide_all,
                           modal=False,                           
                           window_hint=gtk.gdk.WINDOW_TYPE_HINT_DIALOG,
                           window_pos=gtk.WIN_POS_CENTER,
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
        # left.
        self.left_x = 20
        self.left_y = 20
        self.left_offset_x = 0
        self.left_offset_y = 0
        # right.
        # self.right_x = 200
        self.right_x = 180
        self.right_y = 20
        self.right_offset_x = 0
        self.right_offset_y = 0
        # move.
        self.move_offset_x = 0
        self.move_offset_y = 0
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
        self.main_fixed = gtk.Fixed()
        self.brand_label = Label(_("phone brand : "))
        self.format_label = Label(_("Output format : "))        
        self.bit_rate_label = Label(_("Audio encoder : "))
        self.frame_rate_label = Label(_("Video encoder : "))
        self.path_label = Label(_("Output directory : "))
        self.model_label = Label(_("Phone model : "))
        self.ratio_label = Label('    ' + _("Resolution : "))        
        
        self.path_entry = InputEntry()
        self.save_path_entry = InputEntry()
        self.brand_combo = NewComboBox(110) #ComboBox(supported_containers_imtes, 100, max_width=110)
        self.format_combo = NewComboBox(110) #ComboBox(supported_containers_imtes, 100, max_width=110) # connect         
        self.bit_rate_combo = NewComboBox(110) #ComboBox(supported_containers_imtes, 100)
        self.frame_rate_combo = NewComboBox(110) #ComboBox(supported_containers_imtes, 100)        
        self.model_combo = NewComboBox(110) #ComboBox(supported_containers_imtes, 100)
        self.ratio_combo = NewComboBox(110) #ComboBox(supported_containers_imtes, 100) # Resolution
        
        self.modify_chooser_btn = FileChooserButton("选择") # connect self.FileChooser
        self.save_chooser_btn = Button(_("Change"))
        self.start_btn = Button(_("Start"))
        self.close_btn = Button(_("Close"))
        self.higt_set_bool = False
        self.higt_set_btn = Button(_("Advanced"))
        
        self.show_and_hide_task_btn = Button(_("Task manager"))
        
        self.higt_hbox = gtk.HBox()
        self.higt_hbox.pack_start(self.higt_set_btn)
        # self.higt_hbox.pack_start(self.show_and_hide_task_btn)
        
        self.higt_align = gtk.Alignment()
        # self.align.add(self.higt_set_btn)
        self.higt_align.add(self.higt_hbox)
        self.higt_align.set(1, 0, 1, 0)
        self.higt_align.set_padding(0, 0, 0, 170)
        
        self.right_button_box.set_buttons([self.higt_align, self.start_btn, self.close_btn])
        
        # brand_combo.
        brand_items = []
        for brand in self.read_xml.brand_dict.keys():
            brand_po = brand
            if self.brand_dict.has_key(brand):
                brand_po = self.brand_dict[brand]
            brand_items.append((brand_po, brand))
            
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
        self.brand_combo.set_items(brand_items, 0, max_width=200)
        
        self.brand_combo.prepend_text(_("No Presets"))
        self.brand_combo.connect("changed", self.brand_combo_item_selected)
        # model_combo.
        self.model_label.set_sensitive(False)
        self.model_combo.set_sensitive(False)
        self.model_combo.prepend_text(_("No Model"))
        self.model_combo.connect("changed", self.model_combo_item_selected)
        # ratio_combo.
        # self.ratio_combo.set_items(self.ratio_items)
        # for ratio in self.ratio_combo:
            # self.ratio_combo.append((ratio, ratio))

        self.save_chooser_btn.connect("clicked", self.save_chooser_btn_clicked)
        # format combo.
        # self.format_combo.set_active(0)                
        
        # path_entry.
        PATH_ENTRY_WIDTH = 235
        PATH_ENTRY_HEIGHT = 23
        self.save_path_entry.set_sensitive(False)
        self.save_path_entry.set_text(self.get_home_path())
        self.save_path_entry.set_size(PATH_ENTRY_WIDTH, PATH_ENTRY_HEIGHT)
        self.close_btn.connect("clicked", lambda w : self.hide_all())
        # higt_set_btn.
        self.higt_set_btn.connect("clicked", self.higt_set_btn_clicked)
        
        ''' add all widgets. '''
        #
        self.left_widgets = [self.brand_label, self.brand_combo, self.format_label, self.format_combo,
                             self.bit_rate_label, self.bit_rate_combo, self.frame_rate_label, self.frame_rate_combo,
                             self.path_label, self.save_path_entry, self.save_chooser_btn]
        # add left widgets.
        for widget in self.left_widgets:
            if widget:
                self.main_fixed.put(widget, 0, 0)
        #    
        self.right_widgets = [(self.model_label, self.model_combo),
                              (self.ratio_label, self.ratio_combo)]
        
        self.right_x += 40
        # add right widgets.
        for label, combo in self.right_widgets:
            padding_width, padding_height = label.get_size_request()
            padding_y = int(padding_height/3.5)
            self.main_fixed.put(label,
                                self.right_x,
                                self.right_y + self.right_offset_y - padding_y + 3)
            self.main_fixed.put(combo, 
                                self.right_x + padding_width + 5, 
                                self.right_y + self.right_offset_y - padding_y) 
            self.right_offset_y += 40
            
        # form body box add main fixed.
        self.body_box.pack_start(self.main_fixed, True, True)            
        self.hide_setting()
                
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
            self.model_combo.set_items(model_items, 0, max_width=200)    
            
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
        
    def hide_set_window_hints(self):        
        self.hide_setting()
        self.set_geometry_hints(None, FORM_WIDTH, FORM_HEIGHT-80, FORM_WIDTH, FORM_HEIGHT-80, -1, -1, -1, -1, -1, -1)
        self.set_size_request(FORM_WIDTH, FORM_HEIGHT-80)
        
    def higt_set_btn_clicked(self, widget):    
        if self.higt_set_bool:
            self.hide_set_window_hints()            
        else:    
            self.show_setting()
            self.set_geometry_hints(None, FORM_WIDTH, FORM_HEIGHT, FORM_WIDTH, FORM_HEIGHT, -1, -1, -1, -1, -1, -1)
            self.set_size_request(FORM_WIDTH, FORM_HEIGHT+80) 
            self.higt_set_btn.hide()
            
        self.higt_set_bool = not self.higt_set_bool
        
    def move_left_widgets(self):        
        self.init_value()
        other_padding_x = 5
        button_padding_x = 10
        #
        for label, other, button in self.left_widgets:
            padding_width, padding_height = label.get_size_request()
            padding_y = int(padding_height/3.5)
            # main fixed add label widget.
            self.main_fixed.move(label, 
                                self.left_x, 
                                self.left_y + self.left_offset_y)
            # main fixed add other widget.            
            # print other
            self.main_fixed.move(other, 
                                self.left_x + padding_width + other_padding_x, 
                                self.left_y + self.left_offset_y - padding_y)
            if button:
                # main fixed add button widget.                
                padding_y += 1
                self.main_fixed.move(button, 
                                    self.left_x + padding_width + other.get_size_request()[0] + button_padding_x, 
                                    self.left_y + self.left_offset_y - padding_y) 
            # set left offset y -> left_offset_y + 40. 
            self.left_offset_y += 40                          
        self.main_fixed.show_all()
        
    def hide_setting(self):    
        # hide widget.
        #     
        self.left_widgets = [(self.brand_label, self.brand_combo, None),
                             (self.format_label, self.format_combo, None),
                             (self.path_label, self.save_path_entry, self.save_chooser_btn),
                             ]
        
        self.move_left_widgets()        
        
        for hide_widget in [self.bit_rate_label, self.bit_rate_combo, self.frame_rate_label, self.frame_rate_combo]:
            hide_widget.hide_all()
        
    def show_setting(self):
        # show widget.
        #
        self.left_widgets = [(self.brand_label, self.brand_combo, None),
                             (self.format_label, self.format_combo, None),
                             (self.bit_rate_label, self.bit_rate_combo, None),
                             (self.frame_rate_label, self.frame_rate_combo, None),
                             (self.path_label, self.save_path_entry, self.save_chooser_btn),
                             ]
        self.move_left_widgets()
        self.show_all()
        
if __name__ == "__main__":
    form = Form()
    form.show_all()
    form.hide_setting()
    # form.hide_setting()
    # form.show_setting()
    gtk.main()
    
    
