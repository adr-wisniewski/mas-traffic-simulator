'''
Created on Jan 4, 2012

@author: marek
'''

from Queue import Queue
from random import random

from PySide.QtCore import * 
from PySide.QtGui import *
from PySide.QtSvg import *

from graphs import StreetGraph
from agents.Environment import environmentProxy as environment

import logging
log = logging.getLogger("SimulationScene")

JUNCTION_SIZE = StreetGraph.Junction.JUNCTION_SIZE
GFX_SCALE = JUNCTION_SIZE/100.0
LABEL_SCALE = 0.25

class AgentModelItem(QStandardItem):
    def __init__(self, agentId):
        QStandardItem.__init__(self, agentId)
        self.__properties = {}
        self.setProperty("AID", agentId)
        
        self.setSelectable(True)
        self.setEditable(False)
        self.setColumnCount(2)
        
    def setProperty(self, name, value):
        if self.__properties.has_key(name):
            nameItem, valueItem = self.__properties[name]
            valueItem.setText(str(value))
        else:
            nameItem = QStandardItem(name)
            valueItem = QStandardItem(str(value))
            
            self.appendRow( [nameItem, valueItem] )
            self.__properties[name] = (nameItem, valueItem)
            
            nameItem.setEditable(False)
            valueItem.setEditable(False)
        
    def getProperty(self, name):
        return self.__properties[name]

class AgentSceneItem(QObject, QGraphicsItemGroup):
    
    selected = Signal(str, QGraphicsItem)
    
    def __init__(self, agentIds, parent = None, scene = None):
        QObject.__init__(self)
        QGraphicsItemGroup.__init__(self, parent, scene)
        
        self._selected = False
        self.setFlag(self.ItemIsSelectable)

        if type(agentIds) in (str, unicode):
            agentIds = [agentIds,]

        self._agentIds = agentIds
        self._labels = []
        self._modelItems = []
        for agentId in agentIds:
            label = QGraphicsTextItem(agentId)
            self._labels.append(label)
            self.addToGroup(label)
            
            modelItem = AgentModelItem(agentId)
            modelItem.setProperty("AID", agentId)
            self._modelItems.append(modelItem)
            
        self._outline = QGraphicsRectItem()
        self.addToGroup(self._outline)
        
        self._selectedId = self._agentIds[0]
        
        self.setOutlineVisible(self._selected)
        self.setLabelVisible(self._selected)
        
    @Slot(bool)
    def setSelected(self, selected):
        QGraphicsItemGroup.setSelected(self, selected)
        
        if selected:
            self.selected.emit(self.selectedAID(), self)
            
        self.setOutlineVisible(selected)
        self.setLabelVisible(selected)
    
    def setSelectedAID(self, agentId):
        self._selectedId = agentId
        self.setLabelVisible(self.isVisible())
    
    def selectedAID(self):
        return self._selectedId
    
    def AID(self):
        return self._agentIds[0]
    
    def modelItem(self, agentId):
        i = self._agentIds.index(agentId)
        return self._modelItem[i]
    
    def modelItems(self):
        return self._modelItems
    
    def mousePressEvent(self, event):
        self.setSelected(True)
        return QGraphicsItemGroup.mousePressEvent(self, event)
    
    def paint(self, painter, option, widget):
        option.state &= not QStyle.State_Selected
        QGraphicsItemGroup.paint(self, painter, option, widget)
        
    def setLabelVisible(self, visible):
        for label in self._labels:
            if label.toPlainText() == self._selectedId:
                label.setVisible(visible)
            else:
                label.setVisible(False)
        
    def setOutlineVisible(self, visible):
        self._outline.setVisible(visible)
        
    def center(self):
        boundingRect = self.shape().boundingRect()
        return self.pos() + (boundingRect.topLeft() + boundingRect.bottomRight())/2
        
