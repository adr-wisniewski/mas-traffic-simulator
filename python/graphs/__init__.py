'''
Created on Jan 4, 2012

@author: marek
'''

import os
from os import path
from StreetGraph import StreetGraph

sampleGraphs = {}

for filename in os.listdir(path.dirname(__file__)):
    if not filename.startswith("graph_") or not filename.endswith(".py"):
        continue
    
    moduleName = filename[:-3]
    graphName = moduleName[len("graph_"):]
    className = "Graph_%s" % graphName
    
    exec("from %s import %s" % (moduleName, className))
    sampleGraphs[graphName] = eval("%s()" % className) 
    