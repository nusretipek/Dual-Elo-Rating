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
    def __init__(self, data):
        # Data / Players
        self.data = data
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
                            options={'maxiter': 10000, },)

        # Set Parameters
        params = optimalK.x
        K = params[0]
        expK = np.exp(K)
        finalElo = np.array(params[1:], dtype=np.float64)

        # Get Train Loss, Accuracy and Scores
        trainLoss, trainAcc = 0, 0
        for _ in range(len(self.data)):
            elo_diff = finalElo[self.d[_][0]] - finalElo[self.d[_][1]]
            probabilityWin = 1 / (1 + np.exp(-0.01 * elo_diff))
            finalElo[self.d[_][0]] += expK * (1 - probabilityWin)
            finalElo[self.d[_][1]] -= expK * (1 - probabilityWin)
            trainLoss += np.log(probabilityWin)
            if probabilityWin >= 0.5:
                trainAcc += 1
        trainAcc /= len(self.data)

        # Time
        end = time.time()
        t = end - start

        # Return Statement
        return t, params, finalElo, trainLoss, trainAcc, expK


# noinspection PyShadowingNames
class AdaptiveEloK:
    def __init__(self, data, kCount, burnInPeriod=0, plot=False):
        # Data / Players
        self.data = data
        self.kCount = kCount
        self.players = list(set(np.concatenate(self.data.values)))
        self.playerCount = len(self.players)
        self.burnInPeriod = burnInPeriod
        self.plot = plot

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
            arrK = np.array(parameters[:self.kCount], dtype=np.float64)
            currentElo = np.array(parameters[self.kCount:], dtype=np.float64)
            arrExpK = np.exp(arrK)
            x_values = np.linspace(self.burnInPeriod, len(self.data), self.kCount)
            spline = scipy.interpolate.interp1d(x_values, arrExpK)
            splineK = spline(np.arange(self.burnInPeriod, len(self.data)))
            splineK = np.concatenate([np.full((self.burnInPeriod,), 100, dtype=np.float64), splineK])

            loss = 0
            for _ in range(len(self.data)):
                elo_diff = currentElo[self.d[_][0]] - currentElo[self.d[_][1]]
                probabilityWin = 1 / (1 + np.exp(-0.01 * elo_diff))
                currentElo[self.d[_][0]] += splineK[_] * (1 - probabilityWin)
                currentElo[self.d[_][1]] -= splineK[_] * (1 - probabilityWin)
                loss += np.log(probabilityWin)

            return -loss

        optimalK = minimize(fun=eloModel,
                            x0=[5] * self.kCount + [1000] * self.playerCount,
                            method='L-BFGS-B',
                            tol=1e-20,
                            options={'maxiter': 10000, },
                            bounds=self.kCount * [(-10, 10)] + self.playerCount * [(-np.inf, np.inf)],)

        # Set Parameters
        params = optimalK.x
        currentElo = np.array(params[self.kCount:], dtype=np.float64)
        arrK = np.array(params[:self.kCount], dtype=np.float64)
        arrExpK = np.exp(arrK)
        x_values = np.linspace(self.burnInPeriod, len(self.data), self.kCount)
        spline = scipy.interpolate.interp1d(x_values, arrExpK)
        splineK = spline(np.arange(self.burnInPeriod, len(self.data)))
        splineK = np.concatenate([np.full((self.burnInPeriod,), 100, dtype=np.float64), splineK])

        # Plot the interpolated K values
        if self.plot:
            plt.figure(figsize=(8, 6))
            plt.plot(x_values, arrExpK, 'o', label='Data Points')
            plt.plot(np.arange(len(self.data)), splineK, label='Spline Interpolation')
            plt.xlabel('Time (t)')
            plt.ylabel('Value')
            plt.title('Cubic Spline Interpolation')
            plt.legend()
            plt.grid(True)
            plt.show()

        # Get Train Loss, Accuracy and Scores
        trainLoss, trainAcc = 0, 0
        for _ in range(len(self.data)):
            elo_diff = currentElo[self.d[_][0]] - currentElo[self.d[_][1]]
            probabilityWin = 1 / (1 + np.exp(-0.01 * elo_diff))
            currentElo[self.d[_][0]] += splineK[_] * (1 - probabilityWin)
            currentElo[self.d[_][1]] -= splineK[_] * (1 - probabilityWin)
            trainLoss += np.log(probabilityWin)
            if probabilityWin >= 0.5:
                trainAcc += 1
        trainAcc /= len(self.data)

        # Time
        end = time.time()
        t = end - start

        # Return Statement
        return t, params, currentElo, trainLoss, trainAcc, arrExpK


# Sudden data
suddenOptimizedEloKValues = []
suddenOptimizedAdaptiveEloKValues = []
for dataFile in sorted(glob.glob("data/switchedHierarchy*.csv")):

    # Read data
    switchedHierarchy = pd.read_csv(dataFile, index_col=None)

    # Optimized Elo
    model = optimizedElo(data=switchedHierarchy)
    tOpt, paramsOpt, finalEloOpt, trainLossOpt, trainAccOpt, expKOpt = model.runElo()
    suddenOptimizedEloKValues.append(expKOpt)

    # Adaptive Elo K
    model = AdaptiveEloK(data=switchedHierarchy, kCount=8, burnInPeriod=0, plot=False)
    tAdaptive, paramsAdaptive, currentEloAdaptive, trainLossAdaptive, trainAccAdaptive, arrExpKAdaptive = model.runElo()
    suddenOptimizedAdaptiveEloKValues.append(arrExpKAdaptive)

# Gradual Data
gradualOptimizedEloKValues = []
gradualOptimizedAdaptiveEloKValues = []
for dataFile in sorted(glob.glob("data/switchedGradualHierarchy*.csv")):
    # Read data
    switchedHierarchy = pd.read_csv(dataFile, index_col=None)

    # Optimized Elo
    model = optimizedElo(data=switchedHierarchy)
    tOpt, paramsOpt, finalEloOpt, trainLossOpt, trainAccOpt, expKOpt = model.runElo()
    gradualOptimizedEloKValues.append(expKOpt)

    # Adaptive Elo K
    model = AdaptiveEloK(data=switchedHierarchy, kCount=8, burnInPeriod=0, plot=True)
    tAdaptive, paramsAdaptive, currentEloAdaptive, trainLossAdaptive, trainAccAdaptive, arrExpKAdaptive = model.runElo()
    gradualOptimizedAdaptiveEloKValues.append(arrExpKAdaptive)

# Save the K values
suddenOptimizedEloKValuesArr = np.array(suddenOptimizedEloKValues)
suddenOptimizedAdaptiveEloKValuesArr = np.array(suddenOptimizedAdaptiveEloKValues)
gradualOptimizedEloKValuesArr = np.array(gradualOptimizedEloKValues)
gradualOptimizedAdaptiveEloKValuesArr = np.array(gradualOptimizedAdaptiveEloKValues)
np.save('suddenOptimizedEloKValuesArr.npy', suddenOptimizedEloKValuesArr)
np.save('suddenOptimizedAdaptiveEloKValuesArr.npy', suddenOptimizedAdaptiveEloKValuesArr)
np.save('gradualOptimizedEloKValuesArr.npy', gradualOptimizedEloKValuesArr)
np.save('gradualOptimizedAdaptiveEloKValuesArr.npy', gradualOptimizedAdaptiveEloKValuesArr)

## Checkpoint complete
