# -*- coding:utf-8 -*-
'''
Created on 2010-11-15

@author: leenjewel
'''

class Buddy(object):
    id = None
    name = None
    online = None
    blocked = None
    variables = None
    
    def __init__(self):
        self.variables = {}
        
    def getName(self):
        return self.name
    
    def getId(self):
        return self.id
    
    def setId(self, id):
        self.id = id
        return
    
    def isOnline(self):
        return self.online
    
    def setOnline(self, online):
        self.online = online
        return
    
    def isBlocked(self):
        return self.blocked
    
    def setBlocked(self, blocked):
        self.blocked = blocked
        return
    
    def getVariables(self):
        return self.variables
    
    def setgetVariables(self, variables):
        self.variables = variables
        return