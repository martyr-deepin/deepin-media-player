#coding:utf-8


import os
import sys


clear_fromat = [".pyc"]

class Clear(object):
    def __init__(self):
        if len(sys.argv) >= 2: 
            path_name = sys.argv[1] 
            self.scan_dir(path_name)

    def scan_dir(self, path_name):
            if os.path.exists(path_name):
                for file in os.listdir(path_name):
                    path = os.path.join(path_name, file)
                    if os.path.exists(path):
                        if os.path.isfile(path):
                            if os.path.splitext(path)[1] in clear_fromat or os.path.splitext(path)[1][-1:] == "~":
                                print "删除多余文件", path
                                os.remove(path)
                        elif os.path.isdir(path):
                            self.scan_dir(path)


if __name__ == "__main__":
    clear = Clear()
