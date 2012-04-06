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
import re
import urllib
from utils import *

pygtk.require('2.0')

def drag_motion(wid, context, x, y, time):
    #print "drag_motion:" + ('\n'.join([str(t) for t in context.targets]))
    context.drag_status(gtk.gdk.ACTION_COPY, time)
    return True

def drag_drop(wid, context, x, y, time):
    #print context.targets
    wid.drag_get_data(context, context.targets[-1], time)
    return True

def drag_data_received(wid, context, x, y, data, info, time):
    #print "drag_data_received-1:" + data.get_data_type()
    #print "drag_data_received-2:" + data.target
    #print data.get_uris()
    for f in data.get_uris():
        path = urllib.unquote(f)[7:]
        if os.path.isdir(path):
            print "目录:" + path
        else:
            if os.path.exists(path):
                print "文件:" + path
        
        # if os.path.isdir(path):
    #     print "这是目录"
    # else:
    #     print "不是目录"
    # if data.target in ["text/uri-list", "text/plain", "text/media-player"]:
    #     if data.target == "text/uri-list":
    #         print data.get_uris()
    #     elif data.target == "text/plain":    
    #         if os.path.isdir(data.data):
    #             print "是目录"
    #         if os.path.exists(data.data):
    #             print "是文件"
    #     elif data.target == "text/media-player" and data.data:    
    #         pass # Add play list.

    context.finish(True, False, time)
    return True

def drag_connect(wid):    
    targets = [("text/media-player", gtk.TARGET_SAME_APP, 1),
               ("text/uri-list", 0, 0),
               ("text/plain", 0, 3)]
    
    win.drag_dest_set(gtk.DEST_DEFAULT_ALL, targets, gtk.gdk.ACTION_COPY)
    wid.connect('drag_motion', drag_motion)
    wid.connect('drag_drop', drag_drop)
    wid.connect('drag_data_received', drag_data_received)    
    
if __name__ == "__main__":
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    win.connect("destroy", gtk.main_quit)    
    
    drag_connect(win)
    win.show_all()
    gtk.main()


# drag_begin    
# drag_motion
# drag_data_received
# drag_data_get
# drag_data_delete
# drag_drop
# drag_end

# gtk_drag_dest_set(GtkWidget *widget,
#                   GtkDestDefaults flags,
#                   const GtkTargetEntry *targets,
#                   gint n_targets,
#                   )
