#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 ~ 2013 Deepin, Inc.
#               2012 ~ 2013 Long Wei
#
# Author:     Long Wei <yilang2007lw@gmail.com>
# Maintainer: Long Wei <yilang2007lw@gmail.com>
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

import dbus
import dbus.service
import dbus.mainloop.glib
import gobject
import os
import subprocess
import traceback
    
def authWithPolicyKit(sender, connection, priv, interactive=1):
    system_bus = dbus.SystemBus()
    obj = system_bus.get_object("org.freedesktop.PolicyKit1", 
                                "/org/freedesktop/PolicyKit1/Authority", 
                                "org.freedesktop.PolicyKit1.Authority")

    policykit = dbus.Interface(obj, "org.freedesktop.PolicyKit1.Authority")

    info = dbus.Interface(connection.get_object('org.freedesktop.DBus',
                                                '/org/freedesktop/DBus/Bus', 
                                                False), 
                          'org.freedesktop.DBus')
    pid = info.GetConnectionUnixProcessID(sender) 

    subject = ('unix-process', 
               { 'pid' : dbus.UInt32(pid, variant_level=1),
                 'start-time' : dbus.UInt64(0),
                 }
               )
    details = { '' : '' }
    flags = dbus.UInt32(interactive)
    cancel_id = ''
    (ok, notused, details) = policykit.CheckAuthorization(subject, priv, details, flags, cancel_id)

    return ok

class MountService(dbus.service.Object):
    
    DBUS_INTERFACE_NAME = "com.linuxdeepin.mountservice"

    def __init__(self, bus = None):
        if bus is None:
            bus = dbus.SystemBus()

        bus_name = dbus.service.BusName(self.DBUS_INTERFACE_NAME, bus = bus)    
        dbus.service.Object.__init__(self, bus_name, "/")

    @dbus.service.method(DBUS_INTERFACE_NAME, in_signature = "ss", out_signature = "b", 
                         sender_keyword = 'sender', connection_keyword = 'conn')    
    def mount_iso(self, iso_path, dest_path, sender = None, conn = None):
        if not authWithPolicyKit(sender, conn, "com.linuxdeepin.mountservice.mountiso"):
            print "not authWithPolicyKit"
            return False

        return self._mount_iso(iso_path, dest_path)

    def _mount_iso(self, iso_path, dest_path):
        # if not os.path.exists(iso_path):
        #     print "iso path %s not exists" % iso_path
        #     return False

        # if not os.path.exists(dest_path):
        #     print "dest path %s not exists" % dest_path
        #     return False
        try:
            command = "mount -o loop -t iso9660 %s %s" % (iso_path, dest_path)
            subprocess.Popen("nohup %s > /dev/null 2>&1" % (command), shell=True)
            return True
        except:
            traceback.print_exc()
            return False

if __name__ == "__main__":
    dbus.mainloop.glib.DBusGMainLoop(set_as_default = True)
    MountService()
    gobject.MainLoop().run()
