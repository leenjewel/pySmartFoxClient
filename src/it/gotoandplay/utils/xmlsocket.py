# -*- coding:utf-8 -*-
'''
Created on 2010-11-12

@author: leenjewel
'''

from it.gotoandplay.utils.twistedsocket import build_connect
from it.gotoandplay.utils.threadevent import ThreadEvent

class XMLSocket(object):
    
    def __init__(self):
        self.event_obj = None
        self.socket_client = None
    
    def connect(self, server_host, server_port):
        build_connect(self, server_host, server_port)
        return
    
    def send(self, data):
        self.socket_client.transport.write(data)
        return
    
    def sendXMLObj(self, xml_obj):
        self.send(str(xml_obj.to_string())+"\0")
        return
    
    def onConnection(self, socket_client):
        self.socket_client = socket_client
        ThreadEvent.build_event(self.event_obj, "onConnection")
        return
    
    def onDataReceived(self, data):
        ThreadEvent.build_event(self.event_obj, "onDataReceived", data)
        return
    
    def addEventListener(self, event_obj):
        self.event_obj = event_obj
        return


if __name__ == "__main__":
    xml_client = XMLSocket()
    xml_client.connect("174.37.230.155", 9449)