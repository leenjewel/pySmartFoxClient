# -*- coding:utf-8 -*-
'''
Created on 2010-11-12

@author: leenjewel
'''

from twisted.internet import protocol
from twisted.internet import reactor

class SocketClientProtocol(protocol.Protocol):

    received_data = ""

    def connectionMade(self):
        self.factory.handleEvent("onConnection", self)
        return

    def dataReceived(self, data):
        self.received_data += data
        if self.received_data[-1] == "\0":
            data = self.received_data
            self.received_data = ""
            self.factory.handleEvent("onDataReceived", data[:-1])
        return

class SocketClientFactory(protocol.ClientFactory):
    protocol = SocketClientProtocol
    
    def addEventListener(self, event_obj):
        self.event_obj = event_obj
        return
    
    def handleEvent(self, func_name, *args, **kwargs):
        if self.event_obj and hasattr(self.event_obj, func_name):
            func = getattr(self.event_obj, func_name)
            func(*args, **kwargs)
        return

def build_connect(event_obj, server_host, server_port):
    socket_client_factory = SocketClientFactory()
    socket_client_factory.addEventListener(event_obj)
    reactor.connectTCP(server_host, server_port, socket_client_factory)
    reactor.run()
    return
