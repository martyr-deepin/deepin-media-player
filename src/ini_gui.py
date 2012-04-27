import gtk
from ini import *

class IniGui(object):
    def __init__ (self):
        self.ini = INI(os.path.expanduser("~") + "/.config/deepin-media-player/config.ini")        
        self.ini.connect("Send-Error", self.error_messagebox)        
        self.ini.start()
        
        self.ini_gui_win = gtk.Window(gtk.WINDOW_TOPLEVEL)        
        self.ini_gui_win.add_events(gtk.gdk.ALL_EVENTS_MASK)
        self.ini_gui_win.connect("destroy", gtk.main_quit)
        self.ini_gui_win.show_all()
                        
        
    def error_messagebox(self, INI, STRING):    
        print INI.ini_path
        print STRING
        
        
if __name__ == "__main__":        
    IniGui()    
    gtk.main()
