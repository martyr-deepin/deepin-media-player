# coding:utf-8

import urllib

#进入字幕下载页面
# http://yyets.com/ (链接地址)showsubtitle-2070.html
#下载字幕链接
# http://yyets.com/ (下载链接)?mod=2&ac=download_attachment&id=2070&type=sub
# 下载链接: /?mod=2&ac=download_attachment&id=2070&type=sub
#人人影视

# http://yyets.com/?mod=2&ac=search_result&op=normal&class=subtitle&keyword=%E5%8A%9F%E5%A4%AB%E7%86%8A%E7%8C%AB &search=&page=2

# http://yyets.com/?mod=2&ac=search_result&op=normal&class=subtitle&keyword=%E5%8A%9F%E5%A4%AB%E7%86%8A%E7%8C%AB&search=&page2= (页码)


# main_http = "http://yyets.com/listsubtitle.html"

# HTTP_ADDRES = "http://yyets.com/listsubtitle.html"



import re

class SubTitle(object):
    def __init__(self):
        #用于下载和进入下载页面的.
        self.html_main = "http://yyets.com/"
        #用于搜索下载用的链接地址.[搜索]
        self.html_sourct = "http://yyets.com/?mod=2&ac=search_result&op=normal&class=subtitle&keyword="        
        self.html_page = "&search=&page=" #翻页.
        self.subtitle_num = 0 #搜索的个数.
        self.down_url_dict = {} #保存字幕下载链接的字典类型.
        self.down_url_list = [] #保存搜索到的字符串
        self.file_name = ""
        
        
        
        
    def Find(self, file_name):     
        '''搜索字幕'''
        self.file_name = file_name
        html_search = urllib.urlopen(self.html_sourct + file_name).read()
        fp = open(self.file_name, "w")
        fp.write(html_search)
        fp.close()
                
        self.subtitle_num = self.get_find_subtitle_num() #获取字幕的个数        
        print "测试:获取字幕共:" + str(self.subtitle_num) + "个"
        
        self.get_down_url_address() #得到字幕下载链接地址字符串,并保存在字典类型中.                    

            
    def get_find_subtitle_num(self):    
        '''获取字幕的个数'''
        fp = open(self.file_name, "r")
        str_fp = unicode(fp.read(), "utf-8")
        fp.close()        
        p = re.compile(ur"(共有.+个搜索结果)")
        str_line = p.findall(str_fp)
        p2 = re.compile(ur"(>\d+<)")
        str_num = p2.findall(str_line[0])[0]        
        str_num = str_num.strip("<")
        str_num = str_num.strip(">")
        return int(str_num)
        
    def get_down_url_address(self):
        '''获取字幕下载链接地址字符串'''
        #初始化.
        self.down_url_dict = {}
        self.down_url_list = []
        subtitle_sum = 0
        i = 0
        while subtitle_sum < self.subtitle_num: # 判断是否有下一页
            i += 1
            print "=========第%d次扫描=======" % (i)
            html_search = urllib.urlopen(self.html_sourct + self.file_name + "&search=&page=%d" % (i)).read()
            fp = open(self.file_name, "w")
            fp.write(html_search)
            fp.close()
            
            fp = open(self.file_name, "r")
            str_fp = unicode(fp.read(), "utf-8")
            fp.close()                
            p = re.compile(ur'(<li class="name"><font color.+%s.+</a> <em>  </em></li>)' % (self.file_name.decode('UTF-8')))
            str_line = p.findall(str_fp)                        
            for i_str in str_line: #将各个字幕链接字符串保存进down_url_list.
                self.down_url_list.append(i_str)
            subtitle_sum += len(str_line)
            
        #转成字幕下载dict.    
        # print self.down_url_list
        print "开始转换类型..."
        self.down_list_to_dict()
        
        
    def down_list_to_dict(self):        
        for list_i in self.down_url_list:
            # 获取字幕名字
            p = re.compile(ur'(%s.+</a>)' % (self.file_name.decode('UTF-8')))
            str_line = p.findall(list_i)                                    
            subtitle_pos = str_line[0].index('<')
            subtitle_name = str_line[0][0:subtitle_pos] +  str_line[0][subtitle_pos+7:]
            subtitle_name = subtitle_name[:-4]
            print subtitle_name
            # 获取字幕下载地址.            
            p = re.compile(ur'(<a href=.+html\">)')
            str_line = p.findall(list_i)                                    
            subtitle_down_address = str_line[0][11:]
            subtitle_down_address = subtitle_down_address.strip(">")
            subtitle_down_address = self.html_main + subtitle_down_address.strip('"')
            print subtitle_down_address
            #本地下载
            html_search = unicode(urllib.urlopen(subtitle_down_address).read(), "utf-8")
            p = re.compile(ur'(本地下载.+sub\">)')
            subtitle_down_address = p.findall(html_search)[0][16:].strip(">")
            subtitle_down_address = self.html_main + subtitle_down_address.strip('"')
            print subtitle_down_address            
            
            #保存 字幕名 和 字母下载地址对应.
            self.down_url_dict[subtitle_name] = subtitle_down_address
            #测试
            self.down_url_to_path(self.down_url_dict[subtitle_name], subtitle_name + "rar")
    
    def down_url_to_path(self, down_url, file_path_and_name):
        '''下载文件文件'''
        urllib.urlretrieve(down_url, file_path_and_name)
        
        
        
        
        
if __name__ == "__main__":        
    sub_title = SubTitle()        
    sub_title.Find("黑侠")
    #sub_title.Find("功夫熊猫")
    #sub_title.Find("黑")
    
    
    
        
        
# 要得到搜索结果的个数
# 将各个字幕链接地址保存起来. (有多页,自动进行翻页下载)
# 字典类型. 名字 对应下载地址

