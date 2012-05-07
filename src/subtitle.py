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


from dtk.ui.application import Application
from dtk.ui.entry import TextEntry
from dtk.ui.frame import HorizontalFrame
from utils import app_theme
import gtk
import urllib
import re
import threading
import gobject

from dtk.ui.draw import draw_line
from dtk.ui.utils import container_remove_all
from dtk.ui.listview import ListView
from dtk.ui.listview import get_content_size
from dtk.ui.listview import render_text
from dtk.ui.scrolled_window import ScrolledWindow
from dtk.ui.box import EventBox
# from dtk.ui.frame import VerticalFrame
from dtk.ui.constant import DEFAULT_FONT_SIZE,ALIGN_END
from utils import allocation


gtk.gdk.threads_init()

class PlayList(object):
    
    def __init__(self):
        self.vbox = gtk.VBox()
        self.playlist_vbox = gtk.VBox()
        self.play_list_width = 220
        self.play_list_height = 50
        self.playlist_vbox.set_size_request(self.play_list_width, self.play_list_height)
        self.vbox_vframe = gtk.Alignment()
        self.vbox_vframe.set(0.0, 0.0, 1.0, 1.0)        
        self.vbox_vframe.set_padding(0, 2, 0, 0)
                
        self.scrolled_window = ScrolledWindow()    
        self.list_view = ListView(background_pixbuf=app_theme.get_pixbuf("play_list_bg.jpg"))
        self.item_array = []
        # self.list_view.connect("configure-event", self.init_playlist_path)
        # self.list_view.connect("double-click-item", self.double_click_item)
        self.scrolled_window.add_child(self.list_view)
                
        self.playlist_vbox.pack_start(self.scrolled_window)
        self.vbox_vframe.add(self.playlist_vbox)
        self.vbox.pack_start(self.vbox_vframe, True, True)
        
        self.draw_line_event_box = EventBox()
        self.draw_line_event_box.connect("expose-event", self.draw_lien_expose_event)
        self.vbox.pack_start(self.draw_line_event_box, False, False)
        
        
        
        
    def draw_lien_expose_event(self, widget, event):    
        cr, x, y, w, h = allocation(widget)
        cr.set_source_rgba(1, 1, 1, 0.1) # 10% #FFFFFF
        draw_line(cr, x, y+h-2, x+w, y+h-2)
        return True
        
    # def double_click_item(self, list_view, list_item, colume, offset_x, offset_y):    
    #     pass
    
    # def init_playlist_path(self, widget, event):                     
    #     pass
            
                
    def show_play_list(self):
        if self.vbox.get_children() == [] and self.vbox_vframe != None:
           self.vbox.add(self.vbox_vframe)
           self.vbox.pack_start(self.draw_line_event_box, False, False) 
           
    def hide_play_list(self):
        container_remove_all(self.vbox)    
        
class MediaItem(gobject.GObject):
    '''List item.'''    
    __gsignals__ = {
        "redraw-request" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
    }    
    def __init__(self, title, length):
        '''Init list item.'''
        gobject.GObject.__init__(self)
        self.update(title, length)
        self.index = None
        
    def set_index(self, index):
        '''Update index.'''
        self.index = index
        
    def get_index(self):
        '''Get index.'''
        return self.index
        
    def emit_redraw_request(self):
        '''Emit redraw-request signal.'''
        self.emit("redraw-request")
        
    def update(self, title, length):
        '''Update.'''
        # Update.
        self.title = title
        self.length = length
        
        # Calculate item size.
        self.title_padding_x = 10
        self.title_padding_y = 5
        (self.title_width, self.title_height) = get_content_size(self.title, 4) #DEFAULT_FONT_SIZE
        self.title_width = 400
        
        self.length_padding_x = 10
        self.length_padding_y = 5
        (self.length_width, self.length_height) = get_content_size(self.length, 4) #DEFAULT_FONT_SIZE
        
        
    def render_title(self, cr, rect):
        '''Render title.'''
        rect.x += self.title_padding_x
        render_text(cr, rect, self.title)
    
    def render_length(self, cr, rect):
        '''Render length.'''
        rect.width -= self.length_padding_x
        render_text(cr, rect, self.length, ALIGN_END)
        
    def get_column_sizes(self):
        '''Get sizes.'''
        return [(self.title_width + self.title_padding_x * 2, 
                 self.title_height + self.title_padding_y * 2),
                (self.length_width + self.length_padding_x * 2, 
                 self.length_height + self.length_padding_y * 2),
                ]    
    
    def get_renders(self):
        '''Get render callbacks.'''
        return [self.render_title,
                self.render_length]

    
