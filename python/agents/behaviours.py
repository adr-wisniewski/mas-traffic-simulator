'''
Created on Jan 20, 2012

@author: marek
'''

from spyse.core.behaviours.behaviours import Behaviour, ReceiveBehaviour
from spyse.core.content.content import MessageTemplate
from spyse.core.behaviours.composite import SequentialBehaviour
import json
import logging

class IdleBehaviour(Behaviour):
    def action(self):
        pass


class NullBehaviour(Behaviour):
    def action(self):
        self.set_done()


class SleepBehaviour(Behaviour):
    def action(self):
        self.sleep(5)
    
        
class DieBehaviour(ReceiveBehaviour):
    def __init__(self, name='', **namedargs):
        template = MessageTemplate(MessageTemplate.REQUEST)
        template.protocol = "kill"
        ReceiveBehaviour.__init__(self, name=name, template=template, **namedargs)
    
    def handle_message(self, message):
        self.agent.die()
        logging.info("%s killed", self.agent.name)
        #reply = message.create_reply(performative=MessageTemplate.CONFIRM)
        #reply.content = json.dumps({'type': 'killed'})
        #self.agent.send_message(reply)
        
        
class BehaviourQueue(SequentialBehaviour):
    
    def __init__(self, onEmpty, name='', **namedargs):
        SequentialBehaviour.__init__(self, name=name, **namedargs)
        self.__idleBehaviour = NullBehaviour()
        self.__idleBehaviour.set_done()
        
        self.__behaviours = self._SequentialBehaviour__behaviours   # HACK
        #self.__behaviours = []
        
        self.__empty = True
        self.__onEmpty = onEmpty
        
    def add_behaviour(self, behaviour, name=None):
        SequentialBehaviour.add_behaviour(self, behaviour, name=name)
        self.__empty = len(self.__behaviours) == 0
    
    def schedule_first(self):
        return self.__idleBehaviour
    
    def schedule_next(self, current):
        if current.done() and len(self.__behaviours) == 0:
            if self.__empty == False:
                self.__onEmpty()
                self.__empty = True
            return self.__idleBehaviour
        
        return SequentialBehaviour.schedule_next(self, current)
        
            
        
