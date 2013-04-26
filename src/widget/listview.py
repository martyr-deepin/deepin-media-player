#! /usr/bin/ python
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
from draw import draw_text, draw_pixbuf
from color import color_hex_to_cairo, alpha_color_hex_to_cairo
from utils import get_text_size, get_match_parent, get_offset_coordinate
from utils import is_single_click, is_double_click, is_left_button, is_right_button
from listview_base import type_check
from listview_base import ListViewBase
from listview_base import View, Text, Items
from keymap import get_keyevent_name, ctrl_mask_check, shift_mask_check
import pango
import cairo
import gtk



'''
View 试图:
#LARGEICON, DETAILS, SMALLICON, LIST, TITLE = range(0, 5)
!!再也不用写item了.那是一件幸福的事情.
DrawItem 事件可以针对每个 ListView 项发生。
当 View 属性设置为 View = Details 时，
还会发生 DrawSubItem 和 DrawColumnHeader 事件。
在这种情况下，可以处理 DrawItem 事件以绘制所有项共有的元素（如背景），
并处理 DrawSubItem 事件以便为各个子项（例如文本值）绘制元素。
您还可以仅使用这两个事件中的一个事件绘制 ListView 控件中的所有元素，尽管这可能不十分方便。
若要绘制详细信息视图中的列标题，必须处理 DrawColumnHeader 事件。
'''

