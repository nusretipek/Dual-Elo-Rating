import math
import numpy as np
import pprint
import time
import itertools


class Animal:
    def __init__(self, id, initialDominance, initialX, initialY):
        self.id = id
        self.locX = initialX
        self.locY = initialY
        self.dominanceScore = initialDominance
        self.angle = np.random.randint(0, 360)
        self.waitingTime = np.random.randint(0, 16)

    def move(self):
        self.locX += int(round(math.cos(math.radians(self.angle))))
        self.locY += int(round(math.sin(math.radians(self.angle))))
        self.waitingTime = np.random.randint(8, 8*2)


class DomWorld:
    def __init__(self, size, animals, personalSpaceDistance, nearViewDistance, maxViewDistance, perspectiveAngle,
                 stepDom, iterations, epochs):
        self.size = size
        self.animalsN = animals
        self.iterations = iterations
        self.personalSpaceDistance = personalSpaceDistance
        self.nearViewDistance = nearViewDistance
        self.maxViewDistance = maxViewDistance
        self.perspectiveAngle = perspectiveAngle
        self.stepDom = stepDom
        self.epochs = epochs
        self.animals = []
        self.interactions = []
        self.c = 0
        self.meanDistanceList = []

        # Initialize environment
        self.initializeAnimals()

    def initializeAnimals(self):
        for idx in range(self.animalsN):
            self.animals.append(Animal(id=idx,
                                       initialDominance=np.random.randint(5,15),
                                       initialX=np.random.randint(85, 115),
                                       initialY=np.random.randint(85, 115),))

    def adjustCoordinates(self, animal):
        # adjust X
        if animal.locX > self.size[0]-1:
            animal.locX %= self.size[0]
        elif animal.locX < 0:
            animal.locX += self.size[0]

        # adjust Y
        if animal.locY > self.size[1]-1:
            animal.locY %= self.size[1]
        elif animal.locY < 0:
            animal.locY += self.size[1]

    def searchPersonalSpace(self, searchingAnimal, animalArray):
        personalSpaceAnimals = []
        animalArray = [a for a in animalArray if a.id != searchingAnimal.id]
        for otherAnimal in animalArray:
            deltaX = otherAnimal.locX - searchingAnimal.locX
            deltaY = otherAnimal.locY - searchingAnimal.locY
            deltaWrappedX = min(abs(deltaX), self.size[0] - abs(deltaX))
            deltaWrappedY = min(abs(deltaY), self.size[1] - abs(deltaY))
            distance = math.sqrt(deltaWrappedX ** 2 + deltaWrappedY ** 2)
            if distance <= self.personalSpaceDistance:
                deltaWrappedTX = deltaX if abs(deltaX) <= self.size[0]/2 else deltaX-math.copysign(self.size[0], deltaX)
                deltaWrappedTY = deltaY if abs(deltaY) <= self.size[1]/2 else deltaY-math.copysign(self.size[1], deltaY)
                thetaSO = math.atan2(deltaWrappedTY, deltaWrappedTX)
                thetaSOD = (math.degrees(thetaSO) + 360) % 360
                searchAngleL = searchingAnimal.angle - (self.perspectiveAngle / 2)
                searchAngleL %= 360
                searchAngleR = searchingAnimal.angle + (self.perspectiveAngle / 2)
                searchAngleR %= 360
                winProb = searchingAnimal.dominanceScore / (searchingAnimal.dominanceScore + otherAnimal.dominanceScore)
                if min(searchAngleR, searchAngleL) <= thetaSOD <= max(searchAngleR, searchAngleL) and winProb > 0.5:
                    personalSpaceAnimals.append(otherAnimal)
        return personalSpaceAnimals

    def searchNearView(self, searchingAnimal, animalArray):
        animalArray = [a for a in animalArray if a.id != searchingAnimal.id]
        for otherAnimal in animalArray:
            deltaX = otherAnimal.locX - searchingAnimal.locX
            deltaY = otherAnimal.locY - searchingAnimal.locY
            deltaWrappedX = min(abs(deltaX), self.size[0] - abs(deltaX))
            deltaWrappedY = min(abs(deltaY), self.size[1] - abs(deltaY))
            deltaWrappedTX = deltaX if abs(deltaX) <= self.size[0] / 2 else deltaX - math.copysign(self.size[0], deltaX)
            deltaWrappedTY = deltaY if abs(deltaY) <= self.size[1] / 2 else deltaY - math.copysign(self.size[1], deltaY)
            distance = math.sqrt(deltaWrappedX ** 2 + deltaWrappedY ** 2)
            thetaSO = math.atan2(deltaWrappedTY, deltaWrappedTX)
            thetaSOD = (math.degrees(thetaSO) + 360) % 360
            searchAngleL = searchingAnimal.angle - (self.perspectiveAngle / 2)
            searchAngleL %= 360
            searchAngleR = searchingAnimal.angle + (self.perspectiveAngle / 2)
            searchAngleR %= 360
            if distance <= self.nearViewDistance and (min(searchAngleR, searchAngleL) <=
                                                      thetaSOD <= max(searchAngleR, searchAngleL)):
                return True
        return False

    def searchMaxView(self, searchingAnimal, animalArray):
        animalArray = [a for a in animalArray if a.id != searchingAnimal.id]
        for otherAnimal in animalArray:
            deltaX = otherAnimal.locX - searchingAnimal.locX
            deltaY = otherAnimal.locY - searchingAnimal.locY
            deltaWrappedX = min(abs(deltaX), self.size[0] - abs(deltaX))
            deltaWrappedY = min(abs(deltaY), self.size[1] - abs(deltaY))
            deltaWrappedTX = deltaX if abs(deltaX) <= self.size[0] / 2 else deltaX - math.copysign(self.size[0], deltaX)
            deltaWrappedTY = deltaY if abs(deltaY) <= self.size[1] / 2 else deltaY - math.copysign(self.size[1], deltaY)
            distance = math.sqrt(deltaWrappedX ** 2 + deltaWrappedY ** 2)
            thetaSO = math.atan2(deltaWrappedTY, deltaWrappedTX)
            thetaSOD = (math.degrees(thetaSO) + 360) % 360
            searchAngleL = searchingAnimal.angle - (self.perspectiveAngle / 2)
            searchAngleL %= 360
            searchAngleR = searchingAnimal.angle + (self.perspectiveAngle / 2)
            searchAngleR %= 360
            if distance <= self.maxViewDistance and (min(searchAngleR, searchAngleL) <=
                                                     thetaSOD <= max(searchAngleR, searchAngleL)):
                searchingAnimal.angle = thetaSOD
                return True
        return False

    def retreat(self, animal):
        animal.angle += 180
        animal.angle %= 360
        for _ in range(self.personalSpaceDistance+1):
            animal.move()
            self.adjustCoordinates(animal)
        animal.waitingTime = np.random.randint(8, 16)

    def chase(self, animal):
        animal.move()
        self.adjustCoordinates(animal)

    def fight(self, animalX, animalY):
        self.c += 1
        Rij = animalX.dominanceScore / (animalX.dominanceScore + animalY.dominanceScore)
        if np.random.uniform() < Rij:
            animalX.dominanceScore += ((1-Rij) * self.stepDom)
            animalY.dominanceScore -= ((1-Rij) * self.stepDom)
            self.retreat(animalY)
            self.chase(animalX)
            self.interactions.append((animalX.id, animalY.id))
        else:
            animalX.dominanceScore -= ((1-Rij) * self.stepDom)
            animalY.dominanceScore += ((1-Rij) * self.stepDom)
            self.retreat(animalX)
            self.chase(animalY)
            self.interactions.append((animalY.id, animalX.id))

    def getMeanDistance(self):
        #combinations = list(itertools.combinations(self.animals, 2))
        dist = 0
        for animalI in self.animals:
            tempDist = 9999
            for animalJ in self.animals:
                if animalI.id != animalJ.id:
                    deltaX = animalI.locX - animalJ.locX
                    deltaY = animalI.locY - animalJ.locY
                    deltaWrappedX = min(abs(deltaX), self.size[0] - abs(deltaX))
                    deltaWrappedY = min(abs(deltaY), self.size[1] - abs(deltaY))
                    if tempDist > math.sqrt(deltaWrappedX ** 2 + deltaWrappedY ** 2):
                        tempDist = math.sqrt(deltaWrappedX ** 2 + deltaWrappedY ** 2)
            dist += tempDist
        self.meanDistanceList.append(dist/len(self.animals))

    def run(self):
        startTime = time.time()
        for idx in range(self.epochs):
            for idy in range(self.iterations):
                for animalIdx in range(len(self.animals)):
                    if self.animals[animalIdx].waitingTime == 0:
                        personalSpaceAnimals = self.searchPersonalSpace(self.animals[animalIdx], self.animals)

                        # fight
                        if len(personalSpaceAnimals) != 0:
                            randomAnimal = np.random.randint(0, len(personalSpaceAnimals))
                            self.fight(self.animals[animalIdx], personalSpaceAnimals[randomAnimal])

                        # nearView Search
                        elif self.searchNearView(self.animals[animalIdx], self.animals):
                            self.animals[animalIdx].move()
                            self.adjustCoordinates(self.animals[animalIdx])

                        # maxView Search
                        elif self.searchMaxView(self.animals[animalIdx], self.animals):
                            self.animals[animalIdx].move()
                            self.adjustCoordinates(self.animals[animalIdx])

                        # adjust Angle
                        else:
                            self.animals[animalIdx].angle += np.random.choice([-90, 90])
                            self.animals[animalIdx].angle %= 360
                            self.animals[animalIdx].waitingTime = np.random.randint(5, 16)

                    else:
                        self.animals[animalIdx].waitingTime -= 1
            self.getMeanDistance()
        for animal in self.animals:
            pprint.pprint(animal.__dict__)
        endTime = time.time()
        print("Simulation time:", round(endTime-startTime, 2), "seconds!")


if __name__ == "__main__":
    DW = DomWorld(size=(200, 200),
                  animals=8,
                  personalSpaceDistance=2,
                  nearViewDistance=24,
                  maxViewDistance=50,
                  perspectiveAngle=120,
                  stepDom=0.1,
                  iterations=20,
                  epochs=100)

    #adjust the pass over indexes
    DW.run()
    print(DW.c)
    print(DW.interactions)
    print(DW.meanDistanceList)

