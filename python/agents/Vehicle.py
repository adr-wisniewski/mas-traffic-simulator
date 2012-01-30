'''
Created on Dec 15, 2011

@author: Marek Skrajnowski
'''

from spyse.core.agents.agent import Agent
from spyse.core.behaviours.fsm import State, FSMBehaviour
from spyse.core.content.content import ACLMessage, MessageTemplate

from behaviours import SleepBehaviour, DieBehaviour

from agents.SimTime import time
from heapq import *
from bisect import insort_left

from random import choice, random

import math
import json
from spyse.core.behaviours.behaviours import TickerBehaviour, Behaviour

import logging
from spyse.core.behaviours.composite import SequentialBehaviour
from spyse.core.agents.aid import AID
from graphs.StreetGraph import StreetGraph

def kphToMps(kph):
    return kph/3.6

def distance(tuple1, tuple2):
    if len(tuple1) != len(tuple2):
        raise IndexError("Tuples must be the same length") 
    
    _distance = 0
    for d in range(len(tuple1)):
        _distance += (tuple1[d] - tuple2[d]) ** 2
    return math.sqrt(_distance)

JUNCTION_REACHED = 0
OBSTACLE_REACHED = 1
TARGET_REACHED = 2
NO_OBSTACLE = 3

class Location(object):
    def __init__(self, streetGraph, lane=None, laneId=None, junction=None, junctionId=None, entry=None, exit=None, offset=0):
        assert isinstance(streetGraph, StreetGraph), "streetGraph must be of class StreetGraph"
        assert lane == None or isinstance(lane, StreetGraph.Lane), "lane must be of class StreetGraph.Lane"
        assert junction == None or isinstance(junction, StreetGraph.Junction), "junction must be of class StreetGraph.Junction"
        assert laneId == None or isinstance(laneId, (str, unicode)), "laneId must be a string"
        assert junctionId == None or isinstance(junctionId, (str, unicode)), "junctionId must be a string"
        
        self.streetGraph = streetGraph
        self.laneId = None
        self.lane = None
        self.junctionId = None
        self.junction = None
        self.junctionEntry = entry
        self.junctionExit = exit
        
        if laneId != None or lane != None:
            if laneId != None:
                self.lane = streetGraph.lane(laneId)
                self.laneId = str(laneId)
            else:    
                self.lane = lane
                self.laneId = str(lane.AID())
                
        elif junctionId != None or junction != None:
            if junctionId != None:
                self.junction = streetGraph.junction(junctionId)
                self.junctionId = str(junctionId)
            else:
                self.junction = junction
                self.junctionId = str(junction.AID())
        else:
            raise RuntimeError("No lane or junction specified")
            
        if lane != None and junction != None:
            raise AttributeError("Can't be on both a junction and a lane")
            
        self.offset = offset
        
    def __getOffset(self):
        return self.__offset
    
    def __setOffset(self, offset):
        self.__offset = offset
        self.lastUpdated = time.time()
        
    offset = property(__getOffset, __setOffset)
        
    def isOnStreet(self):
        return self.lane != None
    
    def isAtJunction(self):
        return self.junction != None
    
    def step(self, speed):
        now = time.time()
        self.offset += speed * (now - self.lastUpdated)
        
    def toCoordinates(self, streetGraph=None):
        if streetGraph != None:
            self.streetGraph = streetGraph
            
        if self.streetGraph == None:
            raise AttributeError("No street graph set or passed as argument")
        
        if self.isOnStreet():
            return self.lane.position(self.offset)
        elif self.isAtJunction():
            return self.junction.position()
        else:
            return (0, 0)
        
    def toIdOffset(self):
        if self.isAtJunction():
            return (self.junctionId, self.offset, self.junctionEntry, self.junctionExit)
        return (self.laneId, self.offset)
        
    def distanceFrom(self, coords=None, location=None):
        if coords == None and location == None:
            raise AttributeError("coords or location must be passed as an argument")
        
        if coords == None:
            coords = location.toCoordinates()
            
        myCoords = self.toCoordinates()
        return distance(myCoords, coords)
    
    def getLaneDirection(self):
        return self.lane.direction()
    
    def getLaneOppositeDirection(self):
        return (self.getLaneDirection() + 2) % 4
        
    def __eq__(self, other):
        return self.laneId == other.laneId and self.junctionId == other.junctionId and self.offset == other.offset

