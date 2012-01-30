'''
Created on Jan 13, 2012

@author: marek
'''

from Queue import Queue
from PySide.QtCore import *
from util.ActionQueue import ActionQueue
from graphs.StreetGraph import StreetGraph
import graphs

import logging
log = logging.getLogger("EnvironmentProxy")

class EnvironmentProxy(QObject):

    # Environment signals
    agentRemoved = Signal(str)
    
    agentClosed = Signal(str, bool)
    streetGraphLoaded = Signal(str)
    laneSpeedLimitChanged = Signal(str, int)
    trafficLightsSwitched = Signal(str)
    
    simulationStarted = Signal()
    simulationStopped = Signal()
    simulationPaused = Signal()
    
    vehicleSpawned = Signal(str)
    vehiclePositionUpdated = Signal(str,tuple) #id, position
    vehiclePathUpdated = Signal(str,tuple,list,tuple) #id, start, path, target
    vehicleReachedTarget = Signal(str) #id
    
    
    
    def __init__(self, environmentAgent):
        QObject.__init__(self)
        self.environment = environmentAgent
        
        self.signalQueue = environmentAgent.signalQueue
        self.slotQueue = environmentAgent.slotQueue
        
        self.emitTimer = QTimer()
        self.emitTimer.start(0)
        self.emitTimer.timeout.connect(self.emitSignals)
        
    @Slot()
    def emitSignals(self):
        action = self.signalQueue.getAction(block=False)
        while action != None:
            signal, args = action
            
            getattr(self, signal).emit(*args)
            self.signalQueue.task_done()
            
            action = self.signalQueue.getAction(block=False)
            
            
    @Slot(str)
    @Slot(StreetGraph)
    def setStreetGraph(self, streetGraph):
        log.info("proxy.setStreetGraph begin")
        
        if type(streetGraph) == str:
            streetGraph = graphs.sampleGraphs[streetGraph]
        #self.slotQueue.setStreetGraph(streetGraph)
        self.slotQueue.putAction("setStreetGraph", (streetGraph,))
        
        log.info("proxy.setStreetGraph end")
            
    @Slot(str, bool)
    def setClosed(self, laneId, closed = True):
        #self.slotQueue.setClosed(laneId, closed)
        self.slotQueue.putAction("setClosed", (laneId, closed))
        
    @Slot(str, int)    
    def setSpeedLimit(self, laneId, limit):
        #self.slotQueue.setSpeedLimit(laneId, limit)
        self.slotQueue.putAction("setSpeedLimit", (laneId, limit))
    
    @Slot(str)
    def switchTrafficLights(self, junctionId):
        #self.slotQueue.switchTrafficLights(junctionId)
        self.slotQueue.putAction("switchTrafficLights", (junctionId, ))
        
    @Slot(str)
    def removeAgent(self, agentId):
        #self.slotQueue.removeAgent(agentId)
        self.slotQueue.putAction("removeAgent", (agentId, ))
        
    @Slot()
    def startSimulation(self):
        #self.slotQueue.startSimulation()
        self.slotQueue.putAction("startSimulation", tuple())
        
    @Slot()
    def pauseSimulation(self):
        #self.slotQueue.pauseSimulation()
        self.slotQueue.putAction("pauseSimulation", tuple())
    
    @Slot()
    def stopSimulation(self):
        #self.slotQueue.stopSimulation
        self.slotQueue.putAction("stopSimulation", tuple())
        
    @Slot(float)
    def setSimulationSpeed(self, speed):
        self.slotQueue.putAction("setSimulationSpeed", (speed,))
        
    @Slot(str)
    @Slot(str, int)
    def spawnVehicle(self, laneId, offset = 0):
        #self.slotQueue.putAction("spawnVehicle", (laneId, offset))
        self.slotQueue.putAction("spawnVehicle", (laneId, ))
    
    
    