'''
Created on Jan 3, 2012

@author: marek
'''

from PySide.QtCore import *
from PySide.QtGui import QMainWindow
from ui.ui_MainWindow import Ui_MainWindow
from ui.SimulationScene import SimulationScene

from agents.Environment import environmentProxy as environment

class MainWindow(QMainWindow, Ui_MainWindow):
    
    simulationStarted = Signal()
    simulationPaused = Signal()
    simulationStopped = Signal()
    mapLoaded = Signal()
    
    def __init__(self, parent = None):
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.simulationView.agentSelected.connect(self.statusBar().showMessage)
        self.simulationView.agentSelected.connect(self.simulationView.centerOnAgent)
        self.simulationView.agentSelected.connect(self.agentSelected)
    
    @Slot(str)
    def agentSelected(self, agentId):
        #self.actionJunctionClose.setVisible(False)
        #self.actionJunctionSwitchLights.setVisible(False)
        self.actionRoadClose.setVisible(False)
        #self.actionRoadSetSpeedLimit.setVisible(False)
        self.actionRoadSpawnVehicle.setVisible(False)
        self.actionVehicleRemove.setVisible(False)
        
        if agentId.startswith("lane"):
            self.actionRoadClose.setVisible(True)
            self.actionRoadSetSpeedLimit.setVisible(True)
            self.actionRoadSpawnVehicle.setVisible(True)
        elif agentId.startswith("junction"):
            self.actionJunctionClose.setVisible(True)
            self.actionJunctionSwitchLights.setVisible(True)
        elif agentId.startswith("vehicle"):
            self.actionVehicleRemove.setVisible(True)
        else:
            pass
            
    
    def startSimulation(self):
        self.actionSimStart.setVisible(False)
        self.actionSimStart.setEnabled(False)
        self.actionSimPause.setVisible(True)
        self.actionSimPause.setEnabled(True)
        self.actionSimStop.setEnabled(True)
        
        environment().startSimulation()
        
        self.simulationStarted.emit()
    
    def stopSimulation(self):
        self.actionSimStart.setVisible(True)
        self.actionSimStart.setEnabled(True)
        self.actionSimPause.setVisible(False)
        self.actionSimPause.setEnabled(False)
        self.actionSimStop.setEnabled(False)
        
        environment().stopSimulation()
        
        self.simulationStopped.emit()
    
    def pauseSimulation(self):
        self.actionSimStart.setVisible(True)
        self.actionSimStart.setEnabled(True)
        self.actionSimPause.setVisible(False)
        self.actionSimPause.setEnabled(False)
        
        environment().pauseSimulation()
        
        self.simulationPaused.emit()
        
    def loadMap(self):
        self.mapLoaded.emit()
    
