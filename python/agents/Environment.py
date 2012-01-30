'''
Created on Dec 15, 2011

@author: Marek Skrajnowski
'''

from spyse.core.agents.agent import Agent
from spyse.core.behaviours.behaviours import Behaviour, ReceiveBehaviour, TickerBehaviour
from random import random
import json
import copy

from util.ActionQueue import ActionQueue  
from graphs.StreetGraph import StreetGraph
from agents.Street import Junction, Lane
from agents.Vehicle import Vehicle
from ui.EnvironmentProxy import EnvironmentProxy
from threading import Lock
from spyse.core.content.content import ACLMessage, MessageTemplate
from Queue import Empty

from agents.SimTime import time
import logging

environmentAgent = None

log = logging.getLogger("Environment")

class Environment(Agent):
    
    # GUI handling
    class GuiBehaviour(TickerBehaviour):
        def on_tick(self):
            self.agent.lock.acquire()
            try:
                self.agent.slotQueue.fireActionOn(self.agent, block=False)
            except Empty, e:
                pass
            self.agent.lock.release()
    
    class AgentKilledReceiver(ReceiveBehaviour):
        def __init__(self, name='', **namedargs):
            template = MessageTemplate(performative=MessageTemplate.CONFIRM)
            template.content = json.dumps({'type': 'killed'})
            ReceiveBehaviour.__init__(self, name=name, template=template, **namedargs)
            
        def handle_message(self, message):
            log.info("%s kill confirmed" % message.sender)
    
    class VehicleUpdateReceiver(ReceiveBehaviour):
        def __init__(self, name='', **namedargs):
            template = MessageTemplate(performative=MessageTemplate.INFORM)
            template.protocol = 'vehicle-status-update'
            ReceiveBehaviour.__init__(self, name=name, template=template, **namedargs)
            
        def handle_message(self, message):
            senderId = message.sender.shortname
            content = json.loads(message.content)
            if content['type'] == 'position update':
                position = content['position']
                self.agent.signalQueue.putAction("vehiclePositionUpdated", (senderId, position))
            elif content['type'] == 'path update':
                self.agent.signalQueue.putAction("vehiclePathUpdated", (senderId, content['start'], content['path'], content['target']))
    
    def __init__(self, name, mts, **namedargs):
        global environmentAgent
        if environmentAgent != None:
            raise RuntimeError("Environment agent already created")
        
        environmentAgent = self
        
        Agent.__init__(self, name, mts, **namedargs)
        
        self.__signalQueue = ActionQueue()
        self.__slotQueue = ActionQueue()
        self.__proxy = EnvironmentProxy(self)        
        self.__lock = Lock()

    def setup(self):
        self.agents = []
        self.junctionAgents = []
        self.laneAgents = []
        self.vehicleAgents = []
        
        self.simulationSpeed = 1.0
        
        self.add_behaviour(self.GuiBehaviour(period=0.5))
        self.add_behaviour(self.AgentKilledReceiver())
        self.add_behaviour(self.VehicleUpdateReceiver())

    def setStreetGraph(self, streetGraph):
        #streetGraph = StreetGraph()
        
        log.info("env.setStreetGraph begin")
        
        log.info("env removing agents from old graph")
        for agent in self.agents:
            self.removeAgent(agent)
            
        self.junctionAgents = []
        self.laneAgents = []
        self.vehicleAgents = []
        
        log.info("env assigning new graph")
        self.streetGraph = streetGraph
        if self.streetGraph == None:
            return
        
        log.info("env creating agents")
        junctionQueue = [(streetGraph.junctionsList[0], -1, None, None), ]
        
        while len(junctionQueue) > 0:
            junction, sourceDirection, entryLane, exitLane = junctionQueue.pop()
            log.info("env creating junction %s" % junction.AID())
            
            exitAIDs = [None, ] * 4
            entranceAIDs = [None, ] * 4
            for i in range(4):
                if junction.exit(i) != None:
                    exitAIDs[i] = junction.exit(i).AID()
                if junction.exit(i) != None:
                    entranceAIDs[i] = junction.entrance(i).AID()
            
            for direction in range(4):
                if direction == sourceDirection:
                    continue

                newExit = junction.exit(direction)
                if hasattr(newExit, "envVisited"):
                    newExit = None
                    
                if newExit != None:
                    log.info("env creating exit%d %s" % (direction, newExit.AID()))
                    
                    self.mts.ams.start_agent(Lane, newExit.AID(),
                                             startJunction=junction.AID(),
                                             endJunction=newExit.end().AID(),
                                             length=newExit.length())
                    
                    self.laneAgents.append(newExit.AID())
                    self.agents.append(newExit.AID())
                    #laneAgent.start()
                    newExit.envVisited = True
                
                newEntry = junction.entrance(direction)
                if hasattr(newEntry, "envVisited"):
                    newEntry = None
                
                if newEntry != None:
                    log.info("env creating entry%d %s" % (direction, newEntry.AID()))
                    
                    self.mts.ams.start_agent(Lane, newEntry.AID(),
                                             startJunction=newEntry.start().AID(),
                                             endJunction=junction.AID(),
                                             length=newEntry.length())
                    
                    self.laneAgents.append(newEntry.AID())
                    self.agents.append(newEntry.AID())
                    #laneAgent.start()
                    newEntry.envVisited = True
                
                if newExit != None or newEntry != None:
                    log.info("env adding new junction to the queue: %s" % newExit.end().AID())
                    newJunction = newExit.end()
                    if not hasattr(newJunction, "envVisited"):
                        newJunction.envVisited = True
                        junctionQueue.append((newJunction, (direction + 2) % 4, newEntry, newExit))
            
            log.info("env finishing junction %s" % junction.AID())
            self.mts.ams.start_agent(Junction, junction.AID(),
                                     exits=exitAIDs,
                                     entrances=entranceAIDs)
            
            self.junctionAgents.append(junction.AID())
            self.agents.append(junction.AID())
            #junctionAgent.start()
            
        log.info("env.setStreetGraph end")
        log.info("junctions: %d lanes: %d" % (len(self.junctionAgents), len(self.laneAgents)))
            
    def die(self):
        for agentId in self.agents[:]:
            self.removeAgent(agentId)
        
        self.agents = []
        Agent.die(self)
        
    def setClosed(self, agentId, closed=True):
        log.info("lane %s closed" % agentId)
        
        #TODO: close agent
        
        self.signalQueue.putAction("agentClosed", (agentId, closed))
        
    def setSpeedLimit(self, laneId, limit):
        log.info("lane %s speed limit set to %d" % (laneId, limit))
        
        #TODO: set speed limit
        
        self.signalQueue.putAction("laneSpeedLimitChanged", (laneId, limit))
        
    def removeAgent(self, agentId):
        
        #TODO: remove agent
        # send kill message
        self.agents.remove(agentId)
        msg = ACLMessage(performative=ACLMessage.REQUEST)
        msg.protocol = "kill"
        msg.receivers.add(self.mts.ams.find_agent(agentId))
        self.send_message(msg)
        log.info("agent %s removed" % agentId)
        
        #self.signalQueue.agentRemoved(agent.getAID())
        self.signalQueue.putAction("agentRemoved", (agentId,))
        
    def setSimulationSpeed(self, speed):
        self.simulationSpeed = speed
        time.setSpeed(speed)
        
    def startSimulation(self):
        log.info("simulation resumed")
        
        #TODO: start simulation
        if self.vehicleAgents == []:
            # Start
            pass
        else:
            # Resume
            time.setSpeed(1.0)
        
        self.signalQueue.putAction("simulationStarted", tuple())
        
    def pauseSimulation(self):
        log.info("simulation paused")
        
        #TODO: pause simulation
        time.setSpeed(0.0)
        
        self.signalQueue.putAction("simulationPaused", tuple())
    
    def stopSimulation(self):
        log.info("simulation stopped")
        
        #TODO: stop simulation
        time.setSpeed(0.0)
        
        for vehicle in self.vehicleAgents:
            self.removeAgent(vehicle)
            
        self.vehicleAgents = []
        
        self.signalQueue.putAction("simulationStopped", tuple())
        
    def spawnVehicle(self, laneId):
        vehicleId = "vehicle%d" % len(self.vehicleAgents)
        self.vehicleAgents.append(vehicleId)
        vehicleLength = 3 + random() * 3
        
        self.mts.ams.create_agent(Vehicle, vehicleId, streetGraph=copy.deepcopy(self.streetGraph), startLane=laneId, startOffset=0)        
        
        laneAID = self.mts.ams.find_agent(laneId)
        spawnMsg = ACLMessage(ACLMessage.REQUEST)
        spawnMsg.protocol = 'spawn-vehicle'
        spawnMsg.content = json.dumps({'type': 'spawn vehicle', 'vehicleId': vehicleId, 'length': vehicleLength})
        spawnMsg.set_conversation_id()
        spawnMsg.receivers.add(laneAID)
        self.send_message(spawnMsg)
        
        class SpawnConfirmReceiver(ReceiveBehaviour):
            def __init__(self, name='', **namedargs):
                template = MessageTemplate(MessageTemplate.CONFIRM)
                template.protocol = spawnMsg.protocol
                template.conversation_id = spawnMsg.conversation_id
                ReceiveBehaviour.__init__(self, name=name, template=template, **namedargs)
                
            def handle_message(self, message):
                #self.agent.agents.append(vehicleId)
                #self.agent.vehicleAgents.append(vehicleId)
                
                log.info("vehicle %s spawned on %s" % (vehicleId, laneId))
                #self.signalQueue.vehicleSpawned(vehicle.getAID())
                self.agent.signalQueue.putAction("vehicleSpawned", (vehicleId,))
                self.set_done()
                
        self.add_behaviour(SpawnConfirmReceiver())

    def getSignalQueue(self):
        return self.__signalQueue
    
    def getSlotQueue(self):
        return self.__slotQueue

    def getQtProxy(self):
        return self.__proxy
        
    def getLock(self):
        return self.__lock
        
    signalQueue = property(getSignalQueue, None, None, None)
    slotQueue = property(getSlotQueue, None, None, None)
    proxy = property(getQtProxy, None, None, None)
    lock = property(getLock, None, None, None)
        
        
def environment():
    return environmentAgent


def environmentProxy():
    return environment().proxy        
