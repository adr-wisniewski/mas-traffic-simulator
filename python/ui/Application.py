'''
Created on Jan 11, 2012

@author: marek
'''

import sys
from PySide.QtGui import QApplication
from ui.MainWindow import MainWindow
from ui.SimulationScene import SimulationScene
from graphs.graph_WarszawaCentrum import Graph_WarszawaCentrum
from graphs import sampleGraphs
from agents.Environment import environmentProxy as environment


_application = None


def application():
    global _application
    if _application == None:
        _application = Application()
    return _application


class Application(QApplication):

    def __init__(self):
        global _application
        if _application != None:
            raise Exception("Qt application already created")
        
        QApplication.__init__(self, sys.argv)
        self.mainWindow = MainWindow()
        self.mainWindow.show()
        self.scene = SimulationScene()
         
        self.mainWindow.simulationView.setScene(self.scene)
        self.mainWindow.agentTree.setModel(self.scene.model())
        self.mainWindow.actionQuit.triggered.connect(self.quit)
        
        self.mainWindow.actionRoadClose.triggered.connect(self.scene.closeSelected)
        self.mainWindow.actionJunctionClose.triggered.connect(self.scene.closeSelected)
        self.mainWindow.actionVehicleRemove.triggered.connect(self.scene.removeSelected)
        self.mainWindow.actionJunctionSwitchLights.triggered.connect(self.scene.switchTrafficLightsOnSelected)
        self.mainWindow.actionRoadSpawnVehicle.triggered.connect(self.scene.spawnVehicleOnSelected)
    
        application = self

    def getStreetGraph(self):
        return self.__streetGraph
    
    def setStreetGraph(self, value):
        self.__streetGraph = value

    def getScene(self):
        return self.__scene
    
    def setScene(self, value):
        self.__scene = value

    def getMainWindow(self):
        return self.__mainWindow
    
    def setMainWindow(self, value):
        self.__mainWindow = value

    mainWindow = property(getMainWindow, setMainWindow, None, None)
    scene = property(getScene, setScene, None, None)
    streetGraph = property(getStreetGraph, setStreetGraph, None, None)
        
        