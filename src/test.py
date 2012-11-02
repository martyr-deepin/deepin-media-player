#coding:utf-8

from skin import app_theme
from video_format_conv.transmageddon import TransmageddonUI
from video_information.gui import VideoInformGui
import gtk
import os

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
    test_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "video_format_conv/test.mp3")
    # print 'test_file:', test_file
    hwg = TransmageddonUI([test_file])
    gtk.main()
