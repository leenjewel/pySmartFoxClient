# -*- coding:utf-8 -*-
'''
Created on 2010-11-13

@author: leenjewel
'''

class SFSEvent(object):
    
    onConnection = "onConnection"
    onLogin = "onLogin"
    onLogout = "onLogout"
    onRoomListUpdate = "onRoomListUpdate"
    onUserCountChange = "onUserCountChange"
    onJoinRoom = "onJoinRoom"
    onJoinRoomError = "onJoinRoomError"
    onUserEnterRoom = "onUserEnterRoom"
    onUserLeaveRoom = "onUserLeaveRoom"
    onPublicMessage = "onPublicMessage"
    onPrivateMessage = "onPrivateMessage"
    onAdminMessage = "onAdminMessage"
    onModeratorMessage = "onModeratorMessage"
    onObjectReceived = "onObjectReceived"
    onRoomVariablesUpdate = "onRoomVariablesUpdate"
    onRoomAdded = "onRoomAdded"
    onRoomDeleted = "onRoomDeleted"
    onRandomKey = "onRandomKey"
    onRoundTripResponse = "onRoundTripResponse"
    onUserVariablesUpdate = "onUserVariablesUpdate"
    onCreateRoomError = "onCreateRoomError"
    onBuddyList = "onBuddyList"
    onBuddyListUpdate = "onBuddyListUpdate"
    onBuddyListError = "onBuddyListError"
    onBuddyRoom = "onBuddyRoom"
    onRoomLeft = "onRoomLeft"
    onSpectatorSwitched = "onSpectatorSwitched"
    onPlayerSwitched = "onPlayerSwitched"
    onBuddyPermissionRequest = "onBuddyPermissionRequest"
    onExtensionResponse = "onExtensionResponse"
    
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