class DriveToBehaviour(TickerBehaviour):
            
    ACCELERATING = 1
    DECELERATING = 2
    STOPPED = 3
    MAX_SPEED = 4
    
    
    def setup(self, maxSpeed=kphToMps(100.0), acceleration = kphToMps(20.0), deceleration = kphToMps(20.0)):
        self.speed = 0
        
        self.maxSpeed = maxSpeed
        self.acceleration = acceleration
        self.deceleration = deceleration
        
        self.__checkpoint = None
        self.__checkpointChanged = False
        
        self.brakingDistance = 0
        self.distanceToCheckpoint = 0
        
        self.lastTick = None
        self.state = None
        
    def setCheckpoint(self, checkpoint):
        self.__checkpointChanged = self.__checkpoint != checkpoint
        self.__checkpoint = checkpoint
        
    def getCheckpoint(self):
        return self.__checkpoint
    
    checkpoint = property(getCheckpoint, setCheckpoint)
        
    def starting(self):
        pass
    
    def stopping(self):
        pass
    
    def checkpointReached(self):
        pass
        
    def on_tick(self):
        if self.checkpoint == None:
            return
        
        if self.state == self.STOPPED and not self.__checkpointChanged:
            self.sleep(self.period)
            return
        
        if self.state == self.MAX_SPEED and self.brakingDistance < self.distanceToCheckpoint:
            self.agent.location.step(self.speed)
            self.sleep(self.period)
            return
        
        if self.agent.location.offset < self.checkpoint:
            now = time.time()
            
            if self.lastTick == None:
                self.lastTick = now
                return
            
            dt = now-self.lastTick
            self.lastTick = now
            
            if dt == 0:
                return
            
            increasedSpeed = self.speed + dt * self.acceleration
            self.brakingDistance = (increasedSpeed**2) / (2*self.deceleration)
            self.distanceToCheckpoint = self.checkpoint - self.agent.location.offset
            
            if self.brakingDistance >= self.distanceToCheckpoint:
                self.speed -= dt * self.deceleration
                if self.state != self.DECELERATING:
                    self.state = self.DECELERATING
                    self.stopping()
            else:
                self.speed = increasedSpeed
                if self.state != self.ACCELERATING:
                    self.state = self.ACCELERATING
                    self.starting()
                
            if self.speed > self.maxSpeed:
                self.speed = self.maxSpeed
                if self.state != self.MAX_SPEED:
                    self.state = self.MAX_SPEED
                
            if self.speed < 0:
                self.speed = 0
                
            self.agent.location.step(self.speed)
            
        else:
            if self.state != self.STOPPED:
                self.agent.location.offset = self.checkpoint
                self.speed = 0
                self.state = self.STOPPED
                self.checkpointReached()
                self.checkpoint = None

        # check if drove out of current lane/junction bounds
        location = self.agent.location            
        if location.isOnStreet():
            if location.offset > location.lane.length():
                nextTurn = self.agent.getNextTurn()
                if nextTurn != None:
                    junction, entry, exit = nextTurn
                    self.agent.location = Location(location.streetGraph, junction=junction, entry = entry, exit = exit, offset = location.offset - location.lane.length())
                    self.checkpoint -= location.lane.length()
        else:
            if location.offset > location.junction.JUNCTION_SIZE:
                nextLane = location.junction.exit(location.junctionExit)
                self.agent.location = Location(location.streetGraph, lane=nextLane, offset=location.offset - location.junction.JUNCTION_SIZE )
                self.checkpoint -= location.junction.JUNCTION_SIZE
        
        self.__checkpointChanged = False
            
            
    
