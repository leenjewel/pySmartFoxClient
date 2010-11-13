# -*- coding:utf-8 -*-
'''
Created on 2010-11-13

@author: leenjewel
'''

class User(object):
    id = None
    name = None
    variables = None
    isSpec = None
    isMod = None
    pId = None
    
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.variables = {}
        self.isMod = False
        self.isSpec = False
    
    def getId(self):
        return self.id
    
    def getName(self):
        return self.name
    
    def getVariable(self, key):
        return self.variables.get(key)
    
    def getVariables(self):
        return self.variables
    
    def setVariables(self, key, value):
        self.variables[key] = value
        return
    
    def clearVariables(self):
        self.variables = {}
        return
    
    def setIsSpectator(self, is_spect):
        self.isSpec = is_spect
        return
    
    def isSpectator(self):
        return self.isSpec
    
    def setModerator(self, is_mod):
        self.isMod = is_mod
        return
    
    def isModerator(self):
        return self.isMod
    
    def getPlayerId(self):
        return self.pId
    
    def setPlayerId(self, pid):
        self.pId = pid
        return