#! /usr/bin/env python
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



import gtk
from window import MenuWindow


class Menu(MenuWindow):
    def __init__(self):
        MenuWindow.__init__(self)

    def popup(self):
        pass

    def popup_grab_on_window(self, activate_time):
        if(gtk.gdk.pointer_grab(
            self.window,
            True,
            gtk.gdk.POINTER_MOTION_MASK
            | gtk.gdk.BUTTON_PRESS_MASK
            | gtk.gdk.BUTTON_RELEASE_MASK
            | gtk.gdk.ENTER_NOTIFY_MASK
            | gtk.gdk.LEAVE_NOTIFY_MASK,
            None,
            None,
            #gtk.gdk.CURRENT_TIME)):
            activate_time)):
            #
            if (gtk.gdk.keyboard_grab(
                    self.window, 
                    owner_events=False, 
                    #time=gtk.gdk.CURRENT_TIME)):
                    time=activate_time)):
                return True
            else:
                gtk.gdk.pointer_ungrab(activate_time)
                pass

        return False


    def popdown(self):
        self.grab_remove()


class MenuItem(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self, gtk.WINDOW_POPUP)
        btn = gtk.Button('fdjsf')
        btn.connect("clicked", self.test_btn_event)
        self.add(btn)
        self.connect("show", self.__menu_item_show_event)

    def __menu_item_show_event(self, widget):
        self.grab_add()

    def test_btn_event(self, widget):
        self.grab_remove()
        self.hide_all()

if __name__ == "__main__":
    def test_btn_event(w):
        #
        menu_ite = MenuItem()
        menu_ite.set_size_request(150, 150)
        menu_ite.move(600, 300)
        menu_ite.show_all()
        #
    win = Menu()
    btn = gtk.Button("测试")
    btn.connect("clicked", test_btn_event)
    win.add(btn)
    win.move(300, 300)
    win.set_size_request(300, 300)
    win.show_all()
    gtk.main()

