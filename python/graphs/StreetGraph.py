'''
Created on Jan 4, 2012

@author: marek
'''

from PySide import QtCore

DIRECTIONS = {'SOUTH': 0, 'EAST': 1, 'NORTH': 2, 'WEST': 3,
              'S': 0, 'E': 1, 'N': 2, 'W': 3,
              0: 0, 1: 1, 2: 2, 3: 3}

DIRECTION_VECTORS = (QtCore.QPointF( 0, 1),   # SOUTH
                     QtCore.QPointF( 1, 0),   # EAST
                     QtCore.QPointF( 0,-1),   # NORTH
                     QtCore.QPointF(-1, 0),)  # WEST


class StreetGraph(object):

    class Node(object):
        def __init__(self, agentId):
            self._agentId = agentId
            self._closed = False
            
        def AID(self):
            return self._agentId
            
        def isClosed(self):
            return self._closed
        
        def setClosed(self, closed):
            self._closed = closed
            
    class Junction(Node):
        
        JUNCTION_SIZE = 15.0
        
        def __init__(self, agentId):
            StreetGraph.Node.__init__(self, agentId)
            self._exits = [None,]*4
            self._entrances = [None,]*4
            self._position = (0,0)
        
        def setExit(self, direction, road):
            self._exits[ DIRECTIONS[direction] ] = road
            
        def exits(self):
            return self._exits
            
        def exit(self, direction):
            return self._exits[ DIRECTIONS[direction] ]
            
        def setEntrance(self, direction, road):
            self._entrances[ DIRECTIONS[direction] ] = road
            
        def entrances(self):
            return self._entrances    
        
        def entrance(self, direction):
            return self._entrances[ DIRECTIONS[direction] ]
            
        def position(self):
            return self._position
        
        def point(self):
            return QtCore.QPointF(self._position[0], self._position[1])
            
        def setPosition(self, position):
            self._position = position
            
        def x(self):
            return self._position[0]
        
        def y(self):
            return self._position[1]
    
    class Lane(Node):
        
        LANE_WIDTH = 4.5
        LANE_ADJUSTMENT_VECTORS = (QtCore.QPointF(-LANE_WIDTH/2, 0),  # SOUTH
                                   QtCore.QPointF(0, LANE_WIDTH/2),   # EAST
                                   QtCore.QPointF(LANE_WIDTH/2, 0),   # NORTH
                                   QtCore.QPointF(0, -LANE_WIDTH/2) ) # WEST

        
        def __init__(self, agentId, start, end):
            StreetGraph.Node.__init__(self, agentId)
            self._start = start
            self._end = end
            self._road = None
            self._direction = 0 
            
        def start(self):
            return self._start
        
        def startPoint(self):
            return self._start.point() 
        
        def setStart(self, junction):
            self._start = junction

        def end(self):
            return self._end
        
        def endPoint(self):
            return self._end.point()
        
        def setEnd(self, junction):
            self._end = junction
            
        def speedLimit(self):
            return self._road.speedLimit()
            
        def length(self):
            return self._road.length()
        
        def direction(self):
            return self._direction
        
        def position(self, offset):
            point = self.point(offset)
            return (point.x(), point.y())
        
        def point(self, offset):
            offsetVector = DIRECTION_VECTORS[self._direction] * offset
            laneAdjustmentVector = self.LANE_ADJUSTMENT_VECTORS[self._direction]
            junctionOffset = DIRECTION_VECTORS[self._direction] * StreetGraph.Junction.JUNCTION_SIZE/2.0
            return self.startPoint() + offsetVector + laneAdjustmentVector + junctionOffset
            
    class Road(object):
        
        ROAD_WIDTH = 9
        
        def __init__(self, start, end, length, direction):
            self._start = start
            self._end = end
            self._length = length
            self._speedLimit = 50
            
            self._laneUp = None
            self._laneDown = None
            self._direction = DIRECTIONS[direction]
            
        def setLaneUp(self, lane):
            self._laneUp = lane
            self._laneUp._direction = self._direction
            
        def setLaneDown(self, lane):
            self._laneDown = lane
            self._laneDown._direction = (self._direction+2) % 4

        def newLaneUp(self, laneAID):
            lane = StreetGraph.Lane(laneAID, self._start, self._end)
            lane._road = self
            self.setLaneUp(lane)
            return lane

        def newLaneDown(self, laneAID):
            lane = StreetGraph.Lane(laneAID, self._end, self._start)
            lane._road = self
            self.setLaneDown(lane)
            return lane

        def laneUp(self):
            return self._laneUp
        
        def laneDown(self):
            return self._laneDown

        def start(self):
            return self._start
        
        def startPoint(self):
            return self._start.point()
        
        def setStart(self, junction):
            self._start = junction

        def end(self):
            return self._end
        
        def endPoint(self):
            return self._end.point()
        
        def setEnd(self, junction):
            self._end = junction
            
        def speedLimit(self):
            return self._speedLimit
        
        def setSpeedLimit(self, limit):
            self._speedLimit = limit
            
        def direction(self):
            return self._direction
            
        def length(self):
            return self._length
        
        def setLength(self, length):
            self._length = length
   
    def __init__(self):
        self.junctionsList = []
        self.junctionsDict = {}
        self.roadsList = []
        self.lanesList = []
        self.lanesDict = {}

    def isLoaded(self):
        return len(self.lanesList) > 0
    
    def load(self):
        if not self.isLoaded():
            self.setupGraph()

    def junction(self, junctionId):
        try:
            if type(junctionId) == int:
                return self.junctionsList[junctionId]
            elif type(junctionId) in (str, unicode):
                return self.junctionsDict[junctionId]
        except KeyError:
            return None
        
        raise KeyError("Junction id has to be either an integer or string.")

    def road(self, roadId):
        try:
            if type(roadId) == int:
                return self.roadsList[roadId]
        #elif type(roadId) == str:
        #    return self.roadsDict[roadId]
        except KeyError:
            return None
        
        raise KeyError("Road id has to be an integer")
        
    def lane(self, laneId):
        try:
            if type(laneId) == int:
                return self.lanesList[laneId]
            elif type(laneId) in (str, unicode):
                return self.lanesDict[laneId]
        except KeyError:
            return None
        
        raise KeyError("Lane id has to be either an integer or string.")

    def addJunction(self, junctionAID, position):
        junction = self.Junction(junctionAID)
        junction.setPosition(position)
        self.junctionsList.append(junction)
        self.junctionsDict[junctionAID] = junction
    
    def addRoad(self, laneUpAID, laneDownAID, startId, startDirection, endId, endDirection, length):
        
        start = self.junction(startId)
        end = self.junction(endId)

        road = self.Road(start, end, length - self.Junction.JUNCTION_SIZE, startDirection)
        
        laneUp = road.newLaneUp(laneUpAID)
        laneDown = road.newLaneDown(laneDownAID)
        
        start.setExit(startDirection, laneUp)
        end.setEntrance(endDirection, laneUp)
        
        end.setExit(endDirection, laneDown)
        start.setEntrance(startDirection, laneDown)
        
        self.roadsList.append(road)
        self.lanesList.append(laneUp)
        self.lanesList.append(laneDown)
        self.lanesDict[laneUpAID] = laneUp
        self.lanesDict[laneDownAID] = laneDown
        
