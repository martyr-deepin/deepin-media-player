#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 Deepin, Inc.
#               2012 Hailong Qiu
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

import urllib
import urllib2
import os
import re
from dtk.ui.threads import post_gui


SCAN_URL =  "http://www.yyets.com/php/search/index?keyword="
SCAN_PAGE_URL = "http://www.yyets.com/php/search/index"

class ScanUrlSub:
    def __init__(self):        
        self.init_value()
        
    def init_value(self):    
        self.scan_url = SCAN_URL
        self.mc_url_and_name_list = []
        self.mc_url_and_name_dict = {}
        self.current_page = 0
        # get sum subtitles.
        self.sum_subtitles = 0
        self.sum_page = 0
        # get down page url.
        self.down_page_url = ""
        self.page_string = '?page='
        self.keyword_str = ""
        self.key_dict_i = 1
        
    def scan_page_index(self, index):    
        if (self.current_page) != self.sum_subtitles:
            temp_url = self.page_string + str(index) + self.down_page_url
            temp_url = SCAN_PAGE_URL + temp_url
        else:    
            temp_url = self.page_string + self.down_page_url
            temp_url = SCAN_PAGE_URL + temp_url            
        self.get_page_all_url_list(temp_url)    
        
    def scan_url_function(self, keyword_str):
        self.init_value()
        self.keyword_str = keyword_str
        self.scan_open_url_get_informtiom(self.scan_url + str(keyword_str))
        
    def scan_open_url_get_informtiom(self, url_addr):
        '''get url informtiom.'''
        ret_html = urllib2.urlopen(url_addr)
        ret_html_string = ret_html.read()
        # get sum page.
        self.sum_subtitles = self.scan_url_sum(ret_html_string)
        # get page url.
        self.down_page_url = str(self.get_url_page(ret_html_string))

    def get_page_all_url_list(self, url_addr):
        ret_html = urllib2.urlopen(url_addr)
        ret_html_string = ret_html.read()
        patter = r'<div class="all_search_li2">.+'
        mc_list = re.findall(patter, ret_html_string)
        self.current_page = len(mc_list)
        self.mc_list_scan_function(mc_list)
    
    def get_url_page(self, ret_html_string):
        mc_page = ""
        url_page_patter = r"<a href=([\S]+)>下一页"
        patter = r'<div class="all_search_li2">.+'
        mc_list = re.findall(patter, ret_html_string)
        if len(mc_list) == self.sum_subtitles:
            self.current_page = len(mc_list)
            self.page_string = ''
            mc_page = "?keyword=" + self.keyword_str
        else:    
            self.page_string = '?page='
            self.current_page = len(mc_list)
            mc_page = re.findall(url_page_patter, ret_html_string)
            mc_page = mc_page[0][:-1]                
            mc_page = mc_page[8:]
        return mc_page

    def scan_url_sum(self, ret_html_string):    
        '''Get subtitles sum.'''
        patter_sum = r'<a class="f_out">全部\(([\S]+)\)<span'
        mc_sum = re.findall(patter_sum, ret_html_string)
        return int(mc_sum[0])
    
    def get_sum_page(self):
        '''總的頁數.'''
        # print "当前頁的字幕数:", self.current_page
        # print "总的字幕数目:",  self.sum_subtitles        
        # print "玉樹:",  self.sum_subtitles - (self.sum_subtitles / max(self.current_page, 1)) * self.current_page
        pass
    
    def mc_list_scan_function(self, mc_list):        
        url_patter = r'<a href=([\S]+)'
        # name_patter = r'target="_blank"><strong class="f14 list_title">(.+)\)</strong>'
        name_patter = r'list_title">(.+)</strong>'
        name_last_patter = r'</strong> \[(.+)\]'
        
        for mc in mc_list:
            url_mc = re.findall(url_patter, mc)
            name_mc = re.findall(name_patter, mc)
            name_last_informtiom_mc = re.findall(name_last_patter, mc)
            
            if url_mc:
                if not name_last_informtiom_mc:
                    name_last_informtiom_mc = ""
                else:    
                    name_last_informtiom_mc = " [" + name_last_informtiom_mc[0] + "]"
                    
                key = name_mc[0]+")" 
                key = key.replace("</strong>", " ")
                key = key.replace("<strong class='f1'>", " ")
                key = key.replace("[人人影视字幕组原创翻译]", " ")
                if self.mc_url_and_name_dict.has_key(key):
                    key = key + str(self.key_dict_i)
                    self.key_dict_i += 1
                self.mc_url_and_name_dict[key] = url_mc[0]
                                        
    def down_subtitle(self, url_addr, down_path="/tmp"):  
        url_addr = url_addr[1:][:-1]
        ret_html = urllib2.urlopen(url_addr)
        ret_html_string = ret_html.read()
        # get url_addr down addr..
        down_url_addr = ""
        down_patter = r'字幕下载：</font><a href=(.+)class="f3">'
        down_url_addr = re.findall(down_patter, ret_html_string)
        
        if down_url_addr:
            down_url_addr = down_url_addr[0].strip()
            down_url_addr = down_url_addr[1:][:-1]
            
            print "down_url_addr", down_url_addr
            try:
                down_data = urllib.urlopen(down_url_addr)
                # get_code = down_data.getcode()
                self.get_url = down_data.geturl()
                # get_info = down_data.info()
                # print "get_code:", get_code
                # print "get_url:", get_url
                # print "get_info:", get_info
                self.save_file_name = os.path.split(self.get_url)[1]
                # print "save_file_name:", save_file_name                
                self.save_path = os.path.join(down_path, self.save_file_name)
                # down subtitle file.
                fp = open(self.save_path, "w")
                fp.write(down_data.read())
                fp.close()
            except Exception, e:    
                print "Error:", e
                return False
            return True
        else:
            return False
        
        
                
