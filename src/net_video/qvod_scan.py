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

import urllib2
import urllib
import chardet
import re
# import threading
from dtk.ui.utils import is_network_connected

MAIN_HTML = "http://www.hakuzy.com/"
SCAN_HTML = "http://www.hakuzy.com/search.asp?searchword="
SCAN_HTML_PAGE = "http://www.hakuzy.com/search.asp?page=%d&searchword=%s&searchtype=-1"
scan_index = {
    "动作片":"/list/?1.html",
    "纪录片":"/list/?2.html",
    "动漫片":"/list/?3.html",
    "喜剧片":"/list/?4.html",
    "科幻片":"/list/?5.html",
    "爱情片":"/list/?6.html",
    "战争片":"/list/?7.html",
    "恐怖片":"/list/?8.html",
    "综艺其它":"/list/?9.html",
    "剧情片":"/list/?10.html",
    "大陆剧":"/list/?11.html",
    "港台剧":"/list/?12.html",
    "欧美剧":"/list/?13.html",
    "日韩剧":"/list/?14.html",
    "音乐":"/list/?15.html",
    "QMV高清":"/list/?16.html",
    }


class QvodInfo(object):
    def __init__(self):
        self.addr  = None  # 跳转地址.
        self.anme  = None  # 影片名称
        self.area  = None  # 地区.
        self.tyep  = None  # 类型.
        self.date  = None  # 上映日期.
        self.iamge = None  #
        self.qvod_addr = None # qvod 地址
        
class QvodScan(object):
    def __init__(self):            
        self.page_num = 0
        # self.scan("功夫熊猫")
        self.scan("功夫")
        
    def scan(self, scan_keyword):
        read_buffer = self.__open_url_addr(scan_keyword)
        #
        if read_buffer:
            ######################################
            string_list = self.__read_buffer_to_code(read_buffer)
            ######################################        
            # get page sum.
            self.__get_scan_page_num(string_list)
            # get qvod addr.                
            self.__get_qvod_info(scan_keyword, 1)
            return True
        else:    
            return False
        
    def __get_qvod_info(self, scan_keyword, index):    
        addr_patter = r'value="<!--影片链接开始代码-->(.+)<!--影片链接结束代码-->'
        name_patter = r'<!--影片名称开始代码-->(.+)<!--影片名称结束代码-->'
        area_patter = r'<!--影片地区开始代码-->(.+)<!--影片地区结束代码-->'
        type_patter = r'<!--影片类型开始代码-->(.+)<!--影片类型结束代码-->'
        date_patter = r'<!--上映日期开始代码-->(.+)<!--上映日期结束代码-->'
        
        
        read_buffer = self.__open_url_addr(scan_keyword, index)
        string_list = self.__read_buffer_to_code(read_buffer)
        for line in string_list:
            # addr.
            scan_addr_result = self.__scan_findall(addr_patter, line)
            if scan_addr_result != []:
                print "地址:", scan_addr_result[0]
            scan_name_result = self.__scan_findall(name_patter, line)    
            # name.
            if scan_name_result != []:
                print "名称:", scan_name_result[0]
            # area.    
            scan_area_result = self.__scan_findall(area_patter, line)    
            if scan_area_result != []:
                print "地区:", scan_area_result[0]
            # type.
            scan_type_result = self.__scan_findall(type_patter, line)    
            if scan_type_result != []:
                print "类型:", scan_type_result[0]
            # date.    
            scan_date_result = self.__scan_findall(date_patter, line)    
            if scan_date_result != []:
                print "日期:", scan_date_result[0]
            
    def __read_buffer_to_code(self, read_buffer):    
        try: # no gb2312.
            string_list = self.__to_code_utf_8(read_buffer).split("\n")
        except: # gb2312.
            # check gb2312.
            if chardet.detect(read_buffer)['encoding'] in ['GB2312']:
                string_list = (read_buffer.decode('gbk').encode('utf-8')).split("\n")
        return string_list
                    
    def __open_url_addr(self, scan_keyword, index=1):
        keyword = urllib.quote(self.__to_code_gb2312(scan_keyword))
        # scan_html = SCAN_HTML + keyword
        scan_html = SCAN_HTML_PAGE % (1, keyword)
        if is_network_connected():
            url_open = urllib2.urlopen(scan_html)
            read_buffer = url_open.read()
            return read_buffer
        else:
            return None
        
    def __scan_findall(self, patter, patter_string):
        return re.findall(patter, patter_string)
    
    def __get_scan_page_num(self, string_list):                
        page_num_patter = r'>(.+)条记录'
        page_max_patter = r'value="<!--影片链接开始代码-->'
        scan_record_sum = 0
        page_max = 0
        #
        for line in string_list:                        
            # get page max.
            page_max_result = (self.__scan_findall(page_max_patter, line))
            if page_max_result != []:
                page_max += 1
            # get result.    
            scan_result = self.__scan_findall(page_num_patter, line)    
            if scan_result != []:                
                scan_record_sum = int(scan_result[0].strip())
                print "%d条记录" % (scan_record_sum)
                break
        #    
        print "max:", page_max    
        self.__scan_record_sum_to_page_num(scan_record_sum, page_max)
        
    def __scan_record_sum_to_page_num(self, scan_record_sum, page_max):        
        PAGE_MAX = page_max
        if page_max > 0:
            self.page_num = scan_record_sum / PAGE_MAX
            if (scan_record_sum % PAGE_MAX) > 0:
                self.page_num += 1
        #        
        print "总共有%d页" % (self.page_num)
                
    def __to_code_gb2312(self, keyword):
        return keyword.decode("utf-8").encode("gb2312")
    
    def __to_code_utf_8(self, string):
        return string.decode('gb2312').encode("utf-8")
    
if __name__ == "__main__":    
    QvodScan()
