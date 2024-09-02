import os
import sys
import glob
import pandas as pd
import numpy as np
import warnings
import scipy
import time
import itertools
import random
from scipy.optimize import minimize
import matplotlib.pyplot as plt


# noinspection PyShadowingNames
class optimizedElo:
    def __init__(self, data, name):
        # Data / Players
        self.data = data
        self.name = name
        self.players = list(set(np.concatenate(self.data.values)))
        self.playerCount = len(self.players)

        # Parse Interactions
        ## Train
        self.d = {}
        for _ in range(len(self.data)):
            initiatorID, receiverID = self.data.loc[_, [self.data.columns[0], self.data.columns[1]]]
            self.d[_] = [initiatorID, receiverID]

        # Initial parameters
        self.start_value = 1000
        self.K = np.log(100)
        self.eloScores = np.full((self.playerCount,), self.start_value, dtype=np.float64)

    def runElo(self):
        start = time.time()

        def eloModel(parameters):
            K = parameters[0]
            expK = np.exp(K)
            currentElo = np.array(parameters[1:], dtype=np.float64)
            loss = 0

            for _ in range(len(self.data)):
                elo_diff = currentElo[self.d[_][0]] - currentElo[self.d[_][1]]
                probabilityWin = 1 / (1 + np.exp(-0.01 * elo_diff))
                currentElo[self.d[_][0]] += expK * (1 - probabilityWin)
                currentElo[self.d[_][1]] -= expK * (1 - probabilityWin)
                loss += np.log(probabilityWin)

            return -loss

        optimalK = minimize(fun=eloModel,
                            x0=[5] + self.playerCount * [0],
                            method='BFGS',
                            tol=1e-10,
                            options={'maxiter': 10000, }, )

        # Set Parameters
        params = optimalK.x
        K = params[0]
        expK = np.exp(K)
        finalElo = np.array(params[1:], dtype=np.float64)
        eloEvolution = np.zeros((len(self.data), self.playerCount), dtype=np.float64)

        # Get Train Loss, Accuracy and Scores
        trainLoss, trainAcc = 0, 0

        # Ranking change file
        prevRanking = np.argsort(finalElo)[::-1]
        file_path = 'dataFull/' + self.name + '.txt'
        file = open(file_path, 'a')
        arrayStr = ' '.join(map(str, prevRanking))
        file.write(str(0) + ' - ' + arrayStr + '\n')

        for _ in range(len(self.data)):
            eloEvolution[_] = finalElo
            elo_diff = finalElo[self.d[_][0]] - finalElo[self.d[_][1]]
            probabilityWin = 1 / (1 + np.exp(-0.01 * elo_diff))
            finalElo[self.d[_][0]] += expK * (1 - probabilityWin)
            finalElo[self.d[_][1]] -= expK * (1 - probabilityWin)
            trainLoss += np.log(probabilityWin)
            if probabilityWin >= 0.5:
                trainAcc += 1

            # Check ranking
            tempRanking = np.argsort(finalElo)[::-1]
            if not np.array_equal(prevRanking, tempRanking):
                arrayStr = ' '.join(map(str, tempRanking))
                file.write(str(_) + ' - ' + arrayStr + '\n')
            prevRanking = tempRanking

        trainAcc /= len(self.data)
        file.close()
        np.save('dataFull/' + self.name + '.npy', eloEvolution)

        # Time
        end = time.time()
        t = end - start

        # Return Statement
        return t, params, finalElo, trainLoss, trainAcc


# Read data
for dataFile in sorted(glob.glob("dataFull/*.csv")):
    filename = os.path.splitext(os.path.basename(dataFile))[0]
    switchedHierarchy = pd.read_csv(dataFile, index_col=None)

    # Optimized Elo
    model = optimizedElo(data=switchedHierarchy, name=filename)
    tOpt, paramsOpt, finalEloOpt, trainLossOpt, trainAccOpt = model.runElo()
    print(dataFile + " processed.")

## Checkpoint complete