class ListView(ListViewBase):
    def __init__(self):
        ListViewBase.__init__(self)
        self.__init_keymap()
        self.__init_settings()
        self.__init_values()
        self.__init_events()

    def __init_keymap(self):
        self.__keymap_dict = {
                "Down"     :   self.__listview_down_event,
                "Up"       :   self.__listview_up_event,
                "Home"     :   self.__listview_home_event,
                "End"      :   self.__listview_end_event,
                "Page_Up"  :   self.__listview_page_up_event,
                "Page_Down":   self.__listview_page_down_event,
                "Delete"   :   self.listview_delete_event,
                "Return"   :   self.__listview_return_event,
                "Ctrl + a" :   self.__listview_ctrl_a_event,
                }

    def __listview_down_event(self):
        #print "__listview_down_event..."
        if self.__single_items == []:  # 如果为空,则跳转到开头.
            self.__listview_end_event()
        else:
            vadjustment = get_match_parent(self, ["ScrolledWindow"]).get_vadjustment()
            if vadjustment:
                value = vadjustment.get_value()
                # 获取 start, end index.
                start_index, end_index = self.__get_start_end_index()
                row_index = self.items.index(self.__single_items[len(self.__single_items)-1]) 
                row_index += 1
                if row_index <= len(self.items) - 1:
                    self.__single_items = [self.items[row_index]]
                    self.on_queue_draw_area()
                    # 滚动窗口.
                    if row_index + 1 == end_index:
                        if row_index == len(self.items) - 1:
                            self.__listview_end_event()
                        else:
                            vadjustment.set_value(value + self.__items_padding_height)
    
    def __listview_up_event(self):
        #print "__listview_up_event.."
        if self.__single_items == []:  # 如果为空,则跳转到开头.
            self.__listview_home_event()
        else:
            vadjustment = get_match_parent(self, ["ScrolledWindow"]).get_vadjustment()
            if vadjustment:
                value = vadjustment.get_value()
                start_index, end_index = self.__get_start_end_index()
                row_index = self.items.index(self.__single_items[len(self.__single_items)-1])
                if (row_index - 1) >= 0:
                    self.__single_items = [self.items[max(row_index - 1, 0)]]
                    self.on_queue_draw_area()
                    # 滚动窗口.
                    if row_index - 1 == start_index:
                        vadjustment.set_value(value - self.__items_padding_height)

    def __listview_home_event(self): # 开头第一个项.
        #print "__listview_home_event..."
        vadjustment = get_match_parent(self, ["ScrolledWindow"]).get_vadjustment()
        if vadjustment:
            value = vadjustment.get_lower()
            # 设置选中items.
            if self.items != []:
                self.__single_items = [self.items[0]]
                vadjustment.set_value(value)
                self.on_queue_draw_area()

    def __listview_end_event(self): # 最末尾项.
        #print "__listview_end_event..."
        vadjustment = get_match_parent(self, ["ScrolledWindow"]).get_vadjustment()
        if vadjustment:
            value = vadjustment.get_upper() - vadjustment.get_page_size()
            # 设置选中items.
            if self.items != []:
                self.__single_items = [self.items[len(self.items) - 1]]
                vadjustment.set_value(value)
                self.on_queue_draw_area()
        
    def __listview_page_up_event(self): # 向下翻页.
        #print "__listview_page_up_event..."
        if self.__single_items == []:  # 如果为空,则跳转到开头.
            self.__listview_home_event()
        else:
            vadjustment = get_match_parent(self, ["ScrolledWindow"]).get_vadjustment()
            if vadjustment:
                value = vadjustment.get_value()
                start_index, end_index = self.__get_start_end_index()
                min_value  = vadjustment.get_lower()
                move_value = self.__items_padding_height * abs(start_index - end_index - 1)
                # 滚动窗口.
                value = value - move_value
                # 如果滚动的页超出了最小值,直接到开头.
                if value < min_value:
                    vadjustment.set_value(min_value)
                else:
                    vadjustment.set_value(value)
                self.on_queue_draw_area()
            
    def __listview_page_down_event(self): # 向上翻页.
        #print "__listview_page_down_event.."
        if self.__single_items == []: # 如果为空,则跳转到结尾.
            self.__listview_end_event()
        else:
            vadjustment = get_match_parent(self, ["ScrolledWindow"]).get_vadjustment()
            if vadjustment:
                value = vadjustment.get_value()
                start_index, end_index = self.__get_start_end_index()
                # 滚动窗口.
                max_value  = vadjustment.get_upper() - vadjustment.get_page_size()
                move_value = self.__items_padding_height * abs(end_index - start_index - 1)
                value = value + move_value
                # 如果滚动的页超出了,直接到末尾.
                if value > max_value:
                    vadjustment.set_value(max_value)
                else:
                    vadjustment.set_value(value)
                self.on_queue_draw_area()

    def listview_delete_event(self): # 删除一个选项.
        #print "__listiew_delete_event..."
        if self.__single_items != []:
            for item in self.__single_items:
                self.items.remove(item)
            self.__single_items = []
            self.on_queue_draw_area()

    def __listview_return_event(self):
        #print "__listview_return_event..."
        if self.__single_items != []:
            self.__double_items = self.__single_items[len(self.__single_items)-1]
            self.on_queue_draw_area()

    def __listview_ctrl_a_event(self):
        #print "__listview_ctrl_a_event..."
        if len(self.items) == len(self.__single_items):
            self.__single_items = []
        else:
            self.__single_items = self.items[:]
        self.on_queue_draw_area()

    def __init_settings(self):
        self.add_events(gtk.gdk.ALL_EVENTS_MASK)
        self.set_can_focus(True)

    def __init_values(self):
        #
        self.__init_values_events()
        self.__init_values_columns()
        self.__init_values_items()

    def __init_values_events(self):
        self.__on_draw_column_heade = self.__on_draw_column_heade_hd
        self.__on_draw_sub_item     = self.__on_draw_sub_item_hd
        self.__on_draw_item         = self.__on_draw_item_hd
        # 保存事件.
        self.__double_items_hd    = None
        self.__motion_items_hd    = None
        self.__single_items_hd    = None
        self.__right_items_hd     = None
        #
        self.__motion_columns_hd  = None
        self.__single_columns_hd  = None
        #
        self.__drag_rect    = (None, None, None)
        self.drag_preview_pixbuf = None

    def __init_values_columns(self):
        self.__columns_padding_height = 0
        self.__columns_show_check = False
        self.__move_column_check = False
        self.__save_move_column_x = 0
        self.__save_move_column_index  = 0
        # 需要移动标题头的时候, 按下的触发区域.
        self.__press_columns_area_width = 3

    def __init_values_items(self):
        self.__ctrl_check  = False
        self.__shift_check = False
        self.__save_press_move_item_num = None
        #
        self.__save_press_items_index = 0
        self.__save_press_items_check = False
        #
        self.__move_items_check = False
        self.__save_move_items_x = 0
        self.__save_move_items_index = 0
        #
        self.__items_padding_height = 30
        # 保存双击items.
        self.__double_items = None
        # 保存移动的items.
        self.__motion_items = None
        # 保存单击的items.
        self.__single_items = []
        # 保存移动的columns.
        self.__motion_columns = None
        # 保存单击的columns.
        self.__single_columns = None
        # 保存拖动的items下来.
        self.__drag_items = None

    def __init_events(self):
        self.connect("key-press-event",      self.__listview_key_press_event) 
        self.connect("key-release-event",    self.__listview_key_release_event)
        self.connect("realize",              self.__listview_realize_event)
        self.connect("motion-notify-event",  self.__listview_motion_notify_event)
        self.connect("button-press-event",   self.__listview_button_press_event)
        self.connect("button-release-event", self.__listview_button_release_event)
        self.connect("enter-notify-event",   self.__listview_enter_notify_event)
        self.connect("leave-notify-event",   self.__listview_leave_notify_event)
        self.connect("expose-event",         self.__listview_expose_event)

    def __listview_key_press_event(self, widget, event):
        #
        if ctrl_mask_check(event):
            self.__ctrl_check = True
        if shift_mask_check(event):
            self.__shift_check = True
        #
        key_code = get_keyevent_name(event, False)
        #print "key_code:", key_code
        if self.__keymap_dict.has_key(key_code):
            self.__keymap_dict[key_code]()
        return True

    def __listview_key_release_event(self, widget, event):
        #
        if ctrl_mask_check(event):
            self.__ctrl_check = False
        if shift_mask_check(event):
            self.__shift_check = False

    def __listview_realize_event(self, widget):
        widget.set_realized(True)

        scroll_win = get_match_parent(widget, "ScrolledWindow")
        if scroll_win:
            scroll_win.get_vadjustment().connect("value-changed",
                                    self.__scroll_win_vajustment_changed)
            scroll_win.get_hadjustment().connect("value-changed",
                                    self.__scroll_win_hajustment_changed)
            scroll_win.connect("scroll-event", self.__scroll_win_scroll_event)

    def __scroll_win_scroll_event(self, widget, event):
        self.__scroll_win_event()

    def __scroll_win_vajustment_changed(self, adjustment):
        self.__scroll_win_event()

    def __scroll_win_hajustment_changed(self, adjustment):
        self.__scroll_win_event()

    def __scroll_win_event(self):
        self.on_queue_draw_area()
        '''
        self.window.process_updates(True)
        self.window.process_updates(True)
        self.on_queue_draw_area()
        '''

    def __listview_motion_notify_event(self, widget, event):
        #print "__listview_motion_notify_event..."
        # 标题头移动事件处理.
        if self.view == View.DETAILS:  # 判断是否为试图.
            # 判断是否移动标题头.
            if self.__move_column_check:
                width = self.columns[self.__save_move_column_index].width
                min_width   = self.columns[self.__save_move_column_index].min_width
                value_width = int(event.x) - self.__save_move_column_x
                # 防止超过最小值.
                if width + value_width > min_width:
                    self.columns[self.__save_move_column_index].width += value_width
                    self.__save_move_column_x = int(event.x)
            #
            col_index, column_x, column_y =  self.__get_columns_mouse_data(event)
            if not (None in [col_index]):
                self.__motion_columns = self.columns[col_index]
                if self.__motion_columns_hd:
                    self.__motion_columns_hd(self, self.__motion_columns, col_index, column_x, column_y)
            else:
                self.__motion_columns = None
        #
        # items移动事件处理.
        row_index, col_index, item_x, item_y = self.__get_items_mouse_data(event)
        if not (None in [row_index]) and row_index < len(self.items):
            self.__motion_items = self.items[row_index]
            # 发送信号.
            if self.__motion_items_hd:
                self.__motion_items_hd(self, self.__motion_items, row_index, col_index, item_x, item_y)
        else:
            self.__motion_items = None
        #
        # items 滚动移动..
        if self.__save_press_items_check:
            index  = self.__save_press_items_index
            if self.items[index] in self.__single_items:
                save_y = self.__save_press_items_y
                move_y = int(event.y)
                # 保存画拖动的线的坐标.
                scroll_win  = get_match_parent(self, ["ScrolledWindow"])
                vadjustment = scroll_win.get_vadjustment()
                # set drag icon.
                #####################################################################
                if self.drag_preview_pixbuf == None:
                    width = 180
                    height = 150
                    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
                    w = surface.get_width()
                    h = surface.get_height()
                    cr = cairo.Context(surface)
                    item_width = 0
                    for item in self.__single_items:
                        draw_text(cr, item.sub_items[0].text, 0, item_width)
                        item_width += 30
                        if item_width % 150 == 0:
                            break
                    surface.write_to_png("/tmp/drag.png")

                if self.window.get_cursor() == None:
                    self.drag_preview_pixbuf  = gtk.gdk.pixbuf_new_from_file("/tmp/drag.png")
                    self.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.display_get_default(),
                                                          self.drag_preview_pixbuf,
                                                          0, 0))
                ##########################################################################
                if vadjustment:
                    value = vadjustment.get_value()
                    min_y = scroll_win.allocation.y
                    max_y = scroll_win.allocation.y + scroll_win.allocation.height
                    max_value  = vadjustment.get_upper() - vadjustment.get_page_size()
                    if max_value > 0:
                        if move_y - value < min_y:
                            vadjustment.set_value(value - self.__items_padding_height)
                        elif move_y - value > max_y and (row_index < len(self.items)):
                            vadjustment.set_value(value + self.__items_padding_height)
                if move_y > save_y:
                    if row_index == None:
                        row_index = len(self.items)
                self.__drag_rect = (row_index,  
                                    self.__items_padding_height, 
                                    scroll_win.allocation.width)
        else:
            self.window.set_cursor(None)
        #
        self.on_queue_draw_area()

    def __listview_button_press_event(self, widget, event):
        if is_left_button(event):
            if self.view == View.DETAILS:
                move_index, move_check =  self.__get_columns_mouse_data(event, move_check=True)
                if move_check and move_index != None:
                    self.__move_column_check  = move_check
                    self.__save_move_column_index  = move_index
                    self.__save_move_column_x = int(event.x)
            # 移动items.
            move_index, move_check = self.__get_items_mouse_data(event, move_check=True)
            # 按下items.
            press_index, press_check = move_index, move_check
            if press_check and press_index != None:
                self.__save_press_items_index = press_index
                self.__save_press_items_check = press_check
                self.__save_press_items_y     = int(event.y)
            
            if move_index != None and move_check:
                for item in self.__single_items:
                    if item == self.items[move_index]:
                        self.__move_items_check      = move_check
                        self.__save_move_items_index = move_index
                        self.__save_move_items_x     = int(event.x)
                        break
                else:
                    self.__move_items_check = False
            
        # 判断双击的区域.
        if is_double_click(event):
            row_index, col_index, item_x, item_y = self.__get_items_mouse_data(event)
            if not (None in [row_index]):
                self.__double_items = self.items[row_index]
                # 发送信号.
                if self.__double_items_hd:
                    self.__double_items_hd(self, self.__double_items, row_index, col_index, item_x, item_y)
                self.on_queue_draw_area()
        else:
            row_index, col_index, item_x, item_y = self.__get_items_mouse_data(event)
            #print "press_event:", row_index
            self.__save_press_move_item_num = row_index # 保存按下的items row.

    def __listview_button_release_event(self, widget, event):
        #print "__listview_button_release_event..."
        self.__move_column_check = False # 取消移动标题头.
        # 获取标题头触发的release事件返回的x索引.
        if is_left_button(event):
            # 列标头.
            if self.view == View.DETAILS:
                col_index, column_x, column_y =  self.__get_columns_mouse_data(event)
                if col_index != None: 
                    self.__single_columns = self.columns[col_index]
                    if self.__single_columns_hd:
                        self.__single_columns_hd(self, self.__single_columns, col_index, column_x, column_y)
            # 获取items触发的release事件返回的x,y索引.
            row_index, col_index, item_x, item_y = self.__get_items_mouse_data(event)
            #insert_index = self.__move_column_insert_index
            insert_index = row_index
            if not (None in [row_index]):
                # 发送信号.
                if self.__save_press_items_index == row_index:
                    if not self.__ctrl_check:
                        self.__single_items = []
                    # 判断是否重新选择了,如果是就消除掉.
                    if self.items[row_index] in self.__single_items:
                       self.__single_items.remove(self.items[row_index]) 
                    else:
                        self.__single_items.append(self.items[row_index])
                    if self.__single_items_hd:
                        self.__single_items_hd(self, self.__single_items, row_index, col_index, item_x, item_y)
            else:
                insert_index = len(self.items)
            
            if self.__move_items_check and self.__save_press_items_index != row_index:
                for insert_item in self.__single_items:
                    self.items.remove(insert_item)
                    self.items.add_insert(insert_index, insert_item)
            self.__save_press_items_check = False
            self.__drag_rect = (None, None, None)
            self.drag_preview_pixbuf = None
        elif is_right_button(event):
            row_index, col_index, item_x, item_y = self.__get_items_mouse_data(event)
            if self.__right_items_hd:
                self.__right_items_hd(self, event, row_index, col_index, item_x, item_y)

    def __listview_enter_notify_event(self, widget, event):
        #print "__listview_enter_enter...notify_event..."
        pass

    def __listview_leave_notify_event(self, widget, event):
        #print "__listview_leave_notify_event...."
        self.__motion_columns = None
        self.__motion_items   = None

    def connect_event(self, event_name, function_point):
        if event_name   == "double-items":
            self.__double_items_hd   = function_point
        elif event_name == "motion-notify-items":
            self.__motion_items_hd   = function_point
        elif event_name == "single-items":
            self.__single_items_hd   = function_point
        elif event_name == "right-items-event":
            self.__right_items_hd    = function_point
        elif event_name == "motion-notify-columns":
            self.__motion_columns_hd = function_point
        elif event_name == "single-columns":
            self.__single_columns_hd = function_point

    def __listview_expose_event(self, widget, event):
        #print "__listview_expose_event.."
        cr = widget.window.cairo_create()
        rect = widget.allocation
        #
        if self.view == View.DETAILS: # 带标题头的视图, 比如详细信息.
            self.__draw_view_details(cr, rect, widget)
        #elif self.view == 
        #
        # 设置窗体的高度和宽度.
        self.__set_listview_size()
        return True

    def __draw_view_details(self, cr, rect, widget):
        #
        offset_x, offset_y, viewport = get_offset_coordinate(widget)
        #
        e = ItemEventArgs()
        save_rect = rect
        e.cr = cr
        e.rect = (rect.x, 
                  rect.y + offset_y + self.__columns_padding_height,
                  rect.width, 
                  rect.height)
        e.drag_rect = self.__drag_rect
        self.on_draw_item(e)
        # 画标题头.
        if self.__columns_show_check:
            self.__draw_view_details_column(offset_y, cr, rect)
        # 优化listview.
        # 获取滚动窗口.
        scroll_win = get_match_parent(self, "ScrolledWindow")
        scroll_rect_h = rect.height
        if scroll_win: # 如果没有滚动窗口,直接获取listview的高度.
            scroll_rect_h = scroll_win.allocation.height
        # dtk.ui.listview ===>>>
        start_y = offset_y - self.__columns_padding_height
        end_y   = offset_y + viewport.allocation.height - self.__columns_padding_height
        #start_index  = max(start_y / self.__items_padding_height, 0)
        start_index  = max(int(scroll_win.get_vadjustment().get_value() / self.__items_padding_height), 0)
        end_index    = (start_index + (scroll_rect_h - self.__columns_padding_height)/ self.__items_padding_height) + 2
        # 
        # 剪切出绘制items的区域,防止绘制到标题头上.
        cr.save()
        cr.rectangle(rect.x + offset_x, 
                     rect.y + offset_y + self.__columns_padding_height, 
                     scroll_win.allocation.width, 
                     scroll_win.allocation.height)
        cr.clip()
        # 画 items.
        self.__draw_view_details_items(start_index, end_index, cr, rect)
        cr.restore()

    def __draw_view_details_column(self, offset_y, cr, rect):
        temp_column_w = 0
        for index, column in enumerate(self.columns): # 绘制标题头.
            # 保存属性.
            e = ColumnHeaderEventArgs()
            e.cr     = cr
            e.column = column 
            e.column_index = index
            e.motion_columns = self.__motion_columns
            e.single_columns = self.__single_columns
            e.text = column.text
            e.x = rect.x + temp_column_w
            e.y = offset_y + rect.y
            e.w = column.width
            e.h = self.__columns_padding_height + 1
            e.text_color = column.text_color
            #
            temp_column_w += column.width
            self.on_draw_column_heade(e)

    def __draw_view_details_items(self, start_index, end_index, cr, rect):
        temp_item_h  = self.__columns_padding_height
        for row, item in enumerate(self.items[start_index:end_index]):
            temp_item_w = 0
            # 行中的列元素.
            for column, sub_item in map(lambda s, c:(s, c), 
                                        self.columns,  
                                        item.sub_items):
                if column and sub_item:
                    # 保存subitem的所有信息.
                    e = SubItemEventArgs()
                    e.cr = cr
                    e.sub_item = sub_item
                    e.double_items = self.__double_items
                    e.motion_items = self.__motion_items
                    e.single_items = self.__single_items
                    e.item     = item
                    e.text = sub_item.text
                    e.text_color = sub_item.text_color
                    e.x = rect.x + temp_item_w
                    e.y = rect.y + ((row + start_index) * self.__items_padding_height) + self.__columns_padding_height
                    e.w = column.width
                    e.h = self.__items_padding_height 
                    e.sub_item_index = row + start_index
                    temp_item_w += column.width
                    #
                    self.on_draw_sub_item(e)
            # 保存绘制行的y坐标.
            temp_item_h += self.__items_padding_height


    def __get_start_end_index(self):
        rect = self.allocation
        offset_x, offset_y, viewport = get_offset_coordinate(self)
        #
        # 获取滚动窗口.
        scroll_win = get_match_parent(self, "ScrolledWindow")
        scroll_rect_h = rect.height
        if scroll_win: # 如果没有滚动窗口,直接获取listview的高度.
            scroll_rect_h = scroll_win.allocation.height
        start_y = offset_y - self.__columns_padding_height
        end_y   = offset_y + viewport.allocation.height - self.__columns_padding_height
        start_index  = max(int(scroll_win.get_vadjustment().get_value() / self.__items_padding_height), 0)
        end_index    = (start_index + (scroll_rect_h - self.__columns_padding_height)/ self.__items_padding_height) + 1
        return start_index, end_index

    ################################################
    ## @ on_draw_column_heade : 连接头的重绘函数.
    def __on_draw_column_heade_hd(self, e):
        if e.single_columns == e.column:
            e.cr.set_source_rgba(*alpha_color_hex_to_cairo(("#ebebeb", 0.1)))
            e.text_color = "#000000"
        elif e.motion_columns == e.column:
            e.cr.set_source_rgba(*alpha_color_hex_to_cairo(("#0000FF", 0.1)))
            e.text_color = "#0000FF"
        else:
            e.cr.set_source_rgba(*alpha_color_hex_to_cairo(("#FF00FF", 0.1)))
            e.text_color = "#FF00FF"
        e.cr.rectangle(e.x, e.y, e.w, e.h)
        e.cr.stroke()
        if self.columns[len(self.columns)-1] == e.column:
            e.cr.set_source_rgba(*alpha_color_hex_to_cairo(("#FF00FF", 0.1)))
            e.cr.rectangle(e.x + e.w, e.y, self.allocation.width - e.x, e.h)
            e.cr.stroke()
        # 画标题栏文本.
        draw_text(e.cr, 
                  e.text,
                  e.x, e.y, e.w, e.h,
                  text_color=e.text_color,
                  alignment=Text.CENTER)
        #

    @property
    def on_draw_column_heade(self):
        return self.__on_draw_column_heade

    @on_draw_column_heade.setter
    def on_draw_column_heade(self, hd):
        self.__on_draw_column_heade = hd
        self.on_queue_draw_area()

    @on_draw_column_heade.getter
    def on_draw_column_heade(self):
        return self.__on_draw_column_heade

    @on_draw_column_heade.deleter
    def on_draw_column_heade(self):
        del self.__on_draw_column_heade

    ################################################
    ## @ on_draw_item : 连. 当 owner_draw 设置为真的时候发生.
    def __on_draw_item_hd(self, e):
        #print "__on_draw_item_hd...", e.drag_rect
        e.cr.set_source_rgba(*alpha_color_hex_to_cairo(("#1f1f1f",1.0)))
        e.cr.rectangle(*e.rect)
        e.cr.fill()
        if e.drag_rect[0] != None:
            drag_pixbuf = app_theme.get_pixbuf("listview/drag_line.png").get_pixbuf()
            drag_pixbuf = drag_pixbuf.scale_simple(e.drag_rect[2], 5, gtk.gdk.INTERP_BILINEAR)
            draw_pixbuf(e.cr, drag_pixbuf, 0, e.drag_rect[0] * e.drag_rect[1])

    @property
    def on_draw_item(self, e):
        return self.__on_draw_item

    @on_draw_item.setter
    def on_draw_item(self, hd):
        self.__on_draw_item =  hd
        self.on_queue_draw_area()

    @on_draw_item.getter
    def on_draw_item(self):
        return self.__on_draw_item

    @on_draw_item.deleter
    def on_draw_item(self):
        del self.__on_draw_item

    ################################################
    ## @ on_draw_sub_item : 连.
    def __on_draw_sub_item_hd(self, e):
        if e.double_items == e.item:
            e.text_color = "#0000FF"
            text_size=9
            e.cr.set_source_rgba(0, 0, 0, 0.5)
            e.cr.rectangle(e.x, e.y, e.w, e.h)
            e.cr.fill()
        elif e.item in e.single_items:
            e.text_color = "#00FF00"
            text_size=9
            e.cr.set_source_rgba(0, 0, 0, 0.5)
            e.cr.rectangle(e.x, e.y, e.w, e.h)
            e.cr.fill()
        elif e.motion_items == e.item:
            e.text_color  = "#FF0000"
            text_size=9
            e.cr.set_source_rgba(0, 0, 0, 0.5)
            e.cr.rectangle(e.x, e.y, e.w, e.h)
            e.cr.fill()
        else:
            e.text_color = "#FFFFFF"
            text_size=9

        e.draw_text(e.cr, 
                  str(e.text), 
                  e.x + 10, e.y, e.w, e.h,
                  text_color=e.text_color, 
                  text_size=text_size,
                  alignment=Text.LEFT)
        
    @property
    def on_draw_sub_item(self, e):
        return self.__on_draw_sub_item

    @on_draw_sub_item.setter
    def on_draw_sub_item(self, hd):
        self.__on_draw_sub_item =  hd
        self.on_queue_draw_area()

    @on_draw_sub_item.getter
    def on_draw_sub_item(self):
        return self.__on_draw_sub_item

    @on_draw_sub_item.deleter
    def on_draw_sub_item(self):
        del self.__on_draw_sub_item

    def __set_listview_size(self):
        # 设置listview的高度和宽度.
        rect = self.allocation
        listview_height =  (len(self.items)) * self.__items_padding_height + self.__columns_padding_height
        listview_width  =  0 #138 # 额外添加 188 的宽度.
        for column in self.columns:
            listview_width += column.width 
        if (rect.height != listview_height) or (rect.width != listview_width):
            self.set_size_request(listview_width, listview_height)

    def __get_items_mouse_data(self, event, move_check=False):
        offset_x, offset_y, viewport = get_offset_coordinate(self)
        save_x, save_y = 0, 0
        if self.__in_items_check(offset_y, event):
            event_x = event.x # 获取鼠标x.
            # 获取行号.
            event_y_padding = int(event.y - self.__columns_padding_height)
            row_index = event_y_padding / self.__items_padding_height
            x_padding = 0
            col_index = 0
            # 获取行item,列的sub_items.
            if not move_check:
                for column in self.columns:
                    if x_padding <= int(event.x) <= x_padding + column.width:
                        save_x = int(event.x - x_padding)
                        save_y = int(event_y_padding - row_index * self.__items_padding_height)
                        break
                    x_padding += column.width
                    col_index += 1
            # 判断是否在可显示的列内.
            if ((row_index < len(self.items)) and 
                (col_index < len(self.items[row_index].sub_items))):
                if move_check: # 判断是否移动items.
                    return row_index, True
                else:
                    return row_index, col_index, save_x, save_y
            else:
                if move_check: # 判断是否移动items.
                    return row_index, True
                else:
                    return row_index, None, save_x, save_y
        else: # 鼠标点击不在区域内.
            if move_check: # 判断是否移动items.
                return None, False
            else:
                return None, None, None, None

    def __in_items_check(self, offset_y, event):
        start_y = (offset_y) + self.__columns_padding_height
        end_y   = start_y + ((len(self.items)) * self.__items_padding_height)
        return (start_y < event.y < end_y)

    def __get_columns_mouse_data(self, event, move_check=False):
        offset_x, offset_y, viewport = get_offset_coordinate(self)
        save_x, save_y = 0, 0
        if self.__in_columns_check(offset_y, event):
            # 获取行item,列的sub_items.
            x_padding = 0
            col_index = 0
            for column in self.columns:
                if move_check:
                    padding_width = x_padding + column.width
                    # 判断是否在移动区域内.
                    if (padding_width - self.__press_columns_area_width) <= int(event.x) <= padding_width:
                        return col_index, True
                else:
                    if x_padding <= int(event.x) <= x_padding + column.width:
                        save_x = int(event.x - x_padding)
                        save_y = int(event.y)
                        return col_index, save_x, save_y
                col_index += 1
                x_padding += column.width
        # 返回空数据.
        if move_check:
            return None, False
        else:
            return None, None, None

    def __in_columns_check(self, offset_y, event):
        start_y = offset_y
        end_y   = start_y + self.__columns_padding_height
        return (start_y < event.y < end_y)

    # 设置每行的高度.
    @property
    def items_height(self):
        return self.__items_padding_height
    
    @items_height.setter
    def items_height(self, height):
        self.__items_padding_height = height
        self.on_queue_draw_area()

    @items_height.getter
    def items_height(self):
        return self.__items_padding_height

    @items_height.deleter
    def items_height(self):
        del self.__items_padding_height

    # 设置标题头的高度.
    @property
    def columns_height(slef):
        return self.__columns_padding_height

    @columns_height.setter
    def columns_height(self, height):
        self.__columns_padding_height = height
        self.on_queue_draw_area()

    @columns_height.getter
    def  columns_height(self):
        return self.__columns_padding_height

    @columns_height.deleter
    def columns_height(self):
        del self.__columns_padding_height

    def set_double_items(self, item):
        self.__double_items = item
        #
        vadjustment = get_match_parent(self, ["ScrolledWindow"]).get_vadjustment()
        if vadjustment:
            value = vadjustment.get_value()
            start_index, end_index = self.__get_start_end_index()
            # 滚动窗口.
            max_value  = vadjustment.get_upper() - vadjustment.get_page_size()
            move_value = self.__items_padding_height * self.items.index(item) #abs(end_index - start_index - 1)
            #value = value + move_value
            value = move_value
            # 如果滚动的页超出了,直接到末尾.
            if value > max_value:
                vadjustment.set_value(max_value)
            else:
                vadjustment.set_value(value)
        #
        self.on_queue_draw_area()

    def clear(self):
        self.items.clear()
        self.__single_items = []
        self.__motion_items = []
        self.__double_items = []
        self.on_queue_draw_area()

    def get_single_items(self):
        return self.__single_items 

