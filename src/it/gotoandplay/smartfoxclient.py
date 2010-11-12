# -*- coding:utf-8 -*-
'''
Created on 2010-11-8

@author: leenjewel
'''

from it.gotoandplay.utils.xmlsocket import XMLSocket
from it.gotoandplay.utils.xmllib import XMLObj

class SFSEvent(object):
    pass

class SmartFoxClient(object):
    
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
        self.event_control = {}
    
    def connect(self, server_host, server_port):
        self.socket_client = XMLSocket()
        self.socket_client.addEventListener(self)
        self.socket_client.connect(server_host, server_port)
        return
    
    def addEventListener(self, event_name, event_obj):
        self.event_control[event_name] = event_obj
        return
    
    def print_debug(self, data):
        if self.debug:
            print data
        return
    
    def send(self, header, action, from_room, message):
        xml_msg = self.makeXmlHeader(header)
        xml_msg["body"] = None
        xml_msg.body.set_attribute({"action":action, "r":str(from_room)})
        xml_msg.body += message
        self.print_debug("[Sending] "+xml_msg.to_string())
        self.socket_client.sendXMLObj(xml_msg)
        return
    
    def makeXmlHeader(self, header):
        xml_head = "<msg></msg>"
        xml_msg = XMLObj.build_from_str(xml_head)
        xml_msg.set_attribute({"t":header})
        return xml_msg
        
    
    def onConnection(self):
        self.print_debug("onConnection")
        xml_msg = XMLObj.build_from_str("<ver v='"+self.VER+"'/>")
        self.send(self.MESSAGE_HEADER_SYSTEM, "verChk", -1, xml_msg)
        return
    
    def onDataReceived(self, data):
        self.print_debug("[Received] "+str(data))
        return

if __name__ == "__main__":
    sfc = SmartFoxClient(True)
    sfc.connect("174.37.230.155", 9449)