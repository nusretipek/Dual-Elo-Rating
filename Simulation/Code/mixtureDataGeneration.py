import numpy as np
from DomDGP import DGP
import time


# Get gradually changed hierarchy
def GetHierarchy(t, totalTime):
    assert t <= totalTime, "t cannot exceed totalTime"
    gradualChangeStop = 600 / 800
    totalTime = (totalTime * gradualChangeStop)

    trueHierarchy = [[0, 1, 1, 1, 1, 1, 1, 1],
                     [0, 0, 1, 1, 0, 1, 0, 1],
                     [0, 0, 0, 1, 0, 0, 0, 1],
                     [0, 0, 0, 0, 0, 0, 0, 1],
                     [0, 0, 0, 1, 0, 1, 1, 1],
                     [0, 0, 0, 1, 0, 0, 0, 1],
                     [0, 0, 0, 1, 0, 0, 0, 1],
                     [0, 0, 0, 0, 0, 0, 0, 0]]

    switchHierarchy1 = [[0, 1, 1, 1, 1, 1, 1, 1],
                        [0, 0, 0, 1, 0, 0, 0, 1],
                        [0, 1, 0, 1, 0, 1, 0, 1],
                        [0, 0, 0, 0, 0, 0, 0, 1],
                        [0, 0, 0, 1, 0, 1, 1, 1],
                        [0, 0, 0, 1, 0, 0, 0, 1],
                        [0, 0, 0, 1, 0, 0, 0, 1],
                        [0, 0, 0, 0, 0, 0, 0, 0]]

    switchHierarchy2 = [[0, 0, 0, 1, 0, 1, 1, 1],
                        [0, 0, 0, 1, 0, 0, 0, 1],
                        [0, 1, 0, 1, 0, 1, 0, 1],
                        [0, 0, 0, 0, 0, 0, 0, 1],
                        [1, 1, 1, 1, 0, 1, 1, 1],
                        [0, 0, 0, 1, 0, 0, 0, 1],
                        [0, 0, 0, 1, 0, 0, 0, 1],
                        [0, 0, 0, 0, 0, 0, 0, 0]]

    switchHierarchy3 = [[0, 0, 0, 1, 0, 1, 1, 1],
                        [0, 0, 0, 1, 0, 1, 0, 1],
                        [0, 1, 0, 1, 0, 1, 0, 1],
                        [0, 0, 0, 0, 0, 0, 0, 1],
                        [1, 1, 1, 1, 0, 1, 1, 1],
                        [0, 0, 0, 1, 0, 0, 0, 1],
                        [0, 0, 0, 1, 0, 1, 0, 1],
                        [0, 0, 0, 0, 0, 0, 0, 0]]

    if t >= 600:
        currentHierarchy = switchHierarchy3
    elif t >= 400:
        currentHierarchy = switchHierarchy2
    elif t >= 200:
        currentHierarchy = switchHierarchy1
    else:
        currentHierarchy = trueHierarchy

    currentHierarchy[3][7] = max(((totalTime - t) / totalTime), 0.1) if ((totalTime - t) / totalTime) >= 0 else 0.2
    currentHierarchy[7][3] = 1 - currentHierarchy[3][7]
    currentHierarchy = np.array(currentHierarchy, dtype=np.float64)
    samplingWeights = currentHierarchy.copy()
    samplingWeights[:3, 7] = 1 / 16
    samplingWeights[4:, 7] = 1 / 16
    samplingWeights[3, 7] = (currentHierarchy[3][7] + 3.6 * currentHierarchy[7][3]) / 2
    samplingWeights[7, 3] = samplingWeights[3, 7]

    return currentHierarchy, np.round(samplingWeights, 3)


# DomDGP
startTime = time.time()
for idx, s in enumerate([6, 68, 86, 686, 868]):
    for n in [0.1, 0.2]:
        name = "testGenerate/switchedGradualHierarchy_" + str(n).replace(".", "") + "_" + str(idx) + ".csv"

        DomDGP = DGP(N=8,
                     decisionFunction="elo",
                     initialScores=1000,
                     seed=s * int(10 * n),
                     k=0)

        for timeN in range(0, 800, 20):
            DH, SW = GetHierarchy(timeN, 800)
            DomDGP.directedGraph(interactionN=20,
                                 dominanceMatrix=DH,
                                 samplingWeights=SW,
                                 applyTransitivity=False,
                                 randomNoise=n)

        DomDGP.toCSV(name)
print("Time: ", time.time() - startTime)

## <Checkpoint>
