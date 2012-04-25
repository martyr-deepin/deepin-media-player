# coding:utf-8

from mplayer import *
import threading
from progressbar import *

gtk.gdk.threads_init()

class Test(object):
    def __init__(self):
        self.preview_scrot_bool = False
        self.thread_id = None
        
        self.lenght = 5000
        self.max_pos = 0
        self.min_pos = 0
        self.padding_pos = 5
        self.scrot_bool_break = False
        
        self.win = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.image =gtk.image_new_from_file("/tmp/buffer/00000001.png")
        
        self.win.add_events(gtk.gdk.ALL_EVENTS_MASK)
        self.win.connect("destroy", self.quit)        
        self.win.connect("motion-notify-event", self.motion_notify_scrot)
        self.win.connect("window-state-event", self.init_media_player)
        self.win.add(self.image)
        self.win.show_all()

    def init_media_player(self, widget, event):    
        print "初始化截图"
        self.mp = Mplayer()
        self.mp.path = "/home/long/视频/1.rmvb"        
        self.mp.state = 1
        self.preview_scrot_bool = True        
        self.save_scrot_time()                        
        
    def quit(self, widget):    
        self.preview_scrot_bool = False
        gtk.main_quit()
        
    def motion_notify_scrot(self, widget, event):    
        
        if 0 == int(event.x) % 10:
            self.min_pos  = int(event.x)
            
            read_id = gtk.timeout_add(15, self.read_image_time)                                
            
    def read_image_time(self):            
        self.image.set_from_file("/tmp/preview/" + str(self.min_pos) + ".jpeg")
    
    def save_scrot_time(self):    
        self.thread_id = thread_id = threading.Thread(target = self.scrot_thread)
        self.thread_id.start()    
        
    def scrot_thread(self):                                        
        for i in range(0, 5000, 10):            
            if not os.path.exists("/tmp/preview/" + str(i) + ".jpeg"):    
                self.mp.preview_scrot(str(i), "/tmp/preview/" + str(i) + ".jpeg")
            
                                    
Test()        
gtk.gdk.threads_enter()
gtk.main()
gtk.gdk.threads_leave()


