#coding:utf-8

import os
import xml.etree.ElementTree

class ReadXml(object):
    def __init__(self, directory):
        self.brand_dict = {}
        # print os.path.exists("/usr/share/deepin-media-player-private/src/xml/")
        if os.path.exists(directory):
            self.__load_directory(directory)
        else:
            print "directory error!!", directory
            
    def __load_directory(self, directory):
        for filename in os.listdir(directory):
            if filename.endswith("xml"):
                self.brand_dict[filename[:-4]] = os.path.join(directory, filename)
                
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
        model_dict = {}
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