class LaneCommunicator(TickerBehaviour):
    def setup(self):
        self.laneId = None
        self.template = MessageTemplate(MessageTemplate.INFORM)
        self.template.protocol = 'next-obstacle'
        self.waitingForReply = False
        self.noObstacles = False
    
    def on_tick(self):
        if self.agent.location.isAtJunction():
            return
        
        if self.laneId != self.agent.location.laneId:
            
            self.laneId = self.agent.location.laneId
            self.waitingForReply = False
            self.noObstacles = False
        
        if self.waitingForReply:
            reply = self.agent.get_message(self.template)
            self.waitingForReply = False
            
            if reply != None and not self.noObstacles:
                content = json.loads(reply.content)
                obstacleOffset = content['obstacle']
                
                #self.agent.log.info("Received obstacle at %s from %s" % (str(obstacleOffset), reply.sender.shortname))
                
                if obstacleOffset == None:
                    self.noObstacles = True
                    obstacleOffset = self.agent.location.lane.length()
                else:
                    obstacleOffset -= self.agent.length
                    
                if self.agent.isOnTargetLane() and self.agent.target.offset < obstacleOffset:
                    obstacleOffset = self.agent.target.offset
            
                self.agent.driveBehaviour.checkpoint = obstacleOffset
        
        if not self.waitingForReply:
            msg = ACLMessage(ACLMessage.REQUEST)
            msg.protocol = self.template.protocol
            msg.set_conversation_id()
            msg.content = json.dumps({'offset': self.agent.location.offset})
            laneAID = AID(self.laneId)
            msg.receivers.add(laneAID)
            
            self.template.conversation_id = msg.conversation_id
            
            self.agent.send_message(msg)
            self.waitingForReply = True
            
            #self.agent.log.info("Sent obstacle request to %s" % self.laneId)
      

class JunctionCommunicator(TickerBehaviour):
    ON_STREET = 0
    WAITING = 1
    ENTERING_JUNCTION = 2
    AT_JUNCTION = 3
    
    def setup(self):
        self.state = self.ON_STREET
        self.permissionTemplate = MessageTemplate(MessageTemplate.AGREE)
        self.protocol = 'junction'
        self.turn = None
    
    def on_tick(self):
        if self.state == self.WAITING:
            msg = self.agent.get_message(self.permissionTemplate)
            if msg != None:
                self.agent.log.info("Permission received")
                self.state = self.ENTERING_JUNCTION
                self.agent.driveBehaviour.checkpoint += StreetGraph.Junction.JUNCTION_SIZE+1
        elif self.state == self.ENTERING_JUNCTION:
            if self.agent.location.isAtJunction():
                self.state = self.AT_JUNCTION
                msg = ACLMessage(ACLMessage.INFORM)
                msg.protocol = 'vehicle-left'
                junction, entry, exit = self.turn
                msg.receivers.add(AID(junction.entrance(entry).AID()))
                self.agent.send_message(msg)
        elif self.state == self.AT_JUNCTION:
            if self.agent.location.isOnStreet():
                msg = ACLMessage(ACLMessage.CONFIRM)
                msg.protocol = 'junction'
                junction, entry, exit = self.turn
                msg.receivers.add(AID(junction.AID()))
                self.agent.send_message(msg)
                self.state = self.ON_STREET
        else:
            if self.agent.location.isAtJunction():
                self.sleep(0.01)
                return
            
            if self.agent.driveBehaviour.checkpoint != self.agent.location.lane.length():
                self.sleep(0.01)
                return
            
            location = self.agent.location
            distanceToJunction = location.lane.length() - location.offset 
            
            if distanceToJunction < 50 and not self.state == self.WAITING:
                self.turn = self.agent.getNextTurn()
                junction, entry, exit = self.turn
                
                msg = ACLMessage(ACLMessage.REQUEST)
                msg.protocol = 'junction'
                msg.content = json.dumps({'entry': entry, 'exit': exit, 'length': self.agent.length})
                msg.receivers.add(AID(str(junction.AID())))
                self.agent.send_message(msg)
                self.state = self.WAITING
                self.agent.log.info("Sent request to %s, entry %d, exit %d" % (junction.AID(), entry, exit))
                
        self.sleep(0.01)      
            