class JunctionItem(AgentSceneItem):
    
    def __init__(self, junction, parent = None, scene = None):
        AgentSceneItem.__init__(self, junction.AID(), parent, scene)
        
        self._junction = junction
        self._junctionItem = None
        
        openIndices = []
        closedIndices = []
        
        for i in range(4):
            if junction._exits[i] == None or junction._exits[i].isClosed():
                closedIndices.append(i)
            else:
                openIndices.append(i)
                
        closedCount = len(closedIndices)
        rotate = 0
        
        if closedCount == 0:
            self._junctionItem = QGraphicsSvgItem(":/gfx/junction/four")
        elif closedCount == 1:
            self._junctionItem = QGraphicsSvgItem(":/gfx/junction/three")
            rotate = closedIndices[0]+1
        elif closedCount == 2:
            
            if closedIndices[1] == closedIndices[0] + 2: 
                self._junctionItem = QGraphicsSvgItem(":/gfx/junction/straight")
                rotate = closedIndices[0]
            else:
                self._junctionItem = QGraphicsSvgItem(":/gfx/junction/bend")
                if openIndices == [0,3]:
                    rotate = -1
                else:
                    rotate = openIndices[0]
                
        elif closedCount == 3:
            self._junctionItem = QGraphicsSvgItem(":/gfx/junction/end")
            rotate = openIndices[0]
        
        self.addToGroup(self._junctionItem)
        
        self._junctionItem.rotate(rotate*-90)
        self._junctionItem.translate(-JUNCTION_SIZE/2, -JUNCTION_SIZE/2)
        self._junctionItem.scale(GFX_SCALE, GFX_SCALE)        
        
        self._labels[0].scale(LABEL_SCALE, LABEL_SCALE)
        self._labels[0].rotate(-45)
        
        self._outline.setParentItem(self._junctionItem)
        #self._outline.setTransform(self._junctionItem.transform())
        self._outline.setRect(self._junctionItem.boundingRect())

        self.setPos(junction.point())
        self._labels[0].setPos(JUNCTION_SIZE/2, -(JUNCTION_SIZE/2 + 4))
        
    def shape(self):
        path = QPainterPath()
        path.addRect(-JUNCTION_SIZE/2, -JUNCTION_SIZE/2, JUNCTION_SIZE, JUNCTION_SIZE)
        return path
        
class RoadItem(AgentSceneItem):
    def __init__(self, road, parent = None, scene = None):
        AgentSceneItem.__init__(self, [road.laneUp().AID(), road.laneDown().AID()], parent, scene)
        
        self._road = road
        self._vertical = True
        
        self._roadItem = QGraphicsSvgItem(":/gfx/road")
        self.addToGroup(self._roadItem)
        
        self._outline.setParentItem(self._roadItem)
        
        startPoint = road.startPoint()
        endPoint   = road.endPoint()
        line = QLineF(startPoint, endPoint)
        self._length = line.length()/JUNCTION_SIZE - 1
        
        if startPoint.y() == endPoint.y():
            #horizontal
            self._roadItem.rotate(90)
            self._vertical = False
            
            self._labels[0].translate(0, 10)
            self._labels[1].translate(0, -10)
            self._labels[0].scale(LABEL_SCALE, LABEL_SCALE)
            self._labels[1].scale(LABEL_SCALE, LABEL_SCALE)
            self._labels[0].translate(-self._labels[0].boundingRect().width()/2, -self._labels[0].boundingRect().height()/2)
            self._labels[1].translate(-self._labels[1].boundingRect().width()/2, -self._labels[1].boundingRect().height()/2)
        else:
            self._labels[0].translate(10, 0)
            self._labels[1].translate(-10, 0)
            self._labels[0].scale(LABEL_SCALE, LABEL_SCALE)
            self._labels[1].scale(LABEL_SCALE, LABEL_SCALE)
            self._labels[0].translate(0, -self._labels[0].boundingRect().height()/2)
            self._labels[1].translate(-self._labels[1].boundingRect().width(), -self._labels[1].boundingRect().height()/2)
            
        
        self._roadItem.scale(1,self._length)
        self._roadItem.translate(-JUNCTION_SIZE/2, -JUNCTION_SIZE/2)
        self._roadItem.scale(GFX_SCALE, GFX_SCALE)
        
        #self._outline.setTransform(self._roadItem.transform())
        self._outline.setRect(self._roadItem.boundingRect())
            
        center = startPoint + (endPoint - startPoint)/2
        self.setPos(center)
        #self._labels[0].setPos(center)
        #self._labels[1].setPos(center)
        
    def mousePressEvent(self, event):
        shape = self.shape()
        center = (shape.boundingRect().topLeft() + shape.boundingRect().bottomRight()) / 2
        
        if self._vertical:
            self.setSelectedAID(self._agentIds[0] if event.pos().x() > center.x() else self._agentIds[1])
        else:
            self.setSelectedAID(self._agentIds[0] if event.pos().y() > center.y() else self._agentIds[1])
        
        return AgentSceneItem.mousePressEvent(self, event)
        
    def shape(self):
        path = QPainterPath()
        
        if self._vertical:
            path.addRect(-JUNCTION_SIZE/2, -(JUNCTION_SIZE+self._length)/2, JUNCTION_SIZE, self._length)
        else:
            path.addRect(-(JUNCTION_SIZE+self._length)/2, -JUNCTION_SIZE/2, self._length, JUNCTION_SIZE)
            
        return path
    
    def length(self):
        return self._road.length()
        
