# -*- coding:utf-8 -*-
'''
Created on 2010-11-12

@author: leenjewel
'''

import threading

class ThreadEvent(threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
    
    @classmethod
    def build_event(cls, obj, func_name, *args, **kwargs):
        new_event = cls()
        new_event.obj = obj
        new_event.func_name = func_name
        new_event.args = args
        new_event.kwargs = kwargs
        new_event.start()
    
    def run(self):
        if hasattr(self.obj, self.func_name):
            func = getattr(self.obj, self.func_name)
            return func(*self.args, **self.kwargs)
        return

if __name__ == "__main__":
    class test(object):
        def say(self, msg):
            print msg
    
    for i in range(10):
        t = test()
        ThreadEvent.build_event(t, "say", i)
        print "==",i