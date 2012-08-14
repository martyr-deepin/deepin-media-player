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

from dtk.ui.draw           import draw_text, draw_pixbuf
from dtk.ui.cache_pixbuf   import CachePixbuf

from locales   import _
from skin      import app_theme

import gobject
import gtk


# x, y, width, height
widget_save_attr = []
widget_save_num  = 1

# open button state.
OPEN_BUTTON_STATE_NORMAL = 0
OPEN_BUTTON_STATE_PRESS  = 1
OPEN_BUTTON_STATE_HOVER  = 2


class OpenButton(gobject.GObject):    
    __gsignals__ = {
        "openbutton-clicked-event":(gobject.SIGNAL_RUN_LAST,
                                    gobject.TYPE_NONE,(gobject.TYPE_PYOBJECT,)),        
        "openbutton-press-event":(gobject.SIGNAL_RUN_LAST,
                                    gobject.TYPE_NONE,(gobject.TYPE_PYOBJECT,)),
        "openbutton-release-event":(gobject.SIGNAL_RUN_LAST,
                                    gobject.TYPE_NONE,(gobject.TYPE_PYOBJECT,)),
        "openbutton-motion-event":(gobject.SIGNAL_RUN_LAST,
                                   gobject.TYPE_NONE,(gobject.TYPE_PYOBJECT,)),
        "openbutton-leave-event":(gobject.SIGNAL_RUN_LAST,
                                   gobject.TYPE_NONE,(gobject.TYPE_PYOBJECT,)),
        "openbutton-enter-event":(gobject.SIGNAL_RUN_LAST,
                                   gobject.TYPE_NONE,(gobject.TYPE_PYOBJECT,)),        
        }
    def __init__(self,
                 draw_window,
                 text = "openbutton",
                 width=120, height=40,  
                 normal_pixbuf = app_theme.get_pixbuf("screen_mid/normal_button_left.png"),
                 hover_button_pixbuf = app_theme.get_pixbuf("screen_mid/hover_button_left.png"),
                 press_button_pixbuf = app_theme.get_pixbuf("screen_mid/press_button_left.png")):
        gobject.GObject.__init__(self)
        '''Init set openbutton attr.'''
        self.draw_window = draw_window
        '''Init pixbuf.'''
        self.normal_pixbuf       = normal_pixbuf
        self.hover_button_pixbuf = hover_button_pixbuf
        self.press_button_pixbuf = press_button_pixbuf
        '''Init events.'''
        self.draw_window.add_events(gtk.gdk.ALL_EVENTS_MASK)
        self.draw_window.connect("button-press-event",   self.emit_open_button_press)
        self.draw_window.connect("button-release-event", self.emit_open_button_release)
        self.draw_window.connect("motion-notify-event",  self.emit_open_button_motion)

        '''Init state'''
        self.state = OPEN_BUTTON_STATE_NORMAL
        '''Init value.'''
        self.__padding_x = 0
        self.__padding_y = 0
        self.__x      = 0
        self.__y      = 0
        self.width  = width
        self.height = height
        self.text   = text
        self.visible_bool = False
        
        self.leave_bool = False
        self.clicked_bool = False
        self.press_bool = False        
        
        self.cache_pixbuf = CachePixbuf()
        
        global widget_save_num
        self.widget_num = widget_save_num
        widget_save_num += 1
        # save widget type attr.
        widget_save_attr.append((self.__x, self.__y, self.width, self.height))
                
    def __set_widget_save_attr(self):    
        global widget_save_attr
        widget_save_attr[self.widget_num-1] = (self.__x, self.__y, self.width, self.height)

        
    def move(self, x, y):    
        self.__padding_x = x
        self.__padding_y = y
        self.draw_window.queue_draw()
        self.__set_widget_save_attr()
        
    def set_visible(self, visible_bool):    
        self.visible_bool = visible_bool        
        self.queue_draw()
        
    def set_size(self, w, h):    
        self.width = w
        self.height = h
        self.__set_widget_save_attr()
        
    def emit_open_button_motion(self, widget, event):    
        temp_x = event.x
        temp_y = event.y
        
        
        if (self.__x + self.__padding_x <= temp_x <= self.__x + self.width + self.__padding_x) and (self.__y + self.__padding_y <= temp_y <= self.__y + self.__padding_y + self.height):        
            
            if not self.leave_bool:
                self.emit("openbutton-enter-event", event)
                if not self.press_bool:
                    self.state = OPEN_BUTTON_STATE_HOVER
                    self.queue_draw()
                
            if not self.visible_bool:    
                self.leave_bool = True                
                
            self.emit("openbutton-motion-event", event)            
        else:    
            if self.leave_bool:
                self.emit("openbutton-leave-event", event)                                
                if not self.press_bool:
                    self.state = OPEN_BUTTON_STATE_NORMAL
                    self.queue_draw()
                self.leave_bool = False
                
                                
    def queue_draw(self):            
        self.draw_window.queue_draw()
        self.__set_widget_save_attr()
        
    def emit_open_button_press(self, widget, event):    
        temp_x = event.x
        temp_y = event.y
        
        if (self.__x + self.__padding_x <= temp_x <= self.__x + self.width + self.__padding_x) and (self.__y + self.__padding_y <= temp_y <= self.__y + self.__padding_y + self.height):
            self.emit("openbutton-press-event", event)
            if not self.visible_bool:
                if event.button == 1:
                    self.press_bool = True                                
                    self.state = OPEN_BUTTON_STATE_PRESS
            self.queue_draw()    
            
    def emit_open_button_release(self, widget, event):        
        temp_x = event.x
        temp_y = event.y
        if self.press_bool:
            self.emit("openbutton-release-event", event)
            self.queue_draw()
        if (self.__x + self.__padding_x <= temp_x <= self.__x + self.width + self.__padding_x) and (self.__y + self.__padding_y <= temp_y <= self.__y + self.__padding_y + self.height):           
            if self.press_bool:
                self.state = OPEN_BUTTON_STATE_HOVER
                self.emit("openbutton-clicked-event", event)                
        else:        
            self.state = OPEN_BUTTON_STATE_NORMAL

        self.press_bool = False
        self.queue_draw()
                                
    def draw_open_button(self, widget, event):
        if not self.visible_bool:
            cr = widget.window.cairo_create()
            x, y, w, h = widget.allocation
            
            self.__x = x + w/2 - self.width/2
            self.__y = y + h/2 - self.height/2
            if self.state == OPEN_BUTTON_STATE_NORMAL:            
                pixbuf  = self.normal_pixbuf
            elif self.state == OPEN_BUTTON_STATE_HOVER:
                pixbuf  = self.hover_button_pixbuf
            elif self.state == OPEN_BUTTON_STATE_PRESS:                            
                pixbuf  = self.press_button_pixbuf

            self.cache_pixbuf.scale(pixbuf.get_pixbuf(), self.width, self.height)    
            draw_pixbuf(cr, self.cache_pixbuf.get_cache(), 
                        self.__x + self.__padding_x, 
                        self.__y + self.__padding_y)
    
            # Dra open buton font.
            draw_text(cr, self.text, 
                      self.__x + self.__padding_x + 35,
                      self.__y + self.__padding_y - 4,
                      120, 50, text_size=10, text_color="#FFFFFF")
