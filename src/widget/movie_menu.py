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



from skin import app_theme
from locales import _
from draw import draw_pixbuf, draw_text
from utils import get_text_size
from window import MenuWindow
import gtk


class Menu(MenuWindow):
    def __init__(self):
        MenuWindow.__init__(self)
        self.__init_values()
        self.__init_settings()
        self.__init_events()

    def __init_values(self):
        self.__index = None
        self.__menu_height = 25
        self.__save_show_menu = None
        self.child_check = False
        self.menu_parent = None
        #
        self.bg = app_theme.get_pixbuf("screen_mid/menu_bg_normal.png")
        self.open_cdrom = app_theme.get_pixbuf("screen_mid/screen_menu_open_cdrom.png")
        self.open_dir = app_theme.get_pixbuf("screen_mid/screen_menu_open_dir.png")
        self.open_url = app_theme.get_pixbuf("screen_mid/screen_menu_open_url.png")
        self.menu_items = []
        if self.menu_items == []:
            items = []
            for pixbuf, text in [(self.open_cdrom.get_pixbuf(), _("打开CDROM")),
                                 (self.open_dir.get_pixbuf(), _("打开文件夹")),
                                 (self.open_url.get_pixbuf(), _("打开网址")),]:
                menu_item = MenuItem()
                menu_item.pixbuf = pixbuf
                menu_item.text  = text
                items.append(menu_item)
            #
            self.set_menu_items(items)

    def set_menu_items(self, items):
        self.menu_items = items
        self.set_size_request(140, len(self.menu_items) * self.__menu_height)

    def __init_settings(self):
        pass

    def __init_events(self):
        #
        self.connect("show", self.__show_event)
	self.connect("hide", self.__hide_event)
        self.connect("motion-notify-event",  self.__motion_notify_event)
        self.connect("button-release-event", self.__button_release_event)
        self.connect('button-press-event', self.__button_press_event)
        #
        self.on_paint_expose_event = self.__expose_event

    def __expose_event(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        # 画背景.
        bg_pixbuf = self.bg.get_pixbuf().scale_simple(rect.width, 
                                                      rect.height, 
                                                      gtk.gdk.INTERP_BILINEAR)
        x = rect.x
        y = rect.y
        draw_pixbuf(cr, bg_pixbuf, x, y)
        #
        if None != self.__index:
            cr.set_source_rgba(1, 1, 1, 0.1)
            cr.rectangle(x, 
                         y + self.__index * self.__menu_height, 
                         rect.width, 
                         self.__menu_height)
            cr.fill()
        #
        index = 0
        for item in self.menu_items:
            pixbuf, text = item.pixbuf, item.text
            if pixbuf:
                draw_pixbuf(cr, pixbuf, 
                            x + 8, y + index * self.__menu_height + self.__menu_height/2 - pixbuf.get_height()/2)
            draw_text(cr, text, 
                      x + 35, y + index * self.__menu_height + self.__menu_height/2 - get_text_size(text)[1]/2)
            if item.child_menus:
                pixbuf = app_theme.get_pixbuf("screen_mid/menu_child.png").get_pixbuf()
                draw_pixbuf(cr, pixbuf,
                            x + rect.width - 10, y + index * self.__menu_height + self.__menu_height/2 - pixbuf.get_height()/2)
            index += 1
        

    def __show_event(self, widget):
        if not self.child_check:
            self.popup_grab_on_window()
        else:
            self.grab_add()

    def __hide_event(self, widget):
	menu = self.__save_show_menu
	if menu:
	    menu.child_menus.hide_all()
	    menu.child_menus.grab_remove()

    def __button_release_event(self, widget, event):
        print "__button_release_event..."
	index = int(event.y / self.__menu_height)
        if not self.in_window_check(widget, event.x_root, event.y_root):
            self.hide_all()
            self.grab_remove()
	else:
	    if 0 <= index < len(self.menu_items) and self.menu_items[index].child_menus:
	    	return True

        if self.menu_parent:
            self.menu_parent.event(event)

    def __button_press_event(self, widget, event):
        if self.in_window_check(widget, event.x_root, event.y_root):
            index = int(event.y / self.__menu_height)
            if not self.menu_items[index].child_menus:
                self.hide_all()
                self.grab_remove()

    def __motion_notify_event(self, widget, event):
        app = event.window.get_user_data()
        if app != widget:
            app.event(event)
        # 判断在移动的范围内.
        if self.in_window_check(widget, event.x_root, event.y_root):
            self.__index = int(event.y) / self.__menu_height
            self.queue_draw()
            child_menu = self.menu_items[self.__index]
            #
            if self.__save_show_menu != None and self.__save_show_menu != child_menu:
                self.__save_show_menu.child_menus.hide_all()
                self.__save_show_menu.child_menus.grab_remove()

            if child_menu.child_menus: # 判断是否有子菜单.
                position = self.get_position()
                child_menu.child_menus.popup(int(position[0] + self.allocation.width + 5), 
                                             int(position[1] + self.__index * self.__menu_height))
                #child_menu.child_menus.grab_add()
                self.__save_show_menu = child_menu 
        #

    def in_window_check(self, widget, x_root, y_root):
        toplevel = widget.get_toplevel()
        if toplevel.get_mapped():
            window_x, window_y = toplevel.get_position()
            if ((x_root >= window_x and x_root < window_x + widget.allocation.width) 
                and (y_root >= window_y and y_root < window_y + widget.allocation.height)):
                return True
        #
        return False

    def popup(self, x, y):
        self.move(x, y)
        self.show_all()

    def popup_grab_on_window(self):
        gtk.gdk.pointer_grab(
            self.window,
            True,
            gtk.gdk.POINTER_MOTION_MASK
            | gtk.gdk.BUTTON_PRESS_MASK
            | gtk.gdk.BUTTON_RELEASE_MASK
            | gtk.gdk.ENTER_NOTIFY_MASK
            | gtk.gdk.LEAVE_NOTIFY_MASK,
            None,
            None,
            time=gtk.gdk.CURRENT_TIME)
            #
        gtk.gdk.keyboard_grab(
                    self.window, 
                    owner_events=True, 
                    time=gtk.gdk.CURRENT_TIME)
        #self.grab_add()


class MenuItem(object):
    def __init__(self):
        self.pixbuf =  None
        self.text   =  ""
        self.child_menus = None

if __name__ == "__main__":
    def btn_clicked_event(widget):
        menu.popup(500, 500)
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    #win.fullscreen()
    btn = gtk.Button('测试')
    btn.connect("clicked", btn_clicked_event)
    win.add(btn)
    menu = Menu()
    win.show_all()
    gtk.main()

