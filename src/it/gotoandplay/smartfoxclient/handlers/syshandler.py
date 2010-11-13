# -*- coding:utf-8 -*-
'''
Created on 2010-11-13

@author: leenjewel
'''

from it.gotoandplay.smartfoxclient.sfsevent import SFSEvent
from it.gotoandplay.smartfoxclient.data.room import Room

class SysHandler(object):

    def __init__(self, sfc):
        self.sfc = sfc
    
    def populateVariables(self, variables, xml_obj):
        vars = xml_obj.vars.var
        for v in vars:
            v_name = v.xml_attr.get("n")
            v_type = v.xml_attr.get("t")
            v_value = v.get_cdata()
            if v_type == "x" and variables.has_key(v_name):
                del variables[v_name]
            else:
                variables[v_name] = v_value
        return

    def handleMessage(self, xml_obj):
        action = xml_obj.body.xml_attr("action")
        if action and hasattr(self, "handle_"+action):
            func = getattr(self, "handle_"+action)
            return func(xml_obj)
        return
    
    def handle_apiOK(self, xml_obj):
        evt = SFSEvent(SFSEvent.onConnected, {"success":True})
        self.sfc.dispatchEvent(evt)
        return
    
    def handle_apiKO(self, xml_obj):
        evt = SFSEvent(SFSEvent.onConnected, {"success":False, "error":"API are obsolete, please upgrade"})
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
        return

    def handle_joinOK(self, xml_obj):
        return

    def handle_joinKO(self, xml_obj):
        return

    def handle_uER(self, xml_obj):
        return

    def handle_userGone(self, xml_obj):
        return

    def handle_pubMsg(self, xml_obj):
        return

    def handle_prvMsg(self, xml_obj):
        return

    def handle_dmnMsg(self, xml_obj):
        return

    def handle_modMsg(self, xml_obj):
        return

    def handle_dataObj(self, xml_obj):
        return

    def handle_rVarsUpdate(self, xml_obj):
        return

    def handle_roomAdd(self, xml_obj):
        return

    def handle_roomDel(self, xml_obj):
        return

    def handle_rndk(self, xml_obj):
        return

    def handle_roundTripRes(self, xml_obj):
        return

    def handle_uVarsUpdate(self, xml_obj):
        return

    def handle_createRmKO(self, xml_obj):
        return

    def handle_bList(self, xml_obj):
        return

    def handle_bUpd(self, xml_obj):
        return

    def handle_bAdd(self, xml_obj):
        return
    
    def handle_(self, xml_obj):
        return

    def handle_roomB(self, xml_obj):
        return

    def handle_leaveRoom(self, xml_obj):
        return

    def handle_swSpec(self, xml_obj):
        return

    def handle_swPl(self, xml_obj):
        return

    def handle_bPrm(self, xml_obj):
        return

    def handle_remB(self, xml_obj):
        return