class VehicleItem(AgentSceneItem):
        
    def __init__(self, agentId, parent = None, scene = None):
        AgentSceneItem.__init__(self, agentId, parent, scene)
        
        def shapeOverride():
            path = QPainterPath()
            rect = self._vehicleItem.boundingRect()
            rect.translate(-rect.width()/2, -rect.height()/2)
            path.addRect(rect)
            return path
        
        self._vehicleGroup = QGraphicsItemGroup()
        self._pathGroup = QGraphicsItemGroup()
        self._vehicleGroup.shape = shapeOverride
        self._pathGroup.shape = shapeOverride
        
        self.addToGroup(self._vehicleGroup)
        self.addToGroup(self._pathGroup)
        
        self.removeFromGroup(self._labels[0])
        self._vehicleGroup.addToGroup(self._labels[0])
        self.removeFromGroup(self._outline)
        self._vehicleGroup.addToGroup(self._outline)
        
        #item = QGraphicsSvgItem(":/gfx/car")
        self._vehicleItem = QGraphicsRectItem(0,0, 1.7, 4.2)
        self._targetItem = QGraphicsSvgItem(":/gfx/target")
        self._startItem = QGraphicsSvgItem(":/gfx/start")
        self._path = QPolygonF()
        self._pathItem = QGraphicsPathItem()        
        
        self._vehicleGroup.addToGroup(self._vehicleItem)
        self._pathGroup.addToGroup(self._targetItem)
        self._pathGroup.addToGroup(self._pathItem)
        self._pathGroup.addToGroup(self._startItem)
        self._pathGroup.setVisible(False)
        
        pathPen = QPen(QColor(255,0,0))
        pathPen.setWidth(1)
        pathBrush = QBrush()
        self._pathItem.setPen(pathPen)
        self._pathItem.setBrush(pathBrush)
        
        vehiclePen = QPen(QColor(255,255,255,0))
        vehicleBrush = QBrush(QColor(255,255,255))
        self._vehicleItem.setPen(vehiclePen)
        self._vehicleItem.setBrush(vehicleBrush)
        
        self._targetItem.scale(GFX_SCALE*2, GFX_SCALE*2)
        self._startItem.scale(GFX_SCALE*2, GFX_SCALE*2)
        self._targetItem.translate(-self._targetItem.boundingRect().width()/2, -self._targetItem.boundingRect().height())
        self._startItem.translate(-self._startItem.boundingRect().width()/2, -self._startItem.boundingRect().height())
        
        self._lane = None
        self._position = None
        self._targetLane = None
        self._targetPosition = None
        self._startLane = None
        self._startPosition = None
        self._junction = None
        
    def setSelected(self, selected):
        AgentSceneItem.setSelected(self, selected)
        self._pathGroup.setVisible(selected)
        
    def direction(self):
        if self._lane != None:
            return self._lane.direction()
        return None
                
    def atJunction(self):
        return self._junction != None
                
    def setPosition(self, lane, offset):
        self._lane = lane
        self._junction = None
        self._position = lane.point(offset)
                
        if self._startPosition == None:
            self.setStart(lane, offset)
                
        self._vehicleItem.resetTransform()
        self._vehicleItem.rotate((lane.direction()-2) * -90)
        #self._vehicleItem.scale(GFX_SCALE, GFX_SCALE)
        self._vehicleItem.translate(-self._vehicleItem.rect().width()/2, -self._vehicleItem.rect().height()/2)
        
        self._labels[0].resetTransform()
        self._labels[0].scale(LABEL_SCALE, LABEL_SCALE)
        
        labelBB = self._labels[0].boundingRect()
        labelPlacements = ( QPointF(-labelBB.width(),   -labelBB.height()/2),  #SOUTH
                            QPointF(-labelBB.width()/2, 0),                    #EAST
                            QPointF(0,                  -labelBB.height()/2),  #NORTH
                            QPointF(-labelBB.width()/2, -labelBB.height()) )   #WEST
        direction = self.direction()
        labelPosition = labelPlacements[direction] + StreetGraph.Lane.LANE_ADJUSTMENT_VECTORS[direction]*4
        
        self._labels[0].translate(labelPosition.x(), labelPosition.y())
        
        self._vehicleGroup.setPos(self._position)
        
    def setPositionAtJunction(self, junction, offset, entrance, exit):
        self._junction = junction
        
        entryLane = self._junction.entrance(entrance)
        exitLane  = self._junction.exit(exit)
        entryPoint = entryLane.point(entryLane.length())
        exitPoint  = exitLane.point(0)
        
        self._vehicleGroup.setPos(entryPoint)
        
        if exit == (entrance + 2) % 4:   # straight
            self.setPosition(entryLane, entryLane.length() + offset)
        else:
            self.setPosition(entryLane, entryLane.length())
            self._vehicleItem.resetTransform()
            
            self._vehicleItem.rotate((entryLane.direction()-2) * -90)            
            self._vehicleItem.translate(-self._vehicleItem.rect().width()/2, -self._vehicleItem.rect().height()/2)

            rotateAround = None
            
            if exit == (entrance + 1) % 4: # right turn
                rotateAround = QPointF(4.5/2 + 3,0)
                rotate = 90
            elif exit == (entrance + 3) % 4: # left turn
                rotateAround = QPointF(-4.5/2 - 4.5 -3,0)
                rotate = -90
            elif exit == entrance:           # U-turn
                rotateAround = QPointF(-4.5/2,0)
                rotate = -180
            
            progress = offset/JUNCTION_SIZE
            interpolatedRotation = progress * rotate
            rotateAround += QPointF(self._vehicleItem.rect().width()/2, self._vehicleItem.rect().height()/2)
            
            self._vehicleItem.translate(rotateAround.x(), rotateAround.y())
            self._vehicleItem.rotate(interpolatedRotation)
            self._vehicleItem.translate(-rotateAround.x(), -rotateAround.y())
            
            # adjustment so that two cars turning left from opposite directions dont collide
            self._vehicleItem.translate((2*-abs(0.5 - progress) + 1)*-1, 0)                    
    
    def setStart(self, lane, offset):
        self._startLane = lane
        self._startPosition = lane.point(offset)
        self._startItem.setPos(self._startPosition)
    
    def setTarget(self, lane, offset, junctions = []):
        self._targetLane = lane
        self._targetPosition = lane.point(offset)
        self._targetItem.setPos(self._targetPosition)
        
        self._path.clear()
        if len(junctions) > 0:
            self._path.append(self._startPosition)
            
            if self._startLane.direction() % 2 == 0: #_vertical
                self._path.append(QPointF(self._startPosition.x(),junctions[0].y()))
            else: #horizontal
                self._path.append(QPointF(junctions[0].x(),self._startPosition.y()))
            
            for junction in junctions:
                self._path.append(junction.point())
                
            if self._targetLane.direction() % 2 == 0: #_vertical
                self._path.append(QPointF(self._targetPosition.x(),junctions[-1].y()))
            else: #horizontal
                self._path.append(QPointF(junctions[-1].x(),self._targetPosition.y()))
                
            self._path.append(self._targetPosition)
            
        painterPath = QPainterPath()
        painterPath.addPolygon(self._path)
        self._pathItem.setPath(painterPath)
        
    def center(self):
        return self._position
    
       
