# coding:utf-8

from mplayer import *
import threading

gtk.gdk.threads_init()

class Test(object):
    def __init__(self):
        self.win = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.preview_scrot_bool = False
        self.thread_id = None
        self.win.add_events(gtk.gdk.ALL_EVENTS_MASK)
        self.win.connect("destroy", self.quit)        
        self.win.connect("motion-notify-event", self.motion_notify_scrot)
        self.win.show_all()
        
    def quit(self, widget):    
        self.preview_scrot_bool = False
        gtk.main_quit()
        
    def motion_notify_scrot(self, widget, event):    

        self.mp = Mplayer()
        self.mp.path = "/home/long/视频/1.rmvb"
        self.mp.next()
        self.mp.state = 1
        self.preview_scrot_bool = True
        self.thread_id = thread_id = threading.Thread(target = self.scrot_thread, args = (int(event.x),))
        self.thread_id.start()
            
                    
    def scrot_thread(self, pos):                
        for i in range(1, 50, 5):
            if not self.preview_scrot_bool:                
                break
            
            self.mp.preview_scrot(str(i), "/tmp/preview/" + str(i) + ".jpeg")
            
                                    
Test()        
gtk.gdk.threads_enter()
gtk.main()
gtk.gdk.threads_leave()


