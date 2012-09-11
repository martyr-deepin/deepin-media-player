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

''' [支持视频网站]
优酷网	土豆网	奇艺网	搜狐视频
酷6网	腾讯视频	PPTV	新浪播客
新浪宽频	56网	网易视频	激动网
乐视网	六间房	百度贴吧视频	天翼视讯
PPS	迅雷看看
网络电视台(13)：
中国网络电视台	CCTV	电影网(M1905)	凤凰宽频
江苏网络电视台	北京电视台	广州电视台	湖南卫视
芒果TV	浙江网络电视台	TVS南方电视台	台海宽频
齐鲁网
综合视频网站(25)：
新华网	优米网	时光网	第一视频
中关村在线	TOM视频酷	搜房网	华录坞
播视网	爆米花	琥珀网	偶偶网
CC联播网	中经播客	11688	视友网
艺术中国	知音视频网	MSN直播频道	一一影院
ACFUN	嗶哩嗶哩	看看新闻网	酷米网
淘米视频
教程视频网站(4)：
超星大讲堂	网易公开课	火星视频教育	星火视频教程
游戏视频网站(6)：
17173游戏视频	Replays.Net	星际视频网	太平洋游戏网
爱拍游戏	PLU游戏
音乐MV网站(10)：
音悦台	百度音乐掌门人	巨鲸MV	谷歌音乐
一听音乐	虾米网	巨鲸音乐	SoGua
5721儿歌	酷狗MV
国外视频网站(6)：
YouTube	CollegeHumor	WAT TV	ESL TV
5min	Howcast
'''

import re
import socket
import urllib2
import threading

FLVCD_TO_PLAY_HTML = 'http://www.flvcd.com/parse.php?flag=&format=&kw='
YOUKU_SCAN_HTML = 'http://www.soku.com/search_video/q_'
TUDOU_SCAN_HTML = 'http://www.soku.com/t/nisearch/'
PPAS_SCAN_HTML = ''

class ScanThreads(threading.Thread):
    def __init__(self, threads_queue):
        threading.Thread.__init__(self)
        self.threads_queue = threads_queue
        self.threads_lsit = []
        pass
    
    def run(self):
        pass
    
    def start(self):
        pass
    
    
    
class NetVideoScan(object):
    def __init__(self):
        pass
            
    def scan(self, scan_name, seconds=100):
        return self.scan_threading(scan_name, seconds)
        
    def scan_threading(self, scan_name, seconds):
        # socket.setdefaulttimeout(seconds)
        scan_html = YOUKU_SCAN_HTML + scan_name
        print "scan_html:", scan_html
        # scan_html = "http://www.soku.com/search_video/q_编译原理fdsjfklsjdlkf"
        # scan_html = "http://www.soku.com/t/nisearch/编译原理/"
        scan_html = "http://www.flvcd.com/parse.php?flag=&format=&kw=http%3A%2F%2Fv.pps.tv%2Fplay_32JV2L.html%23from_www&sbt=%BF%AA%CA%BCGO%21"
        headers = {
            "User-Agent":"Opera/9.80 (X11; Linux i686; U; zh-cn) Presto/2.10.289 Version/12.02",
            "Accept": "text/plain"} # 请求头.
        req = urllib2.Request(scan_html, headers=headers)
        url_open = urllib2.urlopen(req)        
        patter_string =  url_open.read()
        # 第一步: 查看搜索到多少个.    
        patter = r'共找到.+个结果'
        findall_return_list = self.scan_findall(patter, patter_string)
        # print findall_return_list
        print patter_string
        if len(findall_return_list) <= 0:
            return False
        else:
            findall_return_list = findall_return_list[0].strip()
            # net_video_sum = int(findall_return_list)
            print "findall_return_list:[视频总数]", findall_return_list
            
        # 第二步: 获取 下一页 信息--->> _orderby_1_page_2 _orderby_1_page_3 _orderby_1_page_?
        return True
    
    def scan_findall(self, patter, patter_string):
        fp = open("123.txt", "w")
        fp.write(patter_string)
        fp.close()
        return re.findall(patter, patter_string)
        
if __name__ == "__main__":
    net_video_scan = NetVideoScan()
    if not net_video_scan.scan("成龙"):
        print "搜索不到"
    else:    
        print "搜索成功"
        
    
    # path_thread_id = threading.Thread(target=self.scan_threading, args=(scan_name, seconds,))
    # path_thread_id.setDaemon(True)
    # path_thread_id.start()
    
