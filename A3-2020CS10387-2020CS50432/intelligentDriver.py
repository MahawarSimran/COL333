'''
Licensing Information: Please do not distribute or publish solutions to this
project. You are free to use and extend Driverless Car for educational
purposes. The Driverless Car project was developed at Stanford, primarily by
Chris Piech (piech@cs.stanford.edu). It was inspired by the Pacman projects.
'''
import util
import random
import itertools
from turtle import Vec2D
from engine.const import Const
from engine.vector import Vec2d
from engine.model.car.car import Car
from engine.model.layout import Layout
from engine.model.car.junior import Junior
from configparser import InterpolationMissingOptionError

# Class: Graph
# -------------
# Utility class
class Graph(object):
    def __init__(self, nodes, edges,bt):
        self.nodes = nodes
        self.edges = edges
        self.btiles=bt
    def getAdjacent(self,node):
            if(node not in self.nodes):
                print("Hello--------------------------------")
                x, y = node[0], node[1]
                adjNodes = [(x, y-1), (x, y+1), (x-1, y), (x+1, y)] 
                # only keep allowed (within boundary) adjacent nodes
                adjacentNodes = []
                for tile in adjNodes:
                    if tile in self.nodes:
                        adjacentNodes.append(tile)
                return adjacentNodes

            else:
                x, y = node[0], node[1]
                adjNodes = [(x, y-1), (x, y+1), (x-1, y), (x+1, y)] 
                # only keep allowed (within boundary) adjacent nodes
                adjacentNodes = []
                for tile in adjNodes:
                    if (node, tile) in self.edges:
                        adjacentNodes.append(tile)
                return adjacentNodes