#################################################################################################                
from skin import app_theme
from dtk.ui.button import Button
from dtk.ui.listview import ListView, render_text
from dtk.ui.dialog import DialogBox, DIALOG_MASK_MULTIPLE_PAGE
from dtk.ui.scrolled_window import ScrolledWindow
from dtk.ui.entry import InputEntry
from dtk.ui.label import Label
from dtk.ui.utils import get_content_size
from dtk.ui.constant import DEFAULT_FONT_SIZE, ALIGN_END

from ini import Config,get_home_path
from locales import _
import gtk
import gobject
import threading

TEMP_FILE_DIR = "/tmp/tmp_sub"

# gtk.gdk.threads_init()

class ScanGui(gobject.GObject):
    __gsignals__ = {
        "add-subtitle-file" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                            (gobject.TYPE_PYOBJECT,))
        }
    def __init__(self):
        gobject.GObject.__init__(self)
        # self.app = Application() 
        self.app = DialogBox(_("Search Subtitles"), 480, 350,
                             mask_type=False,
                             modal=False,
                             window_hint=gtk.gdk.WINDOW_TYPE_HINT_DIALOG,
                             window_pos=gtk.WIN_POS_CENTER,
                             resizable=True)
        self.app.set_size_request(480, 350)
        # init value.
        self.scan_url_sub = ScanUrlSub()
        self.row_height = 1
        self.current_page = 1
        self.sum_subtitle_num = 0
        # self.format_command = {".rar":"unrar x %s %s",
        #                        ".zip":"7za x -o%s"}
        self.down_to_copy_path = "/tmp/tmp_sub"
        self.highlight_item = None
        
        # main_vbox init.
        self.main_vbox = gtk.VBox()
        self.main_vbox_align = gtk.Alignment()
        self.main_vbox_align.set(1, 1, 1, 1)
        self.main_vbox_align.set_padding(6, 0, 2, 2)
        self.main_vbox_align.add(self.main_vbox)
        
        self.items = []
        self.list_view = ListView(
        [(lambda item: item.title, cmp)
         # (lambda item: item.artist, cmp),
         # (lambda item: item.length, cmp)
         ])
        self.list_view.set_expand_column(0)
        # self.list_view.add_titles([_("Subtiles"), _("Language"), _("Duration")])        
        self.list_view.add_titles([_("Subtiles")])        
        self.scrolled_window = ScrolledWindow(0, 0)        
        self.scrolled_window.add_child(self.list_view)

        # init temp dir file.
        self.init_tmp_dir()
        # top hbox init.
        self.top_hbox_init()
        # bottom hbox init.
        
        self.app.body_box.pack_start(self.top_hbox_align, False, False)
        self.app.body_box.pack_start(self.scrolled_window, True, True)
        
        self.bottom_hbox_init()

        self.scrolled_window.get_vadjustment().connect("value-changed", self.scrolled_window_load_last_sub_page)
        # list view connect events.
        self.list_view.connect("double-click-item", self.list_view_double_click_item)
        self.list_view.connect("single-click-item", self.list_view_single_click_item)
                                        
    def show_window(self):    
        # self.app.window.show_all()
        self.app.show_all()
        
    def init_tmp_dir(self):    
        if not os.path.exists(TEMP_FILE_DIR):
            os.makedirs(TEMP_FILE_DIR) # create down path.
        
    def scrolled_window_load_last_sub_page(self, vadjustment):
        try:
            self.row_height = self.list_view.items[0].get_column_sizes()[0][1]
            start_position_row = int(self.scrolled_window.get_vadjustment().get_value() / self.row_height)
            end_position_row_padding   = int(self.scrolled_window.allocation.height / self.row_height)            
            end_position_row   = end_position_row_padding + start_position_row            
            if (self.sum_subtitle_num - self.scan_url_sub.current_page) > 0 and (end_position_row >= int(self.scan_url_sub.sum_subtitles - self.sum_subtitle_num - 5)): # 动态加载页. 滚动的位置 >= 搜索总数 - 当前总数 - 5 ->> 才去加载.
                self.sum_subtitle_num -= self.scan_url_sub.current_page
                
                path_thread_id = threading.Thread(target=self.add_subtitle_page)
                path_thread_id.setDaemon(True)
                path_thread_id.start()        
                
        except Exception, e:    
            print "Error", e
            
    def add_subtitle_page(self):    
        self.current_page += 1
        self.scan_url_sub.scan_page_index(self.current_page)
        
        for key in self.scan_url_sub.mc_url_and_name_dict.keys():
            self.items.append(ListItem(str(key), ))          
            
        self.add_subtitle_page_to_play_list()
        
    @post_gui    
    def add_subtitle_page_to_play_list(self):        
        self.list_view.add_items(self.items)
    
    def list_view_double_click_item(self, ListView, item, column, offset_x, offset_y):
        self.__down_subtitle_function(item.title)
        
    def list_view_single_click_item(self, ListView, item, column, offset_x, offset_y):        
        self.highlight_item = item
            
    def top_hbox_init(self):        
        self.name_label = Label(_("Movie Name: "))
        self.name_label_align = gtk.Alignment()
        self.name_label_align.add(self.name_label)
        self.name_label_align.set(0, 0, 0, 0)
        self.name_label_align.set_padding(4, 0, 4, 4)
        
        self.name_entry = InputEntry("")
        self.name_entry.set_size(125, 24)
        self.name_entry_align = gtk.Alignment()
        self.name_entry_align.set(1, 1, 1, 1)
        self.name_entry_align.set_padding(0, 0, 2, 2)
        self.name_entry_align.add(self.name_entry)
        self.name_entry.entry.connect("press-return", self.scan_button_clicked)
        
        self.scan_button = Button(_("Search"))
        self.scan_button_align = gtk.Alignment()
        self.scan_button_align.add(self.scan_button)
        self.scan_button_align.set(1, 0, 0, 0)
        self.scan_button_align.set_padding(0, 0, 5, 5)
        
        self.top_hbox = gtk.HBox()
        self.top_hbox_align = gtk.Alignment()
        self.top_hbox_align.add(self.top_hbox)
        self.top_hbox_align.set(0, 0, 1, 1)
        
        self.top_hbox.pack_start(self.name_label_align, False, False)
        self.top_hbox.pack_start(self.name_entry_align, True, True)
        self.top_hbox.pack_start(self.scan_button_align, False, False)

        self.scan_button.connect("clicked", self.scan_button_clicked)
        
    def scan_button_clicked(self, widget):    
        scan_name = self.name_entry.get_text()
        if len(scan_name) != 0:
            # clear value.
            path_thread_id = threading.Thread(target=self.scan_subtitles_function, args=(scan_name, ))
            path_thread_id.setDaemon(True)
            path_thread_id.start()        
    
    def scan_subtitles_function(self, scan_name):
        self.list_view.clear()
        self.items = []
        self.current_page = 1
        self.scan_url_sub.scan_url_function(str(scan_name))
        self.sum_subtitle_num = self.scan_url_sub.sum_subtitles # save sum subtitles.
        
        self.scan_sub_sum_label.set_text("%s: %s" % (_("Total search results"), str(self.scan_url_sub.sum_subtitles)))
        if self.scan_url_sub.sum_subtitles > 0:
            self.scan_url_sub.scan_page_index(1)
            self.scan_url_sub.get_sum_page()        
            
            for key in self.scan_url_sub.mc_url_and_name_dict.keys():
                self.items.append(ListItem(str(key)))
                
            self.play_list_add_scan_file()
        
    @post_gui
    def play_list_add_scan_file(self):    
        self.list_view.add_items(self.items)
        
    def bottom_hbox_init(self):        
        self.scan_sub_sum_label = Label(_("Total search results: 0"))

        self.down_button = Button(_("Download"))
        
        self.close_button = Button(_("Close"))
        
        self.app.left_button_box.set_buttons([self.scan_sub_sum_label])
        self.app.right_button_box.set_buttons([self.down_button, self.close_button])
                
        self.down_button.connect("clicked", self.down_button_clicked)
        self.close_button.connect("clicked", self.close_button_clicked)
        
    def down_button_clicked(self, widget):
        '''down subtitle file.'''
        if self.highlight_item:
            self.__down_subtitle_function(self.highlight_item.title)
        
    def close_button_clicked(self, widget): 
        '''quit scan sub window.'''
        self.app.destroy()
        
    def __down_subtitle_function(self, title):    
        if self.scan_url_sub.down_subtitle(self.scan_url_sub.mc_url_and_name_dict[title]):
            # print self.scan_url_sub.save_file_name
            file_name, file_type = os.path.splitext(self.scan_url_sub.save_file_name)
            temp_file_path = os.path.join("/tmp", self.scan_url_sub.save_file_name)
            
            if ".rar" == file_type:
                cmd_line = "unrar x %s %s" % (temp_file_path, "/tmp/tmp_sub/")
            elif ".zip" == file_type:
                cmd_line = "7za x -o%s %s" % ("/tmp/tmp_sub", temp_file_path)                
                
            # run 解压缩.
            os.system(cmd_line)
            # scan dir.
            list_dir = os.listdir(TEMP_FILE_DIR)
            subtitles_list = []
            
            for file_ in list_dir:
                file_path = os.path.join("/tmp/tmp_sub/", file_)
                if os.path.isfile(file_path):
                    subtitles_list.append(file_path)
                elif os.path.isdir(file_path):
                    list_dir____ = os.listdir(file_path)
                    for file____ in list_dir____:                        
                        sub_dir_file = file_path + "/"+ file____ #os.path.join(file_path, file____)
                        if os.path.isfile(sub_dir_file):
                            subtitles_list.append(sub_dir_file)
            # messagebox infromtiom.   
            self.scan_sub_sum_label.set_text("%s%s%s" % (_("Subtile has been saved to the"), "/tmp ", _("director")))
            # print "down_subtitle_function:", subtitles_list            
            # send event.
            self.emit("add-subtitle-file", subtitles_list)
            # delete down temp .
            os.system("rm -rf %s"% (temp_file_path))
        else:
            self.scan_sub_sum_label.set_text(_("Failed to download the subtitle!"))
        
    # def messagebox_down_informtion(self):            
        # self.scan_sub_sum_label.set_text("字幕下载中")
        
