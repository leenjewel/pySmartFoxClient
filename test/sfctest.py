# -*- coding:utf-8 -*-
'''
Created on 2010-11-15

@author: leenjewel
'''

import sys, os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__))+"../src")

import md5
from it.gotoandplay.smartfoxclient import SmartFoxClient
from it.gotoandplay.smartfoxclient.sfsevent import SFSEvent

class SFSClient(object):
    _sfs_host = "174.37.230.155"
    _sfs_port = 9449
    _api_url = "http://yuanpeng.haalee.com/"
    _user_id = "1835554439"
    _session_value = "1d34e96f19c4b3b804f7c52ee463a4c8"
    _event_handles = (SFSEvent.onLogin, SFSEvent.onRandomKey, SFSEvent.onExtensionResponse, SFSEvent.onConnection, 
                      SFSEvent.onRoomListUpdate,)
    
    def __init__(self, debug = False):
        self.random_key = None
        self.sfc = SmartFoxClient(debug)
        for event_h in SFSEvent.__dict__.keys():
            if event_h.startswith("on"):
                self.sfc.addEventListener(getattr(SFSEvent, event_h), self)
    
    def run(self):
        self.sfc.connect(self._sfs_host, self._sfs_port)
    
    def handleEvent(self, evt):
        print evt.getName()
        if hasattr(self, evt.getName()):
            func = getattr(self, evt.getName())
            return func(evt)
        return
    
    def onDebugMessage(self, evt):
        print evt
        return
    
    def onConnection(self, evt):
        if not self.random_key:
            self.sfc.getRandomKey()
        return
    
    def onRandomKey(self, evt):
        self.random_key = evt.getParams().get("key")
        hash_key = md5.md5(self.random_key+"23njkcdp9u8").hexdigest()
        passwd = "_".join([hash_key,'1',self._session_value, self._api_url,])
        self.sfc.login('texas', self._user_id, passwd)
        return
    
    def onLogin(self, evt):
        print "onLogin"
        return
    
    def onExtensionResponse(self, evt):
        response_data = evt.getParams()
        params = response_data.get("dataObj")
        _cmd = params.get("_cmd")
        if hasattr(self, _cmd):
            func = getattr(self, _cmd)
            return func(params)
        return
    
    def onRoomListUpdate(self, evt):
        print evt.getParams().get("roomList")
        return
    
    def logOK(self, params):
        try:
            print params.get("err")
        except:
            print "OK"
        return

class TexasClient(SFSClient):
    def __init__(self, debug):
        SFSClient.__init__(self, debug)
    
    def logOK(self, params):
        self.sfc.getRoomList()
        return
    
    def onRoomListUpdate(self, evt):
        self.room_list = evt.getParams().get("roomList")
        print self.room_list

if __name__ == "__main__":
    sfc = TexasClient(True)
    sfc.run()