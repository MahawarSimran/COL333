import util , collections , random , math
from util import Belief, pdf 
from engine.const import Const


def allotparticles(weightpart):
    points = []
    whichelement = []
    for elem in weightpart:
        points.append(weightpart[elem])
        whichelement.append(elem)
    total = 0
    for count in points:
        total += count
    key = random.uniform(0, total)
    runningTotal = 0.0
    index = None
    index =0
    for i in  points:
        runningTotal += i
        if runningTotal > key:
            return whichelement[index]
        index += 1
    raise Exception('Do not come here')


class Estimator(object):
    ParticleCount=2000
    def __init__(self, numRows: int, numCols: int):
        self.belief = util.Belief(numRows, numCols) 
        self.transProb = util.loadTransProb() 
       
        self.transProbDict = dict()
        for (previousPos, latestPos) in self.transProb:
            if not previousPos in self.transProbDict:
                self.transProbDict[previousPos] = dict()
            self.transProbDict[previousPos][latestPos] = self.transProb[(previousPos, latestPos)]

        self.particles = collections.Counter()
        potentialParticles = list(self.transProbDict.keys())
        for i in range(self.ParticleCount):
            particleIndex = int(random.random() * len(potentialParticles))
            self.particles[potentialParticles[particleIndex]] += 1

        self.setbelief()

    def changeparticles(self):
        newParticles = collections.Counter()
        for i in range(self.ParticleCount):
            sample = allotparticles(self.particles)
            newParticles[sample] += 1
        return newParticles
    def changeparticlesmoving(self):
        self.setbelief()
        newParticles = collections.Counter()
        for Pos in self.particles:
            for i in range(self.particles[Pos]):  # if on that tile there're more particles, that tile is an important start point
                newPos = allotparticles(self.transProbDict[Pos])
                # increase the particles.
                newParticles[newPos] += 1
        return newParticles

    def setbelief(self):
        newBelief = util.Belief(self.belief.getNumRows(), self.belief.getNumCols(), 0)
        for Pos in self.particles:
                newBelief.setProb(Pos[0], Pos[1], self.particles[Pos])
        newBelief.normalize()
        self.belief = newBelief
            
    def estimate(self, posX: float, posY: float, observedDist: float, isParked: bool) -> None:
        # BEGIN_YOUR_CODE
        for Pos in self.particles.keys():
            x = util.colToX(Pos[1])
            y = util.rowToY(Pos[0])
            pastparticles = self.particles[Pos]
            chances= util.pdf(math.sqrt((posX - x) ** 2 + (posY - y) ** 2), Const.SONAR_STD, observedDist)
            presentparticles = pastparticles * chances
            self.particles[Pos] = presentparticles
        
        
        NewParticles = self.changeparticles()
        if(isParked):
            if(len(list(NewParticles.keys()))>8):
                self.particles=NewParticles
        else:
            self.particles=NewParticles
        self.setbelief()
        newParticles = collections.Counter()
        if(not isParked):
            for tile in self.particles:
                for i in range(self.particles[tile]):
                    newtile = allotparticles(self.transProbDict[tile])
                    newParticles[newtile] += 1
            self.particles = newParticles
        # self.particles = self.changeparticlesmoving()
        # self.setbelief()
        # END_YOUR_CODE
        return
  
    def getBelief(self) -> Belief:
        return self.belief

   