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

# tabPage

# TabPage 的VBox 根据 tab_page_type 来 包含 vbox 还是 hbox.

import gtk
from dtk.ui.utils import get_content_size, color_hex_to_cairo
from skin import app_theme
from dtk.ui.draw import cairo_state, draw_vlinear, draw_pixbuf, draw_line, draw_text
import gobject

class Button(gtk.Button):
    '''Button.'''
    
    def __init__(self, label="", width=69, height=22, padding_x=10, padding_y=3, index = 0):
        '''Init button.'''
        # Init.
        gtk.Button.__init__(self)
        self.label = label
        self.font_size = 9
        self.index = index
        self.select_index = None
        # Init button size.
        (font_width, font_height) = get_content_size(label, self.font_size)
        self.set_size_request(max(width, font_width + 2 * padding_x), max(height, font_height + 2 * padding_y))
        
        # Handle signal.
        self.connect("expose-event", self.expose_button)
        
    def set_text(self, text):    
        self.label = text
        self.queue_draw()
        
    def set_font_size(self, size):    
        self.font_size = size
        
    def set_size(self, w, h):    
        self.set_size_request(w, h)                
        
    def set_index(self, index):    
        self.select_index = index
        self.queue_draw()
        
    def expose_button(self, widget, event):
        '''Callback for button 'expose-event' event.'''
        # Init.
        cr = widget.window.cairo_create()
        rect = widget.allocation
        x, y, w, h = rect.x, rect.y, rect.width, rect.height
            
        # draw background.
        cr.set_source_rgba(1, 1, 1, 1)
        cr.rectangle(x, y, w, h)
        cr.fill()
            
        if widget.state == gtk.STATE_PRELIGHT: 
            cr.set_source_rgba(0, 0, 0, 0.3)
            cr.rectangle(x, y, w, h)
            cr.fill()
            
        elif widget.state == gtk.STATE_ACTIVE:
            cr.set_source_rgba(0, 0, 0, 0.7)
            cr.rectangle(x, y, w, h)
            cr.fill()
                    
        # Draw font.
        if self.label != "":
            draw_text(cr, self.label, 
                      x, y, w, h,
                      self.font_size,
                      app_theme.get_color("buttonFont").get_color(),
                      )
            
        if self.select_index == self.index:    
            cr.set_source_rgba(0, 0, 0, 0.7)
            cr.rectangle(x, y, w, h)
            cr.fill()
            
            draw_text(cr, self.label, 
                      x, y, w, h,
                      self.font_size,
                      "#FFFFFF",
                      )
            
        
        return True        

gobject.type_register(Button)


class TabPage(gtk.VBox):
    def __init__(self, tab_page_type = "h"):
        gtk.VBox.__init__(self)
        self.tab_page_type = tab_page_type
        self.panel_list = {}
        self.title_num = 0
        
        self.vbox = gtk.VBox()
        self.hbox = gtk.HBox() 
        self.panel_box = gtk.VBox()  
        self.panel_box.add_events(gtk.gdk.ALL_EVENTS_MASK)
        # self.panel_box.connect("expose-event", self.draw_panel_background)
        # Init "v" type struct.
                
        self.hbox.pack_start(self.vbox, False, False)
        self.hbox.pack_start(self.panel_box, True, True)
        self.pack_start(self.hbox, True, True)
        
        
        
    def set_index_text(self, index, text):    
        '''Set title text.'''
        if index < self.title_num:
            childs = self.get_title_childs()
            childs[index].set_text(text)
            return True
        return None
    
    def set_title_size(self, w, h):    
        for child in self.get_title_childs():
            child.set_size(w, h)            
        
    def get_main_childs(self):    
        '''Get container all child container.'''
        return self.get_children()
    
    def get_box_childs(self):
        box = self.return_box_container()
        return box.get_children()
        
    def get_title_childs(self):    
        '''Get title all child container.'''
        if "v" == self.tab_page_type: 
            childs = self.return_title_container().get_children()
            
        if "h" == self.tab_page_type:
            childs = self.return_title_container().get_children()
            
        return childs    
    
    def get_panel_childs(self):
        '''Get panel  widget of curren show '''
        return self.panel_box.get_children()
    
    def return_panel_container(self):
        '''return widget of panel'''
        return self.panel_box
    
    def return_box_container(self):    
        '''return main container in container.'''
        if "v" == self.tab_page_type: 
            return self.vbox
            
        if "h" == self.tab_page_type:
            return self.hbox
                
    def return_title_container(self):
        '''return title container.'''
        if "v" == self.tab_page_type: 
            return self.hbox
            
        if "h" == self.tab_page_type:
            return self.vbox
                
    def create_title(self, text, widget=None, image=None, w=150, h=40):
        # if widget:
        self.panel_list[self.title_num] = widget
            
        box = self.return_title_container()
        button = Button(text, index=self.title_num)
        button.set_size_request(w, h)
        button.connect("clicked", self.clicked_show_panel, self.title_num)
        box.pack_start(button, False, False)
        self.title_num += 1
                    
        
    def show_index_page(self, index):
        '''show select page'''
        if self.panel_lsit_bool(index):
            for child in self.get_panel_childs():
                self.return_panel_container().remove(child)
            if self.panel_list[index]:    
                self.return_panel_container().pack_start(self.panel_list[index], True, True)    
                self.return_panel_container().show_all()
            
        # childs = self.get_title_childs()
        # childs[index].set_index(index)
            
    def panel_lsit_bool(self, index):        
        try:
            self.panel_list[index]
            return True
        except:
            return None
        
    def clicked_show_panel(self, widget, title_num):        
        if self.panel_lsit_bool(title_num):
            self.show_index_page(title_num)
            
        childs = self.get_title_childs()
        for child in childs:
            child.set_index(title_num)
            
    def set_type(self, tab_page_type):                   
        childs = self.get_title_childs()
        for child in childs:
            box = self.return_title_container()
            box.remove(child)

        for child in self.get_box_childs():    
            self.return_box_container().remove(child)

        for child in self.get_main_childs():    
            self.remove(child)
            
        self.tab_page_type = tab_page_type        
        
        # if v, modify -> vbox contaier = title and panel
        if "v" == self.tab_page_type:                
            for child in childs:
                self.hbox.pack_start(child, False, False)

            self.vbox.pack_start(self.hbox, False, False)
            self.vbox.pack_start(self.panel_box, True, True)
            self.pack_start(self.vbox, True, True)
            self.show_all()
            
        if "h" == self.tab_page_type:                                        
            for child in childs:
                self.vbox.pack_start(child, False, False)            
                
            self.hbox.pack_start(self.vbox, False, False)
            self.hbox.pack_start(self.panel_box, True, True)
            self.pack_start(self.hbox, True, True)
            self.show_all()
            
    def draw_panel_background(self, widget, event):            
        cr = widget.window.cairo_create()
        x, y, w, h = widget.allocation
        cr.set_source_rgba(1, 1, 1, 0.5)
        cr.rectangle(x, y, w, h)
        cr.fill()
        
        if "get_child" in dir(widget) and widget.get_child() != None:
            widget.propagate_expose(widget.get_child(), event)                
        return True
    
