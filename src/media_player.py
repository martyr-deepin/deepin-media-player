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
from dtk.ui.menu import Menu
import dtk.ui.tooltip as Tooltip
from dtk.ui.draw import draw_pixbuf
from dtk.ui.utils import color_hex_to_cairo
from locales import _ # 国际化翻译.
from ini     import Config
from user_guide import init_user_guide
from widget.constant import SEEK_VALUE
from widget.constant import VOLUME_VALUE
from widget.utils   import get_config_path
from widget.utils   import get_home_path, get_home_video, get_play_file_name
from widget.utils   import is_file_audio
from widget.utils   import ScanDir
from widget.utils import is_file_sub_type
from widget.ini_gui import IniGui
from widget.init_ldmp import init_media_player_config
from gui import GUI # 播放器界面布局.
from media_player_function import MediaPlayFun
from media_player_menus    import MediaPlayMenus
from media_player_keys     import MediaPlayKeys
from media_player_drag     import MediaPlayDrag
from mplayer.timer import Timer
# mplayer后端.
from mplayer.player import LDMP, set_ascept_function, unset_flags, set_flags, Player
from mplayer.player import STARTING_STATE, PAUSE_STATE
from mplayer.player import ASCEPT_4X3_STATE, ASCEPT_16X9_STATE, ASCEPT_5X4_STATE
from mplayer.player import ASCEPT_16X10_STATE, ASCEPT_1_85X1_STATE, ASCEPT_2_35X1_STATE, ASCEPT_FULL_STATE, ASCEPT_DEFULAT
from mplayer.player import (ERROR_RETRY_WITH_MMSHTTP, ERROR_RESOLVE_AF_INET, ERROR_SOCKET_CONNECT,
                            ERROR_FILE_FORMAT, ERROR_DVD_DEVICE, ERROR_RETRY_ALSA_BUSY,
                            ERROR_RETRY_WITH_HTTP, ERROR_RETRY_WITH_HTTP_AND_PLAYLIST,
                            ERROR_RETRY_WITH_PLAYLIST)
from mplayer.player import TYPE_FILE, TYPE_CD, TYPE_DVD, TYPE_VCD, TYPE_NETWORK, TYPE_DVB, TYPE_TV
from mplayer.playlist import PlayList, SINGLA_PLAY, ORDER_PLAY, RANDOM_PLAY, SINGLE_LOOP, LIST_LOOP 
# 播放列表 .       0        1       2         3          4
#           { 单曲播放、顺序播放、随机播放、单曲循环播放、列表循环播放、}
#            SINGLA_PLAY ... ...                ...LIST_LOOP
from unique_service import UniqueService, is_exists
from format_conv.conv_task_gui import ConvTAskGui
from plugin_manager.plugin_manager import PluginManager
import random
import time
import gtk
import sys
import os
import dbus

APP_DBUS_NAME   = "com.deepin.mediaplayer"
APP_OBJECT_NAME = "/com/deepin/mediaplayer"


