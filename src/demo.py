#! coding:utf-8

from progressbar import *

from mplayer import *
from preview import *

class Test(object):
    def __init__ (self):
        self.win = gtk.Window(gtk.WINDOW_TOPLEVEL)
        
        self.pv = PreView("/home/long/视频/123.rmvb", 500)
        self.win.connect("destroy", gtk.main_quit)
        self.pb = ProgressBar()
        self.pb.pb.connect("enter-notify-event", self.show_preview)
        self.pb.pb.connect("leave-notify-event", self.hide_preview)
        
        self.win.add(self.pb.hbox)
        self.win.show_all()
        
    def show_preview(self, widget, event):    
        self.pv.show_preview()
        
    def hide_preview(self, widget, event):    
        self.pv.hide_preview()
        
Test()        
gtk.main()
