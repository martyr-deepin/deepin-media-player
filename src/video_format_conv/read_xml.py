#coding:utf-8

import os
import xml.etree.ElementTree
import collections

class ReadXml(object):
    def __init__(self, directory):
        # self.brand_dict = {} #         
        self.brand_dict = collections.OrderedDict()
        read_path = directory
        if os.path.exists(read_path):
            self.__load_directory(read_path)
        else:
            print "directory error!!", read_path
            
    def __load_directory(self, directory):
        path_list = os.listdir(directory)
        if path_list != []:
            path_list.sort()
        for filename in path_list: #             
            if filename.endswith("xml"):
                # print "filename:", filename
                self.brand_dict[filename[:-4]] = os.path.join(directory, filename) #
                
    def __load_profile(self, root):
        name = ""
        width = "" 
        height = ""
        
        for child in root.getchildren():
            if child.tag == "name":
                name = child.text.strip()                
            elif child.tag == "width":
                width = child.text.strip()
                # print "width:", width
            elif child.tag == "height":
                height = child.text.strip()
                # print "height:", height
                            
        return (name, width, height)
    
    def load(self, filename):
        tree = xml.etree.ElementTree.parse(filename)
        model_dict = collections.OrderedDict()
        for child in tree.getroot().getchildren():
            if child.tag == "profile":
                name, width, height = self.__load_profile(child)
                model_dict[name] = (width, height)
                                
        return model_dict     
    
if __name__ == "__main__":                
    read_xml = ReadXml("../xml")
    print read_xml.brand_dict["中兴"]
    read_xml.load(read_xml.brand_dict["中兴"])
    read_xml.load(read_xml.brand_dict["诺基亚"])
