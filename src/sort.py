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

import os

class Sort(object):
    def __init__(self):
        self.uta = UnicodeToAscii()        
        
        # name sort.
        self.save_tree_list = []        
        self.en_tree = Tree() 
        self.cn_tree = Tree() 
        self.num_tree = Tree() 
        
        self.index = ""
        self.list_str = ""
        # root node.
        self.name_tree = [self.en_tree, 
                          self.cn_tree, 
                          self.num_tree]
                        
        self.c_point = self.name_tree[1]
        # type sort.
        self.type_dict = {}
        
        
    def name_sort(self, name_list):     

        for list_str in name_list:
            self.list_str = list_str
            self.index = self.uta.unicoe_to_index(list_str, 0).lower()
            if self.uta.en_bool(self.index): 
                self.c_point = self.en_tree
                self.node_cmp() 
            elif self.uta.unicode_bool(self.index):
                self.c_point = self.cn_tree
                self.node_cmp()
            # if self.uta.number_bool(self.index): 
            else:    
                self.c_point = self.num_tree
                self.node_cmp()                
                
    def node_cmp(self): 
        if {} == self.c_point.has_list:
            self.c_point.has_list[self.index] = []
            self.c_point.has_list[self.index].append(self.list_str)      
            return True
        
        elif self.c_point.has_list.has_key(self.index): 
            if [] == self.c_point.has_list[self.index]:
                self.c_point.has_list[self.index].append(self.list_str)
            else:                         
                insert_i = self.str_cmp(self.c_point)    
                self.c_point.has_list[self.index].insert(insert_i, self.list_str)
            return True
        else:         
            if self.index > self.c_point.has_list.keys()[0]: #Right.
                if [] == self.c_point.child_2[1]:                    
                    self.c_point.child_2[1] = Tree()
                    
                self.c_point = self.c_point.child_2[1]            
                self.node_cmp()          
                return True            
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
        if node.has_list:
            if node.child_2[0]: # Right child Node.no None.
                self.mid_tree_2(node.child_2[0])
            key = node.has_list.keys()[0]    
            self.save_tree_list.append(node.has_list[key])
            if node.child_2[1]: # Left child Node no none.
                self.mid_tree_2(node.child_2[1])
                                        
        
    def str_cmp(self, c_point):
        insert_i = 0
        break_bool = False
        for has_list_str in c_point.has_list[self.index]:
            break_bool = cmp(self.list_str.lower(), has_list_str.lower())
            
            if -1 == break_bool: # str2 > str1
                break
            insert_i += 1
            
        return insert_i
        
    # Type sort.    
    def type_sort(self, type_list):
        for list_str in type_list:
            path , geshi = os.path.splitext(list_str)
            if geshi in self.type_dict.keys():
                self.type_dict[geshi].insert(self.type_cmp(self.type_dict[geshi], list_str), list_str)
            else:    
                self.type_dict[geshi] = []
                self.type_dict[geshi].append(list_str)
                
        temp_list = []        
        for key in self.type_dict: 
            for dict_str in self.type_dict[key]:
                temp_list.append(self.get_player_file_name(dict_str))
                
        return temp_list        
    
    def get_player_file_name(self, pathfile2):     
        file1, file2 = os.path.split(pathfile2)
        return os.path.splitext(file2)[0]

    def type_cmp(self, list_str, str1):        
        insert_i = 0
        for str2 in list_str:
            if str2 == str1:
                break
            elif str1 > str2:
                insert_i += 1
            else:    
                break
        return insert_i    
            
class Tree(object):
    def __init__(self):
        self.child_2 = [[],[]] 
        self.has_list = {}
        

if __name__ == "__main__":    
    sort = Sort()
    test_en_list = ["gbcdefg", "gvdeas", "gdfdsf", "gafdsf", "gdjfkd",
                    "fcjsdkfj", "wodkf", "fjdke", "adfjeickmfk", "fjdskeidk"]
    test_type_list = ["/home/long/1.avi",
                      "/home/long/11.avi",
                      "/home/long/21.avi",
                      "/home/long/31.avi",
                      "/home/long/61.avi",
                      "/home/long/1.rmvb",
                      "/home/long/12.rmvb",
                      "/home/long/212.rmvb",
                      "/home/long/13.rmvb",
                      ]
    print "=========Test: Name sort.========="
    print sort.name_sort(test_en_list)
    print sort.mid_tree(sort.en_tree)    
    print "=========Test: Type sort.========="    
    print sort.type_sort(test_type_list)
    
        
