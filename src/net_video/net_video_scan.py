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


from dtk.ui.utils import is_network_connected
import re
import socket
import urllib2
import urllib
import threading

# Error Code.
ERROR_CODE_NETWORK_CONNECT_LOSE     = -1 # 网络链接失败.
ERROR_CODE_SCAN_LOSE                = -2 # 搜索失败.


FLVCD_TO_PLAY_HTML = 'http://www.flvcd.com/parse.php?flag=&format=&kw='
YOUKU_SCAN_HTML = 'http://www.soku.com/search_video/q_'
# TUDOU_SCAN_HTML = 'http://www.soku.com/t/nisearch/'
# PPAS_SCAN_HTML = ''

class ScanThreads(threading.Thread):
    '''线程池'''    
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
        self.error_code = None
        self.scan_sum = 0
            
    def scan(self, scan_name_key, scan_engine="youku", seconds=100):
        if is_network_connected(): # Test networ connect.
            if scan_engine == "youku":
                return_info = self.scan_youku_function(scan_name_key, seconds)
            return return_info
        else:
            self.error_code = ERROR_CODE_NETWORK_CONNECT_LOSE
            return False
        
    ###################################################################    
    ### youku scan engine.
    def scan_youku_function(self, scan_name_key, seconds):
        try:
            scan_name_key = urllib.quote(scan_name_key)
            scan_html = YOUKU_SCAN_HTML + scan_name_key
            # Open url.
            url_open = urllib2.urlopen(scan_html)
            patter_string =  url_open.read()
            # Get scan sum.
            self.scan_youku_sum(patter_string)
            # Get page url.
            self.scan_page_url(patter_string)
            return True
        except Exception, e:
            print "scan_youku_function[Error]:", e
    
    def scan_youku_sum(self, patter_string):
        patter = r'共找到.+个结果'
        findall_return_list = self.scan_findall(patter, patter_string)
            
        if len(findall_return_list) <= 0:
            self.error_code = ERROR_CODE_SCAN_LOSE
            self.scan_sum   = 0
            return False
        else:
            self.scan_sum = findall_return_list[0].strip()
        
    def scan_page_url(self, patter_string):
        # patter = r"<li class=\"v_link\">.+"
        # findall_return_list = self.scan_findall(patter, patter_string)
        # for i in findall_return_list:
            # print i
        
        # Get url adder.
        # Get image.
        patter = r'<img alt=.+>'
        findall_return_list = self.scan_findall(patter, patter_string)
        image_patter = r'src=\"(.+)\" '
        name_patter = r'alt=\"(.+)\" src='
        i = 0
        for findall_text in findall_return_list:
            scan_image = self.scan_findall(image_patter, findall_text)[0]
            name_image = self.scan_findall(name_patter, findall_text)[0]
            url_image = urllib2.urlopen(scan_image)
            fp = open("/tmp/%s.jpg"%(name_image), "w")
            fp.write(url_image.read())
            fp.close()
            i += 1
            print "name:",  name_image
            print "image:", scan_image
        pass
    
    def scan_findall(self, patter, patter_string):
        # fp = open("123.html", "w")
        # fp.write(patter_string)
        # fp.close()
        return re.findall(patter, patter_string)
        
if __name__ == "__main__":
    net_video_scan = NetVideoScan()
    if not net_video_scan.scan("编译原理"):
        if net_video_scan.error_code == ERROR_CODE_NETWORK_CONNECT_LOSE:
            print "网络链接失败"
        elif net_video_scan.error_code == ERROR_CODE_SCAN_LOSE:    
            print "搜索不到.."
    else:
        print "搜索成功"
            

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
当我写视频播放器的视频,我已经看见我离监狱越来越近了,^_^..哈哈哈..搞起!!爬.
'''
