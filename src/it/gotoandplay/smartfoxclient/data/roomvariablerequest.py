# -*- coding:utf-8 -*-
'''
Created on 2010-11-16

@author: leenjewel
'''

class RoomVariableRequest(dict):
    
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
    
    def isPrivate(self):
        if self.get("isPrivate", False) is False or int(self.get("isPrivate")) == 0:
            return "0"
        return "1"
    
    def setPrivate(self, isPrivate):
        self["isPrivate"] = isPrivate
        return
    
    def isPersistent(self):
        if self.get("isPersistent", False) is False or int(self.get("isPersistent")) == 0:
            return "0"
        return "1"
    
    def setPersistent(self, isPersistent):
        self["isPersistent"] = isPersistent
        return
    
    def getType(self):
        return self["type"]
    
    def setType(self, t):
        self["type"] = t
        return
    
    def getValue(self):
        return self.get("value")
    
    def setValue(self, value):
        self["value"] = value
        return