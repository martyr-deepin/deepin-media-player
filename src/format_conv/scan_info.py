#coding:utf-8

import urllib
import urllib2
import re
import sys
from write_xml import WriteXml

# gb2312
# HTML_CONNECT = "http://www.sdxgame.com"
HTML_CONNECT = "http://www.3533.com"
# HTML_INFO = "http://www.sdxgame.com/mobilephone.html"
HTML_INFO = "http://www.3533.com/phone/"

class Test(object):
    def __init__(self):
        self.brand_dict = {} # {品牌:链接地址}
        self.model_dict = {} # {型号:链接地址}
        
        url_open = urllib2.urlopen(HTML_INFO)
        patter_string =  url_open.read()
        self.scan_info_connect(patter_string)
        
    def scan_info_connect(self, patter_string):    
        '''搜索品牌的title和html地址'''
        patter_list = patter_string.split("\n")
        index = 0
        while True:            
            try:                
                if patter_list[index] == '<a href="#a1" name="a1"><span>欧美地区</span></a>':
                    self.while_get_info(patter_list, index)
                elif patter_list[index] == '<a href="#a2" name="a2"><span>日韩地区</span></a>':        
                    self.while_get_info(patter_list, index)
                elif patter_list[index] == '<a href="#a3" name="a3"><span>中国·台湾</span></a>':        
                    self.while_get_info(patter_list, index)
                elif patter_list[index] == '<a href="#a4" name="a4"><span>中国·大陆</span></a>':   
                    self.while_get_info(patter_list, index)
                # line number add one.    
                index += 1
            except Exception, e:    
                print "scan_info_connect[error]", e
                break
            
    def while_get_info(self, patter_list, index):            
        while True:
            if patter_list[index] == "</ul>":
                break
            else:
                patter = r'<li><a href=(.+)</a></li>'
                brand_info = self.scan_findall(patter, patter_list[index])
                if brand_info != []:
                    title = self.get_brand_title(brand_info[0])
                    html = self.get_connect_html(brand_info[0])
                    if (title != "") and (html != ""):
                        self.brand_dict[title] = html
            # line number add one.            
            index += 1
                        
        # get brand of model.    
        for title in self.brand_dict.keys():
            html = self.brand_dict[title]
            self.scan_brand_of_model(title, html)
            
    def get_brand_title(self, brand_info):
        patter = r'alt="(.+)"/>'        
        title = self.scan_findall(patter, brand_info)[0]
        return title
                
    def get_connect_html(self, brand_info):
        patter = r'"/(.+)/"'
        html = self.scan_findall(patter, brand_info)[0]
        if html != "":
            return "/" + html + "/"
        return ""

    def scan_brand_of_model(self, title, html):
        '''搜索品牌的所有型号!!'''
        year_list = ["", "2011.htm#t", "2010.htm#t", "2009.htm#t"]
        brand_html = HTML_CONNECT + html 
        self.brand = title
        
        for year in year_list:
            year_brand_html = brand_html.strip() + year
            print "brand_html:", year_brand_html
            url_fd = urllib2.urlopen(year_brand_html.strip())
            patter_string = url_fd.read()
            patter_list = patter_string.split("\n")
            # print patter_list
            index = 0            
            self.title = ""
            self.ratio = ""
            self.title_bool = False
            self.ratio_bool = False
        
            while True:
                try:
                    if patter_list[index].startswith('<dt><a href="'):
                        while True:
                            if patter_list[index].endswith('</li>'):
                                break
                            elif patter_list[index].startswith('<dt><a href="'):
                                self.title = self.get_model_title(patter_list[index])              
                                print "self.title:", self.title
                                if len(self.title):                                
                                    self.title_bool = True
                            elif patter_list[index].endswith('像素'):
                                self.ratio = self.get_model_ratio(patter_list[index])
                                print "self.ratio:", self.ratio
                                if len(self.ratio):
                                    self.ratio_bool = True
                            
                            # save title and ratio.
                            if self.title_bool and self.ratio_bool:
                                self.title_bool = False
                                self.ratio_bool = False
                                self.model_dict[self.title] = self.ratio
                                self.ratio = ""
                                self.title = ""
                                
                            index += 1                        
                        
                    index += 1       
                except Exception, e:    
                    print "scan_brand_of_model[error]:", e
                    break
            
        temp_list = []
        for title in self.model_dict.keys():
            # print "title:", title
            # print "width:", self.model_dict[title][0]
            # print "height:", self.model_dict[title][1]
            temp_list.append((title, 
                              self.model_dict[title][0],
                              self.model_dict[title][1]))
            
        WriteXml(self.brand, temp_list)
        self.model_dict = {}
        
    def get_model_title(self, patter_string):    
        '''得到型号的名字'''
        patter = r'<dt><a href=\"(.+)\" t'
        return self.scan_findall(patter, patter_string)[0].split("/")[2]
        
    def get_model_ratio(self, patter_string):
        '''得到型号的分辨率'''
        if patter_string == "":
            return patter_string
        height_patter = r'(.+)x'
        height = self.scan_findall(height_patter, patter_string[:-6])
        # print "height:", height
        width_patter = r'x(.+)'
        width = self.scan_findall(width_patter, patter_string[:-6])
        # print "width:", width
        return (height[0], width[0])
        # return patter_string[:-6]
    
    def scan_findall(self, patter, patter_string):
        return re.findall(patter, patter_string)
        
if __name__ == "__main__":
    Test()