class SimulationScene(QGraphicsScene):
    
    agentSelected = Signal(str)
    
    def __init__(self, streetGraph = None, parent = None):
        QGraphicsScene.__init__(self, parent)
        
        self._streetGraph = None
        self._model = QStandardItemModel()
        self._model.setHorizontalHeaderLabels(["Agent/Property", "Property Value"])
        self._agents = {}
        
    def model(self):
        return self._model
        
    def agentItem(self, agentId):
        return self._agents[agentId]
        
    @Slot(str)
    def selectAgent(self, agentId):
        item = self._agents[agentId]
        
        item.setSelectedAID(agentId)
        
        if item in self.selectedItems():
            return
        
        item.setSelected(True)        
        
    def selectedAgent(self):
        for item in self.selectedItems():
            return item.selectedAID()
        
    @Slot(str, QGraphicsItem)
    def _agentSelected(self, agentId, item):
        for selectedItem in self.selectedItems():
            if selectedItem != item:
                selectedItem.setSelected(False)
                
        self.agentSelected.emit(agentId)
        
    def addAgent(self, agentId, item, addItem = True):
        self._agents[agentId] = item
        item.selected.connect(self._agentSelected)
        
        if addItem:
            self.addItem(item)
            for modelItem in item.modelItems():
                self._model.appendRow(modelItem)
        
    def setStreetGraph(self, streetGraph):
        self.clear()
        self._streetGraph = streetGraph
        
        log.info("scene.setStreetGraph begin")
        
        if streetGraph != None:
            streetGraph.load()
            environment().setStreetGraph(streetGraph)
        else:
            environment().setStreetGraph(streetGraph)
            return
        
        log.info("scene.setStreetGraph end")
        
        for junction in streetGraph.junctionsList:
            self.addAgent(junction.AID(), JunctionItem(junction))
            
        i = 0
        for road in self._streetGraph.roadsList:
            roadItem = RoadItem(road)
            self.addAgent(road.laneUp().AID(), roadItem)
            self.addAgent(road.laneDown().AID(), roadItem, addItem = False)
            
            #vehicleUp = VehicleItem("vehicleUp%d@localhost" % i)
            #vehicleUp.setPosition(road.laneUp(),     100 % int(road.laneUp().length()))
            #vehicleUp.setTarget(road.laneDown(),     100 % int(road.laneDown().length()), [road.end(),])
            #i+=1
            
            #vehicleDown = VehicleItem("vehicleDown%d@localhost" % i)
            #vehicleDown.setPosition(road.laneDown(), 100 % int(road.laneDown().length()))
            #vehicleDown.setTarget(road.laneUp(),     100 % int(road.laneUp().length()), [road.start(),])
            #i+=1
            
            #self.addAgent(vehicleUp.AID(), vehicleUp)
            #self.addAgent(vehicleDown.AID(), vehicleDown)

    def mousePressEvent(self, *args, **kwargs):
        for selectedItem in self.selectedItems():
            selectedItem.setSelected(False)
        return QGraphicsScene.mousePressEvent(self, *args, **kwargs)
        
    @Slot()
    def closeSelected(self):
        for item in self.selectedItems():
            environment().setClosed(item.selectedAID(), True)
           
    @Slot() 
    def removeSelected(self):
        for item in self.selectedItems():
            environment().removeAgent(item.selectedAID())
    
    @Slot(int) 
    def setSpeedLimitOnSelected(self, limit):
        for item in self.selectedItems():
            environment().setSpeedLimit(item.selectedAID(), limit)
           
    @Slot() 
    def switchTrafficLightsOnSelected(self):
        for item in self.selectedItems():
            environment().switchTrafficLights(item.selectedAID())    
           
    @Slot()
    def spawnVehicleOnSelected(self):
        for item in self.selectedItems():
            environment().spawnVehicle(item.selectedAID())
            