gobject.type_register(TabPage)            
            
            
# demo ============            
def modify_v(widget):        
    tabpage.set_type('v')
    
def modify_h(widget):    
    tabpage.set_type('h')
    
if __name__ == "__main__":        
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    win.connect("destroy", gtk.main_quit)
    vbox = gtk.VBox()
    tabpage = TabPage()
    
    tab_vbox_0 = gtk.Fixed()
    tab_vbox_0.put(gtk.Button("反击的是浪费加快速度分"), 20, 50)
    tab_vbox_0.put(gtk.Button("发觉了送到附近都开始了"), 70, 100)
    
    tabpage.panel_box.pack_start(tab_vbox_0)
    tabpage.create_title("文件播放", tab_vbox_0)    
    
    tab_vbox_1 = gtk.Fixed()
    tab_vbox_1.put(gtk.Button("fjsdlfjdsklf"), 20, 50)
    tab_vbox_1.put(gtk.Button("fdsljfdsklfjdklf"), 120, 50)
    
    tabpage.create_title("系统设置", tab_vbox_1)
    
    tab_vbox_2 = gtk.Fixed()
    text1 = gtk.Entry()
    text1.set_text("fjskldjfdskfjkdl")
    text2 = gtk.Entry()
    text2.set_text("fjldskfjksdfjdsklfjsdkfjsdklfjskfjkfl房价是大力开发几点思考放假看")
    tab_vbox_2.put(text1, 20, 50)
    tab_vbox_2.put(text2, 100, 200)
    
    tab_vbox_3 = gtk.Fixed()
    text3 = gtk.Entry()
    text3.set_text("fjskldjfdskfjkdl")
    tab_vbox_3.put(text3, 20, 50)

    tabpage.create_title("热键/鼠标", tab_vbox_2)
    tabpage.show_index_page(0)
    tabpage.create_title("高清加速")
    tabpage.create_title("字幕设置")
    tabpage.create_title("视频截图")
    tabpage.create_title("声音设置")
    tabpage.create_title("画面设置")
    tabpage.create_title("其它设置")
    tabpage.create_title("测试一下", tab_vbox_3)
    
    tabpage.set_index_text(10, "我知道的我知道的")
    vbtn = gtk.Button("改变方向: 纵向")
    vbtn.connect("clicked", modify_v)
    hbtn = gtk.Button("改变方向: 横向")
    hbtn.connect("clicked", modify_h)    
    vbox.pack_start(tabpage)
    vbox.pack_start(vbtn)
    vbox.pack_start(hbtn)
    tabpage.set_title_size(150, 40)
    win.add(vbox)        
    win.show_all()
    gtk.main()
    
    
