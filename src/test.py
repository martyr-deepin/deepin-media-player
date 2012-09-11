#coding:utf-8

from video_information.gui import  VideoInformGui, get_video_information
import gtk

if __name__ == "__main__":        
    def btn_clicked(widget):
        video_inform_gui = VideoInformGui()
        video_inform_gui.show_window()
        get_video_information("/home/long/视频/123.rmvb")
        
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    win.set_size_request(300, 300)
    btn = gtk.Button("ok")
    btn.connect("clicked", btn_clicked)
    win.add(btn)
    win.show_all()
    gtk.main()
