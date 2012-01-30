# Generated using Blender.

from StreetGraph import StreetGraph

class Graph_LazyEight(StreetGraph):

    def setupGraph(self):
        self.addJunction('junction0', (263, 131) )
        self.addJunction('junction1', (0, 131) )
        self.addJunction('junction2', (132, 131) )
        self.addJunction('junction3', (263, 0) )
        self.addJunction('junction4', (0, 0) )
        self.addJunction('junction5', (132, 0) )
        self.addRoad('lane0', 'lane1', 2, 'EAST', 0, 'WEST', 131)
        self.addRoad('lane2', 'lane3', 1, 'EAST', 2, 'WEST', 132)
        self.addRoad('lane4', 'lane5', 0, 'NORTH', 3, 'SOUTH', 132)
        self.addRoad('lane6', 'lane7', 1, 'NORTH', 4, 'SOUTH', 132)
        self.addRoad('lane8', 'lane9', 4, 'EAST', 5, 'WEST', 132)
        self.addRoad('lane10', 'lane11', 5, 'EAST', 3, 'WEST', 131)
        self.addRoad('lane12', 'lane13', 2, 'NORTH', 5, 'SOUTH', 132)
