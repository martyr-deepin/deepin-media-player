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
from utils import app_theme
from dtk.ui.draw import cairo_state, draw_vlinear, draw_pixbuf, draw_line, draw_font
from dtk.ui.constant import DEFAULT_FONT_SIZE
import gobject

class Button(gtk.Button):
    '''Button.'''
    
    def __init__(self, label="", width=69, height=22, padding_x=10, padding_y=3):
        '''Init button.'''
        # Init.
        gtk.Button.__init__(self)
        self.label = label
        
        # Init button size.
        (font_width, font_height) = get_content_size(label, DEFAULT_FONT_SIZE)
        self.set_size_request(max(width, font_width + 2 * padding_x), max(height, font_height + 2 * padding_y))
        
        # Handle signal.
        self.connect("expose-event", self.expose_button)
        
    def expose_button(self, widget, event):
        '''Callback for button 'expose-event' event.'''
        # Init.
        cr = widget.window.cairo_create()
        rect = widget.allocation
        x, y, w, h = rect.x, rect.y, rect.width, rect.height
        top_left = app_theme.get_pixbuf("button.png").get_pixbuf()
        top_right = top_left.rotate_simple(90)
        bottom_right = top_left.rotate_simple(180)
        bottom_left = top_left.rotate_simple(270)
        
        # Clip rectangle with four corner.
        with cairo_state(cr):
            cr.rectangle(x + 1, y, w - 2, 1)
            cr.rectangle(x, y + 1, w, h - 2)
            cr.rectangle(x + 1, y + h - 1, w - 2, 1)
            cr.clip()
            
            # Draw background.
            if widget.state == gtk.STATE_NORMAL:
                background_color = app_theme.get_shadow_color("buttonBackgroundNormal").get_color_info()
                border_color = app_theme.get_color("buttonBorderNormal").get_color()
            elif widget.state == gtk.STATE_PRELIGHT:
                background_color = app_theme.get_shadow_color("buttonBackgroundPrelight").get_color_info()
                border_color = app_theme.get_color("buttonBorderPrelight").get_color()
            elif widget.state == gtk.STATE_ACTIVE:
                background_color = app_theme.get_shadow_color("buttonBackgroundActive").get_color_info()
                border_color = app_theme.get_color("buttonBorderActive").get_color()
            draw_vlinear(cr, x, y, w, h, background_color)    

        # Draw button corner.
        draw_pixbuf(cr, top_left, x, y)
        draw_pixbuf(cr, top_right, x + w - 2, y)
        draw_pixbuf(cr, bottom_right, x + w - 2, y + h - 2)
        draw_pixbuf(cr, bottom_left, x, y + h - 2)
        
        # Draw button corner mask.
        (r, g, b) = color_hex_to_cairo(border_color)
        cr.set_source_rgba(r, g, b, 0.4)
        
        # Draw top-left corner mask.
        draw_line(cr, x + 1, y + 1, x + 2, y + 1)
        draw_line(cr, x, y + 2, x + 2, y + 2)
        
        # Draw top-right corner mask.
        draw_line(cr, x + w - 2, y + 1, x + w - 1, y + 1)
        draw_line(cr, x + w - 2, y + 2, x + w, y + 2)
        
        # Draw bottom-left corner mask.
        draw_line(cr, x + 1, y + h, x + 2, y + h)
        draw_line(cr, x, y + h - 1, x + 2, y + h - 1)

        # Draw bottom-right corner mask.
        draw_line(cr, x + w - 2, y + h, x + w - 1, y + h)
        draw_line(cr, x + w - 2, y + h - 1, x + w, y + h - 1)
        
        # Draw button border.
        cr.set_source_rgb(*color_hex_to_cairo(border_color))
        draw_line(cr, x + 2, y + 1, x + w - 2, y + 1)
        draw_line(cr, x + 2, y + h, x + w - 2, y + h)
        draw_line(cr, x + 1, y + 2, x + 1, y + h - 2)
        draw_line(cr, x + w, y + 2, x + w, y + h - 2)
        
        # Draw font.
        if self.label != "":
            draw_font(cr, self.label, DEFAULT_FONT_SIZE, 
                      app_theme.get_color("buttonFont").get_color(),
                      x, y, w, h)
        
        return True        

gobject.type_register(Button)