gobject.type_register(OpenButton)        


    

class ScreenMenu(gobject.GObject):
    __gsignals__ = {
        "screenmenu-active-event":(gobject.SIGNAL_RUN_LAST,
                                    gobject.TYPE_NONE,(gobject.TYPE_PYOBJECT,)),        
        }    
    def __init__(self,
                 draw_window,                 
                 menu_item = [],
                 x = 0, y = 0,
                 menu_bg_pixbuf=app_theme.get_pixbuf("screen_mid/menu_bg_normal.png")
                 ):
        gobject.GObject.__init__(self)
        '''Init pixbuf.'''
        self.menu_bg_pixbuf = menu_bg_pixbuf
        '''Init value.'''
        self.draw_window = draw_window
        self.menu_item = menu_item                
        self.menu_list = []
        
        self.x      = x
        self.y      = y
        self.save_x = 0
        self.save_y = 0
        self.width  = self.menu_bg_pixbuf.get_pixbuf().get_width()
        self.height = self.menu_bg_pixbuf.get_pixbuf().get_height()
        self.__padding_x    = 0
        self.__padding_y    = 0
        # show and hide menu value.
        self.show_menu_bool = False
        self.show_bool = False
        self.move_bool = False
        self.leave_bool = False
        # icon value.
        self.icon_padding_x = 2
        self.icon_padding_y = 2
        self.icon_padding_height = 26
        self.index = 0
        for item in self.menu_item:
            self.menu_list.append([item[0], item[1], item[2]])
        '''Init events'''        
        if draw_window:
            self.draw_window.add_events(gtk.gdk.ALL_EVENTS_MASK)
            self.draw_window.connect("motion-notify-event", self.motion_move_fg)
            self.draw_window.connect("button-press-event",  self.press_widget_emit_active)
            
        global widget_save_num
        self.widget_num = widget_save_num
        widget_save_num += 1
        # save widget type attr.
        widget_save_attr.append((self.x, self.y, self.width, self.height))
                
    def size(self, w, h):    
        self.width = w
        self.height = h
        self.queue_draw()
        
    def __set_widget_save_attr(self):    
        global widget_save_attr
        widget_save_attr[self.widget_num-1] = (self.x, self.y, self.width, self.height)
        
    def show_menu(self, x, y):        
        self.x = x
        self.y = y
        self.show_menu_bool = True
        self.queue_draw()
        self.__set_widget_save_attr()
        
    def hide_menu(self):
        self.show_menu_bool = False        
        
    def queue_draw(self):        
        self.draw_window.queue_draw()
        self.__set_widget_save_attr()
        
    def press_widget_emit_active(self, widget, event):    
         temp_x = int(event.x)
         temp_y = int(event.y)         
         # 
         if self.show_menu_bool:             
             if (self.x  <= temp_x <= self.x + self.width) and (self.y  <= temp_y <= self.y + self.height):
                 if event.button == 1: # Left clicked.
                     self.hide_menu()
                     if self.menu_list[self.index][2]:
                         self.menu_list[self.index][2]()
             else:
                 temp_clicked_bool = True
                 global widget_save_attr
                 for widget in widget_save_attr:
                     if (widget[0] <= temp_x <= widget[0] + widget[2]):
                         temp_clicked_bool = False
                         
                 if temp_clicked_bool:
                     self.hide_menu()
                     
                     
        
    def motion_move_fg(self, widget, event):
         temp_x = int(event.x)
         temp_y = int(event.y)         
         # 
         if self.show_menu_bool:
             
             if (self.x  <= temp_x <= self.x + self.width) and (self.y  <= temp_y <= self.y + self.height):
                 index_y = int(event.y)
                 self.leave_bool = True
                 if index_y < self.y + self.icon_padding_height * len(self.menu_list)-1:
                     index = int((index_y-self.y)/ self.icon_padding_height)
                     if self.index != index:
                         self.index = index
                         self.move_bool = True
                         self.queue_draw()
             else:
                 self.move_bool = False
                 self.leave_bool = False
                 
    def draw_move_rectagnle(self, cr, x, y):     
        cr.set_source_rgba(1, 1, 1, 0.1)
        cr.rectangle(self.x + self.icon_padding_x, 
                     self.y + self.icon_padding_y + self.icon_padding_height * self.index, self.width-4,
                     self.icon_padding_height)
        cr.fill()
        
    def draw_screen_menu(self, widget, event):
        cr = widget.window.cairo_create()
        x, y, w, h = widget.allocation
        if self.show_menu_bool:
            self.draw_background(cr, x, y)
            # Draw menu rectangle.
            self.draw_move_rectagnle(cr, x, y)
            self.draw_menu_left_icon(cr, x, y)    

            
        
    def draw_background(self, cr, x, y):    
        # Draw background.
        menu_bg_pixbuf = self.menu_bg_pixbuf.get_pixbuf().scale_simple(self.width, self.height, gtk.gdk.INTERP_BILINEAR)
        draw_pixbuf(cr, menu_bg_pixbuf, self.x, self.y)
        
    def draw_menu_left_icon(self, cr, x, y):    
        # Draw menu left icon.
        temp_icon_height = 0
        for item in self.menu_list:            
            # Draw menu left icon.
            draw_pixbuf(cr, 
                        item[0].get_pixbuf(), 
                        self.x + self.icon_padding_x*2 + 7,
                        self.y + temp_icon_height + item[0].get_pixbuf().get_height()/2
                        )
            
            # Draw menu right font. 123456
            draw_text(cr, item[1], 
                      self.x + self.icon_padding_x*2 + 30,
                      self.y + temp_icon_height - 9,
                      120, 50, text_size=10, text_color="#FFFFFF")

            temp_icon_height += self.icon_padding_height 

