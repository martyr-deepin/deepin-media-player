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

import os
import xml.etree.ElementTree

#
class ConvXML(object):
    def __init__(self):
        self.tree = None
    
    def read_xml(self, xml_file):
        if os.path.exists(xml_file):
            self.tree = xml.etree.ElementTree.parse(xml_file)
            
    def get_value(self):       
        if self.tree:
            try:
                for child in self.tree.getroot().getchildren():
                    if child.tag == "make":
                        print "<make>%s</make>" % child.text.strip()
                    elif child.tag == "version":    
                        print "<version>%s</version>" % child.text.strip()
                    elif child.tag == "author":    
                        self.get_child_value(child)
            except Exception, e:
                print "get_value:[Error]", e
                
    def get_child_value(self, secction):            
        for child in secction.getchildren():
            if child.tag == "name":
                pass
            elif child.tag == "email":
                pass
            