class ReportPositionBehaviour(TickerBehaviour):
    def setup(self):
        TickerBehaviour.setup(self)
        self.lastLocationUpdate = 0
        
    def on_tick(self):
        location = self.agent.location 
        if location.lastUpdated > self.lastLocationUpdate:
            msg = ACLMessage(ACLMessage.INFORM)
            msg.protocol = 'vehicle-status-update'
            msg.content = json.dumps({'type': 'position update', 'position': self.agent.location.toIdOffset()})
            msg.receivers.add(self.agent.environmentAID)
            msg.receivers.add(self.agent.laneAID)
            self.agent.send_message(msg)
            self.lastLocationUpdate = location.lastUpdated
    
            
class CalculatePathBehaviour(Behaviour):
    def action(self):
        self.agent.path, self.agent.pathDistance = self.agent.calculatePath(self.agent.target)
        pathIds = []
        for (junction, direction) in self.agent.path:
            pathIds.append(junction.AID())
        
        self.agent.nextTurnIndex = 0
        
        pathMsg = ACLMessage(ACLMessage.INFORM)
        pathMsg.protocol = 'vehicle-status-update'
        pathMsg.content = json.dumps({'type': 'path update', 'start': self.agent.start.toIdOffset(), 'target': self.agent.target.toIdOffset(), 'path': pathIds})
        pathMsg.receivers.add(self.agent.environmentAID)
        self.agent.send_message(pathMsg)
        
        self.set_done()
            
