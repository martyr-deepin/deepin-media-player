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
from dtk.ui.dialog import DialogBox, DIALOG_MASK_MULTIPLE_PAGE
from dtk.ui.entry import InputEntry
from file_choose_button import FileChooserButton
from dtk.ui.button import Button
from dtk.ui.label import Label
from dtk.ui.combo import ComboBox
from new_combobox import NewComboBox
from read_xml import ReadXml

import gtk
import os

from locales import _

FORM_WIDTH = 465
FORM_HEIGHT = 280


class Form(DialogBox):
    def __init__(self):
        DialogBox.__init__(self, 
                           _("Format converter"), 
                           FORM_WIDTH, FORM_HEIGHT- 80, 
                           mask_type=DIALOG_MASK_MULTIPLE_PAGE,
                           modal=False,
                           window_hint=gtk.gdk.WINDOW_TYPE_HINT_DIALOG,
                           window_pos=gtk.WIN_POS_CENTER,
                           resizable=False
                           )                        
        # Init value.
        self.init_value()
        # Init all widgets.
        self.InitializeComponent()
        self.draw_mask = self.draw_dialogbox_mask
        
    def draw_dialogbox_mask(self, cr, x, y, width, height):
        pass
                
    def init_value(self): 
        self.read_xml = ReadXml("/usr/share/deepin-media-player/src/xml/")
        self.model_dict = {}
        # left.
        self.left_x = 20
        self.left_y = 20
        self.left_offset_x = 0
        self.left_offset_y = 0
        # right.
        self.right_x = 200
        self.right_y = 20
        self.right_offset_x = 0
        self.right_offset_y = 0
        # move.
        self.move_offset_x = 0
        self.move_offset_y = 0
        
    def InitializeComponent(self):
        # Init form event.
        self.connect("destroy", lambda w : self.destroy())
        # Init widgets.
        self.main_fixed = gtk.Fixed()
        self.brand_label = Label(_("phone brand : "))
        self.format_label = Label(_("Output format : "))        
        self.bit_rate_label = Label(_("Audio encoder : "))
        self.frame_rate_label = Label(_("Video encoder : "))
        self.path_label = Label(_("Output directory : "))
        self.model_label = Label(_("Phone model : "))
        self.ratio_label = Label(_("Resolution : "))        
        
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
        self.higt_hbox.pack_start(self.show_and_hide_task_btn)
        
        self.higt_align = gtk.Alignment()
        # self.align.add(self.higt_set_btn)
        self.higt_align.add(self.higt_hbox)
        self.higt_align.set(1, 0, 1, 0)
        self.higt_align.set_padding(0, 0, 0, 113)
        
        self.right_button_box.set_buttons([self.higt_align, self.start_btn, self.close_btn])
        
        # brand_combo.
        brand_items = []
        i = 0
        for brand in self.read_xml.brand_dict.keys():
            brand_items.append((brand, i))
            i += 1
            # print brand
            # self.brand_combo.append_text(brand)
        self.brand_combo.set_items(brand_items)    
        self.brand_combo.prepend_text("No Presets")
        self.brand_combo.connect("changed", self.brand_combo_item_selected)
        # model_combo.
        self.model_combo.prepend_text("No Model")
        self.model_combo.connect("changed", self.model_combo_item_selected)
        # ratio_combo.
        self.ratio_combo.prepend_text("No Ratio")
        self.save_chooser_btn.connect("clicked", self.save_chooser_btn_clicked)
        
        # self.format_combo.set_active(0)        
        # path_entry.
        PATH_ENTRY_WIDTH = 240
        PATH_ENTRY_HEIGHT = 25
        self.save_path_entry.set_sensitive(False)
        self.save_path_entry.set_text(self.get_home_path())
        self.save_path_entry.set_size(PATH_ENTRY_WIDTH, PATH_ENTRY_HEIGHT)
        self.close_btn.connect("clicked", lambda w : self.destroy())
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
                                self.right_y + self.right_offset_y - padding_y)
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
        if item_content != "No Presets":
            # print "item_value:", self.read_xml.brand_dict[item_content]
            self.model_dict = self.read_xml.load(self.read_xml.brand_dict[item_content])
            # print 'self.model_dict:', self.model_dict
            if self.model_dict != {}:
                model_items = []
                i = 0
                for model in self.model_dict:            
                    # self.model_combo.append_text(model)
                    model_items.append((model, i))
                    i += 1
                self.model_combo.set_items(model_items)    
                self.model_combo.droplist.set_size_request(-1, self.model_combo.droplist_height)
                self.model_combo.set_active(0)
            else:    
                self.model_combo.append_text("No Model")
                self.ratio_combo.append_text("No Ratio")    
        else:        
            # clear model and ratio all text.
            self.model_combo.append_text("No Model")
            self.ratio_combo.append_text("No Ratio")    
            
    def model_combo_item_selected(self, combo, item_content):        
        if len(item_content):
            width, height = self.model_dict[item_content]
            self.ratio_combo.clear_items()
            self.ratio_combo.prepend_text("%s x %s"%(width, height))
        
    def higt_set_btn_clicked(self, widget):    
        if self.higt_set_bool:
            self.hide_setting()
            self.set_geometry_hints(None, FORM_WIDTH, FORM_HEIGHT-80, FORM_WIDTH, FORM_HEIGHT-80, -1, -1, -1, -1, -1, -1)
            self.set_size_request(FORM_WIDTH, FORM_HEIGHT-80)
            # self.set_geometry_hints(None, FORM_WIDTH, FORM_HEIGHT, -1, -1, -1, -1, -1, -1, -1, -1)
        else:    
            self.show_setting()
            self.set_geometry_hints(None, FORM_WIDTH, FORM_HEIGHT, FORM_WIDTH, FORM_HEIGHT, -1, -1, -1, -1, -1, -1)
            self.set_size_request(FORM_WIDTH, FORM_HEIGHT+80) 
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
            self.main_fixed.move(other, 
                                self.left_x + padding_width + other_padding_x, 
                                self.left_y + self.left_offset_y - padding_y)
            if button:
                # main fixed add button widget.                
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
    
    
