'''
Created on Dec 15, 2011

@author: Marek Skrajnowski
'''

from spyse.core.agents.agent import Agent
from spyse.core.behaviours.behaviours import Behaviour, ReceiveBehaviour
from spyse.core.content.content import MessageTemplate, ACLMessage

from behaviours import SleepBehaviour, DieBehaviour
from random import random
from agents.Vehicle import Vehicle
from spyse.core.behaviours.composite import SequentialBehaviour
from agents.behaviours import BehaviourQueue

import json
import logging
import random
from spyse.core.agents.aid import AID

class VehicleEntry(object):
    def __init__(self, position, length, vehicleId, nextEntry = None):
        self.position = position
        self.length = length
        self.vehicleId = vehicleId
        self.nextEntry = nextEntry

    def getStart(self):
        return self.position - self.length/2.0
    start = property(getStart)

    def getEnd(self):
        return self.position + self.length/2.0
    end = property(getEnd)

class SpawnReceiver(ReceiveBehaviour):
        
    class SpawnBehaviour(Behaviour):
        def setup(self, message=None):
            self.message = message
            content = json.loads(message.content)
            self.vehicleId = content['vehicleId']  
            self.vehicleLength = content['length']
            
        def action(self):
            if self.agent.getFreeSpace() > self.vehicleLength:
                self.agent.addVehicleEntry(VehicleEntry(0, self.vehicleLength, self.vehicleId))
                
                aid = self.agent.mts.ams.find_agent(self.vehicleId)
                self.agent.mts.ams.invoke_agent(aid.name)
                reply = self.message.create_reply(MessageTemplate.CONFIRM)
                reply.content = json.dumps({'type': 'vehicle spawned', 'vehicleId': self.vehicleId})
                self.agent.send_message(reply)
                
                self.set_done()
            self.sleep(0.1)
    
    def __init__(self, name='', **namedargs):
        template = MessageTemplate(MessageTemplate.REQUEST)
        template.protocol = 'spawn-vehicle'
        ReceiveBehaviour.__init__(self, name=name, template=template, **namedargs)
        
    def setup(self):
        self.log = logging.getLogger(self.name)
        self.spawnQueueBehaviour = None
        
    def action(self):
        if self.spawnQueueBehaviour == None:
            self.spawnQueueBehaviour = BehaviourQueue(onEmpty=self.openLane)
            self.agent.add_behaviour(self.spawnQueueBehaviour)
        ReceiveBehaviour.action(self)
        
    def closeLane(self):
        self.agent.setFull(True)
        
    def openLane(self):
        self.agent.setFull(False)
        
    def handle_message(self, message):
        self.agent.setFull(True)
        self.spawnQueueBehaviour.add_behaviour(self.SpawnBehaviour(message=message))
        self.sleep(0.1)


class LeaveReceiver(ReceiveBehaviour):
    def __init__(self, name='', **namedargs):
        template = MessageTemplate(MessageTemplate.INFORM)
        template.protocol = 'vehicle-left'
        ReceiveBehaviour.__init__(self, name=name, template=template, **namedargs)
    
    def handle_message(self, message):
        entry = self.agent.getVehicleEntry(message.sender.shortname)
        self.agent.removeVehicleEntry(entry)
        

class ObstacleHandler(ReceiveBehaviour):
    def __init__(self, name='', **namedargs):
        template = MessageTemplate(MessageTemplate.REQUEST)
        template.protocol = 'next-obstacle'
        
        ReceiveBehaviour.__init__(self, name=name, template=template, **namedargs)
        
    def getNextObstacle(self, vehicleId):
        nextEntry = self.agent.getVehicleEntry(vehicleId).nextEntry
        if nextEntry != None:
            return nextEntry.start()
        return None
        
    def action(self):
        ReceiveBehaviour.action(self)
        
    def handle_message(self, message):
        #self.agent.log.info("Received an obstacle request from %s" % message.sender.shortname)
        
        msgContent = json.loads(message.content)
        entry = self.agent.getVehicleEntry(message.sender.shortname)
        entry.position = msgContent['offset']
        
        reply = message.create_reply(ACLMessage.INFORM)
        
        obstacle = entry.nextEntry.start if entry.nextEntry != None else None
        reply.content = json.dumps({"obstacle": obstacle})
        
        self.agent.send_message(reply)
        #self.agent.log.info("Sent obstacle at %s to %s" % (str(obstacle), message.sender.shortname))
        self.sleep(0.1)

