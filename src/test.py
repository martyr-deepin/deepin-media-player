#coding:utf-8

from skin import app_theme
from ldmp_script.ldmp import LDMP
import gtk

if __name__ == "__main__":
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    win.connect("destroy", lambda w : gtk.main_quit())
    win.set_size_request(500, 500)
    main_vbox = gtk.VBox()
    ldmp = LDMP() # 脚本运行.    
    win.connect("key-press-event", ldmp.key_press_event)
    ldmp.open("ldmp_script/test.ldmp")
    main_vbox.pack_start(gtk.Entry(), False, False)
    main_vbox.pack_start(ldmp, True, True)
    win.add(main_vbox)
    win.show_all()
    
