# -*- coding:utf-8 -*-
'''
Created on 2010-11-13

@author: leenjewel
'''

class Room(object):
    id = None
    name = None
    maxUsers = None
    maxSpectators = None
    temp = None
    game = None
    priv = None
    limbo = None
    userCount = None
    specCount = None
    myPlayerIndex = None
    userList = None
    variables = None

    def __init__(self, id, name, maxUsers, maxSpectators, isTemp, isGame, isPrivate, isLimbo, userCount, specCount):
        self.id = int(id)
        self.name = name
        self.maxSpectators = int(maxSpectators)
        self.maxUsers = int(maxUsers)
        self.temp = isTemp
        self.game = isGame
        self.priv = isPrivate
        self.limbo = isLimbo

        self.userCount = int(userCount)
        self.specCount = int(specCount)
        self.userList = {}
        self.variables = {}

    def addUser(self, u, id):
        self.userList[id] = u
        if(self.game and u.isSpectator()):
            self.specCount += 1    
        else:
            self.userCount += 1
        return

    def removeUser(self, id):
        user = self.userList.pop(id)   
        if user:        
            if(self.game and user.isSpectator()):            
                    self.specCount -= 1           
            else:           
                    self.userCount -= 1
        return

    def getUserList(self):
        return self.userList
    

    def setUserList(self, userList):
        self.userList = userList
        return
    
    def getUser(self, userName):
        if self.userList.has_key(userName):
            return self.userList[userName]
        for user in self.userList:
            if user.getName() == userName:
                return user
        return

    def clearUserList(self):   
        self.userList = {}
        self.userCount = 0
        self.specCount = 0
        return

    def getVariable(self, varName):    
        return self.variables.get(varName)

    def getVariables(self):
        return self.variables

    def setVariables(self, vars):
        self.variables = vars
        return

    def clearVariables(self):   
        self.variables = {}
        return

    def getName(self):   
        return self.name

    def getId(self):   
        return self.id

    def isTemp(self):   
        return self.temp

    def isGame(self):
        return self.game

    def isPrivate(self):
        return self.priv
    
    def getUserCount(self):
        return self.userCount
    
    def getSpectatorCount(self):
        return self.specCount
    
    def getMaxUsers(self):
        return self.maxUsers
    
    def getMaxSpectators(self):
        return self.maxSpectators
    
    def setMyPlayerIndex(self, id):
        self.myPlayerIndex = id
        return    


    def getMyPlayerIndex(self):
        return self.myPlayerIndex
    
    def setIsLimbo(self, b):
        self.limbo = b
        return
    
    def isLimbo(self):
        return self.limbo
    
    def setUserCount(self, n):
        self.userCount = n
        return
    
    def setSpectatorCount(self, n):
        self.specCount = n
        return
    
