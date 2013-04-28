#! /usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (C) 2013 XXX, Inc.
#               2013 红铭曼,王芳
#
# Author:     红铭曼,王芳 <hongmingman@sina.com>
# Maintainer: 红铭曼,王芳 <hongmingman@sina.com>
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

from BeautifulSoup import BeautifulSoup
import urllib2
import re

class YoukuWebParse(object):
    def __init__(self):
        self.headers = {"Accept":"*/*", "Accept-Language":"zh-CN", "":"", 
                        "User-Agent":"Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1)", 
                        #"Accept-Encoding":"gzip, deflate", 
                        "Connection":"Keep-Alive"}

    def scan_movie_leave(self, addr):
        temp_info = None
        url = addr
        req = urllib2.Request(url=url, headers=self.headers)
        data = urllib2.urlopen(url).read()
        #
        sounp = BeautifulSoup(data)
        music_list = sounp.findAll("a", {"class":"btnShow btnplayposi"})
        for link in music_list:
            addr = link.get("href") # 获取地址.
            title = link.get("title") # 获取标题.
            temp_info = (addr, title)
        return temp_info

    def scan_3_leave(self, addr):
        url = addr
        req = urllib2.Request(url=url, headers=self.headers)
        data = urllib2.urlopen(url).read()
        #
        sounp = BeautifulSoup(data)
        p_title_list = sounp.findAll("a", 
                {"href": re.compile("http://"),
                 "title" : re.compile("\d"),
                 "charset" : re.compile("-"),
                 "target" : re.compile('_')
                 })
        temp_list = []
        #print p_title_list
        for list_ in p_title_list:
            addr_ = list_.get("href")
            name_ = list_.get("title")
            #print name_, addr_
            temp_list.append((addr_, name_))
        return temp_list


    def parse_web(self, addr, index=1):
        page_num = None
        all_sum  = None
        info_list = []

        url = addr + "%d.html" % (index)
        #print url
        #data = urllib2.urlopen(url).read()
        req = urllib2.Request(url=url, headers=self.headers)
        data = urllib2.urlopen(url).read()
        #
        sounp = BeautifulSoup(data)
        p_title_list = sounp.findAll('li', {"class" : "p_title"})
        for link in p_title_list:
            a_link = link.a # <a href = "......" title.....> 中的 'a'.
            addr = a_link.get("href") # 获取地址.
            title = a_link.get("title") # 获取标题.
            #print "addr:", addr, "title:", title
            info_list.append((addr, title))
        
        if index == 1:
            page_num = len(p_title_list)
            #print "link len:", page_num
            all_sum_str = sounp.findAll("div", {"class" : "stat"})
            all_sum_utf_8 = str(all_sum_str[0].string).replace("条", "")
            all_sum = int(str(all_sum_utf_8.split("/")[1].strip()))
            #print "总数:", all_sum
        return info_list, page_num, all_sum


def get_sum_page(all_sum, page_num):
    page_sum = all_sum / page_num
    page_mod    = all_sum % page_num
    if page_mod > 0:
        page_sum += 1
    return page_sum

if __name__ == "__main__":
    from youku_web import v_olist_dict
    v_olist_keys =  v_olist_dict.keys() 
    youku_web_parse = YoukuWebParse()
    #youku_web_parse.parse_web("http://www.youku.com/show_page/id_zcc001eb6962411de83b1.html")
    #youku_web_parse.parse_web("http://www.youku.com/show_page/id_zcc000b60962411de83b1.html")
    #youku_web_parse.parse_web("http://www.youku.com/show_page/id_z84933d227a4911e1b2ac.html")
    #youku_web_parse.parse_web("http://www.youku.com/show_page/id_z8820e97ecfeb11e19013.html")
    #youku_web_parse.parse_web("http://www.youku.com/show_page/id_z0bb2a948c24311df97c0.html")

    info_list, page_num, all_sum = youku_web_parse.parse_web(v_olist_dict["热血"])
    '''
    info_list, page_num, all_sum = youku_web_parse.parse_web(v_olist_dict["格斗"])
    info_list, page_num, all_sum = youku_web_parse.parse_web(v_olist_dict["恋爱"])
    print get_sum_page(all_sum, page_num)
    print get_sum_page(all_sum, page_num)
    '''
    for i in range(1, get_sum_page(all_sum, page_num + 1)):
        info_list, page_num, all_sum = youku_web_parse.parse_web(v_olist_dict["热血"], i)
        for info in info_list:
            print info[0], info[1]


        
            


