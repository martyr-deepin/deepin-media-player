#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Hai longqiu.
# 
# Author:     Hai longqiu <qiuhailong@linuxdeepin.com>
# Maintainer: Hai longqiu <qiuhailong@linuxdeepin.com>
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

from skin import app_theme
from dtk.ui.button import Button
import gtk
import gobject

class FileChooserButton(Button):
    __gsignals__ = {
        "changed":(gobject.SIGNAL_RUN_LAST,
                   gobject.TYPE_NONE, (gobject.TYPE_STRING, gobject.TYPE_STRING)),
        }    
    def __init__(self, title="(无文件)"):
        Button.__init__(self, title)
        self.filename = None # conv file name.
        self.uri = None # uri file name.
        self.folder_path = None # dir path.        
        # button connect signal (clicked).
        self.connect("clicked", self.fil_choose_button_clicked)
        
    def set_filename(self, filename):    
        import urllib
        self.uri = "file://" + urllib.quote(filename)
        self.filename = filename
        self.emit("changed", self.filename, self.uri)
        
    def fil_choose_button_clicked(self, widget):    
        '''button clicked event connect function'''
        dialog = gtk.FileChooserDialog("Select Files",
                                       None,
                                       gtk.FILE_CHOOSER_ACTION_OPEN,
                                       (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                        gtk.STOCK_OPEN, gtk.RESPONSE_OK))        
        if self.folder_path:
            dialog.set_current_folder(self.folder_path)
        # dialog = self.dialog
        res = dialog.run()
        if res == gtk.RESPONSE_OK:
            # self.set_label(dialog.get_filename()) # set button label.
            self.filename = dialog.get_filename() # save filename.
            self.uri = dialog.get_uri() # save uri.
            self.emit("changed", self.filename, self.uri)
        dialog.destroy() # destroy select file of dialog window.
        
    def run(self):    
        return self.dialog.run()
    
    def destroy(self):
        self.dialog.destroy()
        
    def set_current_folder(self, folder_path):    
        self.folder_path = folder_path
        
    def get_filename(self):    
        return self.filename
    
    def get_uri(self):
        return self.uri        
    
class Test(object):
    def __init__(self):
        self.win = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.win.connect("destroy", lambda w : gtk.main_quit())
        
        self.FileChoose = FileChooserButton()
        self.get_name_btn = gtk.Button("获取")
        self.get_name_btn.connect("clicked", self.get_name_btn_clicked)
        self.hbox1 = gtk.HBox()
        self.hbox1.pack_start(self.FileChoose, False, False)
        self.hbox1.pack_start(self.get_name_btn, False, False)        
        self.win.add(self.hbox1)
        self.win.show_all()
                       
        
    def get_name_btn_clicked(self, widget):
        print "uri:", self.FileChoose.get_uri()
        print "filename:", self.FileChoose.get_filename()
        
if __name__ == "__main__":
    Test()
    gtk.main()
