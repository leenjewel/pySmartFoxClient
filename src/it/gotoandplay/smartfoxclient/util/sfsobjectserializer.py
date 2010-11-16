# -*- coding:utf-8 -*-
'''
Created on 2010-11-16

@author: leenjewel
'''

from it.gotoandplay.utils.xmllib import XMLObj

class SFSObjectSerializer(object):
    
    asciiTable_e = {
        ">":"&gt",
        "<":"&lt",
        "&":"&amp",
        "'":"&apos",
        "\\":"&quot",
        "\n":"",
        "\t":"",
        "\r":"",
    }
    asciiTable_d = {
        "&gt":">",
        "&lt":"<",
        "&amp":"&",
        "&apos":"'",
        "&quot":"\\",
    }
    
    @staticmethod
    def encodeEntities(in_sb):
        for s in SFSObjectSerializer.asciiTable_e:
            in_sb = in_sb.replace(s, "")
        return in_sb

    @staticmethod
    def serialize(sfsobj, need_obj = False):
        if need_obj:
            return XMLObj.build_from_str(SFSObjectSerializer.obj2xml(sfsobj, 0, "", None))
        else:
            return SFSObjectSerializer.obj2xml(sfsobj, 0, "", None)
    
    @staticmethod
    def obj2xml(ao, depth, nodeName, xmlData = None):
        if xmlData is None:
            xmlData = ""
        if depth == 0:
            xmlData += "<dataObj>"
        else:
            xmlData += "<obj o='" + nodeName + "' t='a'>"
        for key, o in ao.items():
            if not o:
                xmlData += "<var n='" + str(key) + "' t='x' />"
            elif isinstance(o, dict):
                xmlData = SFSObjectSerializer.obj2xml(o, depth + 1, key, xmlData)
                xmlData += "</obj>"
            elif isinstance(o, float):
                xmlData += "<var n='" + key + "' t='n'>" + str(o) + "</var>"
            elif isinstance(o, basestring):
                xmlData += "<var n='" + key + "' t='s'>" + SFSObjectSerializer.encodeEntities(str(o)) + "</var>"
            elif isinstance(o, bool):
                if o:
                    xmlData += "<var n='" + key + "' t='b'>1</var>"
                else:
                    xmlData += "<var n='" + key + "' t='b'>0</var>"
        if depth == 0:
            xmlData += "</dataObj>"
        return xmlData