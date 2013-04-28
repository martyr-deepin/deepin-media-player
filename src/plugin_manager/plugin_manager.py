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


import imp
import sys
import os

from widget.utils import get_ldmp_plugin_path, get_user_plugin_path
from widget.utils import get_config_path

'''
name = "插件管理"
author = "hailongqiu@linuxdeepin.com"
run_check = True
version = "1.0"
class_name = "PluginManager"
'''

class PluginManager(object):
    def __init__(self, this=None, load_check=True):
        self.__init_plugins_dir()
        if load_check: # 是否加载插件.
            self.__init_values(this)
            # 判断插件是否超过 0 个.
            if not self.__plugin_modules_exist():
                print "没有可用的插件!!"
                #return False
            else:
                # 初始化插件管理.
                self.__init_manager()
    
    def __init_plugins_dir(self):
        path = get_config_path()
        for dir_ in ["plugins"]:
            path = os.path.join(path, dir_)
            if not os.path.exists(path):
                os.makedirs(path)

    def __init_manager(self):
        self.__insert_sys_paths()
        self.__load_plugins()

    def __init_values(self, this):
        # 插件目录.
        self.__user_path = get_user_plugin_path()
        self.__ldmp_path = get_ldmp_plugin_path()
        self.__dir_list = ["ldmp", "user"]
        self.plugin_dirs = {
                "ldmp" : self.__ldmp_path,
                "user" : self.__user_path,
                }
        self.__this = this
        self.__modules_count = 0 # 统计模块总数.
        #
        self.__reload_modules = {}
        self.__plugin_modules = {}
        #
        self.__faile_modules  = {} # 保存加载失败.
        #
        self.__auto_plugin_modules = {}
        self.__auto_plugin_plugins = {}
        #
        self.__auto_flase_modules = {}
        self.__auto_flase_plugins = {}

    def __plugin_modules_exist(self):
        ldmp_path = self.plugin_dirs["ldmp"]
        self.__ldmp_modules = self.get_plugin_modules(ldmp_path)
        user_path = self.plugin_dirs["user"]
        self.__user_modules = self.get_plugin_modules(user_path)

        return len(self.__ldmp_modules + 
                   self.__user_modules) > 0

    def get_plugin_modules(self, path):
        plugin_files = []
        if os.path.exists(path):
            files = [f[:-3] for f in os.listdir(path) \
                    if self.is_plugin_name_check(f)]
            plugin_files = files
        return plugin_files[:]

    def is_plugin_name_check(self, name):
        # 过滤不属于插件的文件.
        return (name.startswith("plugin_") and
                name.endswith(".py"))

    def __insert_sys_paths(self):
        # sys.path 添加模块路径.
        for key in self.__dir_list:
            if (self.plugin_dirs.has_key(key) and 
                not self.plugin_dirs[key] in sys.path):
                sys_path = self.plugin_dirs[key] 
                sys.path.insert(2, sys_path)

    def __load_plugins(self):
        ###############################
        # @ 加载自带插件模块.
        ldmp_path = self.plugin_dirs["ldmp"]
        for name in self.__ldmp_modules:
            self.load_plugin(name, ldmp_path)
        ###############################
        # @ 加载用户编写插件模块.
        user_path = self.plugin_dirs["user"]
        for name in self.__user_modules:
            # 防止出现重复的模块名.
            if name not in self.__ldmp_modules:
                self.load_plugin(name, user_path)
        ###############################

    def load_plugin(self, name, directory):
        path = os.path.join(directory, name)
        fname = "%s.py" % path
        # 初始化模块.
        module = imp.load_source(name, fname)
        #
        if not hasattr(module, "auto_check"):
            print "插件模块加载失败...模块",\
                  name, "缺少变量auto_check = True"
            self.__faile_modules[name] = module
            return False
        # 保存用于热更新.
        self.__reload_modules[name] = module
        # 保存.
        self.__plugin_modules[name] = module
        #
        module.ldmp_module_name = name
        module.ldmp_module_file_name = fname
        self.__modules_count += 1
        '''
        print "-----------------------"
        print module.ldmp_module_name
        print module.ldmp_module_file_name
        print "-----------------------"
        '''
    def load_auto_flase_plugins(self):
        names = self.__plugin_modules.keys()
        names.sort()
        #
        for name in names:
            self.auto_plugin(name, auto=False)
    
    def load_auto_plugins(self): 
        names = self.__plugin_modules.keys()
        names.sort()
        #
        for name in names:
            self.auto_plugin(name)

    def auto_plugin(self, name, auto=True, open=None):
        module = self.__plugin_modules[name]
        if not (getattr(module, "auto_check") == auto) and open==None: # 不加载的过滤.
            return False
        # 判断是否满足加载的条件.
        if not self.__can_auto_plugin(module):
            # 加入失败中去.
            self.__faile_modules[name] = module
            return False
        # 读取信息.
        version       = getattr(module,   "version")
        class_name    = getattr(module,   "class_name")
        plugin_class  = getattr(module,   class_name)
        plugin_object = None
        # 判断插件是否已经存在(加载..).
        if self.__auto_plugin_plugins.has_key(name):
            plugin_object = self.__auto_plugin_plugins[name]
        else:
            # 无则创建.
            plugin_object = plugin_class(self.__this)
        #
        try:
            if auto:
                plugin_object.start_plugin()
        except Exception, err:
            print "模块:%s中的类:%s调用start_plugin函数错误:%s" % (name, class_name, err)
        #
        plugin_object.ldmp_module = module
        plugin_object.ldmp_name   = class_name
        plugin_object.ldmp_version = version
        # 删除.
        self.__plugin_modules.pop(name)
        if auto:
            # 保存已经加载好的插件.
            self.__auto_plugin_plugins[name] = plugin_object
            self.__auto_plugin_modules[name] = module
        else:
            self.__auto_flase_plugins[name] = plugin_object
            self.__auto_flase_modules[name] = module

    def __can_auto_plugin(self, module):
        # 判断是否满足加载的条件.
        if not hasattr(module, "version"):
            return self.__can_error_msg(module, "version")
        if not hasattr(module, "class_name"):
            return self.__can_error_msg(module, "class_name")
        #
        class_name = getattr(module, "class_name")
        if not hasattr(module, class_name):
            return self.__can_error_msg(module, class_name)
        #
        plugin_class = getattr(module, class_name)
        if not hasattr(plugin_class, "__init__"):
            return self.__can_error_msg(module, "__init__")

        if not hasattr(plugin_class, "start_plugin"):
            return self.__can_error_msg(module, "start_plugin")

        if not hasattr(plugin_class, "stop_plugin"):
            return self.__can_error_msg(module, "stop_plugin")

        return True

    def __can_error_msg(self, module, msg):
        error_msg = "模块:"+ str(module) + "缺少: " + str(msg)
        module.error_msg = error_msg
        print error_msg
        return False

    #########################################
    def close_plugin(self, name):
        # 关闭插件.
        if not self.__auto_plugin_plugins.has_key(name):
            return False
        plugin_object = self.__auto_plugin_plugins[name]
        module = self.__auto_plugin_modules[name]
        plugin_object.stop_plugin()
        self.__plugin_modules[name] = module
        self.auto_plugin(name, auto=False, open=True)
        del self.__auto_plugin_modules[name]
        del self.__auto_plugin_plugins[name]
        #
        self.__modules_count -= 1
        return True

    def open_plugin(self, name):
        # 开启插件.
        if not self.__auto_flase_plugins.has_key(name):
            return False
        #
        module = self.__auto_flase_modules[name] 
        self.__plugin_modules[name] = module
        self.auto_plugin(name)
        #
        del self.__auto_flase_plugins[name] 
        del self.__auto_flase_modules[name] 
        #
        self.__modules_count += 1
        return True

    #@ 热更新 reload(module) =>> 开发插件，调试方便
    def module_reload(self, class_, god_mode=False):
        module_name = class_.__module__
        name_ = module_name
        module = self.__reload_modules[str(name_)]
        # 热更新.
        reload(module)
        class_name       = getattr(module, "class_name")
        plugin_class     = getattr(module, class_name)
        class_.__class__ = plugin_class
        if god_mode:
            '''
            @ 上帝模式，可以任意的更改模块的东西(包括$类中的属性).
              但是，插件的加载和卸载会出现问题，所以只有完全调试
              的时候使用，切忌在正常模式的情况下，不要开启.
            '''
            plugin_object    = plugin_class(self.__this)
            class_.__dict__  = plugin_object.__dict__
    
    def get_plugin_info(self, name):
        # 获取插件信息.
        infos = {}
        #
        auto_check = 1
        #
        if self.__auto_plugin_modules.has_key(name):
            module = self.__auto_plugin_modules[str(name)]
        elif self.__auto_flase_modules.has_key(name):
            module = self.__auto_flase_modules[str(name)]
            auto_check = 0
        elif self.__faile_modules.has_key(name):
            module = self.__faile_modules[name]
            auto_check = -1
        else:
            return None
        # 
        infos["title"]  = getattr(module, "title", "deepin_media_plugin")
        infos["module_name"] = name
        infos["version"] = getattr(module, "version", "") # 获取插件版本.
        infos["author"]  = getattr(module, "author", "hailongqiu 356752238@qq.com") # 获取插件作者.
        infos["auto"]  = auto_check
        infos["error"] = getattr(module, "error_msg", "")
        return infos

