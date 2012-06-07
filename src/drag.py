#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 Deepin, Inc.
#               2012 Hailong Qiu
#
# Author:     Hailong Qiu <356752238@qq.com>
# Maintainer: Hailong Qiu <356752238@qq.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import pygtk
import gtk
import os
import urllib
from utils import path_threads

pygtk.require('2.0')


def drag_motion(wid, context, x, y, time):
    context.drag_status(gtk.gdk.ACTION_COPY, time)
    return True

def drag_drop(wid, context, x, y, time):
    wid.drag_get_data(context, context.targets[-1], time)
    return True

def drag_data_received(wid, context, x, y, data, info, time, mp, play_list, widget_bool):    
    if data.get_uris():
        if widget_bool:            
            mp.clearPlayList() # clear mplayer play list.    
        
    for f in data.get_uris():
        path = urllib.unquote(f)[7:]
        # print path
        # Add Dir.
        if os.path.isdir(path):            
            path_threads(path, mp)

        # Add .Dmp.    
        if mp.findDmp(path):
            mp.loadPlayList(path)
            
        # Add play file.    
        if os.path.isfile(path):    
            mp.addPlayFile(path)

    context.finish(True, False, time)    
    return True

def drag_connect(wid, mp, play_list, widget_bool):    
    targets = [("text/media-player", gtk.TARGET_SAME_APP, 1),
               ("text/uri-list", 0, 0),
               ("text/plain", 0, 3)]
    
    wid.drag_dest_set(gtk.DEST_DEFAULT_MOTION | gtk.DEST_DEFAULT_DROP, targets, gtk.gdk.ACTION_COPY)
    
    wid.connect('drag_motion', drag_motion)
    wid.connect('drag_drop', drag_drop)
    wid.connect('drag_data_received', drag_data_received, mp, play_list, widget_bool)    
    
def click_get_playlist(widget, event, mp):    
    print mp.playList
    
from mplayer import Mplayer    
if __name__ == "__main__":    
    mp = Mplayer()
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    win.connect("destroy", gtk.main_quit)        
    drag_connect(win, mp)
    win.connect("button-press-event", click_get_playlist, mp)
    win.show_all()
    gtk.main()