class SubTitle(gobject.GObject):
    __gsignals__ = {
        "get-subtitle-info":(gobject.SIGNAL_RUN_LAST,
                             gobject.TYPE_NONE,(gobject.TYPE_STRING, gobject.TYPE_STRING)),
        "down-end":(gobject.SIGNAL_RUN_LAST,
                             gobject.TYPE_NONE,(gobject.TYPE_STRING, gobject.TYPE_STRING))        
        }
    def __init__(self):
        gobject.GObject.__init__(self)        
        #用于下载和进入下载页面的.
        self.html_main = "http://yyets.com/"
        #用于搜索下载用的链接地址.[搜索]
        self.html_sourct = "http://yyets.com/?mod=2&ac=search_result&op=normal&class=subtitle&keyword="        
        self.html_page = "&search=&page=" #翻页.
        self.subtitle_num = 0 #搜索的个数.
        self.down_url_dict = {} #保存字幕下载链接的字典类型.
        self.down_url_list = [] #保存搜索到的字符串
        self.file_name = ""
        
        
        
        
    def Find(self, file_name):     
        '''find subtitle.'''
        self.file_name = file_name
        html_search = urllib.urlopen(self.html_sourct + file_name).read()
        fp = open(self.file_name, "w")
        fp.write(html_search)
        fp.close()
                
        self.subtitle_num = self.get_find_subtitle_num() #获取字幕的个数        
        print "Test:Get subtitle:" + str(self.subtitle_num)
        
        self.get_down_url_address() #得到字幕下载链接地址字符串,并保存在字典类型中.                    

            
    def get_find_subtitle_num(self):    
        fp = open(self.file_name, "r")
        str_fp = unicode(fp.read(), "utf-8")
        fp.close()        
        p = re.compile(ur"(共有.+个搜索结果)")
        str_line = p.findall(str_fp)
        p2 = re.compile(ur"(>\d+<)")
        str_num = p2.findall(str_line[0])[0]        
        str_num = str_num.strip("<")
        str_num = str_num.strip(">")
        return int(str_num)
        
    def get_down_url_address(self):
        # Init.
        self.down_url_dict = {}
        self.down_url_list = []
        subtitle_sum = 0
        i = 0
        while subtitle_sum < self.subtitle_num:
            i += 1
            html_search = urllib.urlopen(self.html_sourct + self.file_name + "&search=&page=%d" % (i)).read()
            fp = open(self.file_name, "w")
            fp.write(html_search)
            fp.close()
            
            fp = open(self.file_name, "r")
            str_fp = unicode(fp.read(), "utf-8")
            fp.close()                
            p = re.compile(ur'(<li class="name"><font color.+%s.+</a> <em>  </em></li>)' % (self.file_name.decode('UTF-8')))
            str_line = p.findall(str_fp)                        
            for i_str in str_line: # save down_url_list.
                self.down_url_list.append(i_str)
            subtitle_sum += len(str_line)
            
        # subtitle down url to dict.    
        # print self.down_url_list
        path_thread_id = threading.Thread(target=self.down_list_to_dict)
        path_thread_id.start()                        
        
    def down_list_to_dict(self):        
        for list_i in self.down_url_list:
            # get subtitle name.
            p = re.compile(ur'(%s.+</a>)' % (self.file_name.decode('UTF-8')))
            str_line = p.findall(list_i)                                    
            subtitle_pos = str_line[0].index('<')
            subtitle_name = str_line[0][0:subtitle_pos] +  str_line[0][subtitle_pos+7:]
            subtitle_name = subtitle_name[:-4]
            # print subtitle_name
            # get subtitle down address.            
            p = re.compile(ur'(<a href=.+html\">)')
            str_line = p.findall(list_i)                                    
            subtitle_down_address = str_line[0][11:]
            subtitle_down_address = subtitle_down_address.strip(">")
            subtitle_down_address = self.html_main + subtitle_down_address.strip('"')
            # print subtitle_down_address
            
            #Save subtitle name and down address.
            # self.down_url_dict[subtitle_name] = subtitle_down_address                        
            self.emit("get-subtitle-info", subtitle_name, subtitle_down_address)
                        
        # print self.down_url_dict
        
    def down_url_to_path(self, down_url, file_path_and_name):
        #local down.
        html_search = unicode(urllib.urlopen(down_url).read(), "utf-8")
        p = re.compile(ur'(本地下载.+sub\">)')
        subtitle_down_address = p.findall(html_search)[0][16:].strip(">")
        subtitle_down_address = self.html_main + subtitle_down_address.strip('"')           
        urllib.urlretrieve(subtitle_down_address, file_path_and_name)
        self.emit("down-end", file_path_and_name, subtitle_down_address)
        
        
