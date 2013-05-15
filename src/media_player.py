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
from dtk.ui.utils import color_hex_to_cairo, propagate_expose
from locales import _ # 国际化翻译.
from ini     import Config
from user_guide import init_user_guide
from widget.constant import SEEK_VALUE
from widget.constant import VOLUME_VALUE
from widget.utils   import get_config_path
from widget.utils   import get_home_path, get_home_video, get_home_image, get_play_file_name, open_file
from widget.utils   import is_file_audio
from widget.utils   import ScanDir
from widget.utils import is_file_sub_type
from widget.utils import get_play_file_path, get_play_file_type
from widget.keymap  import get_keyevent_name
from widget.ini_gui import IniGui
from widget.init_ldmp import init_media_player_config
from gui import GUI # 播放器界面布局.
from media_player_function import MediaPlayFun
from media_player_menus    import MediaPlayMenus
from media_player_keys     import MediaPlayKeys
from media_player_drag     import MediaPlayDrag
from mplayer.timer import Timer
# mplayer后端.
from mplayer.player import LDMP, set_ascept_function, unset_flags, set_flags, Player, length_to_time, preview_scrot
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
from plugins.youku.youku_to_flvcd import YouToFlvcd
from screen_mid.open_url import OpenUrlDialog
from widget.tooltip import tooltip_text 
import random
import time
import gtk
import sys
import os
import dbus

APP_DBUS_NAME   = "com.deepin.mediaplayer"
APP_OBJECT_NAME = "/com/deepin/mediaplayer"

