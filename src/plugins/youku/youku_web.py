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

from collections import OrderedDict
od = OrderedDict
youku_root = od([
('电视剧'  , 'http://tv.youku.com/'),       
('电影'    , 'http://movie.youku.com/'),   
('综艺'   , 'http://zy.youku.com/'), 
('音乐'    , 'http://music.youku.com/'),    
('动漫'    , 'http://comic.youku.com/'),
             ])

# 电视剧类型的列表.
tv_type_dict = od([
("古装", "http://www.youku.com/v_olist/c_97_a__s__g_%E5%8F%A4%E8%A3%85_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("武侠", "http://www.youku.com/v_olist/c_97_a__s__g_%E6%AD%A6%E4%BE%A0_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("警匪", "http://www.youku.com/v_olist/c_97_a__s__g_%E8%AD%A6%E5%8C%AA_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("军事", "http://www.youku.com/v_olist/c_97_a__s__g_%E5%86%9B%E4%BA%8B_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("神话", "http://www.youku.com/v_olist/c_97_a__s__g_%E7%A5%9E%E8%AF%9D_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("科幻", "http://www.youku.com/v_olist/c_97_a__s__g_%E7%A7%91%E5%B9%BB_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("悬疑", "http://www.youku.com/v_olist/c_97_a__s__g_%E6%82%AC%E7%96%91_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("历史", "http://www.youku.com/v_olist/c_97_a__s__g_%E5%8E%86%E5%8F%B2_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("儿童", "http://www.youku.com/v_olist/c_97_a__s__g_%E5%84%BF%E7%AB%A5_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("农村", "http://www.youku.com/v_olist/c_97_a__s__g_%E5%86%9C%E6%9D%91_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("都市", "http://www.youku.com/v_olist/c_97_a__s__g_%E9%83%BD%E5%B8%82_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("家庭", "http://www.youku.com/v_olist/c_97_a__s__g_%E5%AE%B6%E5%BA%AD_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("搞笑", "http://www.youku.com/v_olist/c_97_a__s__g_%E6%90%9E%E7%AC%91_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("偶像", "http://www.youku.com/v_olist/c_97_a__s__g_%E5%81%B6%E5%83%8F_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("言情", "http://www.youku.com/v_olist/c_97_a__s__g_%E8%A8%80%E6%83%85_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("时装", "http://www.youku.com/v_olist/c_97_a__s__g_%E6%97%B6%E8%A3%85_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("优酷出品", "http://www.youku.com/v_olist/c_97_a__s__g_%E4%BC%98%E9%85%B7%E5%87%BA%E5%93%81_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html")
                 ])

# 电影按类型的列表.
movie_type_dict = od([
("武侠", "http://www.youku.com/v_olist/c_96_a__s__g_%E6%AD%A6%E4%BE%A0_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("警匪", "http://www.youku.com/v_olist/c_96_a__s__g_%E8%AD%A6%E5%8C%AA_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("犯罪", "http://www.youku.com/v_olist/c_96_a__s__g_%E7%8A%AF%E7%BD%AA_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("科幻", "http://www.youku.com/v_olist/c_96_a__s__g_%E7%A7%91%E5%B9%BB_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("战争", "http://www.youku.com/v_olist/c_96_a__s__g_%E6%88%98%E4%BA%89_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("恐怖", "http://www.youku.com/v_olist/c_96_a__s__g_%E6%81%90%E6%80%96_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("惊悚", "http://www.youku.com/v_olist/c_96_a__s__g_%E6%83%8A%E6%82%9A_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("纪录片", "http://www.youku.com/v_olist/c_96_a__s__g_%E7%BA%AA%E5%BD%95%E7%89%87_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("西部", "http://www.youku.com/v_olist/c_96_a__s__g_%E8%A5%BF%E9%83%A8_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("戏曲", "http://www.youku.com/v_olist/c_96_a__s__g_%E6%88%8F%E6%9B%B2_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("歌舞", "http://www.youku.com/v_olist/c_96_a__s__g_%E6%AD%8C%E8%88%9E_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("奇幻", "http://www.youku.com/v_olist/c_96_a__s__g_%E5%A5%87%E5%B9%BB_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("冒险", "http://www.youku.com/v_olist/c_96_a__s__g_%E5%86%92%E9%99%A9_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("悬疑", "http://www.youku.com/v_olist/c_96_a__s__g_%E6%82%AC%E7%96%91_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("历史", "http://www.youku.com/v_olist/c_96_a__s__g_%E5%8E%86%E5%8F%B2_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("动作", "http://www.youku.com/v_olist/c_96_a__s__g_%E5%8A%A8%E4%BD%9C_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("传记", "http://www.youku.com/v_olist/c_96_a__s__g_%E4%BC%A0%E8%AE%B0_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("动画", "http://www.youku.com/v_olist/c_96_a__s__g_%E5%8A%A8%E7%94%BB_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("儿童", "http://www.youku.com/v_olist/c_96_a__s__g_%E5%84%BF%E7%AB%A5_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("喜剧", "http://www.youku.com/v_olist/c_96_a__s__g_%E5%96%9C%E5%89%A7_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("爱情", "http://www.youku.com/v_olist/c_96_a__s__g_%E7%88%B1%E6%83%85_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("剧情", "http://www.youku.com/v_olist/c_96_a__s__g_%E5%89%A7%E6%83%85_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("运动", "http://www.youku.com/v_olist/c_96_a__s__g_%E8%BF%90%E5%8A%A8_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("短片", "http://www.youku.com/v_olist/c_96_a__s__g_%E7%9F%AD%E7%89%87_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("优酷出品", "http://www.youku.com/v_olist/c_96_a__s__g_%E4%BC%98%E9%85%B7%E5%87%BA%E5%93%81_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html")
                    ])
                    
# 综艺按类型的列表.
zy_type_dict = od([
('优酷出品', 'http://www.youku.com/v_olist/c_85_a__s__g_%E4%BC%98%E9%85%B7%E5%87%BA%E5%93%81_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html'),
('优酷牛人', 'http://www.youku.com/v_olist/c_85_a__s__g_%E4%BC%98%E9%85%B7%E7%89%9B%E4%BA%BA_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html'),
('脱口秀', 'http://www.youku.com/v_olist/c_85_a__s__g_%E8%84%B1%E5%8F%A3%E7%A7%80_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html'),
('真人秀', 'http://www.youku.com/v_olist/c_85_a__s__g_%E7%9C%9F%E4%BA%BA%E7%A7%80_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html'),
('选秀', 'http://www.youku.com/v_olist/c_85_a__s__g_%E9%80%89%E7%A7%80_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html'),
('美食', 'http://www.youku.com/v_olist/c_85_a__s__g_%E7%BE%8E%E9%A3%9F_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html'),
('旅游', 'http://www.youku.com/v_olist/c_85_a__s__g_%E6%97%85%E6%B8%B8_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html'),
('汽车', 'http://www.youku.com/v_olist/c_85_a__s__g_%E6%B1%BD%E8%BD%A6_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html'),
('访谈', 'http://www.youku.com/v_olist/c_85_a__s__g_%E8%AE%BF%E8%B0%88_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html'),
('纪实', 'http://www.youku.com/v_olist/c_85_a__s__g_%E7%BA%AA%E5%AE%9E_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html'),
('搞笑', 'http://www.youku.com/v_olist/c_85_a__s__g_%E6%90%9E%E7%AC%91_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html'),
('时尚', 'http://www.youku.com/v_olist/c_85_a__s__g_%E6%97%B6%E5%B0%9A_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html'),
('晚会', 'http://www.youku.com/v_olist/c_85_a__s__g_%E6%99%9A%E4%BC%9A_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html'),
('理财', 'http://www.youku.com/v_olist/c_85_a__s__g_%E7%90%86%E8%B4%A2_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html'),
('演唱会', 'http://www.youku.com/v_olist/c_85_a__s__g_%E6%BC%94%E5%94%B1%E4%BC%9A_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html'),
('曲艺', 'http://www.youku.com/v_olist/c_85_a__s__g_%E6%9B%B2%E8%89%BA_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html'),
('益智', 'http://www.youku.com/v_olist/c_85_a__s__g_%E7%9B%8A%E6%99%BA_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html'),
('音乐', 'http://www.youku.com/v_olist/c_85_a__s__g_%E9%9F%B3%E4%B9%90_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html'),
('舞蹈', 'http://www.youku.com/v_olist/c_85_a__s__g_%E8%88%9E%E8%B9%88_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html'),
('体育娱乐', 'http://www.youku.com/v_olist/c_85_a__s__g_%E4%BD%93%E8%82%B2%E5%A8%B1%E4%B9%90_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html'),
('游戏', 'http://www.youku.com/v_olist/c_85_a__s__g_%E6%B8%B8%E6%88%8F_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html'),
('生活', 'http://www.youku.com/v_olist/c_85_a__s__g_%E7%94%9F%E6%B4%BB_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html')
               ])

# 音乐按类型的列表.
music_type_dict = od([
("音乐MV" , "http://www.youku.com/v_olist/c_95_a__s__g__r__lg__im__st__mt_%E9%9F%B3%E4%B9%90MV_d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("现场版" , "http://www.youku.com/v_olist/c_95_a__s__g__r__lg__im__st__mt_%E7%8E%B0%E5%9C%BA%E7%89%88_d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("演唱会" , "http://www.youku.com/v_olist/c_95_a__s__g__r__lg__im__st__mt_%E6%BC%94%E5%94%B1%E4%BC%9A_d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("电影原声" , "http://www.youku.com/v_olist/c_95_a__s__g__r__lg__im__st__mt_%E7%94%B5%E5%BD%B1%E5%8E%9F%E5%A3%B0_d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("电视剧原声" , "http://www.youku.com/v_olist/c_95_a__s__g__r__lg__im__st__mt_%E7%94%B5%E8%A7%86%E5%89%A7%E5%8E%9F%E5%A3%B0_d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("动漫音乐" , "http://www.youku.com/v_olist/c_95_a__s__g__r__lg__im__st__mt_%E5%8A%A8%E6%BC%AB%E9%9F%B3%E4%B9%90_d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("游戏音乐" , "http://www.youku.com/v_olist/c_95_a__s__g__r__lg__im__st__mt_%E6%B8%B8%E6%88%8F%E9%9F%B3%E4%B9%90_d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("广告音乐" , "http://www.youku.com/v_olist/c_95_a__s__g__r__lg__im__st__mt_%E5%B9%BF%E5%91%8A%E9%9F%B3%E4%B9%90_d_1_et_0_fv_0_fl__fc__fe__o_7.html")
             ])

# 动漫按类型的列表.
comic_type_dict = od([
("热血", "http://www.youku.com/v_olist/c_100_a__s__g_%E7%83%AD%E8%A1%80_r__lg__im__st__mt__tg__d_1_et_0_fv_0_fl__fc__fe__o_7_p_"),
("格斗" , "http://www.youku.com/v_olist/c_100_a__s__g_%E6%A0%BC%E6%96%97_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("恋爱" , "http://www.youku.com/v_olist/c_100_a__s__g_%E6%81%8B%E7%88%B1_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("美少女" , "http://www.youku.com/v_olist/c_100_a__s__g_%E7%BE%8E%E5%B0%91%E5%A5%B3_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("校园" , "http://www.youku.com/v_olist/c_100_a__s__g_%E6%A0%A1%E5%9B%AD_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
 ("搞笑" , "http://www.youku.com/v_olist/c_100_a__s__g_%E6%90%9E%E7%AC%91_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
 ("LOLI" , "http://www.youku.com/v_olist/c_100_a__s__g_LOLI_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
 ("神魔" , "http://www.youku.com/v_olist/c_100_a__s__g_%E7%A5%9E%E9%AD%94_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
 ("机战" , "http://www.youku.com/v_olist/c_100_a__s__g_%E6%9C%BA%E6%88%98_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("科幻" , "http://www.youku.com/v_olist/c_100_a__s__g_%E7%A7%91%E5%B9%BB_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("真人" , "http://www.youku.com/v_olist/c_100_a__s__g_%E7%9C%9F%E4%BA%BA_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("青春" , "http://www.youku.com/v_olist/c_100_a__s__g_%E9%9D%92%E6%98%A5_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("魔法" , "http://www.youku.com/v_olist/c_100_a__s__g_%E9%AD%94%E6%B3%95_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("神话" , "http://www.youku.com/v_olist/c_100_a__s__g_%E7%A5%9E%E8%AF%9D_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("冒险" , "http://www.youku.com/v_olist/c_100_a__s__g_%E5%86%92%E9%99%A9_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("运动" , "http://www.youku.com/v_olist/c_100_a__s__g_%E8%BF%90%E5%8A%A8_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("竞技" , "http://www.youku.com/v_olist/c_100_a__s__g_%E7%AB%9E%E6%8A%80_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("童话" , "http://www.youku.com/v_olist/c_100_a__s__g_%E7%AB%A5%E8%AF%9D_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("亲子" , "http://www.youku.com/v_olist/c_100_a__s__g_%E4%BA%B2%E5%AD%90_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("教育" , "http://www.youku.com/v_olist/c_100_a__s__g_%E6%95%99%E8%82%B2_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("励志" , "http://www.youku.com/v_olist/c_100_a__s__g_%E5%8A%B1%E5%BF%97_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("剧情" , "http://www.youku.com/v_olist/c_100_a__s__g_%E5%89%A7%E6%83%85_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("社会" , "http://www.youku.com/v_olist/c_100_a__s__g_%E7%A4%BE%E4%BC%9A_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("历史" , "http://www.youku.com/v_olist/c_100_a__s__g_%E5%8E%86%E5%8F%B2_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html"),
("战争" , "http://www.youku.com/v_olist/c_100_a__s__g_%E6%88%98%E4%BA%89_r__lg__im__st__mt__d_1_et_0_fv_0_fl__fc__fe__o_7.html")
        ])




        
        
