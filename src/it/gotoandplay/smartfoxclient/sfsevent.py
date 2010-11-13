# -*- coding:utf-8 -*-
'''
Created on 2010-11-13

@author: leenjewel
'''

class SFSEvent(object):
    
    onConnected = "onConnected"
    onLogin = "onLogin"
    onLogout = "onLogout"
    onRoomListUpdate = "onRoomListUpdate"
    
    def __init__(self, event_name, params = {}):
        self.event_name = event_name
        self.params = params
    
    @classmethod
    def build_evt(cls, event_name, success, **kwargs):
        kwargs["success"] = success
        if hasattr(cls, event_name):
            return cls(event_name, kwargs)
        return
    
    def getName(self):
        return self.event_name
    
    def getParams(self):
        return self.params