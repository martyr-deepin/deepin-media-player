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

from unicode_to_ascii import UnicodeToAscii

class Sort(object):
    def __init__(self):
        self.uta = UnicodeToAscii()        
        
        self.save_tree_list = []        
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
            self.index = self.uta.unicoe_to_index(list_str, 0).lower()
            if self.uta.number_bool(self.index): # 数字
                self.c_point = self.num_tree
                self.node_cmp()                
            elif self.uta.en_bool(self.index):  # 英文
                self.c_point = self.en_tree
                self.node_cmp() # 递归检索
            elif self.uta.unicode_bool(self.index): # 判断中文字符              
                self.c_point = self.cn_tree
                self.node_cmp()

                
    def node_cmp(self): 
        # 检查 has_list 是否为空.
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
                insert_i = self.str_cmp(self.c_point)    
                self.c_point.has_list[self.index].insert(insert_i, self.list_str)
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
    
    def mid_tree(self, node):        
        self.save_tree_list = []
        self.mid_tree_2(node)        
        return self.save_tree_list
    
    def mid_tree_2(self, node):    
        '''中序遍历'''
        if node.has_list:
            if node.child_2[0]:
                self.mid_tree_2(node.child_2[0])
            key = node.has_list.keys()[0]    
            self.save_tree_list.append(node.has_list[key])
            if node.child_2[1]:
                self.mid_tree_2(node.child_2[1])
                                        
        
    def str_cmp(self, c_point):
        '''对比字符(str1, str2).'''
        insert_i = 0
        break_bool = False
        for has_list_str in c_point.has_list[self.index]:
            break_bool = cmp(self.list_str.lower(), has_list_str.lower())
            
            if -1 == break_bool: # str2 > str1
                break
            insert_i += 1
            
        return insert_i
        
        
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
    test_en_list = ["gbcdefg", "gvdeas", "gdfdsf", "gafdsf", "gdjfkd",                    
                    "fcjsdkfj", "wodkf", "fjdke", "adfjeickmfk", "fjdskeidk"]
    
    sort.name_sort(test_en_list)
    sort.c_point = sort.en_tree
    print "!@@@@@@@@@@@@@@@@@@@@@@@@2"
    print sort.mid_tree(sort.en_tree)
    # print sort.save_tree_list    
    # print "~!~!~!~!~!~!~!~!~!~!~!~"
    # # sort.mid_tree(sort.cn_tree)    
    # print "@@#@#@#@#@#@#@#!@#@#@#@#"
    # sort.mid_tree(sort.num_tree)
    
        

        
