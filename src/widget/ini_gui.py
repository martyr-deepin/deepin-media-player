#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Hailong Qiu
# 
# Author:     Hailong Qiu <qiuhailong@linuxdeepin.com>
# Maintainer: Hailong Qiu <qiuhailong@linuxdeepin.com>
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
from ini import Config
from utils import get_home_path

from dtk.ui.utils import propagate_expose, is_left_button, color_hex_to_cairo
from dtk.ui.dialog import DialogBox, DIALOG_MASK_MULTIPLE_PAGE
from dtk.ui.button import Button
from dtk.ui.entry import InputEntry, ShortcutKeyEntry
from dtk.ui.combo import ComboBox
from dtk.ui.draw import draw_vlinear, draw_text, draw_pixbuf
from dtk.ui.label import Label
from dtk.ui.box import BackgroundBox, ImageBox
from dtk.ui.button import CheckButton, RadioButton
from dtk.ui.line import HSeparator
from dtk.ui.treeview import TreeView, TreeItem

import gtk
import pangocairo
import pango
from locales import _

font_test_window = gtk.Window(gtk.WINDOW_POPUP)
font_test_window.set_default_size(0, 0)
font_test_window.move(-1000000, -1000000)
DEFAULT_FONT = ' '.join(str(font_test_window.get_pango_context().get_font_description()).split(" ")[0:-1])
font_test_window.destroy()

config_path = get_home_path() + "/.config/deepin-media-player/deepin_media_config.ini"
# Ini(configure) window.
INI_WIDTH = 640
INI_HEIGHT = 480

# Label title.
label_width = 100 
label_height = 30
TITLE_WIDTH_PADDING = 10    
TITLE_HEIGHT_PADDING = 2

# Heparator.
heparator_x = 0
heparator_y = 35
heparator_width = INI_WIDTH - 143
heparator_height = 5

# video open state.
VIDEO_ADAPT_WINDOW_STATE = "1"
WINDOW_ADAPT_VIDEO_STATE = "2"
UP_CLOSE_VIDEO_STATE = "3"
AI_FULL_VIDEO_STATE = "4"

def draw_single_mask(cr, x, y, width, height, color_name):
    if color_name.startswith("#"):
        color = color_name
    else:    
        color = app_theme.get_color(color_name).get_color()
    cairo_color = color_hex_to_cairo(color)
    cr.set_source_rgb(*cairo_color)
    cr.rectangle(x, y, width, height)
    cr.fill()
    
def all_widget_to_widgets(widget_left, widget_right):
    return map(lambda left, right:(left, right), widget_left, widget_right)

def widgets_add_widget(fixed, widgets_left, widgets_right, start_x, start_y, offset_x, offset_y):
    widgets_all = all_widget_to_widgets(widgets_left, widgets_right)
    widgets_offset_x = start_x
    widgets_offset_y = start_y
    for widget_left, widget_right in widgets_all:
        widgets_offset_x = start_x        
        if widget_left:
            fixed.put(widget_left, widgets_offset_x, widgets_offset_y) # add left widget.            
        widgets_offset_x += offset_x
        if widget_right:
            fixed.put(widget_right, widgets_offset_x, widgets_offset_y) # add right widget.
        # y positon move widget_left and widget_right.    
        widgets_offset_y += offset_y

def create_separator_box(padding_x=0, padding_y=0):    
    separator_box = HSeparator(
        app_theme.get_shadow_color("hSeparator").get_color_info(),
        padding_x, padding_y)
    return separator_box

import gobject

class ExpandItem(TreeItem):
    
    def __init__(self, title, allocate_widget=None, column_index=0):
        TreeItem.__init__(self)
        self.column_index = column_index
        self.side_padding = 5
        self.item_height = 37
        self.title = title
        self.item_width = 36
        self.allocate_widget = allocate_widget
        self.child_items = []
        
        self.title_padding_x = 30
        self.arrow_padding_x = 10        
        
        # Init dpixbufs.
        self.down_normal_dpixbuf = app_theme.get_pixbuf("arrow/down_normal.png")
        self.down_press_dpixbuf = app_theme.get_pixbuf("arrow/down_press.png")
        self.right_normal_dpixbuf = app_theme.get_pixbuf("arrow/right_normal.png")
        self.right_press_dpixbuf = app_theme.get_pixbuf("arrow/right_press.png")
        
        
    def get_height(self):    
        return self.item_height
    
    def get_column_widths(self):
        return (self.item_width,)
    
    def get_column_renders(self):
        return (self.render_title,)
    
    def unselect(self):
        self.is_select = False
        self.emit_redraw_request()
        
    def emit_redraw_request(self):    
        if self.redraw_request_callback:
            self.redraw_request_callback(self)
            
    def select(self):        
        self.is_select = True
        self.emit_redraw_request()
        
    def render_title(self, cr, rect):        
        # Draw select background.
            
        if self.is_select:    
            draw_single_mask(cr, rect.x, rect.y, rect.width, rect.height, "globalItemHighlight")
        elif self.is_hover:
            draw_single_mask(cr, rect.x, rect.y, rect.width, rect.height, "globalItemHover")
        
        if self.is_select:
            text_color = "#FFFFFF"
        else:    
            text_color = app_theme.get_color("labelText").get_color()
            
        # draw arrow    
        if self.is_expand:    
            if self.is_select:
                arrow_pixbuf = self.down_press_dpixbuf.get_pixbuf()
            else:
                arrow_pixbuf = self.down_normal_dpixbuf.get_pixbuf()
        else:        
            if self.is_select:
                arrow_pixbuf = self.right_press_dpixbuf.get_pixbuf()
            else:
                arrow_pixbuf = self.right_normal_dpixbuf.get_pixbuf()
                
        arrow_x = rect.x + self.arrow_padding_x
        arrow_y = rect.y + (rect.height - arrow_pixbuf.get_height()) / 2
        draw_pixbuf(cr, arrow_pixbuf, arrow_x, arrow_y)
        draw_text(cr, self.title, rect.x + self.title_padding_x, rect.y, 
                  rect.width - self.title_padding_x, rect.height, text_size=10, 
                  text_color = text_color,
                  alignment=pango.ALIGN_LEFT)    
        
    def unhover(self, column, offset_x, offset_y):
        self.is_hover = False
        self.emit_redraw_request()
    
    def hover(self, column, offset_x, offset_y):
        self.is_hover = True
        self.emit_redraw_request()
        
    def button_press(self, column, offset_x, offset_y):
        pass
    
    def single_click(self, column, offset_x, offset_y):
        if self.is_expand:
            self.unexpand()
        else:
            self.expand()

    def double_click(self, column, offset_x, offset_y):
        # if self.is_expand:
        #     self.unexpand()
        # else:
        #     self.expand()
        pass
    
    def add_child_item(self):        
        self.add_items_callback(self.child_items, self.row_index + 1)
    
    def delete_child_item(self):
        self.delete_items_callback(self.child_items)
        
    def expand(self):
        self.is_expand = True
        self.add_child_item()
        self.emit_redraw_request()
    
    def unexpand(self):
        self.is_expand = False
        self.delete_child_item()
        self.emit_redraw_request()
        
    def try_to_expand(self):    
        if not self.is_expand:
            self.expand()
        
    def add_childs(self, child_items, pos=None, expand=False):    
        items = []
        for child_item in child_items:
            items.append(NormalItem(child_item, self.column_index + 1))
            
        for item in items:    
            item.parent_item = self
            
        if pos is not None:    
            for item in items:
                self.child_items.insert(pos, item)
                pos += 1
        else:            
            self.child_items.extend(items)
            
        if expand:    
            self.expand()
            
    def __repr__(self):        
        return "<ExpandItem %s>" % self.title
        
