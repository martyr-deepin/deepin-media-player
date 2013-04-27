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

# 优酷播放地址不变，变的是转换的地址.
# 当要播放的时候才进行转换.

youku_root = {'电视剧'  : 'http://tv.youku.com/',         
              '电影'    : 'http://movie.youku.com/',   
              '综艺'    : 'http://zy.youku.com/', 
              '音乐'    : 'http://music.youku.com/',    
              '动漫'    : 'http://comic.youku.com/'
             }


# 综艺列表.
zy_dict = {
        "最新更新" : "http://zy.youku.com/new/index",
        "最多播放" : "http://zy.youku.com/hot/index",
        "大陆" : "http://zy.youku.com/dalu/index",
        "港台" : "http://www.youku.com/v_olist/c_85_a_%E5%8F%B0%E6%B9%BE_s__g__r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html",
        "韩国" : "http://zy.youku.com/korean/index",
        "美国" : "http://www.youku.com/v_olist/c_85_a_%E7%BE%8E%E5%9B%BD_s__g__r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html",
        "专题" : "http://zy.youku.com/zhuanti/index" 
        }

# 音乐列表.
music_dict = {
        "新歌首播" : "http://music.youku.com/new/index",
        "华语" : "http://music.youku.com/cpop",
        "欧美" : "http://music.youku.com/eapop",
        "日韩" : "http://music.youku.com/jkpop",
        "热播" : "http://music.youku.com/hot",
        "明星" : "http://music.youku.com/starnew/index2",
        "音乐牛人" : "http://music.youku.com/niuren/index"
        }

# 动漫列表.
comic_dict = {
        "热播中" : "http://comic.youku.com/rebo/index",
        "新收录" : "http://comic.youku.com/new/index",
        "国产精品" : "http://comic.youku.com/guochan/index",
        "日韩动漫" : "http://comic.youku.com/rihan/index",
        "欧美动画" : "http://comic.youku.com/oumei/index",
        "亲子益智" : "http://comic.youku.com/qinzi",
        }
# 动漫按类型的列表.
v_olist_dict = {
        "热血" : "http://www.youku.com/v_olist/c_100_a__s__g_%E7%83%AD%E8%A1%80_r__lg__im__st__mt__tg__d_1_et_0_fv_0_fl__fc__fe__o_7_p_",
        "格斗" : "http://www.youku.com/v_olist/c_100_a__s__g_%E6%A0%BC%E6%96%97_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html",
        "恋爱" : "http://www.youku.com/v_olist/c_100_a__s__g_%E6%81%8B%E7%88%B1_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html",
        "美少女" : "http://www.youku.com/v_olist/c_100_a__s__g_%E7%BE%8E%E5%B0%91%E5%A5%B3_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html",
        "校园" : "http://www.youku.com/v_olist/c_100_a__s__g_%E6%A0%A1%E5%9B%AD_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html",
        "搞笑" : "http://www.youku.com/v_olist/c_100_a__s__g_%E6%90%9E%E7%AC%91_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html",
        "LOLI" : "http://www.youku.com/v_olist/c_100_a__s__g_LOLI_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html",
        "神魔" : "http://www.youku.com/v_olist/c_100_a__s__g_%E7%A5%9E%E9%AD%94_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html",
        "机战" : "http://www.youku.com/v_olist/c_100_a__s__g_%E6%9C%BA%E6%88%98_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html",
        "科幻" : "http://www.youku.com/v_olist/c_100_a__s__g_%E7%A7%91%E5%B9%BB_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html",
        "真人" : "http://www.youku.com/v_olist/c_100_a__s__g_%E7%9C%9F%E4%BA%BA_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html",
        "青春" : "http://www.youku.com/v_olist/c_100_a__s__g_%E9%9D%92%E6%98%A5_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html",
        "魔法" : "http://www.youku.com/v_olist/c_100_a__s__g_%E9%AD%94%E6%B3%95_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html",
        "神话" : "http://www.youku.com/v_olist/c_100_a__s__g_%E7%A5%9E%E8%AF%9D_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html",
        "冒险" : "http://www.youku.com/v_olist/c_100_a__s__g_%E5%86%92%E9%99%A9_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html",
        "运动" : "http://www.youku.com/v_olist/c_100_a__s__g_%E8%BF%90%E5%8A%A8_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html",
        "竞技" : "http://www.youku.com/v_olist/c_100_a__s__g_%E7%AB%9E%E6%8A%80_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html",
        "童话" : "http://www.youku.com/v_olist/c_100_a__s__g_%E7%AB%A5%E8%AF%9D_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html",
        "亲子" : "http://www.youku.com/v_olist/c_100_a__s__g_%E4%BA%B2%E5%AD%90_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html",
        "教育" : "http://www.youku.com/v_olist/c_100_a__s__g_%E6%95%99%E8%82%B2_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html",
        "励志" : "http://www.youku.com/v_olist/c_100_a__s__g_%E5%8A%B1%E5%BF%97_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html",
        "剧情" : "http://www.youku.com/v_olist/c_100_a__s__g_%E5%89%A7%E6%83%85_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html",
        "社会" : "http://www.youku.com/v_olist/c_100_a__s__g_%E7%A4%BE%E4%BC%9A_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html",
        "历史" : "http://www.youku.com/v_olist/c_100_a__s__g_%E5%8E%86%E5%8F%B2_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html",
        "战争" : "http://www.youku.com/v_olist/c_100_a__s__g_%E6%88%98%E4%BA%89_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"
        }
'''
===============================
[*] http://tv.youku.com/  电视剧
[*][*] 
===============================
[*] http://movie.youku.com/ 电影
[*][*] 
===============================
[*] http://zy.youku.com/ 综艺
[*][*] 
===============================
[*] http://music.youku.com/ 音乐
[*][*] http://music.youku.com/new/index 新歌首播
[*][*] http://music.youku.com/cpop 华语
===============================
[*] http://comic.youku.com/ 动漫
[*][*] http://comic.youku.com/rebo/index 热播中
[*][*] http://comic.youku.com/new/index  新收录
[*][*] http://comic.youku.com/guochan/index 国产精品
[*][*] http://comic.youku.com/rihan/index 日韩动漫
[*][*] http://comic.youku.com/oumei/index 欧美动画
[*][*] http://comic.youku.com/qinzi 亲子益智
================================
'''



        
        