if __name__ == "__main__":
    import gtk
    class Test(object):
        def __init__(self):
            self.win = gtk.Window(gtk.WINDOW_TOPLEVEL)
            self.win.connect("destroy", lambda w : gtk.main_quit())
            #
            self.open_btn = gtk.Button("开启插件")
            self.close_btn = gtk.Button("关闭插件")
            self.open_btn.connect("clicked", self.open_btn_clicked)
            self.close_btn.connect("clicked", self.close_btn_clicked)
            self.vbox = gtk.VBox()
            self.vbox.pack_start(self.open_btn, False, False)
            self.vbox.pack_start(self.close_btn, False, False)
            self.win.add(self.vbox)
            #
            self.plugin_man = PluginManager(self)
            self.plugin_man.load_auto_plugins()
            self.plugin_man.load_auto_flase_plugins()
            self.win.show_all()

        def open_btn_clicked(self, widget):
            self.plugin_man.open_plugin("plugin_tudou")
            self.plugin_man.open_plugin("plugin_youku")
            print self.plugin_man.get_plugin_info("plugin_window_layic")
            print self.plugin_man.get_plugin_info("plugin_youku")

        def close_btn_clicked(self, widget):
            self.plugin_man.close_plugin("plugin_youku")
            self.plugin_man.close_plugin("plugin_tudou")
            print self.plugin_man.get_plugin_info("plugin_youku")



    Test()
    gtk.main()
