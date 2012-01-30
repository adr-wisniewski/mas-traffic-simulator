'''
Created on Jan 12, 2012

@author: marek
'''

from Queue import Queue, Empty

class ActionQueue(Queue):
    
    def __init__(self, maxsize=0):
        Queue.__init__(self, maxsize)
        #self.queue = Queue(maxsize)
        self.result = Queue
    
    #def __getattr__(self, action):
    #    queue = self
    #    def function(*args):
    #        queue.putAction(action, args)
    #    return function
        
    def putAction(self, action, args, block=True, timeout=None):
        self.put((action, args), block, timeout)
        
    def getAction(self, block=True, timeout=None):
        try:
            return self.get(block, timeout)
        except Empty, e:
            return None
    
    def fireActionOn(self, target, block=True, timeout=None):
        action, args = self.get(block, timeout)
        method = getattr(type(target), action, None)
        
        if method == None:
            raise AttributeError("No attribute called %s in %s" % (method, type(target)))
        elif not callable(method):
            raise AttributeError("Attribute %s is not callable" % (method,))
        else:
            method(target, *args)
            
        self.task_done()