class TabPage(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self)
        self.tab_page_type = "h"
        self.panel_list = []
        self.title_num = 0
        
        self.vbox = gtk.VBox()
        self.hbox = gtk.HBox() 
        self.panel_box = gtk.VBox()  
        # Init "v" type struct.
                
        self.hbox.pack_start(self.vbox, False, False)
        self.hbox.pack_start(self.panel_box, True, True)
        self.pack_start(self.hbox, True, True)
        
        
    def get_main_childs(self):    
        '''获取总容器里面的所有子容器'''
        return self.get_children()
    
    def get_box_childs(self):
        box = self.return_box_container()
        return box.get_children()
        
    def get_title_childs(self):    
        '''获取便签栏里面的所有子控件'''
        if "v" == self.tab_page_type: 
            childs = self.return_title_container().get_children()
            
        if "h" == self.tab_page_type:
            childs = self.return_title_container().get_children()
            
        return childs    
    
    def get_panel_childs(self):
        '''获取面板栏里面 当前显示的控件.'''
        return self.panel_box.get_children()
    
    def return_panel_container(self):
        '''返回面板的容器'''
        return self.panel_box
    
    def return_box_container(self):    
        '''返回总容器里面的容器'''
        if "v" == self.tab_page_type: 
            return self.vbox
            
        if "h" == self.tab_page_type:
            return self.hbox
                
    def return_title_container(self):
        '''返回标签容器'''
        if "v" == self.tab_page_type: 
            return self.hbox
            
        if "h" == self.tab_page_type:
            return self.vbox
        
        
    def create_title(self, text, widget=None, image=None):
        if widget:
            self.panel_list.append(widget)
            
        box = self.return_title_container()
        button = Button(text)
        button.connect("clicked", self.clicked_show_panel, self.title_num)
        box.pack_start(button, False, False)
        self.title_num += 1
        
    # def draw_widget(self, widget, event):    
        
    #     return True
    
    def title_add_child(self, widget):    
        '''便签栏对应添加 显示的控件'''
        pass
        
    def show_index_page(self, index):
        '''显示page的页'''
        if self.panel_list[index]:
            # 清除面板容器内的东西.
            for child in self.get_panel_childs():
                self.return_panel_container().remove(child)
            #     
            self.return_panel_container().pack_start(self.panel_list[index], True, True)    
            self.show_all()
            
    def clicked_show_panel(self, widget, title_num):    
        self.show_index_page(title_num)
        
    def set_type(self, tab_page_type):    
                
        # 清除所以容器里面的东西.
        # 第一步: 清除标签里面的所有容器.
        childs = self.get_title_childs()
        for child in childs:
            box = self.return_title_container()
            box.remove(child)
        # 第二步: 清除标签和面板容器.    
        for child in self.get_box_childs():    
            self.return_box_container().remove(child)
        # 第三步: 总容器清除里面所以东西.    
        for child in self.get_main_childs():    
            self.remove(child)
            
        self.tab_page_type = tab_page_type        
        # 如果为纵向, 改变, vbox 为容器 包含 标签和面板.
        if "v" == self.tab_page_type:                
            # 标签栏添加子控件.
            for child in childs:
                print child
                self.hbox.pack_start(child, False, False)

            self.vbox.pack_start(self.hbox, False, False)
            self.vbox.pack_start(self.panel_box, True, True)
            self.pack_start(self.vbox, True, True)
            self.show_all()
            
        # 如果为横向, 改变, hbox 为容器 包含 标签和面板.    
        if "h" == self.tab_page_type:                                        
            # 标签栏添加子控件.
            for child in childs:
                self.vbox.pack_start(child, False, False)            
                
            self.hbox.pack_start(self.vbox, False, False)
            self.hbox.pack_start(self.panel_box, True, True)
            self.pack_start(self.hbox, True, True)
            self.show_all()
            
gobject.type_register(TabPage)            
            
            
# test ============            
def modify_v(widget):        
    tabpage.set_type('v')
    
def modify_h(widget):    
    tabpage.set_type('h')
    
if __name__ == "__main__":        
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    win.connect("destroy", gtk.main_quit)
    vbox = gtk.VBox()
    tabpage = TabPage()
    
    tab_vbox_0 = gtk.VBox()
    tab_vbox_0.pack_start(gtk.Button("反击的是浪费加快速度分"))
    tab_vbox_0.pack_start(gtk.Button("发觉了送到附近都开始了"))
    
    tabpage.panel_box.pack_start(tab_vbox_0)
    tabpage.create_title("text", tab_vbox_0)    
    
    tab_vbox_1 = gtk.VBox()
    tab_vbox_1.pack_start(gtk.Button("fjsdlfjdsklf"))
    tab_vbox_1.pack_start(gtk.Button("fdsljfdsklfjdklf"))
    
    tabpage.create_title("你的发动机jfdklsjfksdfjsdklfjklsdfjksdlfjdslkfj放开", tab_vbox_1)
    
    tab_vbox_2 = gtk.VBox()
    text1 = gtk.Entry()
    text1.set_text("fjskldjfdskfjkdl")
    text2 = gtk.Entry()
    text2.set_text("fjldskfjksdfjdsklfjsdkfjsdklfjskfjkfl房价是大力开发几点思考放假看")
    tab_vbox_2.pack_start(text1)
    tab_vbox_2.pack_start(text2)
    
    tabpage.create_title("反击的咖啡机", tab_vbox_2)
    tabpage.show_index_page(1)
    
    vbtn = gtk.Button("改变方向: 纵向")
    vbtn.connect("clicked", modify_v)
    hbtn = gtk.Button("改变方向: 横向")
    hbtn.connect("clicked", modify_h)    
    vbox.pack_start(tabpage)
    vbox.pack_start(vbtn)
    vbox.pack_start(hbtn)
    
    win.add(vbox)        
    win.show_all()
    gtk.main()
    
    