class JunctionHandler(Behaviour):
    
    def __init__(self, name='', **namedargs):
        self.template = MessageTemplate(MessageTemplate.REQUEST)
        self.template.protocol = 'request-space'
        self.request = None
        self.requestedEntry = None
        
        Behaviour.__init__(self, name, **namedargs)
        
    def action(self):
        
        if self.request == None:
            self.request = self.agent.get_message(self.template)
            
            if self.request == None:
                return
            
            content = json.loads(self.request.content)
            self.requestedEntry = VehicleEntry(0, content['vehicleLength'], content['vehicleId'])
        
        if self.request != None:
            
            if self.agent.isClosed():
                reply = self.request.create_reply(ACLMessage.REFUSE)
                reply.content = json.dumps({"vehicleId": self.requestedEntry.vehicleId, "reason": "closed"})
                self.agent.send_message(reply)
                
                self.request = None
                self.requestedEntry = None
            
            if self.agent.getFreeSpace() > self.requestedEntry.length:
                self.agent.addVehicleEntry(self.requestedEntry)
                
                reply = self.request.create_reply(ACLMessage.AGREE)
                reply.content = json.dumps({"vehicleId": self.requestedEntry.vehicleId})
                self.agent.send_message(reply)
                
                self.request = None
                self.requestedEntry = None
                
        self.sleep(0.1)

class Lane(Agent):
    '''
    classdocs
    '''
            
    def setup(self, startJunction=None, endJunction=None, length=0):
        '''
        Lane Agent Setup
        '''
        self.vehicles = []
        self.vehiclesDict = {}
        self.full = False
        self.closed = False
        
        self.length = length
        self.startId = startJunction
        self.endId = endJunction
        
        self.log = logging.getLogger(self.aid.shortname)
        
        #self.add_behaviour(SleepBehaviour())
        self.add_behaviour(DieBehaviour())
        self.add_behaviour(SpawnReceiver())
        self.add_behaviour(ObstacleHandler())
        self.add_behaviour(JunctionHandler())
        self.add_behaviour(LeaveReceiver())
        
    def setFull(self, full):
        self.full = full
        
    def setClosed(self, closed):
        self.closed = closed
        
        # inform the start junction
        msg = ACLMessage(ACLMessage.INFORM)
        msg.protocol = 'lane-closed' if closed else 'lane-opened'
        msg.receivers.add(self.mts.ams.find_agent(self.startId))
        self.send_message(msg)
        
    def getFreeSpace(self):
        if not self.vehicles:
            return self.length
        return self.vehicles[0].start;
    
    def addVehicleEntry(self, vehicleEntry):
        assert isinstance(vehicleEntry, VehicleEntry)
        if self.vehicles:
            vehicleEntry.nextEntry = self.vehicles[0]
        self.vehicles.insert(0, vehicleEntry)
        self.vehiclesDict[vehicleEntry.vehicleId] = vehicleEntry
    
    def getVehicleEntry(self, vehicleId):
        if vehicleId not in self.vehiclesDict.keys():
            return None
        return self.vehiclesDict[vehicleId]
    
    def removeVehicleEntry(self, vehicleEntry):
        i = self.vehicles.index(vehicleEntry)
        
        if i > 0:
            self.vehicles[i-1].nextEntry = vehicleEntry.nextEntry
            
        del self.vehicles[i]
        self.vehiclesDict.pop(vehicleEntry.vehicleId)    
    
    def isFull(self):
        return self.full
    
    def isClosed(self):
        return self.closed
    
    
