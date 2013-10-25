#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Hailong Qiu
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

from dtk.ui.skin_config  import skin_config
from dtk.ui.application  import Application
from dtk.ui.utils import propagate_expose
from widget.movie_paned  import Paned
from widget.playlistview import PlayListView
from widget.toolbar      import ToolBar
from widget.draw         import draw_pixbuf
from widget.color        import alpha_color_hex_to_cairo
from widget.bottom_toolbar import BottomToolBar
from widget.play_menus   import PlayMenus
from widget.utils        import get_system_tooptil_icon
from widget.movie_menu   import ScreenMidCombo
from locales import _
import pynotify
import gtk
from deepin_utils.file import get_parent_dir
import os

class GUI(object):
    '''Media Player GUI kernel code.核心界面代码'''
    def __init__(self):        
        '''application.'''
        self.__init_values()
        self.app = Application(False)
        # application set.
        app_w, app_h = 800, 570 # 初始化宽,高.
        min_app_w, min_app_h = 480, 300 # 防止超过,界面布局被破坏.
        self.app.set_default_size(min_app_w, min_app_h)
        self.app.window.set_default_size(app_w, app_h)
        # self.app.window.resize
        image_dir = os.path.join(get_parent_dir(__file__, 2), "image")
        self.app.set_icon(os.path.join(image_dir, "icon.ico"))
        self.app.set_skin_preview(os.path.join(os.path.join(image_dir, "frame.png")))
        # set titlebar.
        self.app.add_titlebar(
            ["theme", "menu", "max", "min", "close"],
            os.path.join(os.path.join(image_dir, "logo.png")),
            _("DPlayer"), " ", 
            add_separator = False,
            )
        self.app.titlebar.set_size_request(-1, 30)
        
        #
        self.play_menus = PlayMenus()
        # 设置主题菜单.
        self.app.set_menu_callback(lambda button: self.play_menus.show_theme_menu(button))
        #
        self.main_ali = gtk.Alignment()
        self.main_vbox = gtk.VBox()
        self.main_ali.add(self.main_vbox)
        self.main_ali.set(0, 0, 1.0, 1.0)
        self.main_ali.set_padding(0, 2, 2, 2)
        #
        self.mid_combo_event = gtk.EventBox()
        self.mid_combo_event.connect("expose-event", self.mid_combo_event_expose_event)
        self.screen_mid_combo = ScreenMidCombo()
        self.mid_combo_event.set_visible_window(True)
        self.mid_combo_event.add(self.screen_mid_combo)
        '''movie screen. 电影播放屏幕.'''
        # 播放屏幕和播放列表的HBOX.
        self.play_list_view = PlayListView()
        self.screen_paned = Paned()
        self.screen_paned.paint_bottom_window = self.__paint_bottom_toolbar_background
        self.screen_frame = gtk.Alignment(0.0, 0.0, 1.0, 1.0)
        self.screen = gtk.DrawingArea()
        self.screen_frame.add(self.screen)
        self.top_toolbar = ToolBar()
        self.bottom_toolbar = BottomToolBar()
        # BUG: 当显示上部工具条的时候,画面抖动.
        self.screen_paned.add_top_widget(self.top_toolbar.hbox_hframe)
        self.screen_paned.add_bottom_widget(self.bottom_toolbar.vbox)
        #self.screen_paned.add_mid_widget(self.screen_mid_combo)
        self.screen_paned.add_mid_widget(self.mid_combo_event)
        #
        self.screen_frame_event = self.screen_paned
        self.screen_paned.screen = self.screen
        #
        self.screen_paned.add1(self.screen_frame)
        self.screen_paned.add2(self.play_list_view.play_list_vbox)
        #
        self.play_control_panel = BottomToolBar(False)
        #
        self.main_vbox.pack_start(self.screen_paned, True, True)
        self.main_vbox.pack_start(self.play_control_panel.vbox, False, False)
        #
        self.app.main_box.pack_start(self.main_ali, True, True)

    def __init_values(self):
        self.child2_show_check = False # True 显示 False 隐藏

    ################################################################################
    ##
    def __paint_bottom_toolbar_background(self, e):
        # 将皮肤的图片画在bottom toolbar上,作为背景.
        cr = e.window.cairo_create()
        bottom_size = e.window.get_size()
        # draw background.
        cr.set_source_rgba(*alpha_color_hex_to_cairo(("#ebebeb", 0.1)))
        cr.rectangle(0, 0, bottom_size[0], bottom_size[1])
        cr.fill()
        # draw background pixbuf.
        pixbuf = skin_config.background_pixbuf
        app_h = self.app.window.allocation.height
        app_w = self.app.window.allocation.width
        bottom_h = bottom_size[1]
        # 当图片的高度小雨窗口高度的时候,只拿出图片的最尾巴.
        if pixbuf.get_height() > app_h + bottom_h:
            h = app_h
        else:
            h = pixbuf.get_height() - bottom_h
        # 当图片小于窗口宽度的时候,拉伸图片.
        if pixbuf.get_width() < app_w:
            pixbuf = pixbuf.scale_simple(app_w,
                                pixbuf.get_width(),
                                gtk.gdk.INTERP_BILINEAR)

        draw_pixbuf(cr, 
                    pixbuf, 
                    0, 
                    -(h))

    def not_in_system_widget(self):
        # 判断handle toolbar 是否显示出来了.
        return (not self.screen_paned.show_check and 
                not self.screen_paned.top_win_show_check and
                not self.screen_paned.bottom_win_show_check) 

    def set_paned_handle(self, event):
        if self.screen_paned.show_check and (0 <= event.x <= 7):
            if self.screen_paned.get_move_width() == 0: # child2 隐藏和显示.
                self.play_control_panel.play_list_btn.button.set_active(True)
            else:
                self.play_control_panel.play_list_btn.button.set_active(False)

    def close_right_child2(self):
        self.screen_paned.set_jmp_end() # 关闭右侧控件(播放列表..).

    def open_right_child2(self):
        self.screen_paned.set_jmp_start() # 打开右侧控件 (播放列表...).

    def hide_handle(self):
        self.screen_paned.set_visible_handle(False)

    def show_handle(self):
        self.screen_paned.set_visible_handle(True)

    def show_play_control_paned(self):
        self.main_vbox.pack_start(self.play_control_panel.vbox, False, False)

    def hide_play_control_paned(self):
        self.main_vbox.remove(self.play_control_panel.vbox)

    def show_tooltip_text(self, text, sec=1500):
        self.screen_paned.show_tooltip_text(text, sec)

    def notify_msgbox(self, title, msg, icon_path=get_system_tooptil_icon()):
        try:
            pynotify.init("deepi-media-player")
            msg = pynotify.Notification(title, msg, icon_path)
            if icon_path:
                msg.set_hint_string("image-path", icon_path)
            msg.show()
        except Exception, e:
            print "message[error]:", e
    
    def tooltip_change_style(self, font, font_size):
        self.screen_paned.change_style(font, font_size)

    def mid_combo_event_expose_event(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        cr.rectangle(*rect)
        cr.set_source_rgba(0, 0, 0, 0.7)
        #cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()
        #
        propagate_expose(widget, event)
        return True



