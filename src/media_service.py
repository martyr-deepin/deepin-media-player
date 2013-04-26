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

import gobject
import gtk
import dbus
import dbus.service
import dbus.mainloop.glib
from locales import _ # 国际化翻译.

'''
as    : 列表
s     : 字符串
(ss)  : 元组
a{ss} : 字典
'''

#DEEPIN_MEDIA_PLAYER_DBUS_NAME = "com.deepin_media_player.SampleInterface"

(STOPING_STATE, PAUSE_STATE, STARTING_STATE)= range(0, 3)
DEEPIN_MEDIA_DBUS_NAME_PROPERTY = "org.freedesktop.DBus.Properties"
DEEPIN_MEDIA_DBUS_NAME = "org.mpris.MediaPlayer2"
DEEPIN_MEDIA_PLAYER_DBUS_NAME = "org.mpris.MediaPlayer2.Player"

DATA_FORMAT = \
"""<node name="/org/mpris/MediaPlayer2">
    <interface name="org.freedesktop.DBus.Introspectable">
        <method name="Introspect">
            <arg direction="out" name="xml_data" type="s"/>
        </method>
    </interface>
    <interface name="org.freedesktop.DBus.Properties">
        <method name="Get">
            <arg direction="in" name="interface_name" type="s"/>
            <arg direction="in" name="property_name" type="s"/>
            <arg direction="out" name="value" type="v"/>
        </method>
        <method name="GetAll">
            <arg direction="in" name="interface_name" type="s"/>
            <arg direction="out" name="properties" type="a{sv}"/>
        </method>
        <method name="Set">
            <arg direction="in" name="interface_name" type="s"/>
            <arg direction="in" name="property_name" type="s"/>
            <arg direction="in" name="value" type="v"/>
        </method>
        <signal name="PropertiesChanged">
            <arg name="interface_name" type="s"/>
            <arg name="changed_properties" type="a{sv}"/>
            <arg name="invalidated_properties" type="as"/>
        </signal>
    </interface>
    <interface name="org.mpris.MediaPlayer2">
        <method name="Raise"/>
        <method name="Quit"/>
        <annotation name="org.freedesktop.DBus.Property.EmitsChangedSignal" value="false"/>
        <property name="CanQuit" type="b" access="read"/>
        <property name="Fullscreen" type="b" access="readwrite"/>
        <property name="CanSetFullscreen" type="b" access="read"/>
        <property name="CanRaise" type="b" access="read"/>
        <property name="HasTrackList" type="b" access="read"/>
        <property name="Identity" type="s" access="read"/>
        <property name="DesktopEntry" type="s" access="read"/>
        <property name="SupportedUriSchemes" type="as" access="read"/>
        <property name="SupportedMimeTypes" type="as" access="read"/>
    </interface>
    <interface name="org.mpris.MediaPlayer2.Player">
        <method name="Next"/>
        <method name="Previous"/>
        <method name="Pause"/>
        <method name="PlayPause"/>
        <method name="Stop"/>
        <method name="Play"/>
        <method name="Seek">
            <arg direction="in" name="Offset" type="x"/>
        </method>
        <method name="SetPosition">
            <arg direction="in" name="TrackId" type="o"/>
            <arg direction="in" name="Position" type="x"/>
        </method>
        <method name="OpenUri">
            <arg direction="in" name="Uri" type="s"/>
        </method>
        <signal name="Seeked">
            <arg name="Position" type="x"/>
        </signal>
        <property name="PlaybackStatus" type="s" access="read">
            <annotation name="org.freedesktop.DBus.Property.EmitsChangedSignal" value="true"/>
        </property>
        <property name="LoopStatus" type="s" access="readwrite">
            <annotation name="org.freedesktop.DBus.Property.EmitsChangedSignal" value="true"/>
        </property>
        <property name="Rate" type="d" access="readwrite">
            <annotation name="org.freedesktop.DBus.Property.EmitsChangedSignal" value="true"/>
        </property>
        <property name="Shuffle" type="b" access="readwrite">
            <annotation name="org.freedesktop.DBus.Property.EmitsChangedSignal" value="true"/>
        </property>
        <property name="Metadata" type="a{sv}" access="read">
            <annotation name="org.freedesktop.DBus.Property.EmitsChangedSignal" value="true"/>
        </property>
        <property name="Volume" type="d" access="readwrite">
            <annotation name="org.freedesktop.DBus.Property.EmitsChangedSignal" value="false"/>
        </property>
        <property name="Position" type="x" access="read">
            <annotation name="org.freedesktop.DBus.Property.EmitsChangedSignal" value="false"/>
        </property>
        <property name="MinimumRate" type="d" access="read">
            <annotation name="org.freedesktop.DBus.Property.EmitsChangedSignal" value="true"/>
        </property>
        <property name="MaximumRate" type="d" access="read">
            <annotation name="org.freedesktop.DBus.Property.EmitsChangedSignal" value="true"/>
        </property>
        <property name="CanGoNext" type="b" access="read">
            <annotation name="org.freedesktop.DBus.Property.EmitsChangedSignal" value="true"/>
        </property>
        <property name="CanGoPrevious" type="b" access="read">
            <annotation name="org.freedesktop.DBus.Property.EmitsChangedSignal" value="true"/>
        </property>
        <property name="CanPlay" type="b" access="read">
            <annotation name="org.freedesktop.DBus.Property.EmitsChangedSignal" value="true"/>
        </property>
        <property name="CanPause" type="b" access="read">
            <annotation name="org.freedesktop.DBus.Property.EmitsChangedSignal" value="true"/>
        </property>
        <property name="CanSeek" type="b" access="read">
            <annotation name="org.freedesktop.DBus.Property.EmitsChangedSignal" value="true"/>
        </property>
        <property name="CanControl" type="b" access="read">
            <annotation name="org.freedesktop.DBus.Property.EmitsChangedSignal" value="false"/>
        </property>
    </interface>
</node>"""
 

