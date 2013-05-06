#! /usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (C) 2013 Deepin, Inc.
#               2013 Hailong Qiu
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


def cmp_char(c1, c2):
    '''比较字符'''
    if c1 == c2:
        return 0
    elif c1 > c2:
        # c1 大于 c2, 返回 1.
        return 1
    else: # c1 小于 c2, 返回 -1.
        return -1

def cmp_string(str1, str2):
    '''比较字符串'''
    if len(str1) == len(str2):
        # str1 > str2
        str1 = str1.decode('utf-8')
        str2 = str2.decode('utf-8')
        for ch1,ch2 in zip(str1, str2):
            value = cmp_char(ch1, ch2) 
            if value == 0:
                continue
            elif value == 1:
                return True
            elif value == -1:
                return False
        return str1 > str2
    elif len(str1) < len(str2):
        # str1 字符串长度小于 str2
        return False
    return True

if __name__ == "__main__":
    list = ["无敌c语言-第52集", 
            "深度影音插件教程-第02集",
            "无敌c语言-第4集",
            "三国演绎-第21集",
            "无敌c语言-第114集",
            "深度影音插件教程-第01集",
            "无敌c语言-第14集",
            "无敌c语言-第24集",
            "三国演绎-第2集",
            "无敌c语言-第43集",
            "无敌c语言-第115集",
            "无敌c语言-第42集",
            "三国演绎-第10集",
            "无敌c语言-第40集",
            "无敌c语言-第117集",
            "无敌c语言-第214集",
            "无敌c语言-第22集",
            "三国演绎-第22集",
            ]
    sum_index = len(list)
    # 冒泡排序.
    for l in range(0, sum_index):
        #print "========================="
        for w in range(l, sum_index):
            #print list[l], list[w], cmp_string(list[l], list[w])
            if list[l] != list[w]:
                if cmp_string(list[l], list[w]):
                    temp_list = list[l]
                    list[l] = list[w]
                    list[w] = temp_list
        #
    print "=======排序完毕[W]:"
    for l in list:
        print l