class ItemEventArgs(object):
    def __init__(self):
        self.cr = None
        self.rect = None
        self.select_items = []
        # 鼠标的起点和结束点.
        self.start_x = 0
        self.start_y = 0
        self.end_x   = 0
        self.end_y   = 0
        self.state   = 0 # 状态.
        # item.
        self.item    = None
        self.drag_rect = None
        # Bounds
        self.x =  0
        self.y =  0
        self.w =  0
        self.h =  0


class SubItemEventArgs(object):
    def __init__(self):
        self.cr = None
        self.item = None
        self.sub_item = None
        self.sub_item_index = None
        self.double_items = None
        self.motion_items = None
        self.single_items = None
        self.text = ""
        self.text_color = "#000000"
        self.text_align = Text.LEFT
        self.draw_text = draw_text
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0

class ColumnHeaderEventArgs(object):
    def __init__(self):
        self.cr     = None
        self.column = None
        self.column_index = 0
        self.motion_columns = None
        self.single_columns = None
        self.text = ""
        self.text_color = "#000000"
        self.text_align = Text.LEFT
        self.draw_text = draw_text
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0

if __name__ == "__main__":

    def test_btn_clicked(widget):
        #listview1.items.clear()
        #listview1.columns[3].width += 5
        #listview1.items.add_range([["微软", "男", "程序员", "美国"]])
        #listview1.items[0].sub_items.add("fdjkf")
        #listview1.items[0].sub_items[0].text = "我爱你,精灵..."
        listview1.begin_update()
        for i in range(0, 10000):
            #listview1.items.add_insert(0, [[str(i), "男", "程序员", "美国" + str(i)]])
            listview1.items.add([str(i), 
                                "男", 
                                "程序员", 
                                "美国" + str(i), 
                                "你是" + str(i), 
                                "#FF" + str(i),
                                "#ED" + str(i)])
        listview1.end_update()
        #listview1.columns[10].width += 5
        
    def listview1_test_on_draw_column_heade(e):
        if e.single_columns == e.column:
            e.cr.set_source_rgba(*alpha_color_hex_to_cairo(("#ebebeb", 0.1)))
            e.text_color = "#000000"
        elif e.motion_columns == e.column:
            e.cr.set_source_rgba(*alpha_color_hex_to_cairo(("#0000FF", 0.1)))
            e.text_color = "#0000FF"
            e.cr.set_source_rgba(0, 0, 1, 0.1)
            e.cr.rectangle(e.x, e.y, e.w, e.h)
            e.fill()
        else:
            e.cr.set_source_rgba(*alpha_color_hex_to_cairo(("#FF00FF", 0.1)))
            e.text_color = "#FF00FF"
        e.cr.rectangle(e.x, e.y, e.w, e.h)
        e.cr.stroke()
        if listview1.columns[len(listview1.columns)-1] == e.column:
            e.cr.set_source_rgba(*alpha_color_hex_to_cairo(("#FF00FF", 0.1)))
            e.cr.rectangle(e.x + e.w, e.y, listview1.allocation.width - e.x, e.h)
            e.cr.stroke()
        # 画标题栏文本.
        draw_text(e.cr, 
                  e.text,
                  e.x, e.y, e.w, e.h,
                  text_color=e.text_color,
                  alignment=Text.CENTER)
        #

    def listview1_test_on_draw_sub_item(e):
        if e.double_items == e.item:
            e.text_color = "#0000FF"
            text_size=10
        elif e.item in e.single_items:
            e.text_color = "#00FF00"
            text_size=10
        elif e.motion_items == e.item:
            e.text_color  = "#FF0000"
            text_size=12
            e.cr.set_source_rgba(0, 0, 0, 0.5)
            e.cr.rectangle(e.x, e.y, e.w, e.h)
            e.cr.fill()
        else:
            e.text_color = "#FFFFFF"
            text_size=10

        e.draw_text(e.cr, 
                  str(e.text), 
                  e.x, e.y, e.w, e.h,
                  text_color=e.text_color, 
                  text_size=text_size,
                  alignment=Text.CENTER)


    def listview1_test_on_draw_item(e):
        pass

    def test_listview_double_items(listview, double_items, row, col, item_x, item_y):
        #print double_items.sub_items[0], row, col, item_x, item_y
        pass
        # 测试双击改变第一个文本.
        #listview.items[row].sub_items[0].text = "明天"
        # 测试删除双击下的items.
        #listview.items.remove(double_items)
        # 测试在指定位置插入items.
        #listview.items.add_insert(row + 1, [["long", "fjdkf", "fjdkf"]])
        # 测试改变标题头高度.
        #listview.columns_height += 5

    def test_listview_motion_notify_items(listview, motion_items, row, col, item_x, item_y):
        if col == None:
            col = 0
        #print "test_listview_motion_notify_items:", motion_items.sub_items[col].text, row, col
        #motion_items.sub_items[col].text = item_x

    def test_listview_motion_notify_columns(listview, motion_columns, col, item_x, item_y):
        #print "test_listview_motion_notify_columns:", motion_columns, item_x, item_y
        pass

    def test_listview_single_items(listview, single_items, row, col, item_x, item_y):
        if col == None:
            col = 0
        #single_items[0].sub_items[col].text = item_x
        print single_items[0].sub_items[col].text, item_x, item_y

    def test_listview_single_columns(listview, single_columns, col, item_x, item_y):
        print single_columns.text, item_x, item_y
        pass
    

    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    win.connect("destroy", lambda w : gtk.main_quit())
    win.set_size_request(500, 500)
    listview1 = ListView()
    # 事件测试.
    listview1.connect_event("double-items",  test_listview_double_items) 
    listview1.connect_event("motion-notify-items", test_listview_motion_notify_items)
    listview1.connect_event("motion-notify-columns", test_listview_motion_notify_columns)
    listview1.connect_event("single-items",  test_listview_single_items) 
    listview1.connect_event("single-columns", test_listview_single_columns)
    #listview1.connect_event("
    #listview1.items_height = 130
    #listview1.columns_height = 150
    # 连接主要绘制函数.
    #listview1.on_draw_column_heade =  listview1_test_on_draw_column_heade
    #listview1.on_draw_sub_item     =  listview1_test_on_draw_sub_item
    #listview1.on_draw_item = listview1_test_on_draw_item
    listview1.columns.add("姓名")
    listview1.columns.add_range(["性别", "职业", "国籍", "企业", "前景", "背景",
                                 "性别", "职业", "国籍", "企业", "前景", "背景",
                                 "性别", "职业", "国籍", "企业", "前景", "背景",
                                ])
    listview1.items.add(["10"])
    listview1.items[0].sub_items.add("男")
    listview1.items[0].sub_items.add("宠物")
    listview1.items[0].sub_items.add("宠物国")
    listview1.items.add_range([["张飞", "10", "武士", "蜀国"], 
                              ["孙策", "男", "骑士", "吴国", "aaa", "b", "c", "d", "f"]])
    listview1.items.add_range([["求伯灿", "男", "程序员", "中国"], 
                              ["linus", "男", "内核开发", "荷兰"]])
    #
    scroll_win = gtk.ScrolledWindow()
    scroll_win.set_policy(gtk.POLICY_NEVER, gtk.POLICY_ALWAYS)
    scroll_win.add_with_viewport(listview1)
    vbox = gtk.VBox()
    test_btn = gtk.Button("test")
    test_btn.connect("clicked",  test_btn_clicked)
    vbox.pack_start(scroll_win, True, True) 
    vbox.pack_start(test_btn, False, False)
    win.add(vbox)
    win.show_all()
    #listview1.view = View.LIST
    #
    listview1.columns[0].width = 245
    listview1.columns[2].width = 145
    listview1.columns[2].text = "职位"
    gtk.main()