drag_dict = {gtk.gdk.WINDOW_EDGE_SOUTH_EAST : gtk.gdk.BOTTOM_RIGHT_CORNER, # 右下.
             gtk.gdk.WINDOW_EDGE_SOUTH_WEST : gtk.gdk.BOTTOM_LEFT_CORNER, # 左下.
             gtk.gdk.WINDOW_EDGE_SOUTH  : gtk.gdk.BOTTOM_SIDE, # 下.
             gtk.gdk.WINDOW_EDGE_WEST : gtk.gdk.LEFT_SIDE, # 左.
             gtk.gdk.WINDOW_EDGE_EAST : gtk.gdk.RIGHT_SIDE# 右.
            }


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
        self.__init_screen_tooltip()
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
                if len(sys.argv) > 1:
                    iface.argv_to_play_list(sys.argv[1:])
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
        self.run_check = False
        self.ldmp = LDMP()
        self.gui = GUI()        
        self.mid_combo_menu = self.gui.screen_mid_combo.menu
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
        # 改变播放区域，提示与原始视频的百分比.
        self.gui.screen.connect("size-request", self.app_window_size_request)
        # self.app.window.connect("leave-notify-event", )
        # self.app.window.connect("focus-out-event", )
        # self.app.window.connect("focus-in-event", )
        # self.app.window.connect("scroll_event", )
        # self.app.window.connect("check-resize",)         

    def app_window_size_request(self, widget, request):
        try:
            video_w, video_h = self.ldmp.player.video_width, self.ldmp.player.video_height
            screen_w, screen_h = self.gui.screen.allocation.width, self.gui.screen.allocation.height
            if self.ldmp.player.state:
                percent_num = int((float(screen_w * screen_h) / (video_w * video_h)) * 100)
                self.show_messagebox("%sx%s(%s%s)" % (screen_w, screen_h, percent_num, "%"), screen=True)
        except Exception, e:
            print "media_player.py=>app_window_size_request[error]:", e

    def app_window_button_press_event(self, widget, event):
        # 判断是否可拖动大小.
        drag = self.in_drag_position(widget, event)
        if drag:
            self.gui.app.window.begin_resize_drag(drag, 
                                event.button,
                                int(event.x_root),
                                int(event.y_root),
                                event.time)

    def app_window_motion_notify_event(self, widget, event):
        # 更改鼠标样式.
        drag = self.in_drag_position(widget, event)
        if drag:
            mouse_drag = drag_dict[drag]
            widget.window.set_cursor(gtk.gdk.Cursor(mouse_drag))
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

        if ((x + w - w_padding) <=  x_padding <= x + w and 
            (y + h - h_padding) <= y_padding <= y+ h):
            # 右下拖动角度.
            return gtk.gdk.WINDOW_EDGE_SOUTH_EAST
        elif ((x <= x_padding <= x + w_padding) and 
              (y + h - h_padding <= y_padding <= y + h)):
            # 左下拖动角度.
            return gtk.gdk.WINDOW_EDGE_SOUTH_WEST
        elif (x + w_padding <= x_padding <= x + w - w_padding) and ((y + h - h_padding <= y_padding <= y + h)):
            # 下方拖动角度.
            return gtk.gdk.WINDOW_EDGE_SOUTH 
        elif ((x <= x_padding <= x + w_padding)) and (y_padding < y + h - h_padding): 
            # 左方向拖动角度.
            return gtk.gdk.WINDOW_EDGE_WEST
        elif ((x + w - w_padding <= x_padding <= x + w) and 
             ((y + h/2  + 128 <= y_padding < y + h - h_padding) or
              (y <= y_padding <= y + h/2 - 128))):
            #  - 128 是为了防止点击弹出弹进的那个控件.[中间区域已经无法点击]
            # 右方向拖动角度.
            return gtk.gdk.WINDOW_EDGE_EAST 
        else:
            return False

    def __init_gui_screen(self):
        '''screen events init.'''
        self.mid_combo_menu.connect("show", self.mid_combo_menu_show_event)
        self.mid_combo_menu.connect("hide", self.mid_combo_menu_hide_event)
        #
        self.draw_check = True
        self.background = app_theme.get_pixbuf("player.png").get_pixbuf()        
        self.gui.screen_frame_event.add_events(gtk.gdk.ALL_EVENTS_MASK)
        self.gui.screen.connect("realize",            self.init_media_player)
        self.gui.screen.connect("expose-event",       self.screen_expose_event)
        self.gui.screen.connect("configure-event",    self.screen_configure_event)
        #
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
            video_w = self.ldmp.player.video_width
            video_h = self.ldmp.player.video_height
            if video_w == 0 or video_h == 0:
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
        self.gui.screen_paned.this = self
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
        # 发送屏幕提示.
        self.ldmp.connect("seek",  self.ldmp_seek_event)
        self.ldmp.connect("fseek", self.ldmp_fseek_event)
        self.ldmp.connect("bseek", self.ldmp_bseek_event)
        #
        # 全部的执行函数方法.
        self.media_play_fun   = MediaPlayFun(self)
        self.media_play_menus = MediaPlayMenus(self)
        self.media_play_kes   = MediaPlayKeys(self)
        self.media_play_drag  = MediaPlayDrag(self)
        # 初始化插件系统.
        self.init_plugin_manage()
        # 初始化命令行进入的时候.
        # import getopt .
        # 不需要用这个东西.如果需要命令行解析，那就用mplayer命令行吧.
        # 没必须要再去把mplayer命令行实现一遍, python抄袭C的东西，恶心.
        self.argv_add_to_play_list(self.argv_path_list[1:])

    def argv_add_to_play_list(self, argv):
        for path in argv:
            path = str(path)
            if os.path.exists(path):
                if os.path.isfile(path):
                    self.files_to_play_list([path])
                elif os.path.isdir(path):
                    self.dirs_to_play_list([path])

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
        # 加载同名的字幕.
        self.init_play_file_sub()

    def init_play_file_sub(self):
        try:
            uri = self.ldmp.player.uri
            video_name = get_play_file_name(uri)
            scan_sub_path = get_play_file_path(uri)
            scan_type = get_play_file_type(uri)
            #
            sub_paths = []
            for path in os.listdir(scan_sub_path):
                if get_play_file_name(path) == video_name:
                    if get_play_file_type(path) != scan_type:
                        sub_path = os.path.join(scan_sub_path, path)
                        if is_file_sub_type(sub_path):
                            # 加载字幕.
                            sub_paths.append(sub_path)
            # 加载字幕到菜单上.
            self.files_to_play_list(sub_paths, False)
        except Exception, e:
            print "media_player.py ==> init_play_file_sub[error]:", e
        
    def player_start_init(self):    
        self.set_power_play_movie()

    def set_power_play_movie(self):
        # 设置电源.
        try:
            import deepin_gsettings
            POWER_SETTINGS_GSET = "org.gnome.settings-daemon.plugins.power"
            self.power_set = deepin_gsettings.new(POWER_SETTINGS_GSET)
            self.power_set.connect("changed", self.__power_set_changed)
            self.save_power_key = self.__get_current_plan()
            self.start_check = True
            self.power_set.set_string("current-plan", "high-performance")
        except ImportError:
            print "media_player.py=>player_start_init[error]: Please install deepin Gsettings.."
    
    def __power_set_changed(self, key):
        if key == "current-plan":
            # 如果用户自行改变了，不作还原.
            if not self.start_check:
                self.save_power_key = self.__get_current_plan()
                self.start_check = False

    def __get_current_plan(self):
        current_plan = self.power_set.get_string("current-plan")
        if current_plan == "balance":
            return current_plan
        elif current_plan == "saving":
            return current_plan
        elif current_plan == "high-performance":
            return current_plan
        elif current_plan == "customized":
            return current_plan
        else:
            pass

    def ldmp_end_media_player(self, ldmp):
        #print "===========播放结束!!==========", ldmp.player.type
        self.player_end_init()
        self.media_play_fun.ldmp_end_media_player(ldmp)
        # BUG：因为全屏播放的时候，如果播放完毕，
        #不设置这个，中间的图就变样了.
        self.gui.screen_frame.set_padding(0, 0, 0, 0)
        # 播放完毕后设置电源.(还原)
        try:
            self.power_set.set_string("current-plan", self.save_power_key)
        except Exception, e:
            print "media_player.py=>ldmp_end_media_player[error]:", e
        
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
        # 提示.
        if not pause_check: # 暂停.
            text = _("Pause")
        else: # 播放.
            text = _("Play")
        self.show_messagebox(text, screen=True)

    def ldmp_mute_play(self, ldmp, mute_check): # 静音状态.
        self.media_play_fun.ldmp_mute_play(mute_check)

    def ldmp_volume_play(self, ldmp, value): # 音量进度.
        self.media_play_fun.ldmp_volume_play(value)

    def ldmp_error_msg(self, ldmp, error_code): # 接收后端错误信息.
        #print "ldmp_error_msg->error_code:", error_code
        # 错误提示.
        #self.show_messagebox(error_code, screen=True)
        pass 
    
    def ldmp_seek_event(self, ldmp, pos):
        self.show_messagebox(_("seek : ") + str(length_to_time(pos)), screen=True)
    
    def ldmp_fseek_event(self, ldmp, pos):
        self.show_messagebox(_("fseek : ") + str(length_to_time(pos)), screen=True)

    def ldmp_bseek_event(self, ldmp, pos):
        self.show_messagebox(_("bseek : ") + str(length_to_time(pos)), screen=True)
        
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
        propagate_expose(widget, event)

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
            # dvd 单击设置.
            self.ldmp.dvd_mouse()

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
            # 设置提示信息.
            tooltip_text(self.gui.top_toolbar.toolbar_full_button, _("Quit Full Screen"))
        else:
            self.gui.top_toolbar.toolbar_radio_button.set_full_state(False)
            self.gui.app.window.unfullscreen()
            self.gui.screen_frame.set_padding(0, 0, 0, 0)
            if not self.concise_check: # 如果是简洁模式,不普通模式.
                self.normal_mode() # 普通模式.
            self.fullscreen_check = False
            # 设置提示信息.
            tooltip_text(self.gui.top_toolbar.toolbar_full_button, _("Full Screen"))

    def concise_mode(self): # 简洁模式调用.
        # 左边部件child2操作.
        self.gui.close_right_child2()
        self.gui.screen_paned.set_all_size()
        self.gui.hide_handle()
        #
        self.gui.hide_play_control_paned()
        self.gui.main_ali.set_padding(0, 0, 0, 0) # 设置下,左右的距离.
        self.gui.app.hide_titlebar() # 隐藏标题栏.
        # 简洁模式四个角被扣过，需要处理掉.
        self.gui.app.window.set_window_shape(False)

    def normal_mode(self): # 普通模式调用.
        self.gui.main_ali.set_padding(0, 2, 2, 2)
        self.gui.app.show_titlebar()
        # 左边部件child2操作.
        self.gui.show_handle()
        self.gui.show_play_control_paned()
        if self.gui.child2_show_check:
            self.gui.open_right_child2() 
            self.gui.screen_paned.set_all_size()
        # 简洁模式四个角被扣过，需要处理掉.(恢复)
        self.gui.app.window.set_window_shape(True)

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
        # dvd 菜单移动设置.
        s_a = self.gui.screen.allocation
        f_a = self.gui.screen_frame.allocation
        x = int(event.x) - (f_a.width - s_a.width) + s_a.x
        y = int(event.y) - (f_a.height - s_a.height) + s_a.y
        self.ldmp.dvd_mouse_pos(x, y)
        #
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
        # 保存音量值.
        volume = self.ldmp.player.volume
        self.ldmp.player = Player()
        self.ldmp.player.start_time = start_time
        self.ldmp.player.volume = volume
        '''
        self.ldmp.player.title_is_menu = False
        self.ldmp.player.subtitle = []
        # 音轨选择初始化.
        self.ldmp.player.audio_index = -1
        self.ldmp.player.audio_list = []
        self.ldmp.player.sub_index = -1
        self.ldmp.player.subtitle = []
        '''

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
        # 提示.
        if self.play_list.get_index() != -1:
            list_view = self.gui.play_list_view.list_view
            name = list_view.items[self.play_list.get_index()].sub_items[0].text
        # 设置 dvd, vcd... media device.
        if self.ldmp.player.uri.startswith("dvd"):
            device_name = list_view.items[self.play_list.get_index()].sub_items[0].text
            self.ldmp.player.media_device = device_name
        if self.ldmp.player.uri.startswith('vcd'):
            device_name = list_view.items[self.play_list.get_index()].sub_items[0].text
            self.ldmp.player.media_device = device_name
        #
        self.ldmp.play()
        #
        if self.ldmp.player.type == TYPE_DVD:
            # 测试DVD.
            self.ldmp.dvd_prev()
        self.show_messagebox(name)

    def mute_umute(self):
        # 静音.
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
        #print type_check
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
        # 查找连续文件.
        from include.string_sort import get_as_num_index
        # 查找连续文件.
        if len(paths) == 1:
            find_check = self.config.get("FilePlay", "find_play_file_relation_file")
            if "True" == find_check and True == run_check:
                # 获取目录.
                find_path = get_play_file_path(paths[0])
                # 获取类型.
                find_type = get_play_file_type(paths[0])
                # 获取目录下的所有文件.
                find_paths = os.listdir(find_path)
                index = get_as_num_index(paths[0])
                for name in find_paths:
                    cmp_path = os.path.join(find_path, name)
                    # 防止浪费时间.!!
                    # 过滤掉多余的类型和相同的名字.
                    if (get_play_file_type(cmp_path) == find_type and 
                        cmp_path not in paths):
                        #
                        if get_as_num_index(cmp_path) == index:
                            paths.append(cmp_path)

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
        self.dirs_to_play_list(paths, type_check)

    def dirs_to_play_list(self, paths, type_check=True):
        if type_check and paths:
            self.gui.play_list_view.list_view.clear()
            self.play_list.set_index(-1)
            self.run_check = True

        for path in paths:
            scan_dir = ScanDir(path)
            scan_dir.connect("scan-file-event", self.scan_file_event)                
            scan_dir.connect("scan-end-event",  self.scan_end_event)
            scan_dir.start()

    def ldmp_to_play_list(self, paths, type_check=True):
        #
        for path in paths:
            self.read_xml(path)

    def load_profile(self, root):
        path = ""
        time = ""
        for child in root.getchildren():
            if child.tag == "path":
                path = child.text.strip()
            elif child.tag == "time":
                time = child.text.strip()
        return (path, time)

    def read_xml(self, path):
        import xml.etree.ElementTree
        tree = xml.etree.ElementTree.parse(path)
        for child in tree.getroot().getchildren():
            if child.tag == "play":
                path, time = self.load_profile(child)
                name = get_play_file_name(path)
                path = str(path)
                time = str(time)
                self.gui.play_list_view.list_view.items.add([str(name), str(time), str(path)])

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
            elif file_name.endswith("ldmp"):
                self.ldmp_to_play_list([file_name])
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
        ini_gui = IniGui(self)
        ini_gui.ini.connect("config-changed", self.restart_load_config_file)

    def open_sort_ini_gui(self):
        ini_gui = IniGui(self)
        ini_gui.set("%s" % (_("Screenshot")))
        ini_gui.ini.connect("config-changed", self.restart_load_config_file)

    def restart_load_config_file(self, ini_gui, sec_root, sec_argv, sec_value):
        #print "ini_gui", ini_gui, "sec_root:", sec_root, "sec_argv:", sec_argv, "sec_value:", sec_value
        self.config.set(sec_root, sec_argv, sec_value)
        self.config.save()

    def open_sort_image_dir(self):
        file_path = self.config.get("ScreenshotSet", "save_path")
        #
        if file_path[0] == "~":
            file_path = get_home_path() + file_path[1:]
        file_path += "/"
        #
        if file_path:
            open_file(file_path)
        else:
            open_file(get_home_image())

    def key_sort_image(self):
        if self.ldmp and self.ldmp.player.state:
            scrot_bool = self.config.get("ScreenshotSet", "current_show_sort")
            save_path = self.config.get("ScreenshotSet", "save_path")
            save_type = self.config.get("ScreenshotSet", "save_type")
            save_clipboard_bool = self.config.get("ScreenshotSet", "save_clipboard")
            #
            if save_path[0] == "~":
                save_path = get_home_path() + save_path[1:]
            # 设置保存的路径.
            save_path += "/%s-%s" % (get_play_file_name(self.ldmp.player.uri),
                                    self.ldmp.player.position)
            # 判断是否为 保存到剪切板.
            if "True" == save_clipboard_bool:
                # 设置剪切板的路径.
                clip_path = "/tmp" + "/%s-%s" % (get_play_file_name(self.ldmp.player.uri),
                                                self.ldmp.player.position)
                #
                if "True" == scrot_bool:
                    self.scrot_current_screen_pixbuf(clip_path, save_type)
                else:
                    preview_scrot(self.ldmp.player.position, 
                                  clip_path + save_type,
                                  self.ldmp.player.uri)
                #
                clip_path += save_type
                pixbuf_clip = gtk.gdk.pixbuf_new_from_file(clip_path)
                clipboard = gtk.Clipboard()
                clipboard.set_image(pixbuf_clip)
                # 提示.
            else: 
                save_file_bool = self.config.get("ScreenshotSet", "save_file")
                # 判断是否为 保存到文件路径.
                if "True" == save_file_bool:
                    if "True" == scrot_bool: # 判断是否按当前尺寸截图.
                        self.scrot_current_screen_pixbuf(save_path, save_type)
                    else:
                        preview_scrot(self.ldmp.player.position, 
                                      save_path, 
                                      self.ldmp.player.uri)
                # 提示.

    def scrot_current_screen_pixbuf(self, save_path_name, save_file_type=".png"):
        x, y, w, h = self.gui.screen_frame.get_allocation()
        #
        screen_pixbuf = gtk.gdk.Pixbuf(
                            gtk.gdk.COLORSPACE_RGB, 
                            False, 8, w, h)
        save_pixbuf = screen_pixbuf.get_from_drawable(
                            self.gui.screen_frame.window, 
                            self.gui.screen_frame.get_colormap(),
                            0, 0, 0, 0, w, h)
        # 保存当前尺寸的图片.
        save_path = save_path_name.strip() + ".png" 
        save_pixbuf.save(save_path, save_file_type[1:])

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
        #self.gui.screen_mid_combo.window.set_composited(True)

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

    def show_messagebox(self, text, icon_path=None, screen=False):
        # 判断是使用影音自带提示还是使用气泡.[读取ini文件]
        sys_check  = self.config.get("SystemSet", "start_sys_bubble_msg")
        play_check = self.config.get("SystemSet", "start_play_win_msg")
        # 是否深度影音自带的提示.
        if "True" == play_check:
            self.gui.show_tooltip_text(text)
        # 还是使用系统的气泡垃圾提示.
        if "True" == sys_check and not screen:
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
        self.list_view.items.add([str(name), str(length), str(play_uri)])
        if check:
            self.play_list.set_index(len(self.list_view.items) - 2)
        #
        if check:
            gtk.timeout_add(100, self.test_next)

    def test_next(self):
        self.next()
        return False

    def open_url_dialog(self, check, clear=True):
        open_url_win = OpenUrlDialog()
        open_url_win.ok_btn.connect("clicked", 
                        self.__url_text_key_press_event, None, open_url_win, check, clear, open_url_win.url_text)
        open_url_win.url_text.connect('key-press-event', 
                        self.__url_text_key_press_event, open_url_win, check, clear)
        open_url_win.show_all()

    def __url_text_key_press_event(self, widget, event, open_url_win, check, clear=True, text_widget=None):
        if event:
            value = get_keyevent_name(event)
        else:
            value = "Return"
            widget = text_widget
        #######################
        if value == "Return":
            open_url_win.hide_all()
            url = widget.get_text()
            text = widget.get_text()
            if url.startswith(("http:", "mms:")): # 判断是否为http连接.
                if url.startswith("http://v.youku.com"): # 添加优酷转换.
                    self.__url_add_to_playlist(text=text, type="youku", bit="优酷视频", check=check, clear=clear)
                elif url.find("pps") != -1:
                    self.__url_add_to_playlist(text=text, type="pps", bit="pps视频", check=check, clear=clear)
                else:
                    self.add_net_to_play_list(
                            text,
                            url,
                            "网络视频", check=check)
            #
    def __url_add_to_playlist(self, text, type, bit, check, clear):
        flvcd = YouToFlvcd(type)
        url_addr = flvcd.parse(text)
        if url_addr or url_addr != -1:
            if clear:
                self.list_view.items.clear()
            index = 0
            for addr in url_addr:
                temp_check = False
                if not index:
                    temp_check = check
                self.add_net_to_play_list(
                        text,
                        addr,
                        bit, temp_check)
                index += 1

    # 画面尺寸.
    def video_0x5_set_ascept(self):
        video_w, video_h = self.get_video_size()
        self.video_set_size_ascept(video_w / 2.0, video_h / 2.0)
    
    def video_1x0_set_ascept(self):
        video_w, video_h = self.get_video_size()
        self.video_set_size_ascept(video_w, video_h)

    def video_1x5_set_ascept(self):
        video_w, video_h = self.get_video_size()
        self.video_set_size_ascept(video_w * 1.5, video_h * 1.5)

    def video_2x0_set_ascept(self):
        video_w, video_h = self.get_video_size()
        self.video_set_size_ascept(video_w * 2.0, video_h * 2.0)

    def get_video_size(self):
        # 要正在播放才能获取.
        if self.ldmp.player.state:
            video  = self.ldmp.player
            video_w, video_h = video.video_width, video.video_height
            return video_w, video_h
        return 0, 0

    def video_set_size_ascept(self, w, h):
        # 播放状态才处理.
        if self.ldmp.player.state:
            # 播放窗口至中间.
            self.gui.app.window.move(0, 0)
            self.gui.app.window.set_position(gtk.WIN_POS_CENTER_ALWAYS)
            # 获取屏幕的 大小(w, h)
            if not self.fullscreen_check:
                screen = self.gui.app.window.get_screen()
                screen_w, screen_h = screen.get_width(), screen.get_height()
                w = min(w, screen_w)
                h = min(h, screen_h)
                self.gui.app.window.resize(int(w), int(h))
            else:
                app_w, app_h = self.gui.app.window.allocation.width, self.gui.app.window.allocation.height
                set_w, set_h = int(app_w - w), int(app_h - h)
                if set_w < 0 or set_h < 0:
                    self.gui.screen_frame.set_padding(0, 0, 0, 0)
                else:
                    self.gui.screen_frame.set_padding(set_h/2, 
                                                      set_h/2, 
                                                      set_w/2,
                                                      set_w/2)
                self.gui.screen_frame.set(0.5, 0.5, 0, 0)

    def mid_combo_menu_show_event(self, widget):
        # 添加cdrom东东.
        from plugins.cdrom.cdrom import scan_cdrom
        from widget.movie_menu import Menu
        self.open_cdrom = app_theme.get_pixbuf("screen_mid/screen_menu_open_cdrom.png")
        cdroms = scan_cdrom() 
        # 如果有光盘.
        if len(cdroms):
            item = (self.open_cdrom.get_pixbuf(), _("打开CDROM"))
            self.mid_combo_menu.add_menu_index_items(0, item)
        for cdrom in cdroms:
            cdrom_child_menu = Menu()
            cdrom_child_menu.set_menu_items([(None, cdrom)])
            cdrom_child_menu.connect("menu-active", self.cdrom_child_menu_play_cdrom)
            self.mid_combo_menu.add_index_child_menu(0, cdrom_child_menu)

    def cdrom_child_menu_play_cdrom(self, child_menu=None, cdrom=""):
        #print "要播放:", cdrom
        DVD, VCD, ERROR = 0, 1, -1
        from plugins.cdrom.cdrom import get_iso_type
        type = get_iso_type(cdrom)
        if DVD == type: # 播放DVD.
            list_view = self.gui.play_list_view.list_view
            self.play_list.set_index(len(list_view.items) - 1)
            item = [str(cdrom), "dvd-play", "dvdnav"]
            list_view.items.add(item)
            self.next()
        elif VCD == type: # 播放VCD.
            list_view = self.gui.play_list_view.list_view
            self.play_list.set_index(len(list_view.items) - 1)
            item = [str(cdrom), "vcd-play", "vcd://2"]
            list_view.items.add(item)
            self.next()
        else:
            pass

    def mid_combo_menu_hide_event(self, widget):
        # 复位中间按钮的菜单.
        from widget.movie_menu import Menu
        remove_items = self.mid_combo_menu.menu_items[-2:]
        self.mid_combo_menu.clear_menu_items(remove_items)

    # 初始化屏幕提示的字体样式和大小.
    def __init_screen_tooltip(self):
        try:
            font = self.config.get("SystemSet", "font")
            font_size = self.config.get("SystemSet", "font_size")
            self.gui.tooltip_change_style(font, font_size)
        except Exception, e:
            print "media_player.py=>__init_screen_tooltip[error]:", e
            
    def save_dir_dialog(self):
        #　保存目录对话框.
        open_dialog = gtk.FileChooserDialog(_("Save Directory"),
                                            None,
                                            gtk.FILE_CHOOSER_ACTION_SAVE,
                                            (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                             gtk.STOCK_SAVE, gtk.RESPONSE_OK))

        open_dialog.set_current_folder(get_home_video())
        res = open_dialog.run()
        paths = []
        if res == gtk.RESPONSE_OK:
            paths = open_dialog.get_filenames()

        open_dialog.destroy()
        return paths

        

