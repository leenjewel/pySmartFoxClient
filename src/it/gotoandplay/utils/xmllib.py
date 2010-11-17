# -*- coding:utf-8 -*-
'''
Created on 2010-11-11

@author: leenjewel
'''

from xml.dom import minidom

class NOXMLRootError(Exception):
    pass

class ElementTypeError(Exception):
    pass

class XMLBase(object):
    def __init__(self, root_element, xml_dom):
        self.root_element = root_element
        self.xml_dom = xml_dom
    
    def __repr__(self):
        return self.root_element.toxml()
    
    def __str__(self):
        return self.get_text() or self.root_element.toxml()
    
    @staticmethod
    def is_same_attr(element, attr_dict):
        for key, value in attr_dict.items():
            if not element.attributes.has_key(key):
                return False
            if element.attributes[key].value != value:
                return False
        return True

    @classmethod
    def build_from_str(cls, xml_str):
        dom = minidom.parseString(xml_str)
        return cls(dom.documentElement, dom)
    
    def to_string(self):
        return self.root_element.toxml()

    def get_elements(self, e_name, e_dict = None):
        result = []
        e_elements = self.root_element.getElementsByTagName(e_name)
        for en in e_elements:
            if e_dict:
                if en.nodeType == en.ELEMENT_NODE and self.is_same_attr(en, e_dict):
                    result.append(XMLBase(xml_dom = self.xml_dom, root_element = en))
            else:
                result.append(XMLBase(xml_dom = self.xml_dom, root_element = en))
        return result

    def get_element(self, e_name, e_dict = None):
        result = self.get_elements( e_name, e_dict)
        if result:
            return result[0]
        else:
            return None
    
    def get_text(self):
        for en in self.root_element.childNodes:
            if en.nodeType == en.TEXT_NODE and not en.data.isspace():
                return en.data.strip()
        return None

    def get_cdata(self):
        for en in self.root_element.childNodes:
            if en.nodeType == en.CDATA_SECTION_NODE and not en.data.isspace():
                return en.data
        return None
    
    def get_data(self):
        return self.get_cdata() or self.get_text()

    def delete_element(self, e_name, e_dict = None, e_num = None):
        result = self.get_elements(self, e_name, e_dict)
        if result:
            for en in result:
                self.root_element.removeChild(en.root_element)
        return

    def get_attribute(self):
        result = {}
        for key in self.root_element.attributes.keys():
            result[key] = self.root_element.attributes[key].value
        return result
    xml_attr = property(get_attribute)
    
    def set_attribute(self, e_dict):
        for key in e_dict.keys():
            self.root_element.setAttribute(key, e_dict[key])
        return

    def add_element(self, e_name, e_dict = None, e_text = None):
        new_e = XMLBase(root_element = self.xml_dom.createElement(e_name), xml_dom = self.xml_dom)
        if e_dict:
            new_e.set_attribute(e_dict)
        if e_text:
            new_t = XMLBase(root_element = self.xml_dom.createTextNode(e_text), xml_dom = self.xml_dom)
            new_e.add_child(new_t)
        self.add_child(new_e)
        return new_e

    def add_child(self,add_e):
        if isinstance(add_e, minidom.Element):
            add_e = XMLBase(root_element = add_e, xml_dom = self.xml_dom)
        elif isinstance(add_e, basestring):
            add_e = XMLBase(root_element = self.xml_dom.createElement(add_e), xml_dom = self.xml_dom)
        self.root_element.appendChild(add_e.root_element)
        return add_e
            
    def __add__(self,add_e):
        self.add_child(add_e)
        return self
    
    def __iadd__(self,add_e):
        self.add_child(add_e)
        return self

class XMLObj(XMLBase):
    def __init__(self, root_element, xml_dom):
        self.xml_dom = xml_dom
        self.my_name = root_element.nodeName
        self.my_childs = []
        self.my_brothers = [self]
        self.node_index = 0
        for child_e in root_element.childNodes:
            if child_e.nodeType == child_e.ELEMENT_NODE:
                node_name = child_e.nodeName
                self.add_xml_obj(node_name, child_e, self.xml_dom)
        if len(self.my_brothers)<=1:
            self.root_element = root_element

    @classmethod
    def build_from_str(cls, xml_str):
        xml_base = XMLBase.build_from_str(xml_str)
        return cls(xml_base.root_element, xml_base.xml_dom)
    
    def append(self, xml_obj):
        if xml_obj.root_element.nodeName == self.my_name:
            self.my_brothers.append(xml_obj)
        else:
            print "It's not my brother"
            
    def __len__(self):
        return len(self.my_brothers)
    
    def __iter__(self):
        return self
    
    def __getitem__(self, index):
        return self.my_brothers[index]
    
    def next(self):
        self.node_index += 1
        if self.node_index > len(self.my_brothers):
            self.node_index = 0
            raise StopIteration
        return self.my_brothers[self.node_index-1]
    
    def __getattr__(self, attr):
        elements = self.get_elements(attr)
        if elements:
            element = XMLObj(elements[0].root_element)
            for em in elements[1:]:
                element.my_brothers.append(XMLObj(em.root_element))
            return element
        else:
            return None
    
    def __setitem__(self, item_key, item_value):
        new_element = self.add_element(item_key, e_text = item_value)
        self.add_xml_obj(item_key, new_element, self.xml_dom)
        return None
    
    def add_xml_obj(self, node_name, xml_o, xml_dom):
        if isinstance(xml_o, minidom.Element):
            xml_obj = XMLObj(xml_o, self.xml_dom)
        else:
            xml_obj = XMLObj(xml_o.root_element, self.xml_dom)
        if hasattr(self, node_name):
            getattr(self, node_name).append(xml_obj)
        else:
            setattr(self, node_name, xml_obj)
            self.my_childs.append(node_name)
        return None
    
    def get(self, key, default_value):
        return self.__dict__.get(key, default_value)