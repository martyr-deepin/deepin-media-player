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



from dtk.ui.menu import Menu
from dtk.ui.utils import get_widget_root_coordinate
from dtk.ui.constant import WIDGET_POS_BOTTOM_LEFT
from skin import app_theme
from locales import _



class PlayMenus(object):
    def __init__(self):
        self.init_system_pixbuf()
        self.__init_menus()
        
    def init_system_pixbuf(self):    
        # aspect state pixbuf.
        self.video_aspect_pixbuf        = app_theme.get_pixbuf("screen/check_normal.png") 
        self.video_aspect_select_pixbuf = app_theme.get_pixbuf("screen/check_hover.png")
        self.video_aspect_none_pixbuf   = app_theme.get_pixbuf("screen/check_none.png")
        self.select_pixbuf = (self.video_aspect_pixbuf, 
                              self.video_aspect_select_pixbuf,
                              self.video_aspect_none_pixbuf)
        '''
        # concie pixbuf.
        self.menu_concie_normal_pixbuf = app_theme.get_pixbuf("screen/menu_concise_normal.png")
        self.menu_concie_hover_pixbuf = app_theme.get_pixbuf("screen/menu_concise_hover.png")
        self.menu_concie_none_pixbuf = app_theme.get_pixbuf("screen/menu_concise_none.png")
        # window mode.
        self.menu_window_mode_normal_pixbuf = app_theme.get_pixbuf("screen/menu_window_mode_normal.png")
        self.menu_window_mode_hover_pixbuf = app_theme.get_pixbuf("screen/menu_window_mode_hover.png")
        self.menu_window_mode_none_pixbuf = app_theme.get_pixbuf("screen/menu_window_mode_none.png")
        # play sequence.
        self.menu_play_sequence_normal_pixbuf = app_theme.get_pixbuf("screen/menu_play_sequence_normal.png")
        self.menu_play_sequence_hover_pixbuf = app_theme.get_pixbuf("screen/menu_play_sequence_hover.png")
        self.menu_play_sequence_none_pixbuf = app_theme.get_pixbuf("screen/menu_play_sequence_none.png")
        # full .
        self.menu_full_normal_pixbuf = app_theme.get_pixbuf("screen/menu_full_normal.png") 
        self.menu_full_hover_pixbuf = app_theme.get_pixbuf("screen/menu_full_hover.png")
        self.menu_full_none_pixbuf = app_theme.get_pixbuf("screen/menu_full_none.png")
        # pre.
        self.menu_pre_normal_pixbuf = app_theme.get_pixbuf("screen/menu_pre_normal.png")
        self.menu_pre_hover_pixbuf = app_theme.get_pixbuf("screen/menu_pre_hover.png")
        self.menu_pre_none_pixbuf = app_theme.get_pixbuf("screen/menu_pre_none.png")
        # next.
        self.menu_next_normal_pixbuf = app_theme.get_pixbuf("screen/menu_next_normal.png")
        self.menu_next_hover_pixbuf = app_theme.get_pixbuf("screen/menu_next_hover.png")        
        self.menu_next_none_pixbuf = app_theme.get_pixbuf("screen/menu_next_none.png")        
        # f seek 5.
        self.menu_f_seek_5_normal_pixbuf = app_theme.get_pixbuf("screen/menu_f_seek_5_normal.png")
        self.menu_f_seek_5_hover_pixbuf = app_theme.get_pixbuf("screen/menu_f_seek_5_hover.png")
        self.menu_f_seek_5_none_pixbuf = app_theme.get_pixbuf("screen/menu_f_seek_5_none.png")
        # b seek 5.
        self.menu_b_seek_5_normal_pixbuf = app_theme.get_pixbuf("screen/menu_b_seek_5_normal.png")
        self.menu_b_seek_5_hover_pixbuf = app_theme.get_pixbuf("screen/menu_b_seek_5_hover.png")
        self.menu_b_seek_5_none_pixbuf = app_theme.get_pixbuf("screen/menu_b_seek_5_none.png")
        # volume.
        self.menu_volume_normal_pixbuf = app_theme.get_pixbuf("screen/menu_volume_normal.png")
        self.menu_volume_hover_pixbuf = app_theme.get_pixbuf("screen/menu_volume_hover.png")
        self.menu_volume_none_pixbuf = app_theme.get_pixbuf("screen/menu_volume_none.png")
        # settin.
        self.menu_setting_normal_pixbuf = app_theme.get_pixbuf("screen/menu_setting_normal.png")
        self.menu_setting_hover_pixbuf = app_theme.get_pixbuf("screen/menu_setting_hover.png")
        self.menu_setting_none_pixbuf = app_theme.get_pixbuf("screen/menu_setting_none.png")
        # quit.
        self.menu_quit_normal_pixbuf = app_theme.get_pixbuf("screen/menu_quit_normal.png")
        self.menu_quit_hover_pixbuf = app_theme.get_pixbuf("screen/menu_quit_hover.png")
        self.menu_quit_none_pixbuf = app_theme.get_pixbuf("screen/menu_quit_none.png")
        # subtitle.
        self.menu_subtitle_normal_pixbuf = app_theme.get_pixbuf("screen/menu_subtitle_normal.png")
        self.menu_subtitle_hover_pixbuf = app_theme.get_pixbuf("screen/menu_subtitle_hover.png")
        self.menu_subtitle_none_pixbuf = app_theme.get_pixbuf("screen/menu_subtitle_none.png")        
        # play sequence pixbuf.
        self.play_sequence_select_normal_pixbuf = app_theme.get_pixbuf("screen/check_normal.png")
        self.play_sequence_select_hover_pixbuf = app_theme.get_pixbuf("screen/check_hover.png")
        self.play_sequence_select_none_pixbuf = app_theme.get_pixbuf("screen/check_none.png")
        # channel_select pixbuf.
        self.select_channel_normal_pixbuf = app_theme.get_pixbuf("screen/check_normal.png")
        self.select_channel_hover_pixbuf = app_theme.get_pixbuf("screen/check_hover.png")        
        self.select_channel_none_pixbuf = app_theme.get_pixbuf("screen/check_none.png")                
        # mute/add/sub volume pixbuf.
        self.mute_normal_pixbuf = app_theme.get_pixbuf("screen/menu_volume_menu_normal.png")
        self.mute_hover_pixbuf = app_theme.get_pixbuf("screen/menu_volume_menu_hover.png")
        self.mute_none_pixbuf = app_theme.get_pixbuf("screen/menu_volume_menu_none.png")                
        self.mute_volume_pixbuf = (self.mute_normal_pixbuf, self.mute_hover_pixbuf, self.mute_none_pixbuf)
        # add volume.
        self.add_volume_normal_pixbuf = app_theme.get_pixbuf("screen/menu_volume_add_normal.png")
        self.add_volume_hover_pixbuf = app_theme.get_pixbuf("screen/menu_volume_add_hover.png")
        self.add_volume_none_pixbuf = app_theme.get_pixbuf("screen/menu_volume_add_none.png")
        self.add_volume_pixbuf = (self.add_volume_normal_pixbuf, self.add_volume_hover_pixbuf, self.add_volume_none_pixbuf)
        # sub volume.
        self.sub_volume_normal_pixbuf = app_theme.get_pixbuf("screen/menu_volume_sub_normal.png")
        self.sub_volume_hover_pixbuf = app_theme.get_pixbuf("screen/menu_volume_sub_hover.png")
        self.sub_volume_none_pixbuf = app_theme.get_pixbuf("screen/menu_volume_sub_none.png")
        self.sub_volume_pixbuf = (self.sub_volume_normal_pixbuf, self.sub_volume_hover_pixbuf, self.sub_volume_none_pixbuf)        
        # down subtitle pixbuf.
        self.down_sub_title_bool = False
        self.down_sub_title_norma_pixbuf = app_theme.get_pixbuf("screen/check_normal.png")
        self.down_sub_title_hover_pixbuf = app_theme.get_pixbuf("screen/check_hover.png")
        self.down_sub_title_none_pixbuf = app_theme.get_pixbuf("screen/check_none.png")
        '''

    def __init_menus(self):
        self.config_gui      = None
        self.quit            = None
        self.init_user_guide = None
        self.full_screen     = None
        self.normal_mode     = None
        self.compact_mode    = None # 简洁模式.
        self.next            = None
        self.prev            = None
        self.fseek           = None
        self.bseek           = None
        self.open_file       = None
        self.open_dir        = None
        self.open_url        = None
        ##############################################################
        self.file_menu = Menu([(None, _("Open File"), self.__menu_open_file),
                               (None, _("Open Directory"), self.__menu_open_dir),
                               (None, _("Play Disc"), None)
                              ])
        self.play_track            = None
        self.play_default          = None
        self.play_random           = None
        self.play_repeat_track     = None
        self.play_repeat_play_list = None
        
        # 播放顺序.
        self.play_state_menu = Menu([(None, _("Play (track)"),      self.__menu_play_track), # 单曲
                                     (None, _("Default"),           self.__menu_play_default), # 顺序
                                     (None, _("Random"),            self.__menu_play_random), # 随机
                                     (None, _("Repeat (track)"),    self.__menu_play_repeat_track), # 单曲循环
                                     (None, _("Repeat (playlist)"), self.__menu_play_repeat_play_list)] # 列表循环
                                    )                       
        self.play_menu = Menu([(None, _("Full Screen"),   self.__menu_full_screen),
                               (None, _("Normal Mode"),   self.__menu_normal_mode),
                               (None, _("Compact Mode"),  self.__menu_compact_mode),
                               (None, _("Previous"),      self.__menu_prev),
                               (None, _("Next"),          self.__menu_next),
                               (None),
                               (None, _("Jump Forward"),  self.__menu_fseek),
                               (None, _("Jump Backward"), self.__menu_bseek),
                               (None, _("Order"),         self.play_state_menu),
                               ])
                               
        self.normal_ascept     = None
        self._4X3_ascept       = None
        self._16X9_ascept      = None
        self._16X10_ascept     = None
        self._1_85X1_ascept    = None
        self._2_35X1_ascept    = None
        
        self.video_menu = Menu([(None, _("Original"), self.__menu_normal_ascept),
                                 (None,    "4:3",     self.__menu_4X3_ascept),
                                 (None,   "16:9",     self.__menu_16X9_ascept),
                                 (None,  "16:10",     self.__menu_16X10_ascept),
                                 (None, "1.85:1",     self.__menu_1_85X1_ascept),
                                 (None, "2.35:1",     self.__menu_2_35X1_ascept),
                                 (None),
                                 (None,  _("50%"),  None),
                                 (None,  _("100%"), None),
                                 (None,  _("150%"), None),
                                 (None,  _("200%"), None),
                                 ])  
        self.stereo_channel = None
        self.left_channel   = None
        self.right_channel  = None
        self.mute_unmute    = None
        self.inc_volume     = None
        self.dec_volume     = None
        ## 格式转换.
        self.format_conversion = None
        self.task_manager      = None
        # 切换左右声道.
        self.channel_select_menu = Menu([
                (None, _("Stereo"), self.__menu_stereo_channel),
                (None, _("Left"),   self.__menu_left_channel),
                (None, _("Right"),  self.__menu_right_channel)
                ])
        self.audio_menu = Menu([(None, _("Channels"), self.channel_select_menu),
                                 (None),
                                 (None, _("Increase Volume"),  self.__menu_inc_volume),
                                 (None, _("Decrease Volume"),  self.__menu_dec_volume),
                                 (None, _("Mute/Unmute"),      self.__menu_mute_unmute),
                               ])
        self.sort_menu = Menu([(None, _("Take Screenshot"),           None),
                               (None, _("Open Screenshot Directory"), None),
                               (None, _("Set Screenshot Directory"),  None)
                              ])
        self.format_menu = Menu([(None, _("Format conversion"), self.__menu_format_conversion),
                                (None, _("Task Manager"),       self.__menu_task_manager)
                                ])
        ################################################################
        ## 主题弹出菜单.
        self.title_root_menu = Menu([
                                    (None, _("File"),  self.file_menu),
                                    (None, _("Play"),  self.play_menu),
                                    (None, _("Video"), self.video_menu),
                                    (None, _("Audio"), self.audio_menu),
                                    (None, _("Take Screenshots"),  self.sort_menu),
                                    (None, _("Format conversion"), self.format_menu),
                                    (None, _("View New Features"), self.__menu_init_user_guide),
                                    (None, _("Preferences"),       self.__menu_config_gui),
                                    (None),
                                    (None, _("Quit"), self.__menu_quit)
                                    ],
                                    True)
        ###############################################################
        # 排序.
        self.sort_menu = Menu([(None, _("By Name"), None),
                           (None, _("By Type"), None)])
        #
        ###############################################################
        self.remove_selected = self.__menu_remove_selected
        self.clear_playlist  = self.__menu_clear_playlist
        self.remove_unavailable_files  = self.__menu_remove_unavailable_files
        self.open_containing_directory = self.__menu_open_containing_directory
        self.add_open_file = None
        self.add_open_dir  = None
        self.add_open_url  = None
        self.screen_format_conversion = None
        ## 播放列表弹出菜单.
        self.play_list_root_menu = Menu([(None, _("Add File"),      self.__menu_add_open_file),
                                         (None, _("Add Directory"), self.__menu_add_open_dir),
                                         (None, _("Add URL"),       self.__menu_add_open_url),
                                         (None),
                                         (None, _("Remove Selected"), self.__menu_remove_selected),
                                         (None, _("Clear Playlist"),  self.__menu_clear_playlist),
                                         (None, _("Remove Unavailable Files"), self.__menu_remove_unavailable_files),
                                         (None),
                                         (None, _("Recent Played"), None),
                                         (None, _("Order"), self.play_state_menu),
                                         (None, _("Sort"),  self.sort_menu),
                                         (None),
                                         (None, _("Format conversion"), self.__menu_screen_format_conversion),
                                         (None, _("Open Containing Directory"), self.__menu_open_containing_directory),
                                         (None, _("Properties"), None),
                                         ],
                                         True)
        #########################################################
        # 播放菜单
        self.screen_play_menu = Menu([            
                          (None, _("Previous"),      self.__menu_prev),
                          (None, _("Next"),          self.__menu_next),
                          (None),
                          (None, _("Jump Forward"),  self.__menu_fseek),
                          (None, _("Jump Backward"), self.__menu_bseek),
                          ])
        ## 音轨选择
        # Menu([(None, "音轨一", None), (... "音轨二", None)...])
        self.switch_audio_menu = Menu(None) 
        self.audio_lang_menu = (None, _("Dubbing selection"), self.switch_audio_menu)
        # 声音.
        self.channel_select = Menu([
                (None, _("Audio channels"), self.channel_select_menu),
                self.audio_lang_menu,
                ])
        ### DVD内置菜单.
        self.dvd_built_in_menu = Menu([
                    (None, _("Move Up"),         None), 
                    (None, _("Move Down"),       None),
                    (None, _("Move Left"),       None),
                    (None, _("Move Right"),      None), 
                    (None, _("Select"),          None),
                    (None, _("Return to Title"), None),
                    (None, _("Return to Root"),  None),
                    ])
        ## DVD控制菜单. 有DVD的时候才显示出来.
        self.dvd_navigation_menu = Menu([(None, _("Previous Title"), None), 
                                         (None, _("Next title"),     None), 
                                         (None, _("Jump to"),        None),
                                         (None, _("DVD Menu"),       self.dvd_built_in_menu),
                                         ]) 
        ## 字幕选择:
        self.subtitles_select = Menu(None)
        # 屏幕弹出菜单.
        self.screen_right_root_menu = Menu([
                (None, _("Open File"),      self.__menu_open_file),
                (None, _("Open Directory"), self.__menu_open_dir),
                (None, _("Open URL"),       self.__menu_open_url),
                (None),
                (None, _("Full Screen On/Off"), self.__menu_full_screen),
                (None, _("Normal Mode"),        self.__menu_normal_mode),
                (None, _("Compact Mode"),       self.__menu_compact_mode),
                (None, _("Order"), self.play_state_menu),
                (None, _("Play"),  self.screen_play_menu),
                (None, _("Video"), self.video_menu),
                (None, _("Audio"), self.channel_select),
                (None, _("Subtitles"),      self.subtitles_select),
                (None, _("DVD Navigation"), self.dvd_navigation_menu),
                (None, _("Preferences"),    self.__menu_config_gui),
                (None),
                ], True)
                                     
    def show_theme_menu(self, button): 
        # 显示主题上菜单.
        self.title_root_menu.show(
             get_widget_root_coordinate(button, WIDGET_POS_BOTTOM_LEFT),
             (button.get_allocation().width, 0)) 
    
    def show_play_list_menu(self, event):
        # 显示播放列表上的菜单.
        self.play_list_root_menu.show((int(event.x_root), int(event.y_root)), (0, 0))
         
    def show_screen_menu(self, event):
        # 显示屏幕右键菜单.
        self.screen_right_root_menu.show(
                        (int(event.x_root),
                        int(event.y_root)),
                        (0, 0))
                 
    def __menu_init_user_guide(self):
        if self.init_user_guide:
            self.init_user_guide()
                      
    def __menu_config_gui(self):
        if self.config_gui:    
            self.config_gui()
    
    def __menu_quit(self):
        if self.quit:
            self.quit()
    
    def __menu_full_screen(self):
        if self.full_screen:
            self.full_screen()
           
    def __menu_normal_mode(self):
        if self.normal_mode:
            self.normal_mode()
    
    def __menu_compact_mode(self):
        if self.compact_mode:
            self.compact_mode()
     
    def __menu_next(self):
        if self.next:
            self.next()
    
    def __menu_prev(self):
        if self.prev:
            self.prev()
    
    def __menu_fseek(self):
        if self.fseek:
            self.fseek()
     
    def __menu_bseek(self):
        if self.bseek:
            self.bseek()
            
    def __menu_inc_volume(self):
        if self.inc_volume:
            self.inc_volume()
                
    def __menu_dec_volume(self):
        if self.dec_volume:
            self.dec_volume()
                  
    def __menu_stereo_channel(self):
        if self.stereo_channel:
            self.stereo_channel()
                
    def __menu_left_channel(self):
        if self.left_channel:
            self.left_channel()
            
    def __menu_right_channel(self):
        if self.right_channel:
            self.right_channel()
            
    def __menu_mute_unmute(self):
        if self.mute_unmute:
            self.mute_unmute()
                                             
    def __menu_normal_ascept(self):
        if self.normal_ascept:
            self.normal_ascept()
    
    def __menu_4X3_ascept(self):
        if self._4X3_ascept:
            self._4X3_ascept()
    
    def __menu_16X9_ascept(self):
        if self._16X9_ascept:
            self._16X9_ascept()       
                
    def __menu_16X10_ascept(self):
        if self._16X10_ascept:
            self._16X10_ascept()    
            
    def __menu_1_85X1_ascept(self):
        if self._1_85X1_ascept:  
            self._1_85X1_ascept()     
            
    def __menu_2_35X1_ascept(self):
        if self._2_35X1_ascept:
            self._2_35X1_ascept()
    
    def __menu_play_track(self):
        if self.play_track:
            self.play_track()
            
    def __menu_play_default(self):
        if self.play_default:
            self.play_default()
            
    def __menu_play_random(self):
        if self.play_random:
            self.play_random()
            
    def __menu_play_repeat_track(self):
        if self.play_repeat_track:
            self.play_repeat_track()
            
    def __menu_play_repeat_play_list(self):
        if self.play_repeat_play_list:
            self.play_repeat_play_list()

    def __menu_remove_selected(self):
        if self.remove_selected:
            self.remove_selected()
    
    def __menu_clear_playlist(self):
        if self.clear_playlist:
            self.clear_playlist()

    def __menu_remove_unavailable_files(self): 
        # 删除无效文件.
        if self.remove_unavailable_files:
            self.remove_unavailable_files()
    
    def __menu_open_containing_directory(self):
        # 开打文件的所在路径.
        if self.open_containing_directory:
            self.open_containing_directory()
    
    def __menu_open_file(self):
        if self.open_file:
            self.open_file()
            
    def __menu_open_dir(self):
        print "__menu_open_dir..."
        if self.open_dir:
            print "run..run"
            self.open_dir()
    
    def __menu_open_url(self):
        if self.open_url:
            self.open_url()
            
    def __menu_add_open_url(self):
        if self.add_open_url:
            self.add_open_url()
            
    def __menu_add_open_file(self):
        if self.add_open_file:
            self.add_open_file()
    
    def __menu_add_open_dir(self):
        if self.add_open_dir:
            self.add_open_dir()
            
    def __menu_format_conversion(self):
        if self.format_conversion:
            self.format_conversion()
    
    def __menu_task_manager(self):
        if self.task_manager:
            self.task_manager()
            
    def __menu_screen_format_conversion(self):
        if self.screen_format_conversion:
            self.screen_format_conversion()
            
            
            
            
            
                                        
