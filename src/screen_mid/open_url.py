#! /usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (C) 2013 Deepin, Inc.
#               2013 Hailong Qiu
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


from skin import app_theme
from locales import _
from dtk.ui.dialog import DialogBox, DIALOG_MASK_MULTIPLE_PAGE
from dtk.ui.entry import InputEntry
from dtk.ui.button import Button
import gtk

class OpenUrlDialog(DialogBox):
    def __init__(self):
        DialogBox.__init__(self, _("Open Url"),
                mask_type=DIALOG_MASK_MULTIPLE_PAGE,
                window_pos=gtk.WIN_POS_CENTER
                )
        self.hbox_ali = gtk.Alignment(0, 0, 1, 1)
        self.hbox_ali.set_padding(5, 5, 5, 5)
        self.hbox = gtk.HBox()
        self.hbox_ali.add(self.hbox)
        self.url_text = InputEntry()
        self.ok_btn = Button(_("Ok"))
        self.cancel_btn = Button(_("Cancel"))
        self.url_text.set_size(280, 25)
        self.hbox.pack_start(self.url_text, True, True)
        #self.hbox.pack_start(self.ok_btn, True, True, 5)
        self.right_button_box.set_buttons([self.ok_btn, self.cancel_btn])
        #
        self.body_box.pack_start(self.hbox_ali, True, True)
        #
        self.cancel_btn.connect("clicked", self.__cancel_btn_clicked_event)

    def __cancel_btn_clicked_event(self, widget):
        self.destroy()


