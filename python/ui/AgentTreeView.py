'''
Created on Jan 14, 2012

@author: marek
'''

from PySide.QtCore import *
from PySide.QtGui import *

class AgentTreeView(QTreeView):
    agentSelected = Signal(str)
    
    @Slot(str)
    def selectAgent(self, agentId):
        items = self.model().findItems(agentId)
        self.setCurrentIndex(items[0].index())
    
    @Slot(QModelIndex, QModelIndex)
    def currentChanged(self, current, previous):
        QTreeView.currentChanged(self, current, previous)
        
        if current.column() == 0 and not current.parent().isValid():
            item = self.model().itemFromIndex(current)
            self.agentSelected.emit(item.text())
            