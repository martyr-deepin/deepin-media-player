#!^-^ coding:utf-8 ^-^

class WriteXml(object):
    def __init__(self, brand, info_list):
        # init value.
        self.init_value()        
        self.write_text += self.version
        self.write_text += self.start_device
        for model, width, height in info_list:
            self.write_xml_info_value(model, width, height)
        self.write_text += self.end_device
        self.fd = open("../xml/%s.xml"%(brand), "w")
        self.write_xml()
        self.close_xml()
        
    def init_value(self):
        self.write_text = ""
        self.version = '<?xml version="1.0"?>\n'
        self.start_device = "<device>\n"
        self.end_device = "</device>\n"
        self.start_profile = "\t<profile>\n"
        self.end_profile = "\t</profile>\n"
        self.start_name = "\t\t<name>"
        self.end_name = "</name>\n"
        self.start_width = "\t\t<width>"
        self.end_width = "</width>\n"
        self.start_height = "\t\t<height>"
        self.end_height = "</height>\n"   
        
    def write_xml_info_value(self, model, width, height):
        self.write_text += self.start_profile
        self.write_text += self.start_name
        self.write_text += model
        self.write_text += self.end_name
        self.write_text += self.start_width
        self.write_text += width
        self.write_text += self.end_width
        self.write_text += self.start_height
        self.write_text += height
        self.write_text += self.end_height
        self.write_text += self.end_profile
                
    def close_xml(self):
        self.fd.close()
            
    def write_xml(self):
        self.fd.write(self.write_text)
        
        
        
        
if __name__ == "__main__":            
    WriteXml("nokie", [("N9990", "800", "600"),
                      ("7390", "120", "120"),
                      ("5800", "250", "380")])
    WriteXml("中兴", [("N9990", "800", "600"),
                      ("7390", "120", "120"),
                      ("5800", "250", "380"),
                      ("u880", "120", "380")])                