class DemoException(dbus.DBusException):
    _dbus_error_name = 'com.deepin_media_player.DemoException'

class SomeObject(dbus.service.Object):
    properties = {'Identity': _('深度影音'), 'DesktopEntry': 'deepin-media-player'}
    player_properties = {'PlaybackStatus': 'Stopped', 'Volume': 1.0, 'Metadata': {'xesam:title': ""}}
    def __init__(self, bus, path):
        dbus.service.Object.__init__(self, bus, path)

    def set_dmp(self, app):
        self.this  = app
        #
        self.ldmp = self.this.ldmp
        self.play_list = self.this.play_list
        self.list_view = self.this.gui.play_list_view.list_view
        #
        self.ldmp.connect("pause-play",         self.dbus_ldmp_pause_play)
        self.ldmp.connect("volume-play",        self.dbus_ldmp_volume_play)
        self.ldmp.connect("start-media-player", self.dbus_ldmp_start_media_player)
        self.ldmp.connect("end-media-player",   self.dbus_ldmp_end_media_player)

    def dbus_ldmp_pause_play(self, ldmp, check):
        if 0 == check: # 暂停.
            self.player_properties["PlaybackStatus"] = "Paused"
        else:
            self.player_properties["PlaybackStatus"] = "Playing"
        # emit.
        self.emit_changed()

    def dbus_ldmp_volume_play(self, ldmp, value):
        self.player_properties["Volume"] = value / 100.0
        self.emit_changed()

    def dbus_ldmp_start_media_player(self, ldmp):    
        from widget.utils import get_play_file_name
        text = self.list_view.items[self.play_list.get_index()].sub_items[0].text
        print text
        file_name =  text
        #
        self.player_properties["PlaybackStatus"] = "Playing"
        data = {
                "xesam:title":file_name,
                }
        self.player_properties["Metadata"] = data
        self.emit_changed()

    def dbus_ldmp_end_media_player(self, ldmp):
        self.player_properties["PlaybackStatus"] = "Stopped"
        self.player_properties["Metadata"]["xesam:title"] = ""
        self.emit_changed()

    @dbus.service.method("org.freedesktop.DBus.Introspectable")
    def Introspect(self):
        return DATA_FORMAT

    '''play video/audio file.'''
    @dbus.service.method(DEEPIN_MEDIA_PLAYER_DBUS_NAME)
    def PlayPause(self):
        print "play media player file..."
        self.ldmp.pause()
        # 暂停和继续播放的时候.
        if self.ldmp.player.state == PAUSE_STATE:
            self.player_properties["PlaybackStatus"] = "Paused"
        elif self.ldmp.player.state == STARTING_STATE:
            self.player_properties["PlaybackStatus"] = "Playing"
        # emit.
        self.emit_changed()

    @dbus.service.method(DEEPIN_MEDIA_PLAYER_DBUS_NAME)
    def Stop(self):  
        # 停止播放.
        self.ldmp.stop()

    @dbus.service.method(DEEPIN_MEDIA_PLAYER_DBUS_NAME)
    def Next(self):  # next play file.
        # 上一曲.
        self.this.next()

    @dbus.service.method(DEEPIN_MEDIA_PLAYER_DBUS_NAME)
    def Previous(self): # prev play file.
        # 下一曲.
        self.this.prev()

    @dbus.service.method(DEEPIN_MEDIA_DBUS_NAME)
    def Quit(self): # prev play file.
        pass

    @dbus.service.method(DEEPIN_MEDIA_DBUS_NAME)
    def Raise(self): # prev play file.
        pass

    @dbus.service.method(dbus.PROPERTIES_IFACE, #DEEPIN_MEDIA_DBUS_NAME_PROPERTY,
                         in_signature='ss', out_signature='v')
    def Get(self, interface, prop):
        if interface == "org.mpris.MediaPlayer2":
            if prop in self.properties:
                return self.properties[prop]
        elif interface == "org.mpris.MediaPlayer2.Player":
            if prop in self.player_properties:
                return self.player_properties[prop]

    @dbus.service.method(dbus.PROPERTIES_IFACE, #DEEPIN_MEDIA_DBUS_NAME_PROPERTY,
                         in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface):
        self.emit_changed()
        if interface == "org.mpris.MediaPlayer2":
            return self.properties
        elif interface == "org.mpris.MediaPlayer2.Player":
            return self.player_properties

    @dbus.service.method(dbus.PROPERTIES_IFACE, #DEEPIN_MEDIA_DBUS_NAME_PROPERTY,
                         in_signature='ssv', out_signature='')
    def Set(self, interface, prop, value):                                      
        if interface == "org.mpris.MediaPlayer2.Player":
            if prop == "Volume":
                self.player_properties[prop] = value
                self.this.key_set_volume(int(value * 100))

    @dbus.service.signal(dbus.PROPERTIES_IFACE, #DEEPIN_MEDIA_DBUS_NAME_PROPERTY, 
            signature='sa{sv}as')           
    def PropertiesChanged(self, interface, updated, invalid):                   
        pass

    def emit_changed(self):
        self.PropertiesChanged(DEEPIN_MEDIA_PLAYER_DBUS_NAME,
                    self.player_properties, [])

    @dbus.service.signal(DEEPIN_MEDIA_PLAYER_DBUS_NAME, signature='x')
    def Seeked(self, pos):
        pass 
        
    @dbus.service.method(DEEPIN_MEDIA_PLAYER_DBUS_NAME,
                         in_signature='i', out_signature='')
    def fseek(self, value): # prev play file.
        self.ldmp.fseek(value)

    @dbus.service.method(DEEPIN_MEDIA_PLAYER_DBUS_NAME,
                         in_signature='i', out_signature='')
    def bseek(self, value): # prev play file.
        self.ldmp.bseek(value)

    '''
    [in_signature]:
    @: s =>> 网络播放名字.
    @: s =>> 网络播放地址.
    @: s =>> 网络播放的长度.
    @: b =>> 是否播放.
    '''
    @dbus.service.method(DEEPIN_MEDIA_PLAYER_DBUS_NAME,
                         in_signature='sssb', out_signature='')
    def add_net_to_play_list(self, name, play_uri, length, check): 
        # 添加网络地址到播放列表，再的判断是否播放.
        if check:
            self.play_list.set_index(len(self.list_view.items) - 1)
        #
        self.list_view.items.add([str(name), str(length), str(play_uri)])
        #
        if check:
            self.this.next()

    

