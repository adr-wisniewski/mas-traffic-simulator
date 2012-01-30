'''
Created on Jan 19, 2012

@author: marek
'''

import sys
from agents.Environment import environment, environmentProxy, Environment
from ui.Application import application as qtApplication
from spyse.app.app import App as SpyseApplication
from graphs import sampleGraphs
from spyse.core.platform.platform import Platform

_application = None


def application():
    global _application
    if _application == None:
        #_application = Application(threading = 'pool', poolsize = 50)
        _application = Application()
    return _application


class Application(SpyseApplication):
    def __init__(self, port=SpyseApplication.DEFAULT_PORT,
                 distribution=None,
                 env='normal',
                 ns=None,
                 poolsize=SpyseApplication.DEFAULT_POOLSIZE,
                 threading=None):
        
        global _application
        if _application != None:
            raise Exception("Spyse application already created")
        
        SpyseApplication.__init__(self, port=port, distribution=distribution, env=env, ns=ns, poolsize=poolsize, threading=threading)
    
    def run(self, args):
        qtApp = qtApplication()
        
        # start environment
        self.start_agent(Environment, 'environment')
        streetGraph = sampleGraphs["LazyEight"]
        #streetGraph = sampleGraphs["WarszawaCentrum"]
        qtApp.scene.setStreetGraph(streetGraph)
        
        environmentProxy().vehiclePositionUpdated.connect(qtApp.scene.setVehiclePosition)
        environmentProxy().vehiclePathUpdated.connect(qtApp.scene.setVehiclePath)
        
        qtApp.exec_()
        
        # shutdown environment
        environment().die()
        Platform.running = False
        
        
        
        