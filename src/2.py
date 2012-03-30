# coding:utf-8

from dtk.ui.draw import *
from mplayer import *
import gtk
import os

from subprocess import *

class Test(object):
    def __init__(self):
        self.i = 0
        self.win = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.win.set_title("影音测试")
        self.win.connect("destroy", gtk.main_quit)
        self.win.add_events(gtk.gdk.ALL_EVENTS_MASK)
        # signal.
        self.win.connect("motion-notify-event", self.motion_notify_event)
        self.win.connect("leave-notify-event", self.leave_notify_event)
        self.pv = PreView()
        self.win.show_all()
        
    def motion_notify_event(self, widget, event):
        self.pv.move_preview(event.x_root, event.y_root - 65)
        
        CMD = "mplaye -ss 50 -noframedrop -nosound -vo png -frames 1 /home/long/视频/1.rmvb"
        
        p = Popen(CMD, 
                  stdin=PIPE,
                  stdout=PIPE,
                  shell=False)
        self.pv.pv.queue_draw()
        
        
    def leave_notify_event(self, widget, event):        
        pass
        #self.pv.quit_preview()
        
class PreView(object):
    def __init__(self):
        self.mp = None        
        
        self.pv = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.pv.set_keep_above(True)
        self.pv.set_size_request(124, 60)
        #设置窗口属性.
        self.pv.set_decorated(False)
        self.pv.add_events(gtk.gdk.ALL_EVENTS_MASK)
        
        self.pv.connect("expose-event", self.draw_background)
        self.pv.show_all()
        
    def draw_background(self, widget, event):    
        cr = widget.window.cairo_create()
        rect = widget.allocation
        print "************************"
        x, y, w, h = rect.x, rect.y, rect.width, rect.height
        pixbuf = gtk.gdk.pixbuf_new_from_file("00000001.png")
        
        image = pixbuf.scale_simple(w, h , gtk.gdk.INTERP_BILINEAR)
        draw_pixbuf(cr, image, x, y)
        
        
        return True
    
    def move_preview(self, x, y):    
        self.pv.move(int(x), int(y))
        
    def show_preview(self):    
        self.pv.show_all()
               
    def quit_preview(self):    
        self.pv.destroy()



        
Test()        
#pv = PreView()        
#pv.show_preview()
gtk.main()
