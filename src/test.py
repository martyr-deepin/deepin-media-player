#coding:utf-8

from skin import app_theme
from video_format_conv.transmageddon import TransmageddonUI
from video_information.gui import VideoInformGui
import gtk

if __name__ == "__main__":        
    # def btn_clicked(widget):
    #     path = "/home/long/视频/fsdjflksdfj附近的色拉夫家死掉了分第三集哭了夫家死掉了分第三集看了夫123.rmvb"
    #     video_inform_gui = VideoInformGui(path)
    #     video_inform_gui.show_window()
                
    # win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    # btn = gtk.Button("ok")
    # #
    # # win.
    # #
    # win.set_size_request(300, 300)
    # #
    # # btn.
    # #
    # btn.connect("clicked", btn_clicked)
    # #
    # win.add(btn)
    # win.show_all()
    hwg = TransmageddonUI(["/home/howl/123.rmvb"])
    gtk.main()
