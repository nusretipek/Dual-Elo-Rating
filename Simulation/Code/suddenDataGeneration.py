import numpy as np
from DomDGP import DGP
import time

# Parameters

trueHierarchy = [[0, 1, 0, 0, 1, 0, 0],
                 [0, 0, 1, 0, 0, 1, 0],
                 [0, 0, 0, 1, 0, 0, 0],
                 [0, 0, 0, 0, 0, 0, 0],
                 [0, 0, 0, 0, 0, 1, 1],
                 [0, 0, 0, 1, 0, 0, 0],
                 [0, 0, 0, 1, 0, 0, 0]]

switchHierarchy1 = [[0, 0, 1, 0, 1, 0, 0],
                    [0, 0, 0, 1, 0, 0, 0],
                    [0, 1, 0, 0, 0, 1, 0],
                    [0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 1, 1],
                    [0, 0, 0, 1, 0, 0, 0],
                    [0, 0, 0, 1, 0, 0, 0]]

switchHierarchy2 = [[0, 0, 0, 0, 0, 1, 1],
                    [0, 0, 0, 1, 0, 0, 0],
                    [0, 1, 0, 0, 0, 1, 0],
                    [0, 0, 0, 0, 0, 0, 0],
                    [1, 1, 0, 0, 0, 0, 0],
                    [0, 0, 0, 1, 0, 0, 0],
                    [0, 0, 0, 1, 0, 0, 0]]

switchHierarchy3 = [[0, 0, 0, 0, 0, 0, 1],
                    [0, 0, 0, 0, 0, 1, 0],
                    [0, 1, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0],
                    [1, 1, 0, 0, 0, 0, 0],
                    [0, 0, 0, 1, 0, 0, 0],
                    [0, 0, 0, 0, 0, 1, 0]]

# DomDGP
startTime = time.time()

for s in range(5):
    for n in [0.1, 0.2]:
        name = "testGenerate/switchedHierarchy_" + str(n).replace(".", "") + "_" + str(s) + ".csv"
        DomDGP = DGP(N=len(trueHierarchy),
                     decisionFunction="elo",
                     initialScores=1000,
                     seed=s,
                     k=0)

        # Generate interactions based on true hierarchy
        DomDGP.directedGraph(interactionN=200,
                             dominanceMatrix=trueHierarchy,
                             samplingWeights=None,
                             applyTransitivity=True,
                             randomNoise=n)

        # Generate interactions based on switch in hierarchy (animal 1-2)
        DomDGP.directedGraph(interactionN=200,
                             dominanceMatrix=switchHierarchy1,
                             samplingWeights=None,
                             applyTransitivity=True,
                             randomNoise=n)

        # Generate interactions based on switch in hierarchy (animal 0-4, alpha)
        DomDGP.directedGraph(interactionN=200,
                             dominanceMatrix=switchHierarchy2,
                             samplingWeights=None,
                             applyTransitivity=True,
                             randomNoise=n)

        # Generate interactions based on switch in hierarchy (5, downgrade)
        DomDGP.directedGraph(interactionN=200,
                             dominanceMatrix=switchHierarchy3,
                             samplingWeights=None,
                             applyTransitivity=True,
                             randomNoise=n)

        DomDGP.toCSV(name)
print("Time: ", time.time() - startTime)

## <Checkpoint>
