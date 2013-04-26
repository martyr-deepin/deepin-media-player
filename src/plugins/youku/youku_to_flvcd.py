#!/usr/bin/python
# -*- coding:utf-8 -*-
import re
import sys
import urllib
import urllib2
import datetime
 
class YouToFlvcd(object):
    def __init__(self):
        self.url = ""
        self.pattern = re.compile(r"<a href *= *\"(http://f\.youku\.com/player/getFlvPath/[^\"]+)")
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
        #print "re_res:", re_res
        if re_res:
            '''
            filename = datetime.datetime.now().strftime("%Y%m%d-%H%M%S.lst")
            fhandle = open("test.lst", "w")
            for url in re_res:
                print "url:", url
                # 注意是\r\n还是\n
                fhandle.write(url + "\n")
            fhandle.close()
            '''
            print("地址解析成功")
            #print re_res
            return re_res
        else:
            print("地址找不到")
            return -1
 
if __name__ == "__main__":
    flvcd = YouToFlvcd()
    flvcd.parse(sys.argv[1])

