'''
Created on Jan 3, 2012

@author: marek
'''

from PySide import QtGui
from PySide import QtCore
from PySide import QtSvg

from agents.Environment import environmentProxy as environment

class SimulationView(QtGui.QGraphicsView):
    
    agentSelected = QtCore.Signal(str)
    zoomChanged = QtCore.Signal(int)
    
    def __init__(self, scene, parent = None):
        QtGui.QGraphicsView.__init__(self, scene, parent)
        self.__zoomLevel = 0
    
    def setScene(self, scene):
        scene.agentSelected.connect(self.agentSelected)
        return QtGui.QGraphicsView.setScene(self, scene)
    
    @QtCore.Slot()
    def zoomIn(self):
        self.setZoom(self.__zoomLevel + 1)
    
    @QtCore.Slot()
    def zoomOut(self):
        self.setZoom(self.__zoomLevel - 1)
    
    @QtCore.Slot(int)
    def setZoom(self, zoomLevel):
        scaleFactor = 2 ** (zoomLevel - self.__zoomLevel)
        self.scale(scaleFactor, scaleFactor)
        self.__zoomLevel = zoomLevel
        self.zoomChanged.emit(self.__zoomLevel)
    
    @QtCore.Slot(str)
    def selectAgent(self, agentId):
        self.scene().selectAgent(agentId)
        
    @QtCore.Slot(str)
    def centerOnAgent(self, agentId):
        agentItem = self.scene().agentItem(agentId)
        self.centerOn(agentItem.center())
    
    
        