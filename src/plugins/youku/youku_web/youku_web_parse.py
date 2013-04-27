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
from youku_web import v_olist_dict
import urllib2

class YoukuWebParse(object):
    def __init__(self):
        self.headers = {"Accept":"*/*", "Accept-Language":"zh-CN", "":"", 
                        "User-Agent":"Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1)", 
                        #"Accept-Encoding":"gzip, deflate", 
                        "Connection":"Keep-Alive"}
    
    def parse_web(self, addr, index=1):
        url = addr + "%d.html" % (index)
        print url
        #data = urllib2.urlopen(url).read()
        req = urllib2.Request(url=url, headers=self.headers)
        data = urllib2.urlopen(url).read()
        #
        sounp = BeautifulSoup(data)
        p_title_list = sounp.findAll('li', {"class" : "p_title"})
        for link in p_title_list:
            a_link = link.a
            addr = a_link.get("href") # 获取地址.
            title = a_link.get("title") # 获取标题.
            print "addr:", addr, "title:", title
        

        print "link len:", len(p_title_list)
        print "总数:", sounp.findAll("div", {"class" : "stat"})



if __name__ == "__main__":
    v_olist_keys =  v_olist_dict.keys() 
    youku_web_parse = YoukuWebParse()
    youku_web_parse.parse_web(v_olist_dict["热血"])