class WaitingVehicle(object):
    def __init__(self, vehicleId, entry, exit, length, request):
        self.vehicleId = vehicleId
        self.vehicleLength = length
        self.entry = entry
        self.exit = exit
        self.exitReady = False
        self.request = request
        self.spaceRequest = None
    
class RegisterVehicleBehaviour(ReceiveBehaviour):
    def __init__(self, name='', **namedargs):
        template = MessageTemplate(MessageTemplate.REQUEST)
        template.protocol = 'junction'
        ReceiveBehaviour.__init__(self, name=name, template=template, **namedargs)
    
    def handle_message(self, message):
        content = json.loads(message.content)
        entry = content['entry']
        exit = content['exit']
        length = content['length']
        waiting = WaitingVehicle(message.sender.shortname, entry, exit, length, message)
        self.agent.exitQueues[exit].append(waiting)
        self.agent.log.info("Registered %s for %d" % (message.sender.shortname, exit))
        self.sleep(0.1)

class TrafficControlBehaviour(Behaviour):
    def setup(self):
        self.laneSpaceTemplate = MessageTemplate(MessageTemplate.AGREE)
        self.laneSpaceTemplate.protocol = 'request-space'
        
        self.vehicleLeftTemplate = MessageTemplate(MessageTemplate.CONFIRM)
        self.vehicleLeftTemplate.protocol = 'junction'
        
        self.chosenVehicleId = None

    def findWaiting(self, vehicleId):
        for queue in self.agent.exitQueues:
            if queue and queue[0].vehicleId == vehicleId:
                return queue[0]
        return None
            
    def removeWaiting(self, vehicleId):
        for queue in self.agent.exitQueues:
            if queue and queue[0].vehicleId == vehicleId:
                del queue[0]
                return

    def action(self):
        
        for i in range(len(self.agent.exitQueues)):
            queue = self.agent.exitQueues[i]
            if queue and queue[0].spaceRequest == None:
                spaceRequest = ACLMessage(ACLMessage.REQUEST)
                spaceRequest.protocol = 'request-space'
                spaceRequest.content = json.dumps({'vehicleId': queue[0].vehicleId, 'vehicleLength': queue[0].vehicleLength})
                spaceRequest.receivers.add(AID(str(self.agent.exits[i])))
                queue[0].spaceRequest = spaceRequest
                self.agent.send_message(spaceRequest)
                self.agent.log.info("sent space request to %s" % self.agent.exits[i])
        
        msg = self.agent.get_message(self.laneSpaceTemplate)
        if msg != None:
            content = json.loads(msg.content)
            waiting = self.findWaiting(content['vehicleId'])
            if msg.performative == ACLMessage.REFUSE:
                reply = waiting.request.create_reply(ACLMessage.REFUSE)
                reply.content = json.dumps({'reason', content['reason']})
                del self.agent.exitQueues[waiting.exit][0]
                
            elif msg.performative == ACLMessage.AGREE:                
                waiting.exitReady = True
        
        if self.chosenVehicleId != None:
            msg = self.agent.get_message(self.vehicleLeftTemplate)
            if msg != None:
                self.chosenVehicleId = None
            
        if self.chosenVehicleId == None:
        
            randomQueues = self.agent.exitQueues[:]
            random.shuffle(randomQueues)
            for queue in randomQueues:
                if queue and queue[0].exitReady:
                    reply = queue[0].request.create_reply(ACLMessage.AGREE)
                    del queue[0]
                    self.agent.send_message(reply)
                    break
            
        self.sleep(0.1)
                
        
            
    
class Junction(Agent):
    '''
    classdocs
    '''
    #TODO: Junction agent
    def setup(self, exits=[], entrances=[]):
        '''
        Junction Agent Setup
        '''
        self.log = logging.getLogger(self.aid.shortname)
        
        self.exits = exits
        self.entrances = entrances
        self.exitQueues = [[], [], [], []]
        
        self.log = logging.getLogger(self.name)
        self.add_behaviour(DieBehaviour())
        self.add_behaviour(RegisterVehicleBehaviour())
        self.add_behaviour(TrafficControlBehaviour())
