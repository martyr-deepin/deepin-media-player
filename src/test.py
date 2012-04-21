# coding:utf-8
import threading
import gtk
import time
import sys


from mplayer import *

gtk.gdk.threads_init()


class Test(object):
    def __init__(self):
        self.thread1_id = None
        self.thread2_id = None
        self.button1_i = 0
        self.button2_i = 0
        
        self.mp = None
        
        self.huchi = True
        self.quit_thread = True
        
        self.win = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.win.connect("destroy", self.quit_window)
        self.win.connect("window-state-event", self.init_media_player)
        self.image = gtk.image_new_from_file("/home/long/.config/deepin-media-player/image/00000001.png")
        self.win.set_size_request(500, 500)
        self.fixed = gtk.Fixed()
        self.button1 = gtk.Button("abcdef")
        self.button2 = gtk.Button("123456")
        self.start_btn = gtk.Button("start")
        self.start_btn.connect("clicked", self.start_thread)
        self.fixed.put(self.start_btn, 10, 10)        
        self.fixed.put(self.button1, 34, 50)
        self.fixed.put(self.button2, 34, 50 + 50)
        self.fixed.put(self.image, 100, 0)
        self.win.add(self.fixed)
        self.win.show_all()
        
        
    def init_media_player(self, widget, event):
        self.mp = Mplayer(widget.window.xid)
        self.mp.path = "/home/long/视频/1.rmvb"
        self.mp.state = 1
        
    def quit_window(self, widget):    
        gtk.main_quit()
        self.quit_thread = False
        self.thread1_id.exit()
        self.thread2_id.exit()
        
    def start_thread(self, widget):
        print "thread init..."
        
        #self.thread1_id = threading.Thread(target = self.thread_move_button1, args=())
        self.thread2_id = threading.Thread(target = self.thread_move_button2, args=())
        #self.thread1_id.start()
        self.thread2_id.start()
        
        print "thread over..."

    def thread_move_button2(self):    
        print "start thread 2..."
        while True:
            if self.huchi:
                # gtk.timeout_add(100, self.jietu_image)                
                self.button2_i = self.button2_i % 1300
                self.mp.scrot(self.button2_i)
                self.button2_i += 1
                
                # self.huchi = False
                self.read_image()
                if not self.quit_window:
                    sys.exit(0)
                
        print "线程2退出"         
        
    def jietu_image(self):    
        self.button2_i = self.button2_i % 1300
        self.mp.scrot(self.button2_i)
        self.button2_i += 1
                
        self.huchi = False
        return False
    
    def read_image(self):
        gtk.gdk.threads_enter()
        self.image.set_from_file("/home/long/.config/deepin-media-player/image/00000001.png")
        self.win.show_all()
        gtk.gdk.threads_leave()
        return False
        
    def thread_move_button1(self):    
        print "start thread 1"
        while True:
            if not self.huchi:
                self.button1_i = self.button1_i % 30
                # gtk.timeout_add(120, self.read_image)
                gtk.gdk.threads_enter()
                self.image.set_from_file("/home/long/.config/deepin-media-player/image/00000001.png")
                self.win.show_all()
                gtk.gdk.threads_leave()

                self.button1_i += 1
                self.huchi = True
                if not self.quit_window:
                    sys.exit(0)
                    
        print "线程1退出"         

    
       
        
               

            
Test()
gtk.gdk.threads_enter()
gtk.main()
gtk.gdk.threads_leave()