gobject.type_register(ScreenMenu)        

####################################################
#  open dialog url window.
####################################################
from dtk.ui.dialog          import InputDialog

class OpenUrl(gobject.GObject):
    __gsignals__ = {
        "openurl-url-name":(gobject.SIGNAL_RUN_LAST,
                            gobject.TYPE_NONE,(gobject.TYPE_STRING, gobject.TYPE_INT)),
        }    
    def __init__(self):
        gobject.GObject.__init__(self)
        # url window dialog.
        self.url_win = InputDialog(_("Enter URL"), _("Please Enter a Valid URL"), confirm_callback = self.get_url_name)
        self.url_win.set_position(gtk.WIN_POS_CENTER)
        self.url_win.entry.connect("key-press-event", self.get_url_text_name)
        self.url_win.show_all()
        
    def get_url_name(self, url_name):    
        self.emit("openurl-url-name", "%s"%(url_name), True)
        
    def get_url_text_name(self, url_text, event):        
        if event.keyval == 65293: # Enter.
            self.emit("openurl-url-name", "%s"%(self.url_win.entry.get_text()), True)
            self.url_win.destroy()
            
gobject.type_register(OpenUrl)

if __name__ == "__main__":
    def get_url_name(openurl, url_name, url_bool):
        print url_name, url_bool
        
    open_url = OpenUrl()
    open_url.connect("openurl-url-name", get_url_name)
    gtk.main()
