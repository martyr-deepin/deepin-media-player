#! /usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (C) 2013 Deepin, Inc.
#               2013 Hailong Qiu
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
############################################
from media_player import MediaPlayer       #
import gtk                                 #
import dbus                                #
import dbus.service                        #
import dbus.mainloop.glib                  #
from media_service import SomeObject       #
############################################
# Linux Deepin Media Player version v 3.0  #
############################################
gtk.gdk.threads_init()#         线程初始化.#
app = MediaPlayer()                        #
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
session_bus = dbus.SessionBus()            #
name = dbus.service.BusName("org.mpris.MediaPlayer2.SampleService" + app.dbus_id, session_bus)
app_ser = SomeObject(session_bus, "/org/mpris/MediaPlayer2")
app_ser.set_dmp(app)                  #
gtk.main()                                 #
############################################
# The core code reference Gmtk code.       #
############################################