class NormalItem(TreeItem):
    '''
    class docs
    '''
	
    def __init__(self, title, column_index=0):
        '''
        init docs
        '''
        TreeItem.__init__(self)
        self.column_index = column_index
        self.side_padding = 5
        if column_index > 0:
            self.item_height = 30
        else:    
            self.item_height = 37
            
        self.title = title
        self.item_width = 36
        self.title_padding_x = 30
        self.column_offset = 15
        
    def get_height(self):
        return self.item_width
    
    def get_column_widths(self):
        return [-1]
    
    def get_column_renders(self):
        return [self.render_title]
    
    def unselect(self):
        self.is_select = False
        self.emit_redraw_request()
        
    def unhover(self, column, offset_x, offset_y):
        self.is_hover = False
        self.emit_redraw_request()
    
    def hover(self, column, offset_x, offset_y):
        self.is_hover = True
        self.emit_redraw_request()
        
    def select(self):        
        self.is_select = True
        self.emit_redraw_request()
        
    def emit_redraw_request(self):    
        if self.redraw_request_callback:
            self.redraw_request_callback(self)
            
    def render_title(self, cr, rect):
        if self.is_select:    
            draw_single_mask(cr, rect.x, rect.y, rect.width, rect.height, "globalItemHighlight")
        elif self.is_hover:
            draw_single_mask(cr, rect.x, rect.y, rect.width, rect.height, "globalItemHover")
        
        if self.is_select:
            text_color = "#FFFFFF"
        else:    
            text_color = app_theme.get_color("labelText").get_color()
            
            
        column_offset = self.column_offset * self.column_index    
        draw_text(cr, self.title, rect.x + self.title_padding_x + column_offset,
                  rect.y, rect.width - self.title_padding_x - column_offset ,
                  rect.height, text_size=10, 
                  text_color = text_color,
                  alignment=pango.ALIGN_LEFT)    
        