class Vehicle(Agent):
    '''
    classdocs
    '''
    
    def setup(self, streetGraph=None, startLane=None, startOffset=0, targetLane=None, targetOffset=0, length=4.0):
        self.log = logging.getLogger(self.name)
        
        self.environmentAID = self.mts.ams.find_agent("environment")
        self.laneAID = self.mts.ams.find_agent(startLane)
        
        self.streetGraph = streetGraph
        
        if targetLane == None:
            lanes = self.streetGraph.lanesList
            randomLane = choice(lanes)
            targetOffset = random() * randomLane.length()
            targetLane = randomLane.AID()
            
        self.target = Location(streetGraph, laneId=targetLane, offset=targetOffset)
        self.start = Location(streetGraph, laneId=startLane, offset=startOffset)
        self.location = self.start
        self.startTime = time.time()
        self.endTime = None
        self.path = []
        self.pathDistance = 0
        self.pathsCalculated = 0
        
        self.length = length
        
        # calculate initial path
        
        self.add_behaviour(DieBehaviour())
        
        self.add_behaviour(CalculatePathBehaviour())
        self.add_behaviour(ReportPositionBehaviour(period=0.1))
        self.add_behaviour(LaneCommunicator(period=1.0))
        self.add_behaviour(JunctionCommunicator(period=1.0))
        
        self.driveBehaviour = DriveToBehaviour(period=0.1)
        self.driveBehaviour.checkpoint = 0
        self.add_behaviour(self.driveBehaviour) 
        
    def calculatePath(self, targetLocation):
        start = self.location
        if start == targetLocation:
            return [start.laneId]
        
        self.pathsCalculated += 1
        pathsCalculated = self.pathsCalculated
        targetCoords = targetLocation.toCoordinates()
        
        self.log.info("Calculating path from %s to %s" % (start.laneId, targetLocation.laneId))
        
        class JunctionDistancePair(object):
            def __init__(self, junction, previousTurn=None, distanceFrom=0.0):
                global distance
                self.pathId = pathsCalculated
                self.junction = junction
                self.junction.pathPair = self
                position = junction.position()
                self.distanceTo = distance(position, targetCoords)
                self.distanceFrom = distanceFrom
                self.previousTurn = previousTurn
                self.visited = False
                
            @classmethod
            def getPair(cls, junction):
                if hasattr(junction, "pathPair") and junction.pathPair.pathId == pathsCalculated:
                    return junction.pathPair
                return None
                
            def update(self, previousTurn, distanceFrom):
                if distanceFrom < self.distanceFrom:
                    self.previousTurn = previousTurn
                    self.distanceFrom = distanceFrom
            
            def getDistance(self):
                return self.distanceFrom + self.distanceTo
            distance = property(getDistance)
            
            def __cmp__(self, other):
                if other == None:
                    return 1
                return cmp(self.distance, other.distance)
        
        junctionQueue = []
                
        if start.isAtJunction():
            junctionQueue.append(JunctionDistancePair(start.junction))
        else:
            junctionQueue.append(JunctionDistancePair(start.lane.end(), (None, start.lane.direction())))
            
        while junctionQueue != []:
            pair = junctionQueue.pop(0)
            
            #self.log.info("Visited %s, from %d, junctionQueue: %s" % (pair.junction.AID(), (pair.previousTurn[1]+2) % 4, str(map(lambda p: p.junction.AID(), junctionQueue))) )
            
            if pair.visited:
                continue
            
            pair.visited = True
            
            for i in range(len(pair.junction.exits())):
                lane = pair.junction.exit(i)
                if lane == None:
                    continue
                
                if lane == targetLocation.lane:
                    # HURAAA!
                    # build path
                    path = [(pair.junction, i), ]
                    distance = pair.distance
                    #self.log.info("Found target %s" % lane.AID())
                    while pair.previousTurn != None and pair.previousTurn[0] != None:
                        self.log.info("Pair %s %d %f" % (pair.junction.AID(), i, pair.distance))
                        path.append(pair.previousTurn)
                        pair = pair.previousTurn[0].pathPair
                    path.reverse()
                    #self.log.info("Found path: %s" % str(path))
                    return path, distance
                
                newJunction = lane.end()
                direction = (lane.direction()+2) % 4
                    
                
                newPair = JunctionDistancePair.getPair(newJunction)
                
                if newPair == None:
                    newPair = JunctionDistancePair(lane.end(), (pair.junction, i), pair.distanceFrom + lane.length())
                    #self.log.info("Adding %s, to the queue" % newJunction.AID())
                else:
                    newPair.update((pair.junction, i), pair.distanceFrom + lane.length())
                    #self.log.info("Updating %s, to the queue" % newJunction.AID())
                
                inserted = False     
                for i in range(len(junctionQueue)):
                    if newPair.getDistance() < junctionQueue[i].getDistance():
                        junctionQueue.insert(i, newPair)
                        inserted = True
                        break
                    
                if not inserted:
                    junctionQueue.append(newPair)
                
        return None
    
    def isOnStreet(self):
        return self.location.isOnStreet()
    
    def isAtJunction(self):
        return self.location.isAtJunction()
    
    def isOnTargetLane(self):
        return self.location.laneId == self.target.laneId

    def getNextTurn(self):
        if self.location.isAtJunction():
            lane = self.location.junction.exit(self.location.junctionExit)
        else:
            lane = self.location.lane
            
        nextJunction = lane.end()
        entry = (lane.direction() + 2) % 4
            
        for i in range(len(self.path)):
            junction, exit = self.path[i]
            if junction == nextJunction:
                return junction, entry, exit
        return None

    def getNextLane(self):
        junction, direction = self.path[self.nextTurnIndex]
        return junction.exit(direction)
