#!coding:utf-8
import dbus
import sys


if __name__ == "__main__":
    bus = dbus.SessionBus()
    dbus_id = ".U.O.R.Q.M.F"
    try:
        remote_object = bus.get_object(
                            "org.mpris.MediaPlayer2.SampleService" + dbus_id,
                            '/org/mpris/MediaPlayer2')
    except dbus.DbusException:
        sys.exit(1)
        #pass
            
    iface = dbus.Interface(remote_object,
                           "org.mpris.MediaPlayer2.Player")
    #print iface.play("i love c and linux /test/debus.com")
    #iface.play()
    #iface.fseek(5)
    #iface.Stop()
    iface.add_net_to_play_list("不要不要舞蹈", 
                               "http://f.youku.com/player/getFlvPath/sid/00_00/st/flv/fileid/03000201005168D84B94B108BFADF6AA425365-E03B-A77C-205E-F6E1D3C29587?K=2ac91a6a7007490a241160e6",
                               "12:12:12", False)
    iface.add_net_to_play_list("不要不要舞蹈", 
                               "http://f.youku.com/player/getFlvPath/sid/00_00/st/flv/fileid/03000201005168D84B94B108BFADF6AA425365-E03B-A77C-205E-F6E1D3C29587?K=2ac91a6a7007490a241160e6",
                               "12:12:12", False)
    iface.add_net_to_play_list("不要不要舞蹈", 
            "http://f.youku.com/player/getFlvPath/sid/00_00/st/flv/fileid/030002010051351F0A7E30005FE900C08CC6C8-B028-7D49-DD4F-8897E30725A3?K=9be1461fcad4b557261cf6d8",
                               "12:12:12", True)
    #iface.stop()
    #iface.prev()


