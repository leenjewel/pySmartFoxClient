# -*- coding:utf-8 -*-
'''
Created on 2010-11-15

@author: leenjewel
'''

from it.gotoandplay.utils.xmllib import XMLObj
from it.gotoandplay.smartfoxclient.sfsevent import SFSEvent

class ExtHandler(object):
    
    def __init__(self, sfc):
        self.sfc = sfc
    
    def handleMessage(self, msg_obj, obj_type = None):
        from it.gotoandplay.smartfoxclient import SmartFoxClient
        params = {}
        if obj_type == SmartFoxClient.XTMSG_TYPE_XML:
            body = msg_obj.body
            action = body.xml_attr.get("action")
            if action == "xtRes":            
                params["dataObj"] = XMLObj.build_from_str(body.get_data())
                params["type"] = obj_type
                evt = SFSEvent(SFSEvent.onExtensionResponse, params)
                self.sfc.dispatchEvent(evt)
        elif obj_type == SmartFoxClient.XTMSG_TYPE_JSON:
            params["dataObj"] = msg_obj.get("o")
            params["type"] = obj_type
            evt = SFSEvent(SFSEvent.onExtensionResponse, params)
            self.sfc.dispatchEvent(evt)
        elif obj_type == SmartFoxClient.XTMSG_TYPE_STR:
            params["dataObj"] = msg_obj
            params["type"] = obj_type
            evt = SFSEvent(SFSEvent.onExtensionResponse, params)
            self.sfc.dispatchEvent(evt)