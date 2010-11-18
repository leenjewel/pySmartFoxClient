# -*- coding:utf-8 -*-
'''
Created on 2010-11-8

@author: leenjewel
'''

import time
import json
from it.gotoandplay.utils.xmlsocket import XMLSocket
from it.gotoandplay.utils.xmllib import XMLObj
from it.gotoandplay.smartfoxclient.sfseventdispatcher import SFSEventDispatcher
from it.gotoandplay.smartfoxclient.handlers.syshandler import SysHandler
from it.gotoandplay.smartfoxclient.handlers.exthandler import ExtHandler
from it.gotoandplay.smartfoxclient.sfsevent import SFSEvent
from it.gotoandplay.smartfoxclient.util.sfsobjectserializer import SFSObjectSerializer

class SmartFoxClient(SFSEventDispatcher):
    
    VER = "158"

    MESSAGE_HEADER_SYSTEM = "sys"
    MESSAGE_HEADER_EXTENSION = "xt"

    MSG_XML = "<"
    MSG_JSON = "{"
    MSG_STR = "%"

    MODMSG_TO_USER = "u"
    MODMSG_TO_ROOM = "r"
    MODMSG_TO_ZONE = "z"

    XTMSG_TYPE_XML = "xml"
    XTMSG_TYPE_STR = "str"
    XTMSG_TYPE_JSON = "json"
    
    def __init__(self, debug = False):
        self.debug = debug
        self.initialize()
        self.setupMessageHandlers()
        super(SmartFoxClient, self).__init__()
    
    def initialize(self):
        self.connected = False
        self.changingRoom = False
        self.playerId = 0
        self.activeRoomId = -1
        self.majVersion = "1"
        self.minVersion = "5"
        self.subVersion = "8"
        self.benchStartTime = None
        self.buddyList = []
        self.messageHandlers = {}
        self.roomList = {}
        self.myBuddyVars = {}
    
    def setupMessageHandlers(self):
        self.messageHandlers["sys"] = SysHandler(self)
        self.messageHandlers["xt"] = ExtHandler(self)
        return
    
    def connect(self, server_host, server_port):
        self.socket_client = XMLSocket()
        self.socket_client.addEventListener(self)
        self.socket_client.connect(server_host, server_port)
        return
    
    def setConnected(self, connected):
        self.connected = connected
        return
    
    def print_debug(self, data):
        if self.debug:
            print data
        return
    
    def send(self, header, action, from_room, message = None):
        xml_msg = self.makeXmlHeader(header)
        xml_msg["body"] = None
        xml_msg.body.set_attribute({"action":action, "r":str(from_room)})
        if message:
            xml_msg.body += message
        self.socket_client.sendXMLObj(xml_msg)
        self.print_debug("[Sending] "+xml_msg.to_string())
        return
    
    def handleMessage(self, data):
        charT = data[0]
        if charT == SmartFoxClient.MSG_XML:
            self.xmlReceived(data)
        elif charT == SmartFoxClient.MSG_JSON:
            self.jsonReceived(data)
        elif charT == SmartFoxClient.MSG_STR:
            self.strReceived(data)
        return
    
    def xmlReceived(self, xml_str):
        xml_obj = XMLObj.build_from_str(xml_str)
        header_id = xml_obj.xml_attr.get("t")
        if header_id and self.messageHandlers.has_key(header_id):
            handler = self.messageHandlers[header_id]
            handler.handleMessage(xml_obj)
        return
    
    def jsonReceived(self, json_str):
        try:
            jso = json.loads(json_str)
            handlerId = jso.get("t")
            handler = self.messageHandlers.get(handlerId)
            if handler:
                handler.handleMessage(jso.get("b"), SmartFoxClient.XTMSG_TYPE_JSON)
        except ValueError:
            self.print_debug("Json Value Error")
        return
    
    def strReceived(self, string):
        params = string.split(SmartFoxClient.MSG_STR)
        handlerId = params[0]
        handler = self.messageHandlers.get(handlerId)
        if handler:
            h_params = [p for p in params[1:]]
            handler.handleMessage(h_params, SmartFoxClient.XTMSG_TYPE_STR)
        return
    
    def makeXmlHeader(self, header):
        xml_head = "<msg></msg>"
        xml_msg = XMLObj.build_from_str(xml_head)
        xml_msg.set_attribute({"t":header})
        return xml_msg
    
    def roundTripBench(self):
        self.benchStartTime = time.time()
        self.send(self.MESSAGE_HEADER_SYSTEM, "roundTrip", self.activeRoomId, None)
        return
    
    def getBenchStartTime(self):
        return self.benchStartTime
    
    def getRandomKey(self):
        self.send(self.MESSAGE_HEADER_SYSTEM, "rndK", -1, None)
        return
    
    def getAllRooms(self):
        return self.roomList
    
    def login(self, zone, name, passwd):
        message = "<login z='" + zone + "'><nick><![CDATA[" + name + "]]></nick><pword><![CDATA[" + passwd + "]]></pword></login>"
        self.send(self.MESSAGE_HEADER_SYSTEM, "login", 0, XMLObj.build_from_str(message))
        return
    
    def checkBuddyDuplicates(self, buddyName):
        for buddy in self.buddyList:
            if buddy.name == buddyName:
                return True
        return False
    
    def addBuddy(self, buddyName):
        if buddyName != self.myUserName and self.checkBuddyDuplicates(buddyName) == False:
            self.send(self.MESSAGE_HEADER_SYSTEM, "addB", -1, XMLObj.build_from_str("<n>" + buddyName + "</n>"))
        return
    
    def checkRoomList(self):
        if self.roomList:
            return True
        return False
    
    def autoJoin(self):
        if self.checkRoomList():
            self.send(self.MESSAGE_HEADER_SYSTEM, "autoJoin", self.activeRoomId, None)
        return
    
    def clearBuddyList(self):
        buddyList = []
        self.send(self.MESSAGE_HEADER_SYSTEM, "clearB", -1, None)
        evt = SFSEvent(SFSEvent.onBuddyList, {"list":buddyList})
        self.dispatchEvent(evt)
        return
    
    def checkJoin(self):
        if self.activeRoomId < 0:
            return False
        return True
    
    def getXmlRoomVariable(self, vName, rVar):
        vValue = rVar.get("value")
        vPrivate = rVar.isPrivate()
        vPersistent = rVar.isPersistent()
        vType = rVar.getType()
        t = None
        if vType == "boolean":
            t = "b"
            if vValue == "true" or vValue == "True":
                vValue = True
            else:
                vValue = False
        elif vType == "number":
            t = "n"
        elif vType == "string":
            t = "s"
        elif vType is not None:
            t = "x"
            vValue = ""
        
        if t:
            return "<var n='" + vName + "' t='" + t + "' pr='" + vPrivate + "' pe='" + vPersistent + "'><![CDATA[" + vValue + "]]></var>"
        return ""
    
    def getXmlUserVariable(self, uVars):
        xmlStr = "<vars>"
        for key, uVal in uVars.items():
            val = uVal.getValue()
            uType = uVal.getType()
            t = None
            if uType == "boolean":
                t = "b"
                if val:
                    val = "1"
                else:
                    val = "0"
            elif uType == "number":
                t = "n"
            elif uType == "string":
                t = "s"
            elif val is None:
                t = "x"
                val = ""
            if t:
                xmlStr += "<var n='" + key + "' t='" + t + "'><![CDATA[" + val + "]]></var>"
            xmlStr += "</vars>"
            return xmlStr
    
    def createRoom(self, name, maxUsers, roomProperties, roomId = -1):
        if self.checkRoomList() is False or self.checkJoin() is False:
            return
        try:
            isGame = "0"
            exitCurrentRoom = "1"
            joinAsSpectator = "0"
            if roomProperties.get("isGame", False):
                isGame = "1"
                if roomProperties.get("exitCurrentRoom"):
                    exitCurrentRoom = "1"
                if roomProperties.get("joinAsSpectator"):
                    joinAsSpectator = "1"
            maxSpectators = roomProperties.get("maxSpectators", "0")
            password = roomProperties.get("password","null")
            uCount = "0"
            if roomProperties.get("uCount"):
                uCount = "1"
            extensionName = roomProperties.get("extensionName")
            extensionScript = roomProperties.get("extensionScript")
            xmlMsg = XMLObj.build_from_str("<room></room>")
            xmlMsg.set_attribute({
                "tmp":"1",
                "gam":isGame,
                "spec":maxSpectators,
                "exit":exitCurrentRoom,
                "jas":joinAsSpectator
            })
            xmlMsg += "<name><![CDATA[" + name + "]]></name>"
            xmlMsg += "<pwd><![CDATA[" + password + "]]></pwd>"
            xmlMsg += "<max>" + maxUsers + "</max>"
            xmlMsg += "<uCnt>" + uCount + "</uCnt>"
            if extensionName and extensionScript:
                xmlMsg += "<xt n='" + extensionName
                xmlMsg += "' s='" + extensionScript + "' />"
            vars = roomProperties.get("vars")
            xmlMsg += "<vars></vars>"
            if vars:
                for varName, varValue in vars.items():
                    xmlMsg += self.getXmlRoomVariable(varName, varValue)
            self.send(self.MESSAGE_HEADER_SYSTEM, "createRoom", roomId, xmlMsg)
        except:
            self.print_debug("[Error] createRoom error")
        return
    
    def getBuddyByName(self, buddyName):
        for buddy in self.buddyList:
            if buddy.getName() == buddyName:
                return buddy
        return None
    
    def getBuddyById(self, buddyId):
        for buddy in self.buddyList:
            if buddy.getId() == buddyId:
                return buddy
        return None
    
    def getBuddyRoom(self, buddy):
        if buddy.getId() != -1:
            self.send(self.MESSAGE_HEADER_SYSTEM, "roomB", -1, XMLObj.build_from_str("<b id='" + buddy.getId() + "' />"))
        return
    
    def getRoom(self, roomId):
        if self.checkRoomList():
            return self.roomList.get(roomId)
        return None
    
    def getRoomByName(self, roomName):
        if not self.checkRoomList():
            return
        for room in self.roomList.values():
            if room.getName() == roomName:
                return room
        return
    
    def getRoomList(self):
        self.send(self.MESSAGE_HEADER_SYSTEM, "getRmList", self.activeRoomId, None)
        return
    
    def getActiveRoom(self):
        if self.checkRoomList():
            return self.roomList.get(self.activeRoomId)
        return None
    
    def getVersion(self):
        return ".".join([self.majVersion, self.minVersion, self.subVersion])
    
    def joinRoom(self, newRoom, pword = "", isSpectator = False, dontLeave = False, oldRoom = -1):
        if isinstance(newRoom, basestring):
            nr = self.getRoomByName(newRoom)
            if not nr:
                return
            newRoom = nr.getId()
        if not self.checkRoomList():
            return
        if isSpectator:
            isSpec = 1
        else:
            isSpec = 0
        if self.changingRoom is False:
            if dontLeave:
                leaveCurrRoom = "0"
            else:
                leaveCurrRoom = "1"
            if oldRoom > -1:
                roomToLeave = oldRoom
            else:
                self.activeRoomId
            if self.activeRoomId == -1:
                leaveCurrRoom = "0"
                roomToLeave = -1
            roomXML = XMLObj.build_from_str("<room/>")
            roomXML.set_attribute({
                "id":newRoom,
                "pwd":pword,
                "spec":isSpec,
                "leave":leaveCurrRoom,
                "old":roomToLeave,
            })
            self.send(self.MESSAGE_HEADER_SYSTEM, "joinRoom", self.activeRoomId, roomXML)
            self.changingRoom = True
        return
    
    def leaveRoom(self, roomId):
        if self.checkRoomList() and self.checkJoin():
            self.send(self.MESSAGE_HEADER_SYSTEM, "leaveRoom", roomId, XMLObj.build_from_str("<rm id='" + roomId + "' />"))
        return
    
    def loadBuddyList(self):
        self.send(self.MESSAGE_HEADER_SYSTEM, "loadB", -1, None)
        return
    
    def logout(self):
        self.send(self.MESSAGE_HEADER_SYSTEM, "logout", -1, None)
        return
    
    def removeBuddy(self, buddyName):
        found = False
        for index, buddy in enumerate(self.buddyList):
            if buddy.getName() == buddyName:
                del self.buddyList[index]
                found = True
                break
        if found:
            self.send(self.MESSAGE_HEADER_SYSTEM, "remB",  -1, XMLObj.build_from_str("<n>" + buddyName + "</n>"))
            evt = SFSEvent(SFSEvent.onBuddyList, {"list":self.buddyList})
            self.dispatchEvent(evt)
        return
    
    def sendBuddyPermissionResponse(self, allowBuddy, targetBuddy):
        if allowBuddy:
            msgXML = XMLObj.build_from_str("<n res='g'>" + targetBuddy + "</n>")
        else:
            msgXML = XMLObj.build_from_str("<n res='r'>" + targetBuddy + "</n>")
        self.send(self.MESSAGE_HEADER_SYSTEM, "bPrm", -1, msgXML)
        return
    
    def sendPublicMessage(self, message, roomId = None):
        if roomId is None:
            roomId = self.activeRoomId
        if self.checkRoomList() and self.checkJoin():
            xmlMsg = XMLObj.build_from_str("<txt><![CDATA[" + message + "]]></txt>")
            self.send(self.MESSAGE_HEADER_SYSTEM, "pubMsg", roomId, xmlMsg)
        return
    
    def sendPrivateMessage(self, message, recipientId, roomId = None):
        if roomId is None:
            roomId = self.activeRoomId
        if self.checkRoomList() and self.checkJoin():
            xmlMsg = XMLObj.build_from_str("<txt rcp='" + recipientId + "'><![CDATA[" + message + "]]></txt>")
            self.send(self.MESSAGE_HEADER_SYSTEM, "prvMsg", roomId, xmlMsg)
        return
    
    def sendModeratorMessage(self, message, mtype, id):
        if self.checkRoomList() and self.checkJoin():
            xmlMsg = XMLObj.build_from_str("<txt t='" + mtype + "' id='" + id + "'><![CDATA[" + message + "]]></txt>")
            self.send(self.MESSAGE_HEADER_SYSTEM, "modMsg", self.activeRoomId, xmlMsg)
        return
    
    def sendXtMessage(self, xtName, cmd, paramsObj, roomId = None, sendType = "xml"):
        if roomId is None:
            roomId = self.activeRoomId
        if self.checkRoomList() is False:
            return
        if sendType == "xml":
            xtReq = {}
            xtReq["name"] = xtName
            xtReq["cmd"] = cmd
            xtReq["param"] = paramsObj
            xmlmsg = XMLObj.build_from_str("<![CDATA[" + SFSObjectSerializer.serialize(xtReq) + "]]>")
            self.send(self.MESSAGE_HEADER_EXTENSION, "xtReq", roomId, xmlmsg)
        elif sendType == "json":
            jobj = {}
            jobj["x"] = xtName
            jobj["c"] = cmd
            jobj["r"] = roomId
            jobj["p"] = paramsObj
            self.sendJson(json.dumps({"t":"xt","b":jobj}))
        elif sendType == "str":
            hdr = self.MSG_STR.join(["xt", xtName, cmd, roomId]+paramsObj) + self.MSG_STR
            self.sendString(hdr)
        return
    
    def sendJson(self, jsMessage):
        self.print_debug("[Sending - JSON]: " + jsMessage)
        self.socket_client.send(jsMessage)
        return
    
    def sendString(self, strMessage):
        self.print_debug("[Sending - STR]: " + strMessage)
        self.socket_client.send(strMessage)
        return
    
    def setBuddyBlockStatus(self, buddyName, status):
        b = self.getBuddyByName(buddyName)
        if b:
            if not b.isBlocked == status:
                b.setBlocked(status)
                if status:
                    xmlMsg = XMLObj.build_from_str("<n x='1'>" + buddyName + "</n>")
                else:
                    xmlMsg = XMLObj.build_from_str("<n x='0'>" + buddyName + "</n>")
                self.send(self.MESSAGE_HEADER_SYSTEM, "setB", -1, xmlMsg)
                evt = SFSEvent(SFSEvent.onBuddyListUpdate, {"buddy":b})
                self.dispatchEvent(evt)
        return
    
    def setBuddyVariables(self, varList):
        xmlMsg = XMLObj.build_from_str("<vars></vars>")
        for vName, vValue in varList.items():
            self.myBuddyVars[vName] = vValue
            xmlMsg += "<var n='" + vName + "'><![CDATA[" + vValue + "]]></var>"
        self.send(self.MESSAGE_HEADER_SYSTEM, "setBvars", -1, xmlMsg)
        return
    
    def setRoomVariables(self, vars, roomId = None, setOwnership = True):
        if roomId is None:
            roomId = self.activeRoomId
        if self.checkRoomList() and self.checkJoin():
            if setOwnership:
                xmlMsg = XMLObj.build_from_str("<vars></vars>")
            else:
                xmlMsg = XMLObj.build_from_str("<vars so='0'></vars>")
            for varName, varValue in vars.items():
                xmlMsg += self.getXmlRoomVariable(varName, varValue)
            self.send(self.MESSAGE_HEADER_SYSTEM, "setRvars", roomId, xmlMsg)
        return
    
    def setUserVariables(self, vars, roomId = None):
        if roomId is None:
            roomId = self.activeRoomId
        if self.checkRoomList() and self.checkJoin():
            currRoom = self.getActiveRoom()
            user = currRoom.getUser(self.myUserId)
            user.setVariables(vars)
            xmlMsg = self.getXmlUserVariable(vars)
            self.send(self.MESSAGE_HEADER_SYSTEM, "setUvars", roomId, xmlMsg)
        return
    
    def switchSpectator(self, roomId = None):
        if roomId is None:
            roomId = self.activeRoomId
        if self.checkRoomList() and self.checkJoin():
            self.send(self.MESSAGE_HEADER_SYSTEM, "swSpec", roomId, "")
        return
    
    def switchPlayer(self, roomId = None):
        if roomId is None:
            roomId = self.activeRoomId
        self.send(self.MESSAGE_HEADER_SYSTEM, "swPl", roomId, None)
        return
    
    def onConnection(self):
        self.print_debug("onConnection")
        xml_msg = XMLObj.build_from_str("<ver v='"+self.VER+"'/>")
        self.send(self.MESSAGE_HEADER_SYSTEM, "verChk", -1, xml_msg)
        return
    
    def onDataReceived(self, data):
        self.print_debug("[Received] "+str(data))
        self.handleMessage(data)
        return