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

# 平衡二叉树 + 散列表

from unicode_to_ascii import UnicodeToAscii


class Sort(object):
    def __init__(self):
        self.uta = UnicodeToAscii()        
        
        self.en_tree = Tree() # 英文树
        self.cn_tree = Tree() # 中文树
        self.num_tree = Tree() # 数字树
        
        self.index = ""
        self.list_str = ""
        
        self.name_tree = [self.en_tree, 
                          self.cn_tree, 
                          self.num_tree] # 名称树 root.
        
        self.type_tree = Tree() # 类型树 root.
                
        self.e_point = self.name_tree[0] # 指向 英文当前的节点.
        self.c_point = self.name_tree[1] # 指向 中文当前的节点.                        
        
        
    def name_sort(self, name_list):     

        for list_str in name_list:
            self.list_str = list_str
            self.index = self.uta.unicoe_to_index(list_str, 0)
            
            if self.uta.number_bool(self.index): # 数字
                print "数字"
            elif self.uta.en_bool(self.index):  # 英文
                self.c_point = self.en_tree
                self.node_cmp() # 递归检索
            elif self.uta.unicode_bool(self.index): # 判断中文字符                
                print "中国字符"

                
    def node_cmp(self): 
        # 坚持 has_list 是否为空.
        if {} == self.c_point.has_list:
            self.c_point.has_list[self.index] = []
            self.c_point.has_list[self.index].append(self.list_str)                           
            return True
        
        # 检查是否有这个 has_list 的 键值.
        elif self.c_point.has_list.has_key(self.index): # 如果有这个键值            
            # 检查 has_list 对应的 键值 里面的 列表是否为空.
            if [] == self.c_point.has_list[self.index]:
                self.c_point.has_list[self.index].append(self.list_str)
            else: # 如果 has_list 对应的 键值 不为空.进行排序.                        
                for has_list_i in self.c_point.has_list[self.index]:
                    insert_i = self.str_cmp(self.list_str ,has_list_i)
                    # 如果大于就加入到后面.
                    if insert_i:
                        self.c_point.has_list[self.index].insert(insert_i, self.list_str) 
                        break                                                                    
            return True
        else: #如果没有对应的键值             
            if self.index > self.c_point.has_list.keys()[0]: # 右边
                if [] == self.c_point.child_2[1]:                    
                    self.c_point.child_2[1] = Tree()

                self.c_point = self.c_point.child_2[1]            
                self.node_cmp()          
                return True
            
            # elif index < self.c_point.has_list.keys()[0]: # 左边
            else:
                if [] == self.c_point.child_2[0]:
                    self.c_point.child_2[0] = Tree()
                    
                self.c_point = self.c_point.child_2[0]
                self.node_cmp()
                return True
                    
        
    def print_sort_tree(self):            
        print self.c_point.has_list
        if self.c_point.child_2[0] != []:
            self.c_point = self.c_point.child_2[0]
            self.print_sort_tree()        

        
        if self.c_point.child_2[1] != []:  
            self.c_point = self.c_point.child_2[1]
            self.print_sort_tree()        

            
        
    def str_cmp(self, str1, str2):
        '''对比字符(str1, str2).'''
        str1_num = len(str1)
        str2_num = len(str2)
        
        str1_point_i = 1
        str2_point_j = 1
        
        if str1 == str2:
            return str1_point_i
                
        while str1_point_i != str1_num: # 'qiuhailong' vs 'qiuilong' i > h
            # if str1[str1_point_i] > str2[str2_point_j]:                
            str1_index = self.uta.unicoe_to_index(str1, str1_point_i)
            str2_index = self.uta.unicoe_to_index(str2, str2_point_j)
            if str1_index > str2_index:
                return str1_point_i
            str1_point_i += 1
            str2_point_j += 1                                        
        
        return False
    
    def type_sort(self):
        pass
    
#****************************************************************************
#            Tree 树型结构.
#        
# self.e_point = 当前的树        
#       保存英文平衡树                保存中文平衡树           保存数字平衡树     
# 左：child_2[0] = Tree() , 中：child_2[1] = Tree()  右: child_2[2] = Tree()    
# has_list 保存的是 散列表.       
#****************************************************************************        
class Tree(object):
    def __init__(self):
        self.child_2 = [[],[]] # 左边 小， 右边 大.
        self.has_list = {}
        

if __name__ == "__main__":    
    sort = Sort()
    test_list = ["gbcdefg", 
              "dcdefg", 
              "fdcdefge",
              "gfjdk",                 
              "jzcvdsfe",
              "cvdeas",
              "adfdsf",
              "ydjfkd",
              "idjfkdf",
              "zcjsdkfj"]
    
    sort.name_sort(test_list)
    # sort.c_point.has_list
    sort.c_point = sort.en_tree
    # print sort.c_point.child_2[1].has_list
    # print sort.c_point.child_2[0].child_2[1].has_list
    # print sort.c_point.child_2[1].child_2[0].has_list
    # print sort.c_point.child_2[1].child_2[0].child_2[1]
    # print sort.c_point.child_2[1].child_2[1].has_list
    # print sort.c_point.child_2[1].child_2[1].child_2[1].has_list


    print "########################"
    sort.print_sort_tree()
    
            
            
        

        