#    @Slot(float) 
#    def spawnVehicleOnSelected(self, offset = None):
#        if offset == None:
#            offset = random()
#        for item in self.selectedItems():
#            environment().spawnVehicle(item.selectedAID(), offset*item.length())
    
    @Slot(str,tuple)
    def setVehiclePosition(self, vehicleId, position):
        placeId, offset = position[:2]
        lane = self._streetGraph.lane(placeId)
        
        try:
            vehicleItem = self.agentItem(vehicleId)
        except KeyError, e:
            vehicleItem = VehicleItem(vehicleId)
            self.addAgent(vehicleItem.AID(), vehicleItem)
            vehicleItem.setStart(lane, offset)
        
        if lane != None:
            vehicleItem.setPosition(lane, offset)
        else:
            junction = self._streetGraph.junction(placeId)
            vehicleItem.setPositionAtJunction(junction, offset, position[2], position[3])
            
    @Slot(str, tuple, list, tuple)
    def setVehiclePath(self, vehicleId, start, path, target):
        startLane = self._streetGraph.lane(start[0])
        startOffset = start[1]
        targetLane = self._streetGraph.lane(target[0])
        targetOffset = target[1]
        
        try:
            vehicleItem = self.agentItem(vehicleId)
        except KeyError, e:
            vehicleItem = VehicleItem(vehicleId)
            self.addAgent(vehicleItem.AID(), vehicleItem)
            vehicleItem.setPosition(startLane, startOffset)
        
        junctions = []
        for junctionId in path:
            junctions.append(self._streetGraph.junction(junctionId))
        
        vehicleItem.setStart(startLane, startOffset)    
        vehicleItem.setTarget(targetLane, targetOffset, junctions = junctions)
        