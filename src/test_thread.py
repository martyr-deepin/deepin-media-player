#!/usr/bin/env python
#!coding=utf-8
    
import threading
import time
import gtk
import os
gtk.gdk.threads_init()
event = threading.Event()

def path_dir(path):        
    os.chdir(path)
    
    if os.path.isdir(path):
        for i in os.listdir(path):
            new_path = path + "/" + i
            if os.path.isdir(new_path):
                #考虑是否一个目录开启一个线程
                path_thread = threading.Thread(target=path_dir, args=(new_path,))
                path_thread.start()
                path_dir(new_path)
                
            if os.path.isfile(new_path):    
                print new_path
                
                
                gtk.gdk.threads_enter()
                text.set_text(new_path)
                gtk.gdk.threads_leave()
        
                
def func():
    path_dir("/home/long/音乐")
    
    
def func2():
    for i in range(1, 10000):
        gtk.gdk.threads_enter()
        text2.set_text(str(i))
        gtk.gdk.threads_leave()
        
t1 = threading.Thread(target=func)    
t2 = threading.Thread(target=func2)

def clicked_button(widget):
    t1.start()
def clicked_button2(widget):   
    t2.start()
    
win = gtk.Window(gtk.WINDOW_TOPLEVEL)
win.connect("destroy", gtk.main_quit)
vbox = gtk.VBox()
btn = gtk.Button("start")
btn2 = gtk.Button("start2")
text = gtk.Label()
text2 = gtk.Label()
btn.connect("clicked", clicked_button)
btn2.connect("clicked", clicked_button2)
vbox.pack_start(btn)
vbox.pack_start(text)
vbox.pack_start(btn2)
vbox.pack_start(text2)
win.add(vbox)
win.show_all()

gtk.gdk.threads_enter()
gtk.main()
gtk.gdk.threads_leave()

    
