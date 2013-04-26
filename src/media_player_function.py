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



from widget.tooltip  import tooltip_text
from widget.preview  import PreView
from widget.utils import is_file_audio



class MediaPlayFun(object):
    def __init__(self, this):
        self.this = this
        self.__init_values()
        self.__init_ldmp_values()

    def __init_values(self):
        self.pre_view = PreView()
        self.app = self.this.gui.app
        self.gui = self.this.gui
        #
        self.__init_top_toolbar()
        self.__init_app_play_control_panel()
        self.__init_bottom_toolbar()
        #
        self.ldmp = self.this.ldmp
        self.play_list = self.this.play_list
        self.list_view = self.this.gui.play_list_view.list_view
        self.list_view.connect_event("double-items",  self.list_view_double_items) 
        self.list_view.connect_event("motion-notify-items", self.list_view_motion_notify_items)
        #

    def list_view_motion_notify_items(self, listview, motion_items, row, col, item_x, item_y):
        text = motion_items.sub_items[0].text
        text = str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        tooltip_text(self.list_view, text)

    def list_view_double_items(self, listview, double_items, row, col, item_x, item_y):
        self.play_list.set_items_index(double_items)
        self.this.play(double_items.sub_items[2].text)

    def __init_top_toolbar(self):
        self.keep_above_check = False

        self.top_toolbar    = self.this.gui.top_toolbar
        self.top_toolbar.toolbar_radio_button.set_full_state(False) # 初始化.
        self.top_toolbar.toolbar_above_button.connect("clicked", self.__top_toolbar_above_button_clicked)
        self.top_toolbar.toolbar_1X_button.connect("clicked",    self.__top_toolbar_1X_button_clicked)
        self.top_toolbar.toolbar_2X_button.connect("clicked",    self.__top_toolbar_2X_button_clicked)    
        self.top_toolbar.toolbar_concise_button.connect("clicked", self.__top_toolbar_concise_button_clicked)
        self.top_toolbar.toolbar_common_button.connect("clicked",  self.__top_toolbar_common_button_clicked) 
        self.top_toolbar.toolbar_full_button.connect("clicked", self.__top_toolbar_full_button_clicked) 

    def __progressbar_motion_notify_event(self, widget, event):
        # self.pre_view.set_preview_path(... ...
        pre_view_check = self.this.config.get("FilePlay", "mouse_progressbar_show_preview") 
        if "True" == pre_view_check:
            if not widget.move_check and (not is_file_audio(self.ldmp.player.uri)):
                #
                if not self.pre_view.mp.player.state: 
                    # 如果突然设置了，没有东西视频在预览窗口中，则.
                    self.pre_view.set_preview_path(self.ldmp.player.uri)
                #
                value = 0
                self.x_root = event.x_root
                self.y_root = event.y_root
                # 
                if widget == self.bottom_toolbar.progressbar:
                    size = self.gui.screen_paned.bottom_window.get_size()
                    preview_y = (self.app.window.get_position()[1] + self.gui.screen_frame.allocation.height - 
                                 self.pre_view.bg.get_allocation()[3] - size[1])
                else:
                    preview_y = (self.app.window.get_position()[1] + self.gui.screen_frame.allocation.height +
                                 self.app.titlebar.allocation.height - self.pre_view.bg.get_allocation()[3])
                ###############################################33
                move_x = self.x_root - self.pre_view.bg.get_allocation()[2]/2
                move_y = preview_y
                min_move_x = self.app.window.get_position()[0] + 8
                max_move_x = min_move_x + self.app.window.allocation.width  - 16
                mid_bg_w = self.pre_view.bg.allocation.width
                #
                if move_x < min_move_x:
                    offset = self.pre_view.bg.get_offset_mid_value() - (min_move_x - move_x)
                elif move_x > (max_move_x - self.pre_view.bg.allocation.width):
                    offset = self.pre_view.bg.get_offset_mid_value() - ((max_move_x - move_x) - 
                             self.pre_view.bg.allocation.width)
                else:
                    offset = self.pre_view.bg.get_offset_mid_value()
                #
                offset_x = offset
                move_x = max(min(move_x, max_move_x - mid_bg_w), min_move_x)
                self.pre_view.bg.set_offset(offset)
                value = event.x / widget.allocation.width * widget.max_value
                pos = min(max(value, 0), widget.max_value - 5)
                self.pre_view.show_preview(pos)
                self.pre_view.move_preview(move_x, preview_y)
            else:
                self.pre_view.hide_preview()
        else:
            # 如果突然关闭预览，则关闭在跑的预览窗口中的mplayer.
            self.pre_view.quit_preview_player()

    def __progressbar_leave_notify_event(self, widget, event):
        self.pre_view.hide_preview()

    def __init_app_play_control_panel(self):
        self.app_play_control_panel    = self.this.gui.play_control_panel
        self.app_play_control_panel.progressbar.connect("value-changed", self.__bottom_toolbar_pb_value_changed)
        self.app_play_control_panel.progressbar.connect("motion-notify-event", self.__progressbar_motion_notify_event)
        self.app_play_control_panel.progressbar.connect("leave-notify-event", self.__progressbar_leave_notify_event)
        self.app_play_control_panel.pb_fseek_btn.connect("clicked", self.__bottom_toolbar_pb_fseek_btn_clicked)
        self.app_play_control_panel.pb_bseek_btn.connect("clicked", self.__bottom_toolbar_pb_bseek_btn_clicked)
        self.app_play_control_panel.play_list_btn.button.connect("clicked", 
                 self.__app_play_control_panel_play_list_btn_clicked)

        start_button  = self.app_play_control_panel.play_control_panel
        stop_button   = self.app_play_control_panel.play_control_panel.stop_button
        pre_button    = self.app_play_control_panel.play_control_panel.pre_button
        next_button   = self.app_play_control_panel.play_control_panel.next_button
        open_button   = self.app_play_control_panel.play_control_panel.open_button
        volume_button = self.app_play_control_panel.volume_button
        #
        start_button.start_button.connect("clicked", self.__bottom_toolbar_start_button_clicked)
        stop_button.connect("clicked",               self.__bottom_toolbar_stop_button_clicked)
        pre_button.connect("clicked",                self.__pre_button_clicked)
        next_button.connect("clicked",               self.__next_button_clicked)
        open_button.connect("clicked",               self.__open_button_clicked)

        volume_button.mute_btn.connect("clicked",               self.__mute_btn_state_changed)
        volume_button.volume_btn.connect("button-press-event",  self.__volume_btn_button_press_event)
        volume_button.volume_btn.connect('motion-notify-event', self.__volume_btn_motion_notify_event)
        '''
            # 这里需要读 ini文件, 是否显示初始化的时候显示播放列表. 默认不显示播放列表.
            self.app_play_control_panel.play_list_btn.button.set_active(True)
        '''

    def __init_bottom_toolbar(self):
        self.bottom_play_control_panel = self.this.gui.bottom_toolbar.play_control_panel
        self.bottom_toolbar = self.this.gui.bottom_toolbar
        self.bottom_toolbar.progressbar.connect("value-changed", self.__bottom_toolbar_pb_value_changed)
        self.bottom_toolbar.progressbar.connect("motion-notify-event", self.__progressbar_motion_notify_event)
        self.bottom_toolbar.progressbar.connect("leave-notify-event", self.__progressbar_leave_notify_event)
        self.bottom_toolbar.pb_fseek_btn.connect("clicked",      self.__bottom_toolbar_pb_fseek_btn_clicked)
        self.bottom_toolbar.pb_bseek_btn.connect("clicked",      self.__bottom_toolbar_pb_bseek_btn_clicked)
        
        stop_button   = self.bottom_toolbar.play_control_panel.stop_button
        start_button  = self.bottom_toolbar.play_control_panel.start_button
        pre_button    = self.bottom_toolbar.play_control_panel.pre_button
        next_button   = self.bottom_toolbar.play_control_panel.next_button
        volume_button = self.bottom_toolbar.volume_button

        stop_button.connect("clicked",  self.__bottom_toolbar_stop_button_clicked)
        start_button.connect("clicked", self.__bottom_toolbar_start_button_clicked)
        pre_button.connect("clicked", self.__pre_button_clicked)
        next_button.connect("clicked", self.__next_button_clicked)
        volume_button.mute_btn.connect("clicked", self.__mute_btn_state_changed)
        volume_button.volume_btn.connect("button-press-event", self.__volume_btn_button_press_event)
        volume_button.volume_btn.connect('motion-notify-event', self.__volume_btn_motion_notify_event)

    def __mute_btn_state_changed(self, widget):
        if self.ldmp.player.volumebool:
            self.ldmp.offmute()
        else:
            self.ldmp.nomute()

    def __volume_btn_button_press_event(self, widget, event):
        value = self.app_play_control_panel.volume_button.value
        self.ldmp.setvolume(value)

    def __volume_btn_motion_notify_event(self, widget, event):
        value = None
        if self.app_play_control_panel.volume_button.move_check:
            value = self.app_play_control_panel.volume_button.value
        elif self.bottom_toolbar.volume_button.move_check:
            value = self.bottom_toolbar.volume_button.value
        #
        if value != None:
            self.ldmp.setvolume(value)

    def __top_toolbar_1X_button_clicked(self, widget):
        print "__top_toolbar_1X_button_clicked..."

    def __top_toolbar_2X_button_clicked(self, widget):   
        print "__top_toolbar_2X_button_clicked..."

    def __top_toolbar_concise_button_clicked(self, widget):
        self.this.top_toolbar_concise_button_clicked()

    def __top_toolbar_common_button_clicked(self, widget):
        self.this.top_toolbar_common_button_clicked()

    def __top_toolbar_full_button_clicked(self, widget):
        self.this.fullscreen_function()

    def __top_toolbar_above_button_clicked(self, widget):
        if not self.keep_above_check:
            self.app.window.set_keep_above(True)
            self.keep_above_check = True
        else:
            self.app.window.set_keep_above(False)
            self.keep_above_check = False

    def __app_play_control_panel_play_list_btn_clicked(self, widget):
        # 设置右部的child2的 播放列表.
        child2_width = self.this.gui.screen_paned.get_move_width()
        self.this.gui.child2_show_check = not self.this.gui.child2_show_check
        if child2_width == 0:
            self.this.gui.open_right_child2()
            self.this.gui.screen_paned.set_all_size()
        else:
            self.this.gui.close_right_child2()
            self.this.gui.screen_paned.set_all_size()

    def __pre_button_clicked(self, widget):
        self.this.prev()

    def __next_button_clicked(self, widget):
        self.this.next()

    def __open_button_clicked(self, widget):
        self.this.open_files_to_play_list()

    def __bottom_toolbar_pb_value_changed(self, pb, value):
        self.ldmp.seek(value)

    def __bottom_toolbar_pb_fseek_btn_clicked(self, widget):
        #self.ldmp.fseek(SEEK_VALUE)
        self.this.key_fseek()

    def __bottom_toolbar_pb_bseek_btn_clicked(self, widget):
        #self.ldmp.bseek(SEEK_VALUE)
        self.this.key_bseek()

    def __bottom_toolbar_stop_button_clicked(self, widget):
        self.this.stop()

    def __bottom_toolbar_start_button_clicked(self, widget):
        self.this.start_button_clicked()
        
    '''
    def __stop_button_clicked(self):
        self.ldmp.stop()

    def __start_button_clicked(self):
        # 判断列表是否为空. 空->添加!!
        if not len(self.gui.play_list_view.list_view.items):
            self.this.open_files_to_play_list()
        else:
            # 判断是否在播放.
            if self.ldmp.player.state:
                self.ldmp.pause()
            else:
                self.this.play(self.ldmp.player.uri)
    '''

    def __init_ldmp_values(self):
        self.__pos = "00:00:00 / "
        self.__length = "00:00:00"

    #######################################################
    ## @ldmp.
    def ldmp_start_media_player(self, ldmp):    
        self.bottom_toolbar.progressbar.set_sensitive(True)
        self.bottom_toolbar.pb_fseek_btn.set_sensitive(True)
        self.bottom_toolbar.pb_bseek_btn.set_sensitive(True)
        self.bottom_play_control_panel.start_button.set_start_bool(False)
        # 
        self.app_play_control_panel.progressbar.set_sensitive(True)
        self.app_play_control_panel.pb_fseek_btn.set_sensitive(True)
        self.app_play_control_panel.pb_bseek_btn.set_sensitive(True)
        self.app_play_control_panel.play_control_panel.start_button.set_start_bool(False)
        #
        self.this.play_list_check = False
        # 预览设置. 预览BUG-->> 会启动好多mplayer进程,杀不掉.
        pre_view_check = self.this.config.get("FilePlay", "mouse_progressbar_show_preview") 
        if "True" == pre_view_check:
            if (not is_file_audio(self.ldmp.player.uri)):
                self.pre_view.set_preview_path(ldmp.player.uri)

    def ldmp_end_media_player(self, ldmp):
        # 退出预览.
        self.pre_view.quit_preview_player()
        # 改变所有的状态.
        self.__pos = "00:00:00 / "
        self.__length = "00:00:00"
        ''' 下部工具条 '''
        self.bottom_toolbar.show_time.set_time_font(self.__pos, self.__length)
        self.bottom_toolbar.progressbar.set_pos(0)
        self.bottom_toolbar.progressbar.set_sensitive(False)
        self.bottom_toolbar.pb_fseek_btn.set_sensitive(False)
        self.bottom_toolbar.pb_bseek_btn.set_sensitive(False)
        self.bottom_play_control_panel.start_button.set_start_bool(True)
        ''' 播放控制面板 '''
        self.app_play_control_panel.show_time.set_time_font(self.__pos, self.__length)
        self.app_play_control_panel.progressbar.set_pos(0)
        self.app_play_control_panel.progressbar.set_sensitive(False)
        self.app_play_control_panel.progressbar.set_sensitive(False)
        self.app_play_control_panel.pb_fseek_btn.set_sensitive(False)
        self.app_play_control_panel.pb_bseek_btn.set_sensitive(False)
        self.app_play_control_panel.play_control_panel.start_button.set_start_bool(True)
        #
        #print self.this.play_list_check
        if not self.this.play_list_check:
            self.this.next()

    def ldmp_pause_play(self, pause_check):
        if pause_check: # 正在播放.
            self.app_play_control_panel.play_control_panel.start_button.set_start_bool(False)
            self.bottom_play_control_panel.start_button.set_start_bool(False)
        else: # 暂停.
            self.app_play_control_panel.play_control_panel.start_button.set_start_bool(True)
            self.bottom_play_control_panel.start_button.set_start_bool(True)

    def ldmp_get_time_pos(self, ldmp, pos, time):
        # 设置显示的时间值.
        self.__set_pos_time(time)
        # 获取播放进度设置进度条.
        self.bottom_toolbar.progressbar.set_pos(pos)
        self.app_play_control_panel.progressbar.set_pos(pos)

    def ldmp_get_time_length(self, ldmp, length, time):    
        # 设置显示的总长度值.
        self.__set_length_time(time)
        # 获取播放总进度设置进度条的最大值.
        self.bottom_toolbar.progressbar.set_max_value(length)
        self.app_play_control_panel.progressbar.set_max_value(length)

    def ldmp_mute_play(self, mute_check): # 静音状态.
        if mute_check:
            self.app_play_control_panel.volume_button.set_mute_state(True)
            self.bottom_toolbar.volume_button.set_mute_state(True)
        else:
            self.app_play_control_panel.volume_button.set_mute_state(False)
            self.bottom_toolbar.volume_button.set_mute_state(False)

    def ldmp_volume_play(self, value):
        self.app_play_control_panel.volume_button.set_value(value)
        self.bottom_toolbar.volume_button.set_value(value)

    def __set_pos_time(self, time):
        self.__pos = str(time) + " / "
        self.bottom_toolbar.show_time.set_time_font(self.__pos, self.__length)
        self.app_play_control_panel.show_time.set_time_font(self.__pos, self.__length)

    def __set_length_time(self, time):
        self.__length = str(time)
        self.bottom_toolbar.show_time.set_time_font(self.__pos, self.__length)
        self.app_play_control_panel.show_time.set_time_font(self.__pos, self.__length)