class SubTitleGui(object):
     def __init__(self):
         self.sub_title = SubTitle()
         
         self.sub_title.connect("get-subtitle-info", self.show_subtitle_info)
         self.sub_title.connect("down-end", self.down_end_messagebox)
         
         self.app = Application("SubTitle", False)
         self.app.window.set_size_request(500, 200) 
         self.app.add_titlebar(["close"],
                              app_theme.get_pixbuf("OrdinaryMode.png"),
                              "字幕搜索", " ", add_separator = True)
        
         # self.label = Label("fjsdfjsdlfk")
         self.sub_title_text = TextEntry()
         self.sub_title_text.set_size(300, 24)
         self.start_btn = gtk.Button("搜索")
         self.start_btn.connect("clicked", self.sub_title_find)
         self.start_btn.set_size_request(80, 24)
         self.top_hbox = gtk.HBox()
         self.top_hbox.pack_start(self.sub_title_text)
         self.top_hbox.pack_start(self.start_btn)
         
         self.show_subtitle_list = PlayList()
         self.show_subtitle_list.list_view.connect("double-click-item", self.down_sub_title)
         self.vbox = gtk.VBox()
         self.vbox_frame = HorizontalFrame(2)
         self.vbox_frame.add(self.vbox)
         
         self.vbox.pack_start(self.top_hbox,False,False)
         self.vbox.pack_start(self.show_subtitle_list.vbox,True,True)
         
         self.app.main_box.pack_start(self.vbox_frame)
         
         self.app.window.show_all()
         # self.app.run()
         
     def down_end_messagebox(self, subtitle, name, address):    
         print name + "下载完毕..."
         
     def down_sub_title(self, list_view, list_item, colume, offset_x, offset_y):    
         self.sub_title.down_url_to_path(self.sub_title.down_url_dict[list_item.title], 
                                         "/home/long/" + list_item.title + ".rar")
         # print self.sub_title.down_url_dict['\u9ed1\u4fa0 Hak hap']
     
     def sub_title_find(self, widget):    
         
         self.show_subtitle_list.list_view.clear()
         self.sub_title.Find(self.sub_title_text.get_text())
         
     def show_subtitle_info(self, subtitle, name, address):    
         self.sub_title.down_url_dict[name] = address
         
         gtk.timeout_add(10, self.show_subtitle_info_time, name)
         
     def show_subtitle_info_time(self, name):             
         media_item = [MediaItem(name, str(""))]                
         self.show_subtitle_list.list_view.add_items(media_item)                
         
         
SubTitleGui()         
gtk.gdk.threads_enter()         
gtk.main()
gtk.gdk.threads_leave()

# # Test get info.        
# def test(subtitle, name, address):        
#     print "'===' + test: ====",
#     print '==' + name + '===='
#     print '==' + address + '==='
#     print address
    
#     subtitle.down_url_to_path(address, "/home/long/" + name + ".rar")
    
# if __name__ == "__main__":        
#     sub_title = SubTitle()        
#     sub_title.connect("get-subtitle-info", test)
#     sub_title.Find("黑侠")
#     # sub_title.Find("功夫熊猫")
#     #sub_title.Find("黑")
    
    
    
     
        

