# -*- coding:utf-8 -*-
'''
Created on 2010-11-13

@author: leenjewel
'''

class Zone(object):
    roomList = None
    name = None
    
    def __init__(self, name):
        self.name = name
        self.roomList = {}
        
    def getRoom(self, room_id):
        return self.roomList.get(room_id)
    
    def getRoomByName(self, room_name):
        for room in self.roomList.values():
            if room.getName() == room_name:
                return room
        return
