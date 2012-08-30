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
import re

SCAN_URL =  "http://www.yyets.com/php/search/index?keyword="
SCAN_PAGE_URL = "http://www.yyets.com/php/search/index"

class ScanUrlSub:
    def __init__(self):        
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
        print "当前頁的字幕数:", self.current_page
        print "总的字幕数目:", self.sum_subtitles        
        print "玉樹:", self.sum_subtitles - (self.sum_subtitles / max(self.current_page, 1)) * self.current_page
        
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
        
if __name__ == "__main__":
    scan_url_sub = ScanUrlSub()
    scan_url_sub.scan_url_function("dsfsdf")    
    
    print "搜索字幕总数:", scan_url_sub.sum_subtitles    
    print '下一页需要的链接:', scan_url_sub.page_string 
    temp_url = scan_url_sub.page_string + "3" + scan_url_sub.down_page_url
    temp_url = SCAN_PAGE_URL + temp_url
    print "搜索:", temp_url
    scan_url_sub.scan_page_index(3)
    # scan_url_sub.get_page_all_url_list(temp_url)
    scan_url_sub.get_sum_page()
    print "第3页:搜索到的东西:", len(scan_url_sub.mc_url_and_name_dict.keys())
    print "=========================="
    for i in scan_url_sub.mc_url_and_name_dict.keys():
        print i
