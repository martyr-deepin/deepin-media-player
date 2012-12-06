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

import MySQLdb
import urllib2
import urllib
import chardet
import re
# import threading
from dtk.ui.utils import is_network_connected




MAIN_HTML = "http://www.hakuzy.com/"
SCAN_HTML = "http://www.hakuzy.com/search.asp?searchword="
SCAN_HTML_PAGE = "http://www.hakuzy.com/search.asp?page=%d&searchword=%s&searchtype=-1"
scan_index_dict = {
    "动作片":"/list/?1-%d.html",
    "纪录片":"/list/?2-%d.html", # 完成搜索
    "动漫片":"/list/?3-%d.html",
    "喜剧片":"/list/?4-%d.html",
    "科幻片":"/list/?5-%d.html",
    "爱情片":"/list/?6-%d.html",
    "战争片":"/list/?7-%d.html",
    "恐怖片":"/list/?8-%d.html",
    "综艺其它":"/list/?9-%d.html",
    "剧情片":"/list/?10-%d.html",
    "大陆剧":"/list/?11-%d.html",
    "港台剧":"/list/?12-%d.html",
    "欧美剧":"/list/?13-%d.html",
    "日韩剧":"/list/?14-%d.html", # 完成、
    "音乐":"/list/?15-%d.html",
    "QMV高清":"/list/?16-%d.html",
    }

class QvodInfo(object):
    def __init__(self):
        self.movie_hash = None # 主键
        self.addr  = None  # 跳转地址.
        self.anme  = None  # 影片名称
        self.area  = None  # 地区.
        self.tyep  = None  # 类型.
        self.date  = None  # 上映日期.
        self.image = None  #
        self.qvod_addr = None # qvod 地址