# scan_gui = ScanGui()
# scan_gui.app.show_all()
# gtk.gdk.threads_enter()
# gtk.main()
# gtk.gdk.threads_leave()

# if __name__ == "__main__":
#     scan_url_sub = ScanUrlSub()
#     scan_url_sub.scan_url_function("功夫熊猫")
#     print "搜索字幕总数:", scan_url_sub.sum_subtitles
#     print '下一页需要的链接:', scan_url_sub.page_string
#     scan_url_sub.scan_page_index(3)
#     scan_url_sub.get_sum_page()
#     print "第3页:搜索到的东西:", len(scan_url_sub.mc_url_and_name_dict.keys())
#     print "=========================="
#     for i in scan_url_sub.mc_url_and_name_dict.keys():
#         print i

            
            
class ListItem(gobject.GObject):
    '''
    ListItem template to build your own item for L{ I{ListView} <ListView>}.
    
    @note: This class just template to build list item, you should build new item with same interface.
    '''
    
    __gsignals__ = {
        "redraw-request" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
    }
    
    def __init__(self, title):
        '''
        Initialize ListItem class.

        @param title: Title.
        @param artist: Artist.
        @param length: Length.
        '''
        gobject.GObject.__init__(self)
        self.update(title)
        self.index = None
        
    def set_index(self, index):
        '''
        Update index.
        
        This is ListView interface, you should implement it.
        
        @param index: Index.
        '''
        self.index = index
                
    def get_index(self):
        '''
        Get index.
        
        This is ListView interface, you should implement it.
        '''
        return self.index
        
    def emit_redraw_request(self):
        '''
        Emit redraw-request signal.
        
        This is ListView interface, you should implement it.
        '''
        self.emit("redraw-request")
        
    def update(self, title):
        '''
        Update.
        
        This is ListView interface, you should implement it.
        
        @param title: Title.
        @param artist: Artist.
        @param length: Length.
        '''
        # Update.
        self.title = title
        
        # Calculate item size.
        self.title_padding_x = 10
        self.title_padding_y = 5
        (self.title_width, self.title_height) = get_content_size(self.title, DEFAULT_FONT_SIZE)
                
    def render_title(self, cr, rect, in_select, in_highlight):
        '''
        Render title.
        
        @param cr: Cairo context.
        @param rect: Redraw rectangle. 
        @param in_select: Whether current item is selected, this value pass from ListView.
        @param in_highlight: Whether current item is highlighted, this value pass from ListView.
        '''
        rect.x += self.title_padding_x
        rect.width -= self.title_padding_x * 2
        render_text(cr, rect, self.title, in_select, in_highlight)
    
    def render_artist(self, cr, rect, in_select, in_highlight):
        '''
        Render artist.
        
        @param cr: Cairo context.
        @param rect: Redraw rectangle. 
        @param in_select: Whether current item is selected, this value pass from ListView.
        @param in_highlight: Whether current item is highlighted, this value pass from ListView.
        '''
        rect.x += self.artist_padding_x
        rect.width -= self.title_padding_x * 2
        render_text(cr, rect, self.artist, in_select, in_highlight)
    
    def render_length(self, cr, rect, in_select, in_highlight):
        '''
        Render length.
        
        @param cr: Cairo context.
        @param rect: Redraw rectangle. 
        @param in_select: Whether current item is selected, this value pass from ListView.
        @param in_highlight: Whether current item is highlighted, this value pass from ListView.
        '''
        rect.width -= self.length_padding_x * 2
        render_text(cr, rect, self.length, in_select, in_highlight, align=ALIGN_END)
        
    def get_column_sizes(self):
        '''
        Get column sizes.
        
        This is ListView interface, you should implement it.
        
        @return: Return column size tuple.
        '''
        return [(self.title_width + self.title_padding_x * 2,
                 self.title_height + self.title_padding_y * 2)
                ]    
    
    def get_renders(self):
        '''
        Get render callbacks.
        
        This is ListView interface, you should implement it.
        
        @return: Return render functions.
        '''
        return [self.render_title]
            