class IniGui(DialogBox):
    __gsignals__ = {
        "config-changed" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                            (gobject.TYPE_STRING, ))
        }
    def __init__(self):
        DialogBox.__init__(self, _("Preferences"), INI_WIDTH, INI_HEIGHT,
                           mask_type=DIALOG_MASK_MULTIPLE_PAGE,
                           window_pos=gtk.WIN_POS_CENTER)
        # Set event.
        self.ini = Config(config_path)        
        # Set event.
        self.connect("motion-notify-event", self.press_save_ini_file)
        self.connect("destroy", lambda w:self.save_configure_file_ok_clicked())
        
        self.main_vbox = gtk.VBox()
        self.main_hbox = gtk.HBox()
        self.configure = Configure()
        tree_view_width = 132 
        
        self.tree_view = TreeView(enable_drag_drop=False, enable_multiple_select=False)
        self.tree_view.set_expand_column(0)
        
        self.playback_item = NormalItem(_("Playback"))
        self.screenshot_item = NormalItem(_("Screenshot"))
        
        self.keyboard_expand_item = ExpandItem(_("Keyboard"), None)
        self.keyboard_expand_item.add_childs([_("Video Control"),
                                              _("Subtitle"),
                                              _("Other"),
                                              ])
        
        self.tree_view.add_items(
            [self.playback_item, 
             NormalItem(_("General")), 
             self.keyboard_expand_item,
             NormalItem(_("Subtitles")),
             self.screenshot_item,
             NormalItem(_("About us"))]
            )
        self.tree_view.draw_mask = self.draw_treeview_mask
        self.tree_view_align = gtk.Alignment()
        self.tree_view_align.set(0, 0, 1, 1,)
        self.tree_view_align.set_padding(0, 1, 0, 0)
        self.tree_view_align.add(self.tree_view)
        
        # TreeView event.
        self.tree_view.connect("button-press-item", self.set_con_widget)

        category_box = gtk.VBox()
        background_box = BackgroundBox()
        background_box.set_size_request(tree_view_width, 11)
        background_box.draw_mask = self.draw_treeview_mask
        category_box.pack_start(background_box, False, False)
        
        category_box.pack_start(self.tree_view_align, True, True)
        
        self.main_hbox.pack_start(category_box, False, False)
        self.main_hbox.pack_start(self.configure)
        
        # bottom button.
        self.cancel_button = Button(_("Close"))
        self.cancel_button.connect("clicked", self.destroy_ini_gui_window_cancel_clicked)
        
        self.body_box.pack_start(self.main_hbox, True, True)
        self.right_button_box.set_buttons([self.cancel_button])
        
        # Init configure index.
        self.set(_("Playback"))        
        self.show_all()
                
    def set(self, type_str):    
        self.configure.set(type_str)
        
        if type_str == _("Playback"):
            self.tree_view.select_items([self.playback_item])
        elif type_str == _("Screenshot"):
            self.tree_view.select_items([self.screenshot_item])
        
    def press_save_ini_file(self, widget, event):    
        gtk.timeout_add(500, self.save_configure_file_ok_clicked)
                
    def draw_scrolled_window_backgournd(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        self.draw_single_mask(cr, rect.x, rect.y-4, rect.width, rect.height+8) 
        return True
        
    def draw_treeview_mask(self, cr, x, y, width, height):
        draw_vlinear(
            cr, x, y, width, height,
            [(0, ("#FFFFFF", 0.9)),
             (1, ("#FFFFFF", 0.9))])
        
    def draw_single_mask(self, cr, x, y, width, height):
        cr.set_source_rgba(1, 1, 1, 0.7)
        cr.rectangle(x, y, width, height)
        cr.fill()        
        
    def draw_backgournd(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.get_allocation()
        cr.set_source_rgba(1, 1, 1, 0.85)
        width_padding = self.scrolled_window_frame.get_allocation()[2]
        cr.rectangle(rect.x + width_padding + 2, 
                     rect.y, 
                     rect.width - width_padding - 4, 
                     rect.height)
        cr.fill()
        
        propagate_expose(widget, event)
        return True
    
    def save_configure_file_ok_clicked(self):    
        # save ini configure file.
        file_play_dict = self.configure.file_play.get_file_play_state()
        for key in file_play_dict.keys():
            if self.ini.get("FilePlay", key) != str(file_play_dict[key]):
                self.ini.set("FilePlay", key, file_play_dict[key])

        system_set_dict = self.configure.system_set.get_system_set_state()
        for key in system_set_dict.keys():
            if self.ini.get("SystemSet", key) != str(system_set_dict[key]):
                self.ini.set("SystemSet", key, system_set_dict[key])

        play_control_dict = self.configure.play_control.get_play_control_state()
        for key in play_control_dict.keys():
            if self.ini.get("PlayControl", key) != str(play_control_dict[key]):
                self.ini.set("PlayControl", key, play_control_dict[key])
                
        subkey_set_dict = self.configure.sub_key.get_subkey_set_state()
        for key in subkey_set_dict.keys():
            if self.ini.get("SubKey", key) != str(subkey_set_dict[key]):
                self.ini.set("SubKey", key, (subkey_set_dict[key]))
        
        other_key_dict = self.configure.other_key.get_other_set_state()
        for key in other_key_dict.keys():
            if self.ini.get("OtherKey",  key) != str((other_key_dict[key])):
                self.ini.set("OtherKey", key, str(other_key_dict[key]))

        sub_set_dict = self.configure.sub_set.get_subtitle_set_state()
        for key in sub_set_dict.keys():
            if self.ini.get("SubtitleSet", key) != str(sub_set_dict[key]):
                self.ini.set("SubtitleSet", key, sub_set_dict[key])
                
        screenshot_dict = self.configure.screen_shot.get_screenshot_state()
        for key in screenshot_dict.keys():
            if self.ini.get("ScreenshotSet", key) != str(screenshot_dict[key]):
                self.ini.set("ScreenshotSet", key, screenshot_dict[key])
                
        return False
                    
    def destroy_ini_gui_window_cancel_clicked(self, widget):    
        # quit configure window.
        self.destroy()
        
    def set_con_widget(self, treeview, item, column, offset_x, offset_y):
        # Configure class Mode.
        self.configure.set(item.title)
        
class Configure(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self)
        self.class_dict = {
            _("Playback"):FilePlay(),
            _("General"):SystemSet(),
            _("Video Control"):PlayControl(),
            _("Subtitle"):SubKey(),
            _("Other"):OtherKey(),
            _("Subtitles"):SubSet(),
            _("Screenshot"):ScreenShot(),
            _("About us"):About()
            }
        
        # Init all configure gui class.
        self.file_play = self.class_dict[_("Playback")]
        self.system_set = self.class_dict[_("General")]
        self.play_control = self.class_dict[_("Video Control")]
        self.sub_key = self.class_dict[_("Subtitle")] 
        self.other_key = self.class_dict[_("Other")]
        self.sub_set = self.class_dict[_("Subtitles")]
        self.screen_shot = self.class_dict[_("Screenshot")]
        self.about = self.class_dict[_("About us")]
        self.show_all()
        
    def set(self, class_name):
        class_name = class_name.strip()
        index = None
        # if class_name in self.class_list:
        if self.class_dict.has_key(class_name):
            # remove other class modual.
            for widget in self.get_children():
                self.remove(widget)
                
            self.pack_start(self.class_dict[class_name])
                
            for widget in self.get_children(): 
                if widget:
                    self.show_all()
                    return True,index      
        return None       
    

class FilePlay(gtk.VBox):    
    def __init__(self):
        gtk.VBox.__init__(self)
        
        radio_table = gtk.Table(2, 2)
        # Init config file.
        self.ini = Config(config_path)
        self.label = Label(_("Playback"))
        self.label.set_size_request(label_width, label_height)
        
        # Video file open.
        self.video_file_open_label = Label(_("On opening video:"))
        
        self.adapt_video_button = RadioButton(_("Fit video to player"))

        self.ai_set_radio_button = RadioButton(_("Fit player to video")) #Fit video to player
        
        self.close_position_radio_button = RadioButton(_("Resize interface to last closed size"))

        self.full_window_radio_button = RadioButton(_("Enter full screen mode"))    
        
        set_num = self.ini.get("FilePlay", "video_file_open")
        
        # Set state(1, 2, 3, 4).
        if '2' == set_num:
            self.ai_set_radio_button.set_active(False)
            self.adapt_video_button.set_active(True) # 视频适应窗口.
        elif '3' == set_num:    
            self.close_position_radio_button.set_active(True) # 上次关闭尺寸.
        elif '4' == set_num:    
            self.full_window_radio_button.set_active(True) # 全屏.
        else:    # config get None type.
            self.ai_set_radio_button.set_active(True) # 窗口适应视频.
        ################################################################
        # open new file clear play list.
        self.clear_play_list_button = CheckButton(_("Clear playlist when opening new file"))        
        ini_bool = self.ini.get("FilePlay", "open_new_file_clear_play_list")

        self.clear_play_list_button.set_active(False)
        if ini_bool and "true" == ini_bool.lower():
            self.clear_play_list_button.set_active(True)
                        
        # memory up close media player -> file play postion.
        self.file_play_postion_button = CheckButton(_("Resume playback after restarting player"))
        ini_bool = self.ini.get("FilePlay", "memory_up_close_player_file_postion")
        self.file_play_postion_button.set_active(False)
        if ini_bool and "true" == ini_bool.lower():
            self.file_play_postion_button.set_active(True)
                    
        # play media when find file play in dir.
        self.find_file_play_button = CheckButton(_("Continue to next video automatically")) 
        ini_bool = self.ini.get("FilePlay", "find_play_file_relation_file")
        self.find_file_play_button.set_active(False)
        if ini_bool and "true" == ini_bool.lower():
            self.find_file_play_button.set_active(True)
                
        # mouse progressbar show preview window.
        self.show_preview_window_button = CheckButton(_("Show thumbnail when hovering over progress bar"))
        ini_bool = self.ini.get("FilePlay", "mouse_progressbar_show_preview")
        self.show_preview_window_button.set_active(False)
        if ini_bool and "true" == ini_bool.lower():
            self.show_preview_window_button.set_active(True)
            
        # check run a deepin-media-player.
        self.run_a_main_pid_radio_button = CheckButton(_("allow multiple instance deepin media player"))  
        ini_bool = self.ini.get("FilePlay", "check_run_a_deepin_media_player")
        self.run_a_main_pid_radio_button.set_active(False)
        if ini_bool and "true" == ini_bool.lower():
            self.run_a_main_pid_radio_button.set_active(True)
        # 最小化暂停
        self.pause_play_button = CheckButton(_("Pause When Minimized"))
        ini_bool = self.ini.get("FilePlay", "minimize_pause_play")
        self.pause_play_button.set_active(False)
        if ini_bool and "true" == ini_bool.lower():
            self.pause_play_button.set_active(True)            
        
        title_box = gtk.VBox(spacing=5)
        title_box.pack_start(self.label, False, False)
        title_box.pack_start(create_separator_box(), False, True)
        title_box.pack_start(self.video_file_open_label, False, False)
        title_box_align = gtk.Alignment()
        title_box_align.set_padding(10, 0, 10, 0)
        title_box_align.set(0, 0, 1, 1)
        title_box_align.add(title_box)
        
        radio_table.set_row_spacings(15)        
        radio_table.attach(self.adapt_video_button, 0, 1, 0, 1, yoptions=gtk.FILL)
        radio_table.attach(self.ai_set_radio_button, 1, 2, 0, 1, yoptions=gtk.FILL)
        radio_table.attach(self.close_position_radio_button, 0, 1, 1, 2, yoptions=gtk.FILL)
        radio_table.attach(self.full_window_radio_button, 1, 2, 1, 2, yoptions=gtk.FILL)
        
        check_box = gtk.VBox(spacing=15)
        check_box.pack_start(self.clear_play_list_button, False, False)
        check_box.pack_start(self.file_play_postion_button, False, False)
        check_box.pack_start(self.find_file_play_button, False, False)
        check_box.pack_start(self.show_preview_window_button, False, False)
        check_box.pack_start(self.run_a_main_pid_radio_button, False, False)
        check_box.pack_start(self.pause_play_button, False, False)
        self.set_spacing(15)
        self.pack_start(title_box_align, False, True)
        self.pack_start(radio_table, False, True)
        self.pack_start(check_box, False, False)
        
    def get_file_play_state(self):           
        video_file_dict = {}
        # video file open.
        video_file_open_num = 1
        if self.ai_set_radio_button.get_active():
            video_file_open_num = 1
        elif self.adapt_video_button.get_active():    
            video_file_open_num = 2
        elif self.close_position_radio_button.get_active():    
            video_file_open_num = 3
        elif self.full_window_radio_button.get_active():    
            video_file_open_num = 4            
            
        video_file_dict["video_file_open"] = video_file_open_num
        #
        video_file_dict["open_new_file_clear_play_list"] = self.clear_play_list_button.get_active()
        video_file_dict["memory_up_close_player_file_postion"] = self.file_play_postion_button.get_active()
        video_file_dict["find_play_file_relation_file"] = self.find_file_play_button.get_active()
        video_file_dict["mouse_progressbar_show_preview"] = self.show_preview_window_button.get_active()
        video_file_dict["check_run_a_deepin_media_player"] = self.run_a_main_pid_radio_button.get_active()
        video_file_dict["minimize_pause_play"] = self.pause_play_button.get_active()

        return video_file_dict
    
class SystemSet(gtk.VBox):        
    def __init__(self):
        gtk.VBox.__init__(self)
        # Init config file.
        self.ini = Config(config_path)

        self.fixed = gtk.Fixed()
        self.label = Label(_("General")) # 提示信息.
        self.label.set_size_request(label_width, label_height)
        self.heparator_hbox = gtk.HBox()
        self.heparator = create_separator_box()
        self.heparator_ali = gtk.Alignment(1, 1, 1, 1)
        self.heparator_ali.add(self.heparator)
        self.heparator_ali.set_padding(0, 0, 20, 0)
        self.heparator_hbox.pack_start(self.heparator_ali, True, True)
        self.heparator_hbox.set_size_request(heparator_width, heparator_height)
        # System setting.
        # 界面布局.
        # 标题栏.
        title_box_align = gtk.Alignment()
        title_box = gtk.VBox(spacing=5)
        title_box.pack_start(self.label, False, False)
        title_box.pack_start(create_separator_box(), True, True)
        title_box_align.set_padding(10, 0, 10, 0)
        title_box_align.set(0, 0, 1, 1)
        title_box_align.add(title_box)
        # 启动系统气泡提示.
        self.start_sys_bubble_msg = CheckButton(_("启用系统气泡提示")) 
        self.start_sys_bubble_msg.set_active(False)
        bubble_check = self.ini.get("SystemSet", "start_sys_bubble_msg")
        if bubble_check and "true" == bubble_check.lower():
            self.start_sys_bubble_msg.set_active(True)
        # 启动播放窗口提示.
        self.start_play_win_msg = CheckButton(_("启用播放窗口提示")) 
        self.start_play_win_msg.set_active(False)
        play_win_check = self.ini.get("SystemSet", "start_play_win_msg")
        if play_win_check and "true" == play_win_check.lower():
            self.start_play_win_msg.set_active(True)
        # 启动播放窗口提示.
        # Font set.        
        self.font_set_button_label = Label(_("Font"))
        # DEFAULT_FONT 默认字体.
        font_set_items = []
        fontmap = pangocairo.cairo_font_map_get_default()
        font_i = 1
        for font_map in fontmap.list_families():
            font_set_items.append([font_map.get_name(), font_i])
            font_i += 1
        combo_width = 200
        self.font_set_combo = ComboBox(font_set_items, combo_width)   
        font_string = self.ini.get("SystemSet", "font")
        # 获取配置文件中的 font类型.
        if font_string:
            self.font_set_combo.label.set_text(font_string)            
        else: # font_string return type None.    
            self.font_set_combo.label.set_text(DEFAULT_FONT) 
         
        # Font size. 字体大小.
        self.font_size_button_label = Label(_("Size"))
        font_set_items = []
        font_set_items_num = 1
        for i in range(8, 32):
            font_set_items.append((str(i), font_set_items_num))
            font_set_items_num += 1
            
        self.font_size_button_combo = ComboBox(font_set_items, 160)
        font_size_string = self.ini.get("SystemSet", "font_size")
        # 获取配置文件中的字体大小.
        if font_size_string:
            self.font_size_button_combo.label.set_text(font_size_string)            
        else:    
            self.font_size_button_combo.label.set_text("8")
        #
        self.font_hbox_align = gtk.Alignment(0, 0, 1, 1)
        self.font_hbox_align.set_padding(5, 0, 32, 0)
        self.font_hbox = gtk.HBox()
        self.font_hbox_align.add(self.font_hbox)
        self.font_type_vbox = gtk.VBox()
        self.font_size_vbox = gtk.VBox()
        #
        self.font_type_vbox.pack_start(self.font_set_button_label, False, False) 
        self.font_type_vbox.pack_start(self.font_set_combo, False, False, padding=5) 
        #
        self.font_size_vbox.pack_start(self.font_size_button_label, False, False)
        self.font_size_vbox.pack_start(self.font_size_button_combo, False, False, padding=5)
        #
        self.font_hbox.pack_start(self.font_type_vbox, False, False)
        self.font_hbox.pack_start(self.font_size_vbox, False, False, padding=20)
        #
        check_box_align = gtk.Alignment(0, 0, 1, 1)
        check_box_align.set_padding(5, 0, 5, 0)
        check_box = gtk.VBox(spacing=10)
        check_box_align.add(check_box)
        # check_box.
        check_box.pack_start(self.start_sys_bubble_msg, False, False)
        check_box.pack_start(self.start_play_win_msg, False, False)
        self.pack_start(title_box_align, False, False)
        self.pack_start(check_box_align, False, False)
        self.pack_start(self.font_hbox_align, False, False)
        
    def get_system_set_state(self):           
        system_set_dict = {}
        # 保存 获取启用系统气泡提示 bool.
        system_set_dict["start_sys_bubble_msg"] = self.start_sys_bubble_msg.get_active() 
        # 保存 获取启用播放窗口提示 bool.
        system_set_dict["start_play_win_msg"] = self.start_play_win_msg.get_active()
        # 控件布局.
        play_win_check = self.start_play_win_msg.get_active()
        # 设置 启动播放窗口提示 的设置.
        self.font_set_button_label.set_sensitive(play_win_check)
        self.font_set_combo.set_sensitive(play_win_check)
        self.font_size_button_label.set_sensitive(play_win_check)
        self.font_size_button_combo.set_sensitive(play_win_check)
        # 保存 字体类型. 
        system_set_dict["font"] = self.font_set_combo.label.get_text()
        # 保存 字体大小.
        system_set_dict["font_size"] = self.font_size_button_combo.label.get_text()
        #
        return system_set_dict
        
class PlayControl(gtk.VBox):       
    def __init__(self):
        gtk.VBox.__init__(self)
        self.ini = Config(config_path)
        self.fixed = gtk.Fixed()
        self.label = Label(_("Video Control"))
        self.label.set_size_request(label_width, label_height)
        # heparator.
        self.heparator = create_separator_box()
        self.heparator_ali = gtk.Alignment(1, 1, 1, 1)
        self.heparator_ali.add(self.heparator)
        self.heparator.set_padding(0, 0, 20, 0)
        self.heparator_hbox = gtk.HBox()
        self.heparator_hbox.pack_start(self.heparator_ali, True, True)
        self.heparator_hbox.set_size_request(heparator_width, heparator_height)
        # setting keys.
        entry_width = 150
        entry_height = 24
        # set PlayControl bool.
        self.play_control_bool_checkbtn = CheckButton(_("Enable hotkeys"))
        self.play_control_bool_checkbtn.connect("button-press-event", self.set_play_control_all_sensitive)                
        # open file key.
        self.open_file_entry_label = Label(_("Open file"))
        self.open_file_entry = ShortcutKeyEntry()
        text_string = self.ini.get("PlayControl", "open_file_key")
        if text_string:
            self.open_file_entry.set_shortcut_key(text_string)
        else:  # text_string return None type.
            self.open_file_entry.set_shortcut_key("Ctrl+o")
            
        self.open_file_entry.set_size(entry_width, entry_height)
        # pre a.
        self.pre_a_entry_label = Label(_("Previous"))
        self.pre_a_entry = ShortcutKeyEntry()
        text_string = self.ini.get("PlayControl", "pre_a_key")
        if text_string:
            self.pre_a_entry.set_shortcut_key(text_string)
        else:    
            self.pre_a_entry.set_shortcut_key("Page_Up")
            
        self.pre_a_entry.set_size(entry_width, entry_height)
        # open file dir.
        self.open_file_dir_entry_label = Label(_("Open directory"))
        self.open_file_dir_entry = ShortcutKeyEntry()
        text_string = self.ini.get("PlayControl", "open_file_dir_key")
        if text_string:
            self.open_file_dir_entry.set_shortcut_key(text_string)
        else:    
            self.open_file_dir_entry.set_shortcut_key("Ctrl+f")
            
        self.open_file_dir_entry.set_size(entry_width, entry_height)
        # next a.
        self.next_a_entry_label = Label(_("Next"))
        self.next_a_entry = ShortcutKeyEntry()
        text_string = self.ini.get("PlayControl", "next_a_key")
        if text_string:
            self.next_a_entry.set_shortcut_key(text_string)
        else: # Page_Down    
            self.next_a_entry.set_shortcut_key("Page_Down")
            
        self.next_a_entry.set_size(entry_width, entry_height)
        # play or pause.
        self.play_or_pause_entry_label = Label(_("Pause/Play"))
        self.play_or_pause_entry = ShortcutKeyEntry()
        text_string = self.ini.get("PlayControl", "play_or_pause_key")
        if text_string:
            self.play_or_pause_entry.set_shortcut_key(text_string)        
        else:#"Space"
            self.play_or_pause_entry.set_shortcut_key("Space")
            
        self.play_or_pause_entry.set_size(entry_width, entry_height)
        # add volume.
        self.add_volume_entry_label = Label(_("Increase Volume"))
        self.add_volume_entry = ShortcutKeyEntry()
        text_string = self.ini.get("PlayControl", "add_volume_key")
        if text_string:
            self.add_volume_entry.set_shortcut_key(text_string)        
        else:   # Up 
            self.add_volume_entry.set_shortcut_key("Up")
            
        self.add_volume_entry.set_size(entry_width, entry_height)
        # seek.
        self.seek_entry_label = Label(_("Forward"))
        self.seek_entry = ShortcutKeyEntry()
        text_string = self.ini.get("PlayControl", "seek_key")
        if text_string:
            self.seek_entry.set_shortcut_key(text_string)        
        else: # Right    
            self.seek_entry.set_shortcut_key("Right")
            
        self.seek_entry.set_size(entry_width, entry_height)
        # sub volume.
        self.sub_volume_entry_label = Label(_("Decrease Volume"))
        self.sub_volume_entry = ShortcutKeyEntry()
        text_string = self.ini.get("PlayControl", "sub_volume_key")
        if text_string:
            self.sub_volume_entry.set_shortcut_key(text_string)        
        else: # Down
            self.sub_volume_entry.set_shortcut_key("Down")
            
        self.sub_volume_entry.set_size(entry_width, entry_height)
        # back.
        self.back_entry_label = Label(_("Rewind"))
        self.back_entry = ShortcutKeyEntry()
        text_string = self.ini.get("PlayControl", "back_key")
        if text_string:
            self.back_entry.set_shortcut_key(text_string)        
        else:    # Left
            self.back_entry.set_shortcut_key("Left")
            
        self.back_entry.set_size(entry_width, entry_height)
        # Mute. 
        self.mute_entry_label = Label(_("Mute"))
        self.mute_entry = ShortcutKeyEntry()
        text_string = self.ini.get("PlayControl", "mute_key")
        if text_string:
            self.mute_entry.set_shortcut_key(text_string)        
        else:   # M 
            self.mute_entry.set_shortcut_key("m")        

        self.mute_entry.set_size(entry_width, entry_height)
        # full.
        self.full_entry_label = Label(_("Full Screen"))
        self.full_entry = ShortcutKeyEntry()
        text_string = self.ini.get("PlayControl", "full_key")
        if text_string:
            self.full_entry.set_shortcut_key(text_string)        
        else:    # Return
            self.full_entry.set_shortcut_key("Return")        
            
        self.full_entry.set_size(entry_width, entry_height)
        # Concise mode.
        self.concise_entry_label = Label(_("Compact mode"))
        self.concise_entry = ShortcutKeyEntry()
        text_string = self.ini.get("PlayControl", "concise_key")
        if text_string:
            self.concise_entry.set_shortcut_key(text_string)        
        else:    #Shift_L/R + Return
            self.concise_entry.set_shortcut_key("Shift+Return")        
            
        self.concise_entry.set_size(entry_width, entry_height)
                        
        
        # set PlayControl bool.
        self.play_control_bool_checkbtn.set_active(True)
        self.set_play_control_true()
        
        play_control_bool = self.ini.get("PlayControl", "play_control_bool")

        if play_control_bool and not (play_control_bool == "True"):
            self.play_control_bool_checkbtn.set_active(False)
            self.set_play_control_false()                

        play_control_x = 20
        play_control_y = 40
        # label.
        self.fixed.put(self.label, play_control_x, TITLE_HEIGHT_PADDING)
        # heparator.
        self.fixed.put(self.heparator_hbox, 0, heparator_y)
        # open file key.
        # play_control_bool_checkbtn.
        
        self.fixed.put(self.play_control_bool_checkbtn, play_control_x, play_control_y)
        
        play_control_x += 10
        play_control_y += self.play_control_bool_checkbtn.get_size_request()[1] + 10
        self.fixed.put(self.open_file_entry_label,
                       play_control_x, play_control_y)        
        
        play_control_y += self.open_file_entry_label.get_size_request()[1] + 2
        self.fixed.put(self.open_file_entry,
                       play_control_x, play_control_y)
        # pre a.
        play_control_x_padding = play_control_x + self.open_file_entry.get_size_request()[0] + self.open_file_entry_label.get_size_request()[0]
        self.fixed.put(self.pre_a_entry,
                       play_control_x_padding, play_control_y)       
        self.fixed.put(self.pre_a_entry_label, play_control_x_padding, play_control_y - self.open_file_entry_label.get_size_request()[1] - 2)
        # open file dir and next a.
        play_control_y += self.pre_a_entry.get_size_request()[1] + 10
        self.fixed.put(self.open_file_dir_entry_label,
                       play_control_x, play_control_y)
        self.fixed.put(self.next_a_entry_label,
                       play_control_x_padding, play_control_y)
        play_control_y += self.next_a_entry.get_size_request()[1] - 8
        self.fixed.put(self.open_file_dir_entry,
                       play_control_x, play_control_y)        
        self.fixed.put(self.next_a_entry,
                       play_control_x_padding, play_control_y)
        play_control_y += self.next_a_entry.get_size_request()[1] + 10
        # play or pause and add volume.
        self.fixed.put(self.play_or_pause_entry_label, 
                       play_control_x, play_control_y)
        self.fixed.put(self.add_volume_entry_label, 
                       play_control_x_padding, play_control_y)
        play_control_y += self.play_or_pause_entry_label.get_size_request()[1] + 2
        self.fixed.put(self.play_or_pause_entry, 
                       play_control_x, play_control_y)
        self.fixed.put(self.add_volume_entry, 
                       play_control_x_padding, play_control_y)
        play_control_y += self.play_or_pause_entry.get_size_request()[1] + 10
        # seek and sub volume.
        self.fixed.put(self.seek_entry_label,
                       play_control_x, play_control_y)
        self.fixed.put(self.sub_volume_entry_label,
                       play_control_x_padding, play_control_y)
        play_control_y += self.sub_volume_entry_label.get_size_request()[1] + 2
        self.fixed.put(self.seek_entry,
                       play_control_x, play_control_y)
        self.fixed.put(self.sub_volume_entry,
                       play_control_x_padding, play_control_y)
        play_control_y += self.sub_volume_entry.get_size_request()[1] + 10
        # back and mute.
        self.fixed.put(self.back_entry_label, 
                       play_control_x, play_control_y)        
        self.fixed.put(self.mute_entry_label,                       
                       play_control_x_padding, play_control_y)
        play_control_y += self.mute_entry_label.get_size_request()[1] + 2
        self.fixed.put(self.back_entry, 
                       play_control_x, play_control_y)                
        self.fixed.put(self.mute_entry,  
                       play_control_x_padding, play_control_y)
        play_control_y += self.mute_entry_label.get_size_request()[1] + 15
        # full and concise mode.
        self.fixed.put(self.full_entry_label,
                       play_control_x, play_control_y)        
        self.fixed.put(self.concise_entry_label,
                       play_control_x_padding, play_control_y)
        play_control_y += self.concise_entry_label.get_size_request()[1] + 5
        self.fixed.put(self.full_entry,
                       play_control_x, play_control_y)        
        self.fixed.put(self.concise_entry,
                       play_control_x_padding, play_control_y)
        play_control_y += self.concise_entry.get_size_request()[1] + 10
        
        
        self.pack_start(self.fixed)
        
    def set_play_control_all_sensitive(self, widget, event):    
        if is_left_button(event):
            checkbtn_bool = self.play_control_bool_checkbtn.get_active()
            if checkbtn_bool:
                self.set_play_control_false()
            else:
                self.set_play_control_true()
                
                
    def set_play_control_true(self):        
        self.set_play_control_function(True)
        
    def set_play_control_false(self):
        self.set_play_control_function(False)
        
    def set_play_control_function(self, type_bool):
        self.open_file_entry.set_sensitive(type_bool)
        self.open_file_dir_entry.set_sensitive(type_bool)
        self.play_or_pause_entry.set_sensitive(type_bool)
        self.seek_entry.set_sensitive(type_bool)
        self.back_entry.set_sensitive(type_bool)
        self.full_entry.set_sensitive(type_bool)
        self.pre_a_entry.set_sensitive(type_bool)
        self.next_a_entry.set_sensitive(type_bool)
        self.add_volume_entry.set_sensitive(type_bool)
        self.sub_volume_entry.set_sensitive(type_bool)
        self.mute_entry.set_sensitive(type_bool)
        self.concise_entry.set_sensitive(type_bool)

        
    def get_play_control_state(self):    
        play_control_dict = {}
        play_control_dict["play_control_bool"] = self.play_control_bool_checkbtn.get_active()
        # Left.
        play_control_dict["open_file_key"] = self.open_file_entry.get_text()
        play_control_dict["open_file_dir_key"] = self.open_file_dir_entry.get_text()
        play_control_dict["play_or_pause_key"] = self.play_or_pause_entry.get_text()
        play_control_dict["seek_key"] = self.seek_entry.get_text()
        play_control_dict["back_key"] = self.back_entry.get_text()
        play_control_dict["full_key"] = self.full_entry.get_text()
        # Right.
        play_control_dict["pre_a_key"] = self.pre_a_entry.get_text()
        play_control_dict["next_a_key"] = self.next_a_entry.get_text()
        play_control_dict["add_volume_key"] = self.add_volume_entry.get_text()
        play_control_dict["sub_volume_key"] = self.sub_volume_entry.get_text()
        play_control_dict["mute_key"] = self.mute_entry.get_text()
        play_control_dict["concise_key"] = self.concise_entry.get_text()
        
        return play_control_dict
    
class SubKey(gtk.VBox):    
    def __init__(self):
        gtk.VBox.__init__(self)
        self.ini = Config(config_path)
        # init fixed.
        self.fixed = gtk.Fixed()
        # heparator.
        self.heparator_hbox = gtk.HBox()
        self.heparator = create_separator_box()
        self.heparator_ali = gtk.Alignment(1, 1, 1, 1)
        self.heparator_ali.add(self.heparator)
        self.heparator.set_padding(0, 0, 20, 0)
        self.heparator_hbox.set_size_request(heparator_width, heparator_height)        
        # add title.        
        title_offset_x = 20
        title_offset_y = 10
        self.title_label = Label(_("Subtitle"))
        # add check_btn.
        check_btn_offset_x = 20
        check_btn_offset_y = 40
        self.check_btn = CheckButton(_("Enable Keyboard Shortcuts"))        
        # add widgets.
        heparator_offset_x = 0
        heparator_offset_y = title_offset_y + 25        
        # create widgets left, right label.
        widgets_label_left = [
            Label(_("Delay-0.5s")),
            Label(_("Delay+0.5s")),
            Label(_("Loading subtiles")),
            ]
        widgets_label_right = [
            Label(_("Increase subtitle scale")),
            Label(_("Decrease subtitle scale")),
            ]        
        # create widgets left.
        self.widgets_left = [
            ShortcutKeyEntry(),
            ShortcutKeyEntry(),
            ShortcutKeyEntry(),
            ]
        # create widgets right.
        self.widgets_right = [
            ShortcutKeyEntry(),
            ShortcutKeyEntry(),
            ]                
        # set active is flase.
        # self.set_subkey_flase()
        # init read ini value and init config value. 
        self.init_read_subkey_value()
        # set widgets left, right size.
        entry_width = 150
        entry_height = 24
        for widget_left, widget_right in all_widget_to_widgets(self.widgets_left, self.widgets_right):
            if widget_left:
                widget_left.set_size(entry_width, entry_height)
            if widget_right:
                widget_right.set_size(entry_width, entry_height)
        # add widgets.
        start_x, start_y = 30, heparator_offset_y + 30
        offset_x, offset_y = entry_width + 50, 50
        self.fixed.put(self.title_label, title_offset_x, title_offset_y)
        self.heparator_hbox.pack_start(self.heparator_ali)
        self.fixed.put(self.heparator_hbox, heparator_offset_x, heparator_offset_y)
        self.fixed.put(self.check_btn, check_btn_offset_x, check_btn_offset_y)
        widgets_add_widget(
            self.fixed, 
            widgets_label_left, widgets_label_right,
            start_x, start_y, 
            offset_x, offset_y)
        widgets_add_widget(
            self.fixed, 
            self.widgets_left, self.widgets_right, 
            start_x, start_y + 20, 
            offset_x, offset_y)
        self.pack_start(self.fixed)
        # init widget connect events.
        self.check_btn.connect("button-press-event", self.check_btn_key_bool_press)        
                
    def init_read_subkey_value(self):    
        try:
            self.key_titles_left = ["subkey_add_delay_key", 
                                    "subkey_sub_delay_key",
                                    "subkey_load_key"
                                    ]
            self.key_titles_right = ["subkey_add_scale_key",
                                     "subkey_sub_scale_key",
                                     ]
            # 
            subkey_bool = self.ini.get("SubKey", "subkey_bool")
            if subkey_bool and "False" == subkey_bool:
                self.check_btn.set_active(False)
                self.set_subkey_flase()
            else:    
                self.check_btn.set_active(True)
                self.set_subkey_true()
            # get config left value.
            self.keys_left = ["[", "]", "Alt + o"]
            for_widgets_left = map(lambda title, widget, key:(title, widget, key), self.key_titles_left, self.widgets_left, self.keys_left)
            for title, widget, init_key in for_widgets_left:
                key_value = self.ini.get("SubKey", title)
                widget.set_text(key_value)
                if key_value:
                    widget.set_shortcut_key(key_value)
                else:    
                    widget.set_shortcut_key(init_key)
            # get config right value. 
            self.keys_right = ["Alt + Left", "Alt + Right"]        
            for_widgets_right = map(lambda title, widget, key:(title, widget, key), self.key_titles_right, self.widgets_right, self.keys_right)
            
            for title, widget, init_key in for_widgets_right:
                key_value = self.ini.get("SubKey", title)
                if key_value:
                    widget.set_shortcut_key(key_value)
                else:    
                    widget.set_shortcut_key(init_key)
                    
        except Exception, e:        
            print "init_read_subkey_value:", e
            
    def check_btn_key_bool_press(self, widget, event):    
        if is_left_button(event):
            if widget.get_active():
                self.set_subkey_flase()
            else:    
                self.set_subkey_true()
        
    def set_subkey_flase(self):            
        self.set_subkey_bool_function(False)
        
    def set_subkey_true(self):    
        self.set_subkey_bool_function(True)
        
    def set_subkey_bool_function(self, key_bool):
        for widget_left in self.widgets_left:
            widget_left.set_sensitive(key_bool)
        for widget_right in self.widgets_right:
            widget_right.set_sensitive(key_bool)
            
    def get_subkey_set_state(self):
        subkey_set_dict = {}
        subkey_set_dict["subkey_bool"] = self.check_btn.get_active()
        #
        for key_title, widget in map(lambda key_title, widget:(key_title, widget), 
                                     self.key_titles_left, self.widgets_left):
            subkey_set_dict[str(key_title)] = widget.get_text()
        #     
        for key_title, widget in map(lambda key_title, widget:(key_title, widget), 
                                     self.key_titles_right, self.widgets_right):    
            subkey_set_dict[str(key_title)] = widget.get_text()            
        return subkey_set_dict
        
class OtherKey(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self)
        self.ini = Config(config_path)

        self.fixed = gtk.Fixed()
        self.label = Label(_("Other"))
        self.label.set_size_request(label_width, label_height)
        self.heparator_hbox = gtk.HBox()
        self.heparator = create_separator_box()
        self.heparator_ali = gtk.Alignment(1, 1, 1, 1)
        self.heparator_ali.add(self.heparator)
        self.heparator_ali.set_padding(0, 0, 20, 0)
        self.heparator_hbox.pack_start(self.heparator_ali)
        self.heparator_hbox.set_size_request(heparator_width, heparator_height)        
        # set other_key bool.        
        self.other_key_bool_checkbtn = CheckButton(_(" Enabled hotkeys"))
        self.other_key_bool_checkbtn.connect("button-press-event", self.set_other_key_bool_checkbtn_press)
                
        entry_width = 120
        entry_height = 24
        # init widgets label left and right.        
        widgets_label_left = [Label(_("Increse brightness")),
                              Label(_("Decrease brightness")),
                              Label(_("Rotate conterclockwise")),
                              Label(_("Rotate clockwise")),
                              Label(_("Take screenshot")),
                              Label(_("Switch audio tracks")),
                              ]
        widgets_label_right = [Label(_("Left click")),
                               Label(_("Double click")),
                               Label(_("Scroll"))
                               ]
        # init widgets Left and right.
        self.widgets_left = [ShortcutKeyEntry(),
                             ShortcutKeyEntry(),
                             ShortcutKeyEntry(),
                             ShortcutKeyEntry(),
                             ShortcutKeyEntry(),
                             ShortcutKeyEntry(),
                             ]
        self.widgets_right = [ComboBox([(_("Pause/Play"), 1), (_("Disabled"), 2)]),
                              ComboBox([(_("Full Screen"), 1), (_("Disabled"), 2)]),
                              ComboBox([(_("Volume"), 1),(_("Disabled"), 2)])
                              ]                
        # init other start set false.
        self.set_other_key_false()
        # init start read config.
        self.init_read_other_key_value()        
        # set widgets left size.
        for widget_left in self.widgets_left:
            if widget_left:
                widget_left.set_size(entry_width, entry_height)
        # set widgets position and add widgets.
        title_offset_x, title_offset_y = 20, 10
        heparator_offset_x, heparator_offset_y = 0, title_offset_y + 25
        other_Key_offset_x = 20
        other_Key_offset_y = 40
        start_x, start_y = 30, heparator_offset_y + 30
        offset_x, offset_y = entry_width + 50, 50        
        self.fixed.put(self.label, title_offset_x, title_offset_y - 8)
        self.fixed.put(self.heparator_hbox, heparator_offset_x, heparator_offset_y)
        self.fixed.put(self.other_key_bool_checkbtn, other_Key_offset_x, other_Key_offset_y)
        widgets_add_widget(
            self.fixed, 
            widgets_label_left, widgets_label_right, 
            start_x, start_y, offset_x, offset_y)        
        widgets_add_widget(
            self.fixed, 
            self.widgets_left, self.widgets_right,
            start_x, start_y + 20, offset_x, offset_y)
        self.pack_start(self.fixed)
    
    def init_read_other_key_value(self):            
        try:
            self.key_titles_left = ["add_brightness_key",
                                "sub_brightness_key",
                                "inverse_rotation_key",
                                "clockwise_key",
                                "sort_image_key",
                                "switch_audio_track_key"
                                ]
            self.key_titles_right = ["mouse_left_single_clicked",
                                 "mouse_left_double_clicked",
                                 "mouse_wheel_event"
                                 ]
            #
            other_other_bool = self.ini.get("OtherKey", "other_key_bool")
            if other_other_bool and "False" == other_other_bool:
                self.other_key_bool_checkbtn.set_active(False)
                self.set_other_key_false()                
            else:    
                self.other_key_bool_checkbtn.set_active(True)
                self.set_other_key_true()                

            # get config left value.
            self.keys_left = ["=", "-", "w", "e", "Alt + a", _("Disabled")]
            for_widgets_left = map(lambda title, widget, key:(title, widget, key), self.key_titles_left, self.widgets_left, self.keys_left)
            
            for title, widget, init_key in for_widgets_left:
                key_value = self.ini.get("OtherKey", title)
                widget.set_text(key_value)                
                if key_value:
                    widget.set_shortcut_key(_(str(key_value)))
                else:                        
                    widget.set_shortcut_key(init_key)
            # get config right value.
            self.keys_right = [_("Pause/Play"), _("Full Screen"), _("Volume")]
            
            for_widgets_right = map(lambda title, widget, key:(title, widget, key), self.key_titles_right, self.widgets_right, self.keys_right)
            
            for title, widget, init_key in for_widgets_right:
                key_value = self.ini.get("OtherKey", title)
                if key_value == "Disabled":                            
                    widget.label.set_text(_(str(key_value)))
                else:    
                    widget.label.set_text(init_key)
                    
        except Exception,e:
            print "other class:init_read_other_key_value:", e
            
    def set_other_key_bool_checkbtn_press(self, widget, event):
        if is_left_button(event):
            if self.other_key_bool_checkbtn.get_active():
                self.set_other_key_false()
            else:
                self.set_other_key_true()
                            
    def set_other_key_false(self):    
        self.set_other_key_bool_function(False)
    
    def set_other_key_true(self):
        self.set_other_key_bool_function(True)
    
    def set_other_key_bool_function(self, type_bool):
        for widget_left in self.widgets_left:
            widget_left.set_sensitive(type_bool)
        for widget_right in self.widgets_right:
            widget_right.set_sensitive(type_bool)
        
    def get_other_set_state(self):
        other_set_dict = {}
        other_set_dict["other_key_bool"] = self.other_key_bool_checkbtn.get_active()
        #
        for key_title, widget in map(lambda key_title, widget:(key_title, widget),
                                     self.key_titles_left, self.widgets_left):
            text = widget.get_text()
            if text == "禁用":
                text = "Disabled"
            other_set_dict[str(key_title)] = text
            
        for key_title, widget in map(lambda key_title, widget:(key_title, widget),
                                     self.key_titles_right, self.widgets_right):
            if key_title in ["mouse_left_single_clicked"]:
                if widget.get_select_index():
                    text = "Disabled"
                else:    
                    text = "Pause/Play"
            elif key_title in ["mouse_left_double_clicked"]:
                if widget.get_select_index():
                    text = "Disabled"
                else:    
                    text = "Full Screen"
            elif key_title in ["mouse_wheel_event"]:
                if widget.get_select_index():
                    text = "Disabled"
                else:    
                    text = "Volume"
                    
            other_set_dict[str(key_title)] = text
        return other_set_dict
    
class SubSet(gtk.VBox):    
    def __init__(self):
        gtk.VBox.__init__(self)
        entry_width = 280
        entry_height = 24
        self.ini = Config(config_path)
        # self.ini = config
        self.fixed = gtk.Fixed()
        self.label = Label(_("Subtitles"))
        self.label.set_size_request(label_width, label_height)
        self.heparator_hbox = gtk.HBox()
        self.heparator = create_separator_box()
        self.heparator_ali = gtk.Alignment(1, 1, 1, 1)
        self.heparator_ali.add(self.heparator)
        self.heparator_ali.set_padding(0, 0, 20, 0)
        self.heparator_hbox.pack_start(self.heparator_ali)
        self.heparator_hbox.set_size_request(heparator_width, heparator_height)
        # Ai load subtitle.
        self.ai_load_subtitle_checkbtn = CheckButton(_("Load subtitles automatically"))
        ini_bool = self.ini.get("SubtitleSet", "ai_load_subtitle")
        self.ai_load_subtitle_checkbtn.set_active(False)
        if ini_bool and "true" == ini_bool.lower():            
            self.ai_load_subtitle_checkbtn.set_active(True)                
                
        self.ai_load_subtitle_checkbtn_label = Label("")
        # Specified Location Search.
        self.specific_location_search_label = Label(_("Subtitle Directory:"))
        self.specific_location_search_entry = InputEntry()
        text_string = self.ini.get("SubtitleSet", "specific_location_search")
        if text_string:
            self.specific_location_search_entry.set_text(text_string)
        else:    
            self.specific_location_search_entry.set_text("~/.config/deepin-media-player/subtitle")
            
        self.specific_location_search_entry.set_size(entry_width, entry_height)
        self.specific_location_search_button = Button(_("Browse"))
        self.specific_location_search_button.connect("clicked", self.load_path_to_sls_entry)
        sub_set_x = 20
        sub_set_y = 40
        self.fixed.put(self.label, sub_set_x, TITLE_HEIGHT_PADDING)
        self.fixed.put(self.heparator_hbox, heparator_x, heparator_y)
        sub_set_x += 10
        # Ai load subtitle.
        self.fixed.put(self.ai_load_subtitle_checkbtn,
                       sub_set_x, sub_set_y)
        self.fixed.put(self.ai_load_subtitle_checkbtn_label,
                       sub_set_x + self.ai_load_subtitle_checkbtn.get_size_request()[0], sub_set_y)
        sub_set_y += self.ai_load_subtitle_checkbtn.get_size_request()[1] + 25
        # Specified Location Search.
        sub_set_x += 5
        self.fixed.put(self.specific_location_search_label,
                       sub_set_x, sub_set_y)
        sub_set_y += self.specific_location_search_label.get_size_request()[1] + 10
        self.fixed.put(self.specific_location_search_entry,
                       sub_set_x, sub_set_y + 1)
        self.fixed.put(self.specific_location_search_button,
                       sub_set_x + self.specific_location_search_entry.get_size_request()[0] + 10, sub_set_y)
        
        self.pack_start(self.fixed)
        
    def load_path_to_sls_entry(self, widget):    
        open_dialog = gtk.FileChooserDialog(_("Open Directory"),
                                            None,
                                            gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                            (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, 
                                             gtk.STOCK_OPEN, gtk.RESPONSE_OK))        
        open_dialog.set_current_folder(get_home_path())
        res = open_dialog.run()
        
        if res == gtk.RESPONSE_OK:
            path_string = open_dialog.get_filename()
            self.specific_location_search_entry.set_text(path_string)
        open_dialog.destroy()

    def get_subtitle_set_state(self):    
        sub_set_dict = {}
        sub_set_dict["ai_load_subtitle"] = self.ai_load_subtitle_checkbtn.get_active()
        sub_set_dict["specific_location_search"] = self.specific_location_search_entry.get_text()
        return sub_set_dict
        
class ScreenShot(gtk.VBox):        
    def __init__(self):
        gtk.VBox.__init__(self)
        entry_width = 250
        entry_height = 24
        self.ini = Config(config_path)

        self.fixed = gtk.Fixed()
        self.label = Label(_("Screenshot"))
        self.label.set_size_request(label_width, label_height)
        self.heparator_hbox = gtk.HBox()
        self.heparator = create_separator_box()
        self.heparator_hbox.pack_start(self.heparator)
        self.heparator_hbox.set_size_request(heparator_width, heparator_height)                
        # Save clipboard.
        self.save_clipboard_radio = RadioButton(_("Copy to clipboard"))
        # save clipboard radio event.
        self.save_clipboard_radio.connect("button-press-event", self.save_clipboard_radio_clicked)
        
        self.save_clipboard_radio_label = Label("")
        # Save File.
        self.save_file_radio = RadioButton(_("Folder"))
        self.save_file_radio.connect("button-press-event", self.save_file_radio_clicked)
        self.save_file_radio.set_active(True)
        self.save_file_radio_label = Label("")
        
        # Save path.
        self.save_path_label = Label(_("Screenshot directory:"))
        self.save_path_entry = InputEntry()
            
        self.save_path_entry.set_size(entry_width, entry_height)                
        self.save_path_button = Button(_("Browse"))
        self.save_path_button.connect("clicked", self.save_path_to_save_path_entry_clicked)
        # Save type.
        self.save_type_label = Label(_("File Type:"))
        self.save_type_combo = ComboBox([(".png", 1),
                                          (".jpeg", 2)])
        
        ini_bool = self.ini.get("ScreenshotSet", "save_clipboard")
        # Init .
        
        self.save_file_radio.set_active(True)
        self.save_clipboard_radio.set_active(False)
        
        text_string = self.ini.get("ScreenshotSet", "save_path")
        if text_string:
            self.save_path_entry.set_text(text_string)
        else:    
            self.save_path_entry.set_text("~/.config/deepin-media-player/image")
            
        text_string = self.ini.get("ScreenshotSet", "save_type")            
        if text_string:
            self.save_type_combo.label.set_text(text_string)
        else:    
            self.save_type_combo.label.set_text(".png")
            
        if ini_bool and "true" == ini_bool.lower():
            self.save_file_radio.set_active(False)
            self.save_clipboard_radio.set_active(True)        
            self.save_path_entry.set_editable(False)
            self.save_path_entry.set_sensitive(False)
            self.save_path_button.set_sensitive(False)
            self.save_type_combo.set_sensitive(False)                 
                 
        self.current_show_sort_label = Label("")
        self.current_show_sort_check = CheckButton(_("Keep current aspect ratio"))
        self.current_show_sort_check.set_active(False)
        ini_bool = self.ini.get("ScreenshotSet", "current_show_sort")
        if ini_bool and "true" == ini_bool.lower():
            self.current_show_sort_check.set_active(True)
                
        title_box = gtk.VBox(spacing=5)
        title_box.pack_start(self.label, False, False)
        title_box.pack_start(create_separator_box(), False, True)
        title_box_align = gtk.Alignment()
        title_box_align.set_padding(10, 0, 10, 0)
        title_box_align.set(0, 0, 1, 1)
        title_box_align.add(title_box)
        
        save_path_button_align = gtk.Alignment()
        save_path_button_align.set(3, 0, 0, 0)
        save_path_button_align.add(self.save_path_button)
        
        path_box = gtk.HBox(spacing=5)
        path_box.pack_start(self.save_path_entry, False, False)
        path_box.pack_start(save_path_button_align, True, True)
        type_box = gtk.HBox(spacing=5)
        type_box.pack_start(self.save_type_label, False, False)
        type_box.pack_start(self.save_type_combo, False, False)
        save_box = gtk.VBox(spacing=5)
        save_box.pack_start(path_box, False, True)
        save_box.pack_start(type_box, False, True)
        save_box_align = gtk.Alignment()
        save_box_align.set_padding(0, 0, 40, 0)
        save_box_align.add(save_box)
        
        self.set_spacing(10)
        self.pack_start(title_box_align, False, True)
        self.pack_start(self.save_clipboard_radio, False, False)
        self.pack_start(self.save_file_radio, False, False)
        self.pack_start(save_box_align, False, True)
        self.pack_start(self.current_show_sort_check, False, False)
        
    def save_path_to_save_path_entry_clicked(self, widget):
        open_dialog = gtk.FileChooserDialog(_("Open Directory"),
                                            None,
                                            gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                            (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, 
                                             gtk.STOCK_OPEN, gtk.RESPONSE_OK))        
        open_dialog.set_current_folder(get_home_path())
        res = open_dialog.run()
        
        if res == gtk.RESPONSE_OK:
            path_string = open_dialog.get_filename()
            self.save_path_entry.set_text(path_string)
        open_dialog.destroy()

        
    def save_file_radio_clicked(self, widget, event):    
        if is_left_button(event):
            self.save_path_entry.entry.set_editable(True)
            self.save_path_entry.entry.set_sensitive(True)            
            self.save_path_button.set_sensitive(True)            
            self.save_path_entry.set_sensitive(True)
            self.save_type_combo.set_sensitive(True)
        
    def save_clipboard_radio_clicked(self, widget, event):    
        if is_left_button(event):
            self.save_path_entry.entry.set_editable(False)
            self.save_path_entry.entry.set_sensitive(False)            
            self.save_path_button.set_sensitive(False) 
            self.save_type_combo.set_sensitive(False)
        
    def get_screenshot_state(self):     
        screenshot_dict = {}
        screenshot_dict["save_clipboard"] = self.save_clipboard_radio.get_active() 
        screenshot_dict["save_file"] = self.save_file_radio.get_active()
        screenshot_dict["save_path"] = self.save_path_entry.get_text()
        screenshot_dict["save_type"] = self.save_type_combo.label.get_text()            
        screenshot_dict["current_show_sort"] = self.current_show_sort_check.get_active()
        return screenshot_dict
        
        
class OtherSet(gtk.VBox):    
    def __init__(self):
        gtk.VBox.__init__(self)
        self.fixed = gtk.Fixed()
        self.label = Label(_("Other"))
        self.label.set_size_request(label_width, label_height)
        self.heparator_hbox = gtk.HBox()
        self.heparator = create_separator_box()
        self.heparator_hbox.pack_start(self.heparator)
        
        otherset_x = 20
        #################################
        self.fixed.put(self.label, otherset_x, TITLE_HEIGHT_PADDING)
        self.fixed.put(self.heparator_hbox, heparator_x, heparator_y)
        
        self.pack_start(self.fixed)
        

class About(gtk.VBox):    
    def __init__(self):
        gtk.VBox.__init__(self)
        main_box = gtk.VBox(spacing=15)
        logo_image = ImageBox(app_theme.get_pixbuf("logo.png"))
        light_color = app_theme.get_color("labelText")
        logo_name = Label(_("Deepin Media Player"), text_size=10)
        logo_box = gtk.HBox(spacing=2)
        logo_box.pack_start(logo_image, False, False)
        logo_box.pack_start(logo_name, False, False)
        
        version_label = Label(_("Version:"))
        version_content = Label("V2.0", light_color)
        info_box = gtk.HBox(spacing=5)
        info_align = gtk.Alignment()
        info_align.set(0.5, 1, 1, 1)
        info_align.add(info_box)
        info_box.pack_start(version_label, False, False)
        info_box.pack_start(version_content, False, False)
        
        title_box = gtk.HBox(spacing=140)
        title_box.pack_start(logo_box, True, True)
        title_box.pack_start(info_align, True, True)
        
        describe = _("\tDeepin Media Player is a video player designed for Linux users. It support a variety of video formats, and features mode switching, video preview, online subtitles, screenshot taking and skin selection. \n\n\tDeepin Media Player is free software licensed under GNU GPLv3. ")
        describe_label = Label(describe, enable_select=False, wrap_width=440, text_size=10)
        main_box.pack_start(title_box, False, False)
        main_box.pack_start(create_separator_box(), False, True)
        main_box.pack_start(describe_label, False, False)
        
        main_align = gtk.Alignment()
        main_align.set_padding(25, 0, 20, 0)
        main_align.set(0, 0, 1, 1)
        main_align.add(main_box)
        
        self.add(main_align)

if __name__ == "__main__":        
    IniGui()
    gtk.main()