# Class: IntelligentDriver
# ---------------------
# An intelligent driver that avoids collisions while visiting the given goal locations (or checkpoints) sequentially. 
class IntelligentDriver(Junior):
   
    count = 0

    # Funciton: Init
    def __init__(self, layout: Layout):
        self.burnInIterations = 30
        self.layout = layout 
        # self.worldGraph = None
        self.worldGraph = self.createWorldGraph()
        self.checkPoints = self.layout.getCheckPoints() # a list of single tile locations corresponding to each checkpoint
        self.transProb = util.loadTransProb()
        
    # ONE POSSIBLE WAY OF REPRESENTING THE GRID WORLD. FEEL FREE TO CREATE YOUR OWN REPRESENTATION.
    # Function: Create World Graph
    # ---------------------
    # Using self.layout of IntelligentDriver, create a graph representing the given layout.
    def createWorldGraph(self):
        nodes = []
        edges = []
        # create self.worldGraph using self.layout
        numCols, numRows = self.layout.getBeliefCols(), self.layout.getBeliefRows()
        print(numCols, numRows)

        # NODES #
        ## each tile represents a node
        nodes = [(x, y) for x, y in itertools.product(range(numCols), range(numRows))]
        
        # EDGES #
        ## We create an edge between adjacent nodes (nodes at a distance of 1 tile)
        ## avoid the tiles representing walls or blocks#
        ## YOU MAY WANT DIFFERENT NODE CONNECTIONS FOR YOUR OWN IMPLEMENTATION,
        ## FEEL FREE TO MODIFY THE EDGES ACCORDINGLY.

        ## Get the tiles corresponding to the blocks (or obstacles):
        blocks = self.layout.getBlockData()
        blockTiles = []
        paddedTiles= []
        for block in blocks:
            row1, col1, row2, col2 = block[1], block[0], block[3], block[2]
            print('This', row1, col1, row2, col2)
            # some padding to ensure the AutoCar doesn't crash into the blocks due to its size. (optional)
            row1, col1, row2, col2 = row1-1, col1-1, row2+1, col2+1
            blockWidth = col2-col1 
            blockHeight = row2-row1 


            for i in range(blockHeight):
                for j in range(blockWidth):
                    blockTile = (col1+j, row1+i)
                    blockTiles.append(blockTile)

            # for i in range(blockHeight):
            #     for j in range(blockWidth):
            #         tile=(col1-1,row1-1+i)
            #         if tile not in paddedTiles

            # for i in range(blockHeight):
            #     tempNodeStart = (col1, row1+i)
            #     tempNodeEnd = (col1-1, row1+i)
            #     if tempNodeEnd not in blockTiles:
            #         edges.append((tempNodeStart, tempNodeEnd))

            #     tempNodeStart = (col2-1, row1+i)
            #     tempNodeEnd = (col2, row1+i)
            #     if tempNodeEnd not in blockTiles:
            #         edges.append((tempNodeStart, tempNodeEnd))

            # for i in range(blockWidth):
            #     tempNodeStart = (col1+i, row1)
            #     tempNodeEnd = (col1+i, row1-1)
            #     if tempNodeEnd not in blockTiles:
            #         edges.append((tempNodeStart, tempNodeEnd))

            #     tempNodeStart = (col2+i, row2-1)
            #     tempNodeEnd = (col2+i, row2)
            #     if tempNodeEnd not in blockTiles:
            #         edges.append((tempNodeStart, tempNodeEnd))
        print(edges)
        ## Remove blockTiles from 'nodes'
        nodes = [x for x in nodes if x not in blockTiles]
        # print(blockTiles)

        for node in nodes:
            x, y = node[0], node[1]
            adjNodes = [(x, y-1), (x, y+1), (x-1, y), (x+1, y)]
            
            # only keep allowed (within boundary) adjacent nodes
            adjacentNodes = []
            for tile in adjNodes:
                if tile[0]>=0 and tile[1]>=0 and tile[0]<numCols and tile[1]<numRows:
                    if tile not in blockTiles:
                        adjacentNodes.append(tile)

            for tile in adjacentNodes:
                edges.append((node, tile))
                edges.append((tile, node))
        print(edges)
        print(blockTiles)
        return Graph(nodes, edges,blockTiles)
    
      #######################################################################################
    PARK_PROB=0.5
    PROB_TOTAL=0.005
    PROB=0.001

    def probCloseToMovingCars(self, beliefOfMovingCars: list, pos: tuple):
        # All 4 direction and self position
        p = 0
        for car in beliefOfMovingCars:
            p += car.getProb(pos[1], pos[0])  # row - 1 - y 
        return p/len(beliefOfMovingCars)

    def probCloseToParkedCars(self, beliefOfParkedCars: list, pos: tuple):
        p = 0
        for car in beliefOfParkedCars:
            p = max(p, car.getProb(pos[1], pos[0]))  # row - 1 - y 
        return p

    def probCloseToCar(self,movingCars,parkedCars,pos):
        return self.probCloseToMovingCars(movingCars,pos)+self.probCloseToParkedCars(parkedCars,pos)
    def isCloseToUnParkedCar(self,movingCars,pos):
        print("P("+str(pos)+"): ",self.probCloseToMovingCars(movingCars,pos))
        return self.probCloseToMovingCars(movingCars,pos)>=self.PROB
    
    def isCloseToParkedCar(self,parkedCars,pos):
        return self.probCloseToParkedCars(parkedCars,pos)>=self.PARK_PROB
    #######################################################################################
    # Function: Get Next Goal Position
    # ---------------------
    # Given the current belief about where other cars are and a graph of how
    # one can driver around the world, chose the next position.
    #######################################################################################
    # def isCloseToOtherCar(self, beliefOfOtherCars, pos):
    #     newBounds = []
    #     offset = self.dir.normalized() * 1.5 * Car.LENGTH
    #     newPos = self.pos + offset
    #     row = util.yToRow(newPos.y)
    #     col = util.xToCol(newPos.x)
    #     p = beliefOfOtherCars[pos].getProb(row, col)
    #     # print('Car', pos, row, col, p)
    #     return p > IntelligentDriver.MIN_PROB
    def getgridpos(self,pos):
        a=util.xToCol(pos.x)
        b=util.yToRow(pos.y)
        return (a,b)
    def Sort_Tuple(self, tup):
        return(sorted(tup, key = lambda x: x[1]))

   

    def getCost(self,start,goal):
        x0=start[0]
        y0=start[1]
        x1=goal[0]
        y1=goal[1]
        return (x0 - x1) ** 2 + (y0 - y1) ** 2

    def getNextGoalPos(self, beliefOfOtherCars: list, parkedCars:list , chkPtsSoFar: int):
        Parked=[]



        #---------------------------------------------------
        # Making separate lists for Parked and unparked cars
        NotParked=[]
        for i in range(len(parkedCars)):
            print(beliefOfOtherCars[i].grid)
            if(parkedCars[i]):
                Parked.append(beliefOfOtherCars[i])
            else:
                NotParked.append(beliefOfOtherCars[i]) 
        #--------------------------------------------------
        # All adjacent states to current position
        currPos = self.pos
        gPos=self.getgridpos(currPos)
        neighbours = self.worldGraph.getAdjacent(gPos)
        print(neighbours)
        #--------------------------------------------------

        goalPos = self.checkPoints[chkPtsSoFar]  # goal to reach
        
        Dist = []
        for neighbour in neighbours:
            d = self.getCost(goalPos,neighbour)
            Dist.append((neighbour, d))
        Dist = self.Sort_Tuple(Dist)
        NextPos = [x for (x,y) in Dist]
        NextPos = NextPos + [gPos]            # all next position reachable from current position

        #----------------------------------------

        
        nextPosProb = []
        for x in NextPos:
            nextPosProb.append(self.probCloseToMovingCars(NotParked, x))
        
        next = (0, 0)
        for i in range(len(nextPosProb)):
            if not self.isCloseToUnParkedCar(NotParked,NextPos[i]):
                if not self.isCloseToParkedCar(Parked, NextPos[i]):
                    next = NextPos[i]
                    print('Break next for', next)
                    break
        # if next == (0,0):
        #     minimum = 2
        #     for i in range(len(nextPosProb)):
        #         if self.probCloseToCar(NotParked,Parked,NextPos[i]) < minimum  and self.isCloseToUnParkedCar(Parked,NextPos[i]):
        #             minimum = nextPosProb[i]
        #             next = NextPos[i]


        #-------------------------------------------------------------------
        index=random.randint(0,len(neighbours)-1)
        random_step=neighbours[index]

        random_num=random.uniform(0,1)
        if(gPos in self.worldGraph.nodes ):
            if(random_num>0.75):
                next=random_step
        #------------------------------------------------------------------
        moveForward = True
        if next == gPos:
            moveForward = False

        if(self.isCloseToUnParkedCar(NotParked,next)):
             moveForward = False

        
        
        goalPos = (util.colToX(next[0]), util.rowToY(next[1]))
        return goalPos, moveForward

    # DO NOT MODIFY THIS METHOD !
    # Function: Get Autonomous Actions
    # --------------------------------
    # def isClosetoCar():
    def getAutonomousActions(self, beliefOfOtherCars: list, parkedCars: list, chkPtsSoFar: int):
        # Don't start until after your burn in iterations have expired
        if self.burnInIterations > 0:
            self.burnInIterations -= 1
            return[]
       
        goalPos, df = self.getNextGoalPos(beliefOfOtherCars, parkedCars, chkPtsSoFar)
        vectorToGoal = goalPos - self.pos
        wheelAngle = -vectorToGoal.get_angle_between(self.dir)
        # print('Wheel', wheelAngle)
        driveForward = df
        actions = {
            Car.TURN_WHEEL: wheelAngle
        }
        if driveForward:
            actions[Car.DRIVE_FORWARD] = 1.0
        return actions
    
    