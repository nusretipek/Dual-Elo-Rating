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

# DomDGP
startTime = time.time()

for s in range(5):
    for n in [0.1, 0.2]:
        name = "testGenerate/noisyHierarchy_" + str(n).replace(".", "") + "_" + str(s) + ".csv"
        DomDGP = DGP(N=len(trueHierarchy),
                     decisionFunction="elo",
                     initialScores=1000,
                     seed=s,
                     k=0)

        # Generate interactions based on true hierarchy
        DomDGP.directedGraph(interactionN=500,
                             dominanceMatrix=trueHierarchy,
                             samplingWeights=None,
                             applyTransitivity=True,
                             randomNoise=n)

        DomDGP.toCSV(name)
print("Time: ", time.time() - startTime)

## <Checkpoint>