class MediaPlayer(object):
    def __init__(self):
        self.__init_config_file()
        #
        self.first_run = False
        self.__init_values()
        # init double timer.
        self.__init_double_timer()
        self.__init_move_window()
        self.__init_gui_app_events()
        self.__init_gui_screen()
        # 判断是否存在这个配置文件.
        if not os.path.exists(os.path.join(get_config_path(), "deepin_media_config.ini")):
            init_media_player_config(self.config)
            init_user_guide(self.start, True)
            self.first_run = True
        # init dubs id.
        self.__init_dbus_id()
        # show gui window.
        if not self.first_run:
            self.start()

    def __init_config_file(self):
        # 配置文件.
        self.ini = Config(get_home_path() + "/.config/deepin-media-player/config.ini")
        self.config = Config(get_home_path() + "/.config/deepin-media-player/deepin_media_config.ini")
        self.config.connect("config-changed", self.modify_config_section_value)

    def __init_dbus_id(self): # 初始化DBUS ID 唯一值.
        self.is_exists_check = False
        # 随机DBUS-ID.
        dbus_id_list = time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime(time.time())).split("-")
        dbus_id = ""
        dbus_id_list[0] = random.randint(0, 1000)
        dbus_id_list[1] = random.randint(0, 1000)
        dbus_id_list[2] = random.randint(0, 1000)
        dbus_id_list[3] = random.randint(0, 1000)
        for num in dbus_id_list:
            number = int(num) + 65
            if ((65 <= number and number <= 90 ) or (97 <= number and number <= 122)):
                dbus_id += "." + chr(number)
            else:
                dbus_id += "." + chr(random.randint(65, 90))
        self.dbus_id = dbus_id
        #print "dbus_id:", dbus_id
        #
        self.in_run_check()

    def in_run_check(self):
        run_check = self.config.get("FilePlay", "check_run_a_deepin_media_player")
        # 判断是否可以是运行一个深度影音.
        if not ("True" == run_check):
            # 判断是否已经在运行了.
            if is_exists(APP_DBUS_NAME, APP_OBJECT_NAME):
                # DBUS控制深度影音 的服务初始化.
                import sys
                bus = dbus.SessionBus()
                # 获取保存下来的单实例ID.
                dbus_id = self.config.get("DBUS", "id")
                #
                try:
                    remote_object = bus.get_object(
                                        "org.mpris.MediaPlayer2.SampleService" + dbus_id,
                                        '/org/mpris/MediaPlayer2')
                except dbus.DbusException:
                    sys.exit(1)
                    #pass
                        
                iface = dbus.Interface(remote_object,
                                       "org.mpris.MediaPlayer2.Player")
                # iface 加入播放文件或者播放文件夹.
                iface.Next()
                #
                sys.exit()
            self.save_dbus_id()
            self.signal_run_ldmp()

    def save_dbus_id(self):
        # 保存ID。
        self.config.set("DBUS", "id", self.dbus_id)
        self.config.save()

    def signal_run_ldmp(self):
        # 单实例一个深度影音.
        app_bus_name = dbus.service.BusName(APP_DBUS_NAME, bus=dbus.SessionBus())
        UniqueService(app_bus_name, APP_DBUS_NAME, APP_OBJECT_NAME)
        self.is_exists_check = True

    def __init_values(self):
        #
        self.minimize_check  = False
        self.play_list_check = False
        self.ldmp = LDMP()
        self.gui = GUI()        
        #
        self.list_view = self.gui.play_list_view.list_view
        #
        self.conv_task_gui = ConvTAskGui()
        self.conv_form     = None
        #
        self.play_list = PlayList(self.gui.play_list_view.list_view) 
        # 初始化播放列表.
        self.play_list.set_file_list(self.gui.play_list_view.list_view.items)
        self.fullscreen_check = False # 全屏
        self.concise_check    = False # 简洁模式 # True 简洁模式 False 普通模式
        #
        #SINGLA_PLAY, ORDER_PLAY, RANDOM_PLAY, SINGLE_LOOP, LIST_LOOP 
        self.play_list.set_state(LIST_LOOP)
        self.argv_path_list = sys.argv # save command argv.        

    def __init_double_timer(self):
        self.interval = 300
        self.timer = Timer(self.interval)
        self.double_check = False
        self.save_double_x = 0
        self.save_double_y = 0
        self.timer.connect("Tick", self.timer_tick_event)

    def __init_move_window(self):
        self.move_win_check = False
        self.save_move_button = None
        self.save_move_time   = None
        self.save_move_x = 0
        self.save_move_y = 0

    def __init_gui_app_events(self):
        '''application events init.'''
        self.gui.app.titlebar.min_button.connect("clicked", self.app_window_min_button_clicked)        
        self.gui.app.window.add_events(gtk.gdk.ALL_EVENTS_MASK)
        self.gui.app.window.connect("destroy", self.app_window_quit)
        self.gui.app.window.connect("configure-event", self.app_window_configure_event)
        self.gui.app.window.connect("check-resize", self.app_window_check_resize)
        self.gui.app.window.connect("button-press-event", self.app_window_button_press_event)
        self.gui.app.window.connect("motion-notify-event", self.app_window_motion_notify_event)
        self.gui.app.window.connect("window-state-event", self.app_window_state_event)
        # self.app.window.connect("leave-notify-event", )
        # self.app.window.connect("focus-out-event", )
        # self.app.window.connect("focus-in-event", )
        # self.app.window.connect("scroll_event", )
        # self.app.window.connect("check-resize",)         

    def app_window_button_press_event(self, widget, event):
        # 判断是否可拖动大小.
        if self.in_drag_position(widget, event):
            drag = gtk.gdk.WINDOW_EDGE_SOUTH_EAST
            self.gui.app.window.begin_resize_drag(drag, 
                                event.button,
                                int(event.x_root),
                                int(event.y_root),
                                event.time)

    def app_window_motion_notify_event(self, widget, event):
        # 更改鼠标样式.
        if self.in_drag_position(widget, event):
            drag = gtk.gdk.BOTTOM_RIGHT_CORNER
            widget.window.set_cursor(gtk.gdk.Cursor(drag))
        else:
            widget.window.set_cursor(None)

    def app_window_state_event(self, widget, event):
        #print widget.window.get_state()
        win_state = widget.window.get_state()
        # bUG: 全屏也暂停.
        if  win_state == gtk.gdk.WINDOW_STATE_ICONIFIED:
            if self.ldmp.player.state == STARTING_STATE:
                self.minimize_pause_state()
            self.minimize_check = True
        elif win_state == 0 and self.minimize_check:
            if self.ldmp.player.state == PAUSE_STATE:
                self.minimize_pause_state()
            self.minimize_check = False

    def minimize_pause_state(self):
        min_pause_check = self.config.get("FilePlay", "minimize_pause_play")
        if "True" == min_pause_check:
            self.key_pause()

    def in_drag_position(self, widget, event):
        # 判断是否在拖动大小的区域内.
        x, y = self.gui.app.window.get_position()
        x_padding = int(event.x_root)
        y_padding = int(event.y_root)
        w, h = widget.allocation.width, widget.allocation.height
        w_padding = h_padding = 5
        return ((x + w - w_padding) <=  x_padding <= x + w and 
                (y + h - h_padding) <= y_padding <= y+ h)

    def __init_gui_screen(self):
        '''screen events init.'''
        self.draw_check = True
        self.background = app_theme.get_pixbuf("player.png").get_pixbuf()        
        self.gui.screen_frame_event.add_events(gtk.gdk.ALL_EVENTS_MASK)
        self.gui.screen.connect("realize",            self.init_media_player)
        self.gui.screen.connect("expose-event",       self.screen_expose_event)
        self.gui.screen.connect("configure-event",    self.screen_configure_event)
        self.gui.screen_frame.connect("expose-event", self.screen_frame_expose_event)
        self.gui.screen_frame_event.connect("button-press-event",   self.screen_frame_event_button_press_event)
        self.gui.screen_frame_event.connect("button-release-event", self.screen_frame_event_button_release_event)
        self.gui.screen_frame_event.connect("motion-notify-event",  self.screen_frame_event_button_motoin_notify_event)
        self.gui.screen_frame_event.connect("leave-notify-event", self.screen_frame_event_leave_notify_event)
    
    '''application event conect function.窗口事件连接函数.'''
    def app_window_min_button_clicked(self, widget): # 缩小按钮单击.
        pass
        
    def app_window_quit(self, widget): # 窗口销毁.destroy
        self.play_list_check  = True
        self.ldmp.quit()
        # save media window size.
        self.save_media_window_size()

    def save_media_window_size(self):
        rect = self.gui.app.window.allocation
        self.config.set("Window", "width", rect.width)
        self.config.set("Window", "height", rect.height)
        self.config.save()
        
    def app_window_configure_event(self, widget, event): # configure-event
        self.set_ascept_restart() # 设置分辨率.
        
    def app_window_check_resize(self, widget):# check-resize    
        self.set_ascept_restart() # 设置分辨率.
        
    def set_ascept_restart(self):    
        try:            
            unset_flags(self.gui.screen)
            if self.ldmp.player.video_width == 0 or self.ldmp.player.video_height == 0:
                set_flags(self.gui.screen)
                ascept_num = None
            elif self.ldmp.player.ascept_state == ASCEPT_4X3_STATE:
                ascept_num = 4.0/3.0
            elif self.ldmp.player.ascept_state == ASCEPT_16X9_STATE:    
                ascept_num = 16.0/9.0
            elif self.ldmp.player.ascept_state == ASCEPT_16X10_STATE:    
                ascept_num = 16.0/10.0
            elif self.ldmp.player.ascept_state == ASCEPT_1_85X1_STATE:    
                ascept_num = 1.85/1.0
            elif self.ldmp.player.ascept_state == ASCEPT_5X4_STATE:    
                ascept_num = 5.0/4.0
            elif self.ldmp.player.ascept_state == ASCEPT_2_35X1_STATE:    
                ascept_num = 2.35/1.0
            elif self.ldmp.player.ascept_state == ASCEPT_FULL_STATE:
                ascept_num = None
            elif self.ldmp.player.ascept_state == ASCEPT_DEFULAT:
                ascept_num = float(self.ldmp.player.video_width) / float(self.ldmp.player.video_height)
            else:
                ascept_num = None
                set_flags(self.gui.screen)
            # set ascept.    
            set_ascept_function(self.gui.screen_frame, ascept_num)
        except Exception, e:
            set_ascept_function(self.gui.screen_frame, None)
            print "set_ascept_restart[error]:", e
            
    '''screen event conect function.播放屏幕事件连接函数'''
    def screen_frame_expose_event(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        cr.set_source_rgb(0, 0, 0)
        cr.rectangle(rect.x, rect.y, rect.width, rect.height)
        cr.fill()
        
    def init_media_player(self, widget): # screen realize.        
        '''初始化mplayer后端'''
        self.ldmp.xid = widget.window.xid
        self.ldmp.connect("get-time-pos",       self.ldmp_get_time_pos)
        self.ldmp.connect("get-time-length",    self.ldmp_get_time_length)
        self.ldmp.connect("end-media-player",   self.ldmp_end_media_player)
        self.ldmp.connect("start-media-player", self.ldmp_start_media_player)
        self.ldmp.connect("screen-changed",     self.ldmp_screen_changed)
        self.ldmp.connect("pause-play",         self.ldmp_pause_play)
        self.ldmp.connect("mute-play",          self.ldmp_mute_play)
        self.ldmp.connect("volume-play",        self.ldmp_volume_play)
        self.ldmp.connect("error-msg",          self.ldmp_error_msg)
        
        # 全部的执行函数方法.
        self.media_play_fun   = MediaPlayFun(self)
        self.media_play_menus = MediaPlayMenus(self)
        self.media_play_kes   = MediaPlayKeys(self)
        self.media_play_drag  = MediaPlayDrag(self)
        # 初始化插件系统.
        self.init_plugin_manage()

    def init_plugin_manage(self):
        # 插件初始化.
        self.plugin_man = PluginManager(self)
        self.plugin_man.load_auto_plugins()
        self.plugin_man.load_auto_flase_plugins()
        
    def ldmp_get_time_pos(self, ldmp, pos, time):
        # print "pos:", pos
        self.media_play_fun.ldmp_get_time_pos(ldmp, pos, time)
        
        
    def ldmp_get_time_length(self, ldmp, length, time):    
        # print "length:", length, time
        self.media_play_fun.ldmp_get_time_length(ldmp, length, time)

    def ldmp_start_media_player(self, ldmp):    
        #print "开始播放了..."
        self.player_start_init()
        self.media_play_fun.ldmp_start_media_player(ldmp)
        
    def player_start_init(self):    
        pass

    def ldmp_end_media_player(self, ldmp):
        #print "===========播放结束!!==========", ldmp.player.type
        self.player_end_init()
        self.media_play_fun.ldmp_end_media_player(ldmp)
        
    def player_end_init(self):        
        # 播放完毕，重置播放设置.
        self.ldmp.player.video_width = 0
        self.ldmp.player.video_height = 0
        self.set_draw_background(0, 0)
        # 防止出现白屏幕的BUG,进行重绘!!
        self.gui.screen.queue_draw()
        self.gui.screen_frame.queue_draw()
        # 设置菜单禁用(字幕/音频语言).
        self.media_play_menus.menus.screen_right_root_menu.set_menu_item_sensitive_by_index(11, False)
        self.media_play_menus.menus.subtitles_select.clear_menus()
        self.media_play_menus.menus.switch_audio_menu.clear_menus()
        self.media_play_menus.menus.channel_select.set_menu_item_sensitive_by_index(1, False)
        # 保存播放完毕的进度.
        self.save_play_position()

    def save_play_position(self):
        uri = '"%s"' % str(self.ldmp.player.uri)
        pos = self.ldmp.player.position 
        length = self.ldmp.player.length
        if pos + 2 < length:
            self.ini.set("PlayMemory", uri, pos) 
            self.ini.save()
        else:
            # 如果超过length, 则是删除里面保存的选项.
            if self.ini.get("PlayMemory", uri): # 判断是否存在.
                # 删除原来保存的东西.
                del self.ini.section_dict["PlayMemory"][uri] 
                self.ini.save()
        
    def ldmp_screen_changed(self, ldmp, video_width, video_height):
        #print "ldmp_screen_changed...", "video_width:", video_width, "video_height:", video_height
        self.set_draw_background(video_width, video_height) # 是否画播放器屏幕显示的背景.
        # 如果是 窗口适应视频.
        win_to_video_check = self.config.get("FilePlay", "video_file_open")
        screen = self.gui.app.window.get_screen()
        screen_h = screen.get_height()
        screen_w = screen.get_width()
        min_app_w, min_app_h = 480, 300
        if "1" == win_to_video_check: # 判断是否为 窗口适应视频.
            video_h = int(self.ldmp.player.video_height)
            video_w = int(self.ldmp.player.video_width)
            app_h = max(min(video_h, screen_h), min_app_h)
            app_w = max(min(video_w, screen_w), min_app_w)
            self.gui.app.window.resize(app_w, app_h)
        elif "3" == win_to_video_check: # 判断是否为 上次关闭尺寸.
            app_w = self.config.get("Window", "width")
            app_h = self.config.get("Window", "height")
            if app_w and app_h: # 第一次没有初始化，不进行.
                app_w = max(min(int(app_w), screen_w), min_app_w)
                app_h = max(min(int(app_h), screen_h), min_app_h)
                self.gui.app.window.resize(app_w, app_h)
        elif "4" == win_to_video_check: # 全屏.
            self.fullscreen_function()
        
    def set_draw_background(self, video_width, video_height):
        if video_width == 0 or video_height == 0:            
            self.draw_check = True # 是否画logo.
        else:
            self.draw_check = False
        self.set_ascept_restart() # 改变屏幕比例.    
        
    def ldmp_pause_play(self, ldmp, pause_check): # 暂停状态.
        self.media_play_fun.ldmp_pause_play(pause_check)

    def ldmp_mute_play(self, ldmp, mute_check): # 静音状态.
        self.media_play_fun.ldmp_mute_play(mute_check)

    def ldmp_volume_play(self, ldmp, value): # 音量进度.
        self.media_play_fun.ldmp_volume_play(value)

    def ldmp_error_msg(self, ldmp, error_code): # 接收后端错误信息.
        #print "ldmp_error_msg->error_code:", error_code
        pass 
        
    def screen_expose_event(self, widget, event):    
        cr = widget.window.cairo_create()
        rect = widget.allocation
        if self.draw_check: # 是否画播放器屏幕显示的背景.
            # 画周围logo黑边.
            cr.set_source_rgb(*color_hex_to_cairo("#0D0D0D")) # 1f1f1f
            cr.rectangle(rect.x, rect.y, rect.width, rect.height)
            cr.fill()
            # draw deepin media player logo.
            draw_pixbuf(cr,
                        self.background, 
                        rect.x + rect.width/2 - self.background.get_width()/2, 
                        rect.y + rect.height/2 - self.background.get_height()/2)

    def screen_configure_event(self, widget, event):
        self.set_ascept_restart() # 设置分辨率.

    def screen_frame_event_button_press_event(self, widget, event):
        if event.button == 1:
            self.save_double_data(event)
            self.save_move_data(event)

    def save_double_data(self, event):
        # 保存双击 x_root 和 y_root 坐标, 用于判断是否单击/双击区域内.
        self.save_double_x = int(event.x_root)
        self.save_double_y = int(event.y_root)

    def save_move_data(self, event):
        # 保存 event 的 button, x_root, y_root, time, 用于移动窗口.
        self.save_move_button = event.button
        self.save_move_x = int(event.x_root)
        self.save_move_y = int(event.y_root)
        self.save_move_time = event.time
        # 设置移动标志位.
        self.move_win_check = True

    def screen_frame_event_button_release_event(self, widget, event): # 连接屏幕单击/双击事件.
        if event.button == 1:
            # setting screen paned handle.
            self.gui.set_paned_handle(event)
            # move app window.
            self.run_double_and_click(event)

    def run_double_and_click(self, event):
        self.move_win_check = False # 取消移动窗口.
        new_double_x = int(event.x_root)
        new_double_y = int(event.y_root)
        double_width = 5
        # 判断如果点击下去移动了以后的距离,才进行单击和双击.
        if self.gui.not_in_system_widget():
            if ((self.save_double_x - double_width <= new_double_x <= self.save_double_x + double_width) and 
                (self.save_double_y - double_width <= new_double_y <= self.save_double_y + double_width)):
                if not self.timer.Enabled:
                    self.timer.Interval = self.interval
                    self.timer.Enabled = True
                else:
                    self.double_check  = True

                if self.timer.Enabled and self.double_check:
                    self.double_clicked_connect_function() # 执行双击的代码.
                    self.set_double_bit_false()
            else:
                self.set_double_bit_false()
            
    def timer_tick_event(self, tick):
        self.click_connect_function() # 执行单击的代码.
        self.set_double_bit_false()

    def double_clicked_connect_function(self):
        double_check = self.config.get("OtherKey", "mouse_left_double_clicked")
        if _("Full Screen") == double_check:
            self.fullscreen_function() # 全屏和退出全屏处理函数.

    def fullscreen_function(self):
        if not self.fullscreen_check: # 判断是否全屏.
            self.concise_mode() # 简洁模式.
            self.gui.app.window.fullscreen() # 全屏.
            self.fullscreen_check = True
            self.gui.top_toolbar.toolbar_radio_button.set_full_state(True)
        else:
            self.gui.top_toolbar.toolbar_radio_button.set_full_state(False)
            self.gui.app.window.unfullscreen()
            if not self.concise_check: # 如果是简洁模式,不普通模式.
                self.normal_mode() # 普通模式.
            self.fullscreen_check = False

    def concise_mode(self): # 简洁模式调用.
        # 左边部件child2操作.
        self.gui.close_right_child2()
        self.gui.screen_paned.set_all_size()
        self.gui.hide_handle()
        #
        self.gui.hide_play_control_paned()
        self.gui.main_ali.set_padding(0, 0, 0, 0) # 设置下,左右的距离.
        self.gui.app.hide_titlebar() # 隐藏标题栏.

    def normal_mode(self): # 普通模式调用.
        self.gui.main_ali.set_padding(0, 2, 2, 2)
        self.gui.app.show_titlebar()
        # 左边部件child2操作.
        self.gui.show_handle()
        self.gui.show_play_control_paned()
        if self.gui.child2_show_check:
            self.gui.open_right_child2() 
            self.gui.screen_paned.set_all_size()

    def click_connect_function(self):
        # 暂停/继续. 
        # 应该去连接后端事件,暂停/播放的时候去改变按钮状态.
        pause_play_check = self.config.get("OtherKey", "mouse_left_single_clicked")
        #[OtherKey] 其它快捷键.
        if _("Pause/Play") == pause_play_check:
            self.ldmp.pause()

    def set_double_bit_false(self):
        self.double_check = False
        self.timer.Enabled = False

    def screen_frame_event_button_motoin_notify_event(self, widget, event):
        if self.move_win_check:
            self.move_window_function(event)
        # 显示下部工具条.
        if (self.__in_bottom_window_check(widget, event) and 
            (self.fullscreen_check or self.concise_check)):
            self.gui.screen_paned.bottom_window.show()
            self.gui.screen_paned.bottom_win_show_check = True

    def move_window_function(self, event): # move window 移动窗口.
        if self.gui.not_in_system_widget():
            move_width = 5
            new_move_x = int(event.x_root)
            new_move_y = int(event.y_root)
            if not ((self.save_move_x - move_width <= new_move_x <= self.save_move_x + move_width) and 
                (self.save_move_y - move_width <= new_move_y <= self.save_move_y + move_width)):
                self.gui.app.window.begin_move_drag(self.save_move_button, 
                                                    self.save_move_x, 
                                                    self.save_move_y, 
                                                    self.save_move_time) 

    def screen_frame_event_leave_notify_event(self, widget, event):
        # 隐藏下部工具条.
        if event.window == self.gui.screen_frame.window:
            self.gui.screen_paned.bottom_window.hide()
            self.gui.screen_paned.bottom_win_show_check = False
            if (self.__in_bottom_window_check(widget, event) and 
                (self.fullscreen_check or self.concise_check)):
                self.gui.screen_paned.bottom_window.show()
                self.gui.screen_paned.bottom_win_show_check = True

    def __in_bottom_window_check(self, widget, event):
        if event.window == self.gui.screen_paned.window:
            min_x = 0
            max_x = self.gui.screen_paned.top_window.get_size()[0]
            min_y = widget.allocation.height - self.gui.screen_paned.bottom_win_h
            max_y = widget.allocation.height
            return ((min_y <= int(event.y) < max_y) and 
                (min_x <= int(event.x) < max_x))

    def play(self, play_name):
        play_file = play_name
        if play_file:
            self.init_ldmp_player(play_file)
            self.ldmp_play(play_file)

    def init_ldmp_player(self, play_file=None):
        self.play_list_check = True
        if self.ldmp.player.state: # 判断是否在播放,如果在播放就先退出.
            self.ldmp.quit()
        ####################################
        ## 初始化设置, 比如加载的字幕或者起始时间等等.
        start_time = 0
        pos_check = self.config.get("FilePlay", "memory_up_close_player_file_postion") 
        if "True" == pos_check:
            uri = '"%s"' % (play_file)
            pos = self.ini.get("PlayMemory", uri)
            if pos:
                start_time = float(pos)
        self.ldmp.player.start_time = start_time
        self.ldmp.player.subtitle = []
        # 音轨选择初始化.
        self.ldmp.player.audio_index = 0
        self.ldmp.player.audio_list = []
        self.ldmp.player.sub_index = -1
        self.ldmp.player.subtitle = []

    # 上一曲.
    def prev(self):    
        play_file = self.play_list.get_prev_file()
        if play_file:
            self.init_ldmp_player(play_file)
            self.ldmp_play(play_file)
    
    # 下一曲.
    def next(self):    
        play_file = self.play_list.get_next_file()
        if play_file:
            self.init_ldmp_player(play_file)
            self.ldmp_play(play_file)

    def ldmp_play(self, play_file):
        self.ldmp.player.uri = "%s" % play_file
        if self.play_list.get_index() != -1:
            list_view = self.gui.play_list_view.list_view
            name = list_view.items[self.play_list.get_index()].sub_items[0].text
        self.show_messagebox(name)
        self.ldmp.play()

    def mute_umute(self):
        if self.ldmp.player.volumebool:
            self.ldmp.offmute()
        else:
            self.ldmp.nomute()

    def stop(self):
        self.play_list_check = True
        self.ldmp.stop()
        
    def key_fseek(self):
        self.ldmp.fseek(SEEK_VALUE)

    def key_bseek(self):
        self.ldmp.bseek(SEEK_VALUE)

    def key_inc_volume(self): # 添加音量.
        self.ldmp.addvolume(VOLUME_VALUE)

    def key_dec_volume(self): # 减少音量.
        self.ldmp.decvolume(VOLUME_VALUE)

    def key_set_volume(self, volume):
        self.ldmp.setvolume(volume)

    ########################################
    def open_file_dialog(self):
        # 多选文件对话框.
        open_dialog = gtk.FileChooserDialog(_("Select Files"),
                                            None,
                                            gtk.FILE_CHOOSER_ACTION_OPEN,
                                            (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                             gtk.STOCK_OPEN, gtk.RESPONSE_ACCEPT))

        open_dialog.set_current_folder(get_home_video())
        open_dialog.set_select_multiple(True) # 多选文件.
        res = open_dialog.run()
        paths = []
        if res == gtk.RESPONSE_ACCEPT:
            paths = open_dialog.get_filenames()

        open_dialog.destroy()
        return paths

    def open_files_to_play_list(self, type_check=True):
        paths = self.open_file_dialog()
        self.files_to_play_list(paths, type_check)

    def files_to_play_list(self, paths, type_check=True):
        self.run_check = False
        run_check = self.run_check
        sub_check = True
        # 判断字幕和播放文件.
        # 修复BUG：字幕和播放文件一起拖进去，没有清空播放列表.
        # 修复BUG：字幕拖进去，清空了播放列表.
        for path in paths:
            if not is_file_sub_type(path):
                sub_check = True
            else:
                sub_check = False

        if type_check and paths and sub_check:
            self.gui.play_list_view.list_view.clear()
            self.play_list.set_index(-1)
            run_check = True
        gtk.timeout_add(1, self.timeout_add_paths, paths, run_check)

    def timeout_add_paths(self, paths, run_check):
        for path in paths:
            self.scan_file_event(None, path)

        if run_check: # 如果是清空列表添加的文件,播放东西.
            self.next()

    def open_dir_dialog(self):
        # 多选目录对话框.
        open_dialog = gtk.FileChooserDialog(_("Select Directory"),
                                            None,
                                            gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                            (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                             gtk.STOCK_OPEN, gtk.RESPONSE_OK))

        open_dialog.set_current_folder(get_home_video())
        open_dialog.set_select_multiple(True) # 多选文件夹.
        res = open_dialog.run()
        paths = []
        if res == gtk.RESPONSE_OK:
            paths = open_dialog.get_filenames()

        open_dialog.destroy()
        return paths

    def open_dirs_to_play_list(self, type_check=True):
        paths = self.open_dir_dialog()
        self.run_check = False
        self.dirs_to_play_list(paths)

    def dirs_to_play_list(self, paths, type_check=True):
        self.type_check = type_check
        self.run_check = False
        if type_check and paths:
            self.gui.play_list_view.list_view.clear()
            self.play_list.set_index(-1)
            self.run_check = True

        for path in paths:
            scan_dir = ScanDir(path)
            scan_dir.connect("scan-file-event", self.scan_file_event)                
            scan_dir.connect("scan-end-event",  self.scan_end_event)
            scan_dir.start()


    def get_length(self, file_path):
        import subprocess
        cmd = "ffmpeg -i '%s' 2>&1 | grep 'Duration' | cut -d ' ' -f 4 | sed s/,//" % (file_path)
        fp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        cmd_str = fp.communicate()[0]
        if cmd_str:
            try:
                cmd_str = cmd_str.replace("\n", "")
                time = cmd_str.split(":")
                hour = time[0]
                min  = time[1]
                sec  = time[2].split(".")[0]
                cmd_str = hour + ":" + min + ":" + sec
            except:
                cmd_str = None
        return cmd_str

    def scan_file_event(self, scan_dir, file_name):
        # 判断文件类型是否可播放..
        # get_play_type(file_name)
        if True: #is_file_audio(file_name):
            if is_file_sub_type(file_name):
                self.ldmp.sub_add(file_name)
            else:
                uri = '"%s"' % (file_name)
                ini_len = self.ini.get("PlayTime", uri) 
                if ini_len:
                    cmd_str = ini_len
                else:
                    cmd_str = self.get_length(file_name)
                    self.ini.set("PlayTime", uri, cmd_str)
                    self.ini.save()
                if cmd_str:
                    self.gui.play_list_view.list_view.items.add([get_play_file_name(file_name), cmd_str, file_name])

    def scan_end_event(self, scan_dir, sum):
        if self.run_check:
            self.next()
            self.run_check = False

    def config_gui(self):
        ini_gui = IniGui()
        ini_gui.ini.connect("config-changed", self.restart_load_config_file)

    def restart_load_config_file(self, ini_gui, sec_root, sec_argv, sec_value):
        #print "ini_gui", ini_gui, "sec_root:", sec_root, "sec_argv:", sec_argv, "sec_value:", sec_value
        self.config.set(sec_root, sec_argv, sec_value)
        self.config.save()

    def top_toolbar_concise_button_clicked(self):
        if self.concise_check == False or self.fullscreen_check:
            self.concise_check = False
            self.key_concise_mode()

    def top_toolbar_common_button_clicked(self):
        if self.concise_check == True or self.fullscreen_check: 
            self.concise_check = True
            self.key_concise_mode()

    ######################################################
    ## keymap press event
    def key_concise_mode(self):
        if self.fullscreen_check:
            self.fullscreen_function()
        if not self.concise_check:
            if self.fullscreen_check:
                self.fullscreen_function()
            self.concise_mode()
            self.concise_check = True
            self.gui.top_toolbar.toolbar_radio_button.set_window_mode(True)
        else:
            self.normal_mode()
            self.concise_check = False
            self.gui.top_toolbar.toolbar_radio_button.set_window_mode(False)

    def key_quit_fullscreen(self):
        if self.fullscreen_check:
            self.fullscreen_function()

    def key_pause(self):
        self.ldmp.pause()

    def start(self):
        self.gui.app.window.show_all()
        self.gui.screen.window.set_composited(True)

    def modify_config_section_value(self, config, section, argv, value):
        if section == "SystemSet" and (argv in ["font", "font_size"]):
            font = config.get(section, "font")
            font_size = config.get(section, "font_size")
            # 设置深度影音提示字体和颜色.
            self.gui.tooltip_change_style(font, font_size)
        # 判断是否设置了 可以运行多个深度影音的选项.
        if section == "FilePlay" and (argv in ["check_run_a_deepin_media_player"]):
            run_check = self.config.get("FilePlay", "check_run_a_deepin_media_player")
            # 判断是否可以是运行一个深度影音.
            if not ("True" == run_check):
                self.save_dbus_id() # 保存dbus ID.
                if (not self.is_exists_check) and not is_exists(APP_DBUS_NAME, APP_OBJECT_NAME):
                    self.signal_run_ldmp()
                    self.is_exists_check = True

    def show_messagebox(self, text, icon_path=None):
        # 判断是使用影音自带提示还是使用气泡.[读取ini文件]
        sys_check  = self.config.get("SystemSet", "start_sys_bubble_msg")
        play_check = self.config.get("SystemSet", "start_play_win_msg")
        # 是否深度影音自带的提示.
        if "True" == play_check:
            self.gui.show_tooltip_text(text)
        # 还是使用系统的气泡垃圾提示.
        if "True" == sys_check:
            self.gui.notify_msgbox("deepin-media-player", text)

    def start_button_clicked(self):
        # 判断列表是否为空. 空->添加!!
        if not len(self.gui.play_list_view.list_view.items):
            self.open_files_to_play_list()
        else:
            # 判断是否在播放.
            if self.ldmp.player.state:
                self.ldmp.pause()
            else:
                self.play(self.ldmp.player.uri)

    def add_net_to_play_list(self, name, play_uri, length, check): 
        # 添加网络地址到播放列表，再的判断是否播放.
        if check:
            self.play_list.set_index(len(self.list_view.items) - 1)
        #
        self.list_view.items.add([str(name), str(length), str(play_uri)])
        #
        if check:
            self.next()

