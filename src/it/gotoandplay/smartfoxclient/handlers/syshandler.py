# -*- coding:utf-8 -*-
'''
Created on 2010-11-13

@author: leenjewel
'''

import time
from it.gotoandplay.utils.xmllib import XMLObj
from it.gotoandplay.smartfoxclient.sfsevent import SFSEvent
from it.gotoandplay.smartfoxclient.data.buddy import Buddy
from it.gotoandplay.smartfoxclient.data.user import User
from it.gotoandplay.smartfoxclient.data.room import Room

class SysHandler(object):

    def __init__(self, sfc):
        self.sfc = sfc
    
    def populateVariables(self, variables, xml_obj):
        changed_vars = {}
        vars = xml_obj.vars.var
        for v in vars:
            v_name = v.xml_attr.get("n")
            v_type = v.xml_attr.get("t")
            v_value = v.get_cdata()
            if v_type == "x" and variables.has_key(v_name):
                del variables[v_name]
            else:
                changed_vars[v_name] = variables[v_name] = v_value
        return changed_vars

    def handleMessage(self, xml_obj, obj_type = None):
        action = xml_obj.body.xml_attr.get("action")
        if action and hasattr(self, "handle_"+action):
            func = getattr(self, "handle_"+action)
            return func(xml_obj)
        return
    
    def handle_apiOK(self, xml_obj):
        evt = SFSEvent(SFSEvent.onConnection, {"success":True})
        self.sfc.dispatchEvent(evt)
        return
    
    def handle_apiKO(self, xml_obj):
        evt = SFSEvent(SFSEvent.onConnection, {"success":False, "error":"API are obsolete, please upgrade"})
        self.sfc.dispatchEvent(evt)
        return

    def handle_logOK(self, xml_obj):
        uid = xml_obj.body.login.xml_attr.get("id", "-1")
        mod = xml_obj.body.login.xml_attr.get("mod", "0")
        name = xml_obj.body.xml_attr.get("n")
        self.sfc.amIModerator = (int(mod) == 1)
        self.sfc.myUserId = uid
        self.sfc.myUserName = name
        self.sfc.playerId = -1
        evt = SFSEvent.build_evt(SFSEvent.onLogin, True, name = name, error = "")
        self.sfc.dispatchEvent(evt)
        return

    def handle_logKO(self, xml_obj):
        error = xml_obj.body.xml_attr.get("e", "")
        evt = SFSEvent.build_evt(SFSEvent.onLogin, False, error = error)
        self.sfc.dispatchEvent(evt)
        return

    def handle_logout(self, xml_obj):
        self.sfc._logout()
        evt = SFSEvent.build_evt(SFSEvent.onLogout, True)
        self.sfc.dispatchEvent(evt)
        return

    def handle_rmList(self, xml_obj):
        room_list = self.sfc.getAllRooms()
        rooms = xml_obj.body.rmList.rm
        for room in rooms:
            room_id = room.xml_attr.get("id","-1")
            room_name = room.xml_attr.get("n","")
            maxu = room.xml_attr.get("maxu", 0)
            maxs = room.xml_attr.get("maxs",0)
            temp = room.xml_attr.get("temp",0)
            game = room.xml_attr.get("game",0)
            priv = room.xml_attr.get("priv",0)
            lmb = room.xml_attr.get("lmb",0)
            ucnt = room.xml_attr.get("ucnt",0)
            scnt = room.xml_attr.get("scnt",0)
            roomobj = Room(room_id, room_name, maxu, maxs, temp == 1, game == 1, priv == 1, lmb == 1, ucnt, scnt)
            if room.vars and room.vars.var:
                self.populateVariables(room.getVariables(), room)
            old_room = room_list.get(roomobj.getId())
            if old_room:
                roomobj.setVariables(old_room.getVariables())
                roomobj.setUserList(old_room.getUserList())
            room_list[room_id] = roomobj
        evt = SFSEvent(SFSEvent.onRoomListUpdate, {"roomList":room_list})
        self.sfc.dispatchEvent(evt)
        return

    def handle_uCount(self, xml_obj):
        uCount = int(xml_obj.body.xml_attr.get("u", 0))
        sCount = int(xml_obj.body.xml_attr.get("s", 0))
        roomId = int(xml_obj.body.xml_attr.get("r", -1))
        room = self.sfc.getAllRooms().get(roomId)
        if room:
            room.setUserCount(uCount)
            room.setSpectatorCount(sCount)
            evt = SFSEvent(SFSEvent.onUserCountChange, {"room":room})
            self.sfc.dispatchEvent(evt)
        return

    def handle_joinOK(self, xml_obj):
        roomId = int(xml_obj.body.xml_attr.get("r", -1))
        playerId = 0
        if xml_obj.body.pid:
            playerId = int(xml_obj.body.pid.xml_attr.get("id", 0))
        self.sfc.activeRoomId = roomId
        currRoom = self.sfc.getRoom(roomId)
        self.sfc.playerId = playerId
        currRoom.setMyPlayerIndex(playerId)
        if xml_obj.body.vars and xml_obj.body.vars.var:
            currRoom.clearVariables()
            self.populateVariables(currRoom.getVariables(), xml_obj)
        for usr in xml_obj.body.uLs.u:
            name = usr.n.get_data()
            id = int(usr.xml_attr.get("i", -1))
            mod = int(usr.xml_attr.get("m", 0))
            spec = int(usr.xml_attr.get("s", 0))
            isMod = (mod == 1)
            isSpec = (spec == 1)
            pId = int(usr.xml_attr.get("p", -1))
            user = User(id, name)
            user.setModerator(isMod)
            user.setIsSpectator(isSpec)
            user.setPlayerId(pId)
            if usr.vars and usr.vars.var:
                self.populateVariables(user.getVariables(), usr)
            currRoom.addUser(user, id)
        self.sfc.changingRoom = False
        evt = SFSEvent.build_evt(SFSEvent.onJoinRoom, {"room":currRoom})
        self.sfc.dispatchEvent(evt)
        return

    def handle_joinKO(self, xml_obj):
        evt = SFSEvent(SFSEvent.onJoinRoomError, {"error":xml_obj.body.error.xml_attr.get("msg")})
        self.sfc.dispatchEvent(evt)
        return

    def handle_uER(self, xml_obj):
        roomId = int(xml_obj.body.xml_attr.get("r", -1))
        userId = int(xml_obj.body.u.xml_attr.get("i", -1))
        user = xml_obj.body.u
        userName = ""
        if user.n:
            userName = user.n.get_data()
        mod = int(user.xml_attr.get("m", 0))
        spec = int(user.xml_attr.get("s", 0))
        isMod = (mod == 1)
        isSpec = (spec == 1)
        pid = int(user.xml_attr.get("p", -1))
        currRoom = self.sfc.getRoom(roomId)
        newUser = User(userId, userName)
        newUser.setModerator(isMod)
        newUser.setIsSpectator(isSpec)
        newUser.setPlayerId(pid)
        if user.vars and user.vars.var:
            self.populateVariables(newUser.getVariables(), user)
        currRoom.addUser(newUser, userId)
        evt = SFSEvent(SFSEvent.onUserEnterRoom, {"roomId":roomId, "user":newUser})
        self.sfc.dispatchEvent(evt)
        return

    def handle_userGone(self, xml_obj):
        roomId = int(xml_obj.body.xml_attr.get("r", -1))
        user = xml_obj.body.u
        userId = int(user.xml_attr.get("i", -1))
        theRoom = self.sfc.getRoom(roomId)
        uName = theRoom.getUser(userId).getName()
        theRoom.removeUser(userId)
        params = {}
        params["roomId"] = roomId
        params["userId"] = userId
        params["userName"] = uName
        evt = SFSEvent(SFSEvent.onUserLeaveRoom, params)
        self.sfc.dispatchEvent(evt)
        return

    def handle_pubMsg(self, xml_obj):
        body = xml_obj.body
        roomId = int(xml_obj.body.xml_attr.get("r", -1))
        message = body.txt.get_data()
        user = body.user
        userId = int(user.xml_attr.get("id", -1))
        sender = self.sfc.getRoom(roomId).getUser(userId)
        params = {}
        params["roomId"] = roomId
        params["sender"] = sender
        params["message"] = message
        evt = SFSEvent(SFSEvent.onPublicMessage, params)
        self.sfc.dispatchEvent(evt)
        return

    def handle_prvMsg(self, xml_obj):
        body = xml_obj.body
        roomId = int(xml_obj.body.xml_attr.get("r", -1))
        message = body.txt.get_data()
        user = body.user
        userId = int(user.xml_attr.get("id", -1))
        sender = self.sfc.getRoom(roomId).getUser(userId)
        params = {}
        params["roomId"] = roomId
        params["sender"] = sender
        params["message"] = message
        evt = SFSEvent(SFSEvent.onPrivateMessage, params)
        self.sfc.dispatchEvent(evt)
        return

    def handle_dmnMsg(self, xml_obj):
        body = xml_obj.body
        message = body.txt.get_data()
        evt = SFSEvent(SFSEvent.onAdminMessage, {"message":message})
        self.sfc.dispatchEvent(evt)
        return

    def handle_modMsg(self, xml_obj):
        body = xml_obj.body
        roomId = int(body.xml_attr.get("r", -1))
        message = body.txt.get_data()
        user = body.user
        userId = int(user.xml_attr.get("id", -1))
        sender = None
        room = self.sfc.getRoom(roomId)
        if room:
            sender = self.sfc.getRoom(roomId).getUser(userId)
        params = {}
        params["sender"] = sender
        params["message"] = message
        evt = SFSEvent(SFSEvent.onModeratorMessage, params)
        self.sfc.dispatchEvent(evt)
        return

    def handle_dataObj(self, xml_obj):
        body = xml_obj.body
        roomId = int(body.xml_attr.get("r", -1))
        xmlStr = body.dataObj.get_cdata()
        user = body.user
        userId = int(user.xml_attr.get("id", -1))
        sender = self.sfc.getRoom(roomId).getUser(userId)
        xmlObj = XMLObj.build_from_str(xmlStr)
        params = {}
        params["sender"] = sender
        params["obj"] = xmlObj
        evt = SFSEvent(SFSEvent.onObjectReceived, params)
        self.sfc.dispatchEvent(evt)
        return

    def handle_rVarsUpdate(self, xml_obj):
        body = xml_obj.body
        roomId = int(body.xml_attr.get("r", -1))
        currRoom = self.sfc.getRoom(roomId)
        if body.vars and body.vars.var:
            changedVars = self.populateVariables(currRoom.getVariables(), body)
        params = {}
        params["room"] = currRoom
        params["changedVars"] = changedVars
        evt = SFSEvent(SFSEvent.onRoomVariablesUpdate, params)
        self.sfc.dispatchEvent(evt)
        return

    def handle_roomAdd(self, xml_obj):
        body = xml_obj.body
        rm = body.rm
        rId = int(rm.xml_attr.get("id", -1))
        rName = rm.name.get_data()
        rMax = int(rm.xml_attr.get("max", 0))
        rSpec = int(rm.xml_attr.get("spec", 0))
        temp = int(rm.xml_attr.get("temp", 0))
        isTemp = (temp == 1)
        game = int(rm.xml_attr.get("game", 0))
        isGame = (game == 1)
        priv = int(rm.xml_attr.get("priv", 0))
        isPriv = (priv == 1)
        limbo = int(rm.xml_attr.get("limbo", 0))
        isLimbo = (limbo == 1)
        
        newRoom = Room(rId, rName, rMax, rSpec, isTemp, isGame, isPriv, isLimbo, 0, 0)
        rList = self.sfc.getAllRooms()
        if rm.vars and rm.vars.var:
            self.populateVariables(newRoom.getVariables(), rm)
        rList[rId] = newRoom
        params = {}
        params["room"] = newRoom
        evt = SFSEvent(SFSEvent.onRoomAdded, params)
        self.sfc.dispatchEvent(evt)
        return

    def handle_roomDel(self, xml_obj):
        body = xml_obj.body
        rm = body.rm
        roomId = int(rm.xml_attr.get("id", -1))
        roomList = self.sfc.getAllRooms()
        params = {}
        params["room"] = roomList.pop(roomId)
        evt = SFSEvent(SFSEvent.onRoomDeleted, params)
        self.sfc.dispatchEvent(evt)
        return

    def handle_rndK(self, xml_obj):
        body = xml_obj.body
        key = body.k.get_data()
        params = {}
        params["key"] = key
        evt = SFSEvent(SFSEvent.onRandomKey, params)
        self.sfc.dispatchEvent(evt)
        return

    def handle_roundTripRes(self, xml_obj):
        now = time.time()
        res = now - self.sfc.getBenchStartTime()
        params = {}
        params["elapsed"] = res
        evt = SFSEvent(SFSEvent.onRoundTripResponse, params)
        self.sfc.dispatchEvent(evt)
        return

    def handle_uVarsUpdate(self, xml_obj):
        body = xml_obj.body
        user = body.user
        userId = int(user.xml_attr.get("id", -1))
        returnUser = None
        if body.vars and body.vars.var:
            for room in self.sfc.getAllRooms().values():
                varOwner = room.getUser(userId)
                if varOwner:
                    if not returnUser:
                        returnUser = varOwner
                    changedVars = self.populateVariables(varOwner.getVariables(), body)
        params = {}
        params["user"] = returnUser
        params["changedVars"] = changedVars
        evt = SFSEvent(SFSEvent.onUserVariablesUpdate, params)
        self.sfc.dispatchEvent(evt)
        return

    def handle_createRmKO(self, xml_obj):
        body = xml_obj.body
        room = body.room
        errMsg = room.xml_attr.get("e")
        params = {}
        params["error"] = errMsg
        evt = SFSEvent(SFSEvent.onCreateRoomError, params)
        self.sfc.dispatchEvent(evt)
        return

    def handle_bList(self, xml_obj):
        body = xml_obj.body
        bList = body.bList
        myVars = body.mv
        if myVars and myVars.v:
            for myVar in myVars.v:
                varName = myVar.xml_attr.get("n")
                self.sfc.myBuddyVars[varName] = myVar.get_data()
        if bList:
            if bList.b:
                for b in bList.b:
                    buddy = Buddy()
                    online = int(b.xml_attr.get("s", 0))
                    buddy.setOnline(online == 1)
                    name = b.n.get_data()
                    buddy.setName(name)
                    id = int(b.xml_attr.get("i", -1))
                    buddy.setId(id)
                    blocked = int(b.xml_attr.get("x", 0))
                    buddy.setBlocked(blocked == 1)
                    bVarsXML = b.vs
                    if bVarsXML and bVarsXML.v:
                        variables = {}
                        for bVar in bVarsXML.v:
                            bVarName = bVar.xml_attr.get("n")
                            variables[bVarName] = bVar.get_data()
                        buddy.setVariables(variables)
                    self.sfc.buddyList.append(buddy)
            params = {"list":self.sfc.buddyList}
            evt = SFSEvent(SFSEvent.onBuddyList, params)
        else:
            err = body.err            
            params = {}
            params["error"] = err.get_data()
            evt = SFSEvent(SFSEvent.onBuddyListError, params)
        self.sfc.dispatchEvent(evt)
        return

    def handle_bUpd(self, xml_obj):
        body = xml_obj.body
        b = body.b
        params = {}
        if b:
            buddy = Buddy()
            online = int(b.xml_attr.get("s", 0))
            buddy.setOnline(online == 1)
            name = b.n.get_data()
            buddy.setName(name)
            id = int(b.xml_attr.get("i", -1))
            buddy.setId(id)
            blocked = int(b.xml_attr.get("x", 0))
            buddy.setBlocked(blocked == 1)
            bVars = b.vs
            found = False
            for index, tempB in enumerate(self.sfc.buddyList):
                if tempB.getName() == buddy.getName():
                    buddy.setBlocked(tempB.isBlocked())
                    buddy.setVariables(tempB.getVariables())
                    if bVars and bVars.v:
                        for bVar in bVars.v:
                            bVarName = bVar.xml_attr.get("n")
                            buddy.variables[bVarName] = bVar.get_data()
                    
                    self.sfc.buddyList[index] = buddy
                    found = True
                    break
            if found:
                params["buddy"] = buddy
                evt = SFSEvent(SFSEvent.onBuddyListUpdate, params)
        else:
            err = body.err
            params["error"] = err.get_data()
            evt = SFSEvent(SFSEvent.onBuddyListError, params)
        self.sfc.dispatchEvent(evt)
        return

    def handle_bAdd(self, xml_obj):
        buddy = Buddy()
        body = xml_obj.body
        b = body.b
        online = int(b.xml_attr.get("s", 0))
        buddy.setOnline(online == 1)
        name = b.n.get_data()
        buddy.setName(name)
        id = int(b.xml_attr.get("i", -1))
        buddy.setId(id)
        blocked = int(b.xml_attr.get("x", 0))
        buddy.setBlocked(blocked == 1)
        bVarsXML = b.vs
        if bVarsXML and bVarsXML.v:
            variables = {}
            for bVar in bVarsXML.v:
                bVarName = bVar.xml_attr.get("n")
                variables[bVarName] = bVar.get_data()
            buddy.setVariables(variables)
        self.sfc.buddyList.append(buddy)
        params = {"list":self.sfc.buddyList}
        evt = SFSEvent(SFSEvent.onBuddyList, params)
        self.sfc.dispatchEvent(evt)
        return

    def handle_roomB(self, xml_obj):
        body = xml_obj.body
        roomIds = body.br.xml_attr.get("r","")
        idStr = roomIds.split(",")
        ids = [int(ids) for ids in idStr]
        params = {"idList":ids}
        evt = SFSEvent(SFSEvent.onBuddyRoom, params)
        self.sfc.dispatchEvent(evt)
        return

    def handle_leaveRoom(self, xml_obj):
        body = xml_obj.body
        rm = body.rm
        roomLeft = int(rm.xml_attr.get("id", -1))
        params = {"roomId":roomLeft}
        evt = SFSEvent(SFSEvent.onRoomLeft, params)
        self.sfc.dispatchEvent(evt)
        return

    def handle_swSpec(self, xml_obj):
        body = xml_obj.body
        roomId = int(body.xml_attr.get("r", -1))
        pid = body.pid
        playerId = int(pid.xml_attr.get("id", -1))
        theRoom = self.sfc.getRoom(roomId)
        if playerId > 0:
            theRoom.setUserCount(theRoom.getUserCount() + 1)
            theRoom.setSpectatorCount(theRoom.getSpectatorCount() - 1)
        if pid.xml_attr.has_key("u"):
            userId = int(pid.xml_attr.get("u", -1))
            user = theRoom.getUser(userId)
            if user:
                user.setIsSpectator(False)
                user.setPlayerId(playerId)
        else:
            self.sfc.playerId = playerId
            evt = SFSEvent.build_evt(SFSEvent.onSpectatorSwitched, self.sfc.playerId > 0, newId = self.sfc.playerId, room = theRoom)
            self.sfc.dispatchEvent(evt)
        return

    def handle_swPl(self, xml_obj):
        body = xml_obj.body
        roomId = int(body.xml_attr.get("r", -1))
        pid = body.pid
        playerId = int(pid.xml_attr.get("id", -1))
        theRoom = self.sfc.getRoom(roomId)
        if playerId == -1:
            theRoom.setUserCount(theRoom.getUserCount() - 1)
            theRoom.setSpectatorCount(theRoom.getSpectatorCount() + 1)
        if pid.xml_attr.has_key("u"):
            userId = int(pid.xml_attr.get("u", -1))
            user = theRoom.getUser(userId)
            if user:
                user.setIsSpectator(True)
                user.setPlayerId(playerId)
        else:
            self.sfc.playerId = playerId
            evt = SFSEvent.build_evt(SFSEvent.onPlayerSwitched, self.sfc.playerId == -1, newId = self.sfc.playerId, room = theRoom)
            self.sfc.dispatchEvent(evt)
        return

    def handle_bPrm(self, xml_obj):
        body = xml_obj.body
        params = {}
        params["sender"] = body.n.get_data()
        message = body.txt.get_data()
        params["message"] = message
        evt = SFSEvent(SFSEvent.onBuddyPermissionRequest, params)
        self.sfc.dispatchEvent(evt)
        return

    def handle_remB(self, xml_obj):
        body = xml_obj.body
        buddyName = body.n.get_data()
        for buddy in self.sfc.buddyList:
            if buddy.getName() == buddyName:
                self.sfc.buddyList.remove(buddy)
                params = {"list":self.sfc.buddyList}
                evt = SFSEvent(SFSEvent.onBuddyList, params)
                self.sfc.dispatchEvent(evt)
                break
        return
        return