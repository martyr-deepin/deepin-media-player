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



import re
import sys
import urllib
import urllib2
import datetime
 
class YouToFlvcd(object):
    def __init__(self, type="youku"):
        self.url = ""
        if "youku" == type:
            self.pattern = re.compile(r"<a href *= *\"(http://f\.youku\.com/player/getFlvPath/[^\"]+)")
        elif "pps" == type:
            self.pattern = re.compile(r"<a href *= *\"(http://vurl\.pps[^\"]+)")
        self.headers = {"Accept":"*/*", "Accept-Language":"zh-CN", "":"", 
                        "User-Agent":"Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1)", 
                        #"Accept-Encoding":"gzip, deflate", 
                        "Connection":"Keep-Alive"}
 
    def parse(self, url):
        # http://www.flvcd.com/parse.php?format=&kw=
        self.url = "http://www.flvcd.com/parse.php?format=&kw=" + str(url)
        req = urllib2.Request(url=self.url, headers=self.headers)
        #res = urllib2.urlopen(self.url)
        res = urllib2.urlopen(req)
        data = res.read()
        #print "data:", data
        re_res = self.pattern.findall(data)
        if re_res:
            #print("地址解析成功")
            return re_res
        else:
            print("地址找不到")
            return -1
 
if __name__ == "__main__":
    flvcd = YouToFlvcd("youku")
    print flvcd.parse(sys.argv[1])