class QvodScan(object):
    def __init__(self):                    
        self.page_num = 0
        self.keyword = ""
                
    def scan(self, scan_keyword):
        read_buffer = self.__open_url_addr(scan_keyword)
        self.keyword = scan_keyword # save keyword.
        #
        if read_buffer:
            ######################################
            string_list = self.__read_buffer_to_code(read_buffer)
            ######################################        
            # get page sum.
            self.__get_scan_page_num(string_list)
            return True
        else:    
            return False
        
    def get_main_index_info(self):
        try:
            conn = MySQLdb.connect(host='localhost',
                                   user='root',
                                   passwd='root',
                                   db='dp_media',
                                   charset='utf8'
                                   )        
            cur = conn.cursor()                        
            # cur.execute("select * from medias")
            
            # for row in cur:
            #     print "=========================="
            #     print "类型:", row[2]
            #     print "地址:", row[3]
            #     print "名称:", row[4]
            #     print "地区:", row[5]                
            #     print "日期:", row[6]
            #     print "qvod地址:", row[7]
            #     print "图片:", row[8]
            
        except MySQLdb.Error, e:
            print "mysql error %d:%s" % (e.args[0], e.args[1])
            
        for key in scan_index_dict.keys():
        # if True:    
            try:
                # key = "纪录片"
                print "key:", key
                scan_index_html = scan_index_dict[key]
                read_buffer = self.__open_url_addr(scan_index_html % (1), None)
                string_list = self.__read_buffer_to_code(read_buffer)
                self.__get_scan_page_num(string_list)
                for index in range(1, self.page_num + 1):             
                    import time
                    time.sleep(5)
                # if True:
                    # index = 2
                    read_buffer = self.__open_url_addr(scan_index_html % (index), None)
                    string_list = self.__read_buffer_to_code(read_buffer)
                
                    for info in self.__scan_get_qvod_info(string_list):
                        #
                        info.qvod_addr,info.image = self.__get_qvod_addr(info.addr)
                        # print "=========================="
                        # print "类型:", info.type
                        # print "地址:", info.addr
                        # print "名称:", info.name
                        # print "地区:", info.area                    
                        # print "日期:", info.date
                        # print "qvod地址:", info.qvod_addr
                        # print "图片地址:", info.image
                        self.__save_to_mysql(cur, conn, info) # save to msyql.
                        print info.name, "save to mysql...", self.page_num, "页", "下载:", index, "页"
            except Exception, e:        
                print "for key in scan_index_dict[error]:", e
                
        self.__close_mysql(cur, conn)
 
    def __get_qvod_addr(self, go_addr):
        # qvod_addr_patter = r"<a>(.+)</a>"
        qvod_addr_patter = r"<a>(.+)[\||</a>]"
        image_patter = 'src="http://(.+)" width'
        read_buffer = self.__open_url_addr(go_addr, None)
        string_list = self.__read_buffer_to_code(read_buffer)
        for line in string_list:
            image_result = self.__scan_findall(image_patter, line)
            if image_result != []:
                temp_image_result = "http://" + image_result[0]
            qvod_addr_result = self.__scan_findall(qvod_addr_patter, line)
            if qvod_addr_result != []:
                if line.endswith("|"):
                    return qvod_addr_result[0] + "|", temp_image_result
                
                result_string = ""
                for result in qvod_addr_result[0].split("checked/> <a>"):
                    qvod_result_find = result[:result.find("</a><!--")]
                    # if qvod_result_find.endswith("|"):
                    # qvod_result_find = qvod_result_find[:-1]
                    result_string += qvod_result_find + ","
                    
                return result_string, temp_image_result
                
    def __save_to_mysql(self, cur, conn, info):
        # print info.qvod_addr
        inser_sql = "insert into medias(name_hash,type,url,name,zone,date,qvod_url,img_url) values('%s','%s','%s','%s','%s','%s','%s','%s')"
        cur.execute(inser_sql % ("None",
                                 info.type,
                                 info.addr,
                                 info.name,
                                 info.area,
                                 info.date,
                                 info.qvod_addr,
                                 "image")
                    )
        conn.commit()
        
    def __close_mysql(self, cur, conn):    
        cur.close()
        conn.close()
        
    def get_qvod_info(self, index):          
        read_buffer = self.__open_url_addr(self.keyword, index)
        string_list = self.__read_buffer_to_code(read_buffer)
        return self.__scan_get_qvod_info(string_list)
        
    def __scan_get_qvod_info(self, string_list):
        qvod_info = QvodInfo()
        qvod_info_list = []
        # patter.
        addr_patter = r'value="<!--影片链接开始代码-->(.+)<!--影片链接结束代码-->'
        name_patter = r'<!--影片名称开始代码-->(.+)<!--影片名称结束代码-->'
        last_name_patter = r'<!--影片副标开始代码-->(.+)<!--影片副标结束代码-->'
        area_patter = r'<!--影片地区开始代码-->(.+)<!--影片地区结束代码-->'
        type_patter = r'<!--影片类型开始代码-->(.+)<!--影片类型结束代码-->'
        date_patter = r'<!--上映日期开始代码-->(.+)<!--上映日期结束代码-->'
        
        line_index = 0
        add_info_bool = [False, False, False, False, False]
        #
        for line in string_list:
            # addr.
            scan_addr_result = self.__scan_findall(addr_patter, line)
            if scan_addr_result != []:
                addr = scan_addr_result[0]          
                # print "addr:", addr
                line_index += 1
                add_info_bool[0] = True
            # name.    
            scan_name_result = self.__scan_findall(name_patter, line)
            if scan_name_result != []:
                name = scan_name_result[0]                                
                line_index += 1
                add_info_bool[1] = True
                # get name ->>last name.    
                scan_last_name_result = self.__scan_findall(last_name_patter, line)    
                if scan_last_name_result != []:
                    last_name = scan_last_name_result[0]
                    name += last_name
                # print "name:", name    
            # area.    
            scan_area_result = self.__scan_findall(area_patter, line)    
            if scan_area_result != []:
                area = scan_area_result[0]
                line_index += 1
                add_info_bool[2] = True
            # type.
            scan_type_result = self.__scan_findall(type_patter, line)    
            if scan_type_result != []:
                type_ = scan_type_result[0]                
                line_index += 1
                add_info_bool[3] = True
            # date.
            scan_date_result = self.__scan_findall(date_patter, line)
            if scan_date_result != []:
                date = scan_date_result[0]                
                line_index += 1
                add_info_bool[4] = True
            # save info.    
            if not (line_index % 5) and self.__add_info_check(add_info_bool):
                # save info to qvod_info.
                qvod_info.addr = addr
                qvod_info.date = date
                qvod_info.type = type_                
                qvod_info.area = area                
                qvod_info.name = name                
                # add to qvod_info_list.
                qvod_info_list.append(qvod_info)
                # print "=========================="
                # print "地址:", qvod_info.addr
                # print "名称:", qvod_info.name
                # print "地区:", qvod_info.area
                # print "类型:", qvod_info.type
                # print "日期:", qvod_info.date                
                # clear flags.
                for add_index in range(0, 5):
                    add_info_bool[add_index] = False 
                # clear qvod_info.    
                qvod_info = QvodInfo()    
                
        return qvod_info_list            
    
    def __add_info_check(self, add_info_bool):
        check_bool = True
        for add_index in range(0, 5):
            check_bool = add_info_bool[add_index]
        return check_bool
    
    def __read_buffer_to_code(self, read_buffer):    
        try: # no gb2312.
            string_list = self.__to_code_utf_8(read_buffer).split("\n")
        except: # gb2312.
            # check gb2312.
            if chardet.detect(read_buffer)['encoding'] in ['GB2312']:
                try:
                    string_list = (read_buffer.decode('gbk').encode('utf-8')).split("\n")
                except:    
                    string_list = read_buffer.decode('gbk', 'ignore').encode('utf-8').split("\n")
        return string_list
                    
    def __open_url_addr(self, scan_keyword, index=1):        
        #
        if index:
            keyword = urllib.quote(self.__to_code_gb2312(scan_keyword))
            scan_html = SCAN_HTML_PAGE % (index, keyword)
        else:    
            scan_html = MAIN_HTML + scan_keyword
            
        if is_network_connected():
            url_open = urllib2.urlopen(scan_html)
            read_buffer = url_open.read()
            return read_buffer
        else:
            return ""
        
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
                # print "%d条记录" % (scan_record_sum)
                break
        #    
        # print "max:", page_max    
        self.__scan_record_sum_to_page_num(scan_record_sum, page_max)
        
    def __scan_record_sum_to_page_num(self, scan_record_sum, page_max):        
        PAGE_MAX = page_max
        if page_max > 0:
            self.page_num = scan_record_sum / PAGE_MAX
            if (scan_record_sum % PAGE_MAX) > 0:
                self.page_num += 1
        #        
        # print "总共有%d页" % (self.page_num)
                
    def __to_code_gb2312(self, keyword):
        return keyword.decode("utf-8").encode("gb2312")
    
    def __to_code_utf_8(self, string):
        return string.decode('gb2312').encode("utf-8")
    
    def __get_movie_name(self, qvod_url):
        url = qvod_url.replace("qvod://", "")
        return url.split("|")[2]

    def __get_hash_str(self, qvod_url):
        url = qvod_url.replace("qvod://", "")
        return url.split("|")[1]
    
if __name__ == "__main__":    
    qvod_scan = QvodScan()
    # qvod_scan.scan("功夫")    
    qvod_scan.get_main_index_info()
    #######################################
    # for info in qvod_scan.get_qvod_info(1):
    #     print "=========================="
    #     print "地址:", info.addr
    #     print "名称:", info.name
    #     print "地区:", info.area
    #     print "类型:", info.type
    #     print "日期:", info.date
    #######################################
    # print "总共有%d页" % (qvod_scan.page_num)
