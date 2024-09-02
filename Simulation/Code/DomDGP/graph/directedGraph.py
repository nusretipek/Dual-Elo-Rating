import warnings
import numpy as np
from typing import Optional, Union


def _hasCycle(graph):
    def dfs(nodeX, visitedX, rec_stackX):
        visitedX[nodeX] = True
        rec_stackX[nodeX] = True
        for neighbor in range(len(graph)):
            if graph[nodeX][neighbor]:
                if not visitedX[neighbor]:
                    if dfs(neighbor, visitedX, rec_stackX):
                        return True
                elif rec_stackX[neighbor]:
                    return True
        rec_stackX[nodeX] = False
        return False

    visited = [False] * len(graph)
    rec_stack = [False] * len(graph)

    for node in range(len(graph)):
        if not visited[node]:
            if dfs(node, visited, rec_stack):
                return True
    return False


def _checkGraphConditions(graph):
    n = graph.shape[0]

    for i in range(n):
        for j in range(n):
            if i != j and (graph[i][j] != 0 or graph[j][i] != 0):
                assert graph[i][j] + graph[j][i] == 1, f"graph[{i}][{j}] and graph[{j}][{i}] does not sum to 1!"
        assert graph[i][i] == 0, f"graph[{i}][{i}] must be 0"


def _getNonzeroIndicesValues(graph):
    indices = []
    n = graph.shape[0]

    for i in range(n):
        for j in range(i, n):
            if graph[i][j] > 0 or graph[j][i] > 0:
                indices.append([i, j])
    return indices


def _convertDominanceMatrix(matrix):
    n = matrix.shape[0]
    normalizedMatrix = matrix.copy().astype(float)

    for i in range(n):
        for j in range(n):
            if i != j:
                pair_sum = matrix[i][j] + matrix[j][i]
                if pair_sum != 0:
                    normalizedMatrix[i][j] /= pair_sum
                else:
                    normalizedMatrix[i][j] = 0.0

    return normalizedMatrix


def _transitiveClosure(graph):
    n = len(graph)
    closure = np.array(graph)

    for k in range(n):
        for i in range(n):
            for j in range(n):
                closure[i][j] = closure[i][j] or (closure[i][k] and closure[k][j])

    return closure


def _addRandomNoise(matrix, alpha):
    n = matrix.shape[0]
    noiseMatrix = matrix.copy().astype(float)

    for i in range(n):
        for j in range(i + 1, n):
            if matrix[i, j] + matrix[j, i] == 1:
                randValue = np.random.uniform(0, alpha)
                if matrix[i, j] > matrix[j, i]:
                    noiseMatrix[i, j] -= randValue
                    noiseMatrix[j, i] += randValue
                else:
                    noiseMatrix[i, j] += randValue
                    noiseMatrix[j, i] -= randValue
                assert round(noiseMatrix[i, j] + noiseMatrix[j, i], 6) == 1

    return noiseMatrix


def directedGraph(self, interactionN: int = 100, dominanceMatrix: Optional[Union[list, np.ndarray]] = None,
                  samplingWeights: Optional[Union[list, np.ndarray]] = None, applyTransitivity: bool = False,
                  randomNoise: float = 0) -> None:

    # Assert N type
    assert isinstance(interactionN, int) and interactionN > 0, "interactionN is not an integer > 0!"

    # samplingWeights parameter typing assertions
    if samplingWeights is not None:
        assert (isinstance(samplingWeights, list) or isinstance(samplingWeights, np.ndarray)), \
            "samplingWeights is neither a list, nor a ndarray!"
        if isinstance(samplingWeights, list):
            try:
                samplingWeights = np.array(samplingWeights, dtype=np.float64)
            except:
                raise RuntimeError("List cannot be converted to NumPy array, check size!")
        if isinstance(samplingWeights, np.ndarray):
            samplingWeights = samplingWeights.astype(np.float64)
        assert samplingWeights.shape[0] == samplingWeights.shape[1], "Dominance matrix rows is not equal to columns!"
        assert len(self.animals) == samplingWeights.shape[0], "N is not equal to dominance matrix shape!"

    # dominanceMatrix parameter typing assertions
    if dominanceMatrix is None and samplingWeights is not None:
        warnings.warn("dominanceMatrix is derived from samplingWeights (can be observed interaction matrix)!",
                      RuntimeWarning, stacklevel=3)
        dominanceMatrix = _convertDominanceMatrix(samplingWeights)
    else:
        assert (isinstance(dominanceMatrix, list) or isinstance(dominanceMatrix, np.ndarray)), \
            "dominanceMatrix is neither a list, nor a ndarray!"
        if isinstance(dominanceMatrix, list):
            try:
                dominanceMatrix = np.array(dominanceMatrix, dtype=np.float64)
            except:
                raise RuntimeError("List cannot be converted to NumPy array, check size!")
        if isinstance(dominanceMatrix, np.ndarray):
            dominanceMatrix = dominanceMatrix.astype(np.float64)
        assert dominanceMatrix.shape[0] == dominanceMatrix.shape[1], "Dominance matrix rows is not equal to columns!"
        assert len(self.animals) == dominanceMatrix.shape[0], "N is not equal to dominance matrix shape!"

    # dominanceMatrix assert weights
    _checkGraphConditions(dominanceMatrix)

    # Assert randomNoise
    randomNoise = float(randomNoise)
    assert 0.5 >= randomNoise >= 0, "Random noise can be between 0 and 0.5!"

    # Check cycles
    isDAG = not _hasCycle(dominanceMatrix)
    if (not isDAG) and applyTransitivity:
        raise RuntimeError("Graph is not DAG, transitive closure cannot be applied! ")
    elif applyTransitivity:
        dominanceMatrix = _transitiveClosure(dominanceMatrix)
    else:
        pass

    # Apply random noise
    if randomNoise > 0:
        dominanceMatrix = _addRandomNoise(dominanceMatrix, alpha=randomNoise)

    # Get indices and probabilities
    indices = _getNonzeroIndicesValues(dominanceMatrix)
    pairs = [[self.animals[idx] for idx in pair] for pair in indices]

    # samplingWeights
    p = []
    if samplingWeights is not None:
        for pair in pairs:
            p.append(samplingWeights[pair[0], pair[1]] + samplingWeights[pair[1], pair[0]])
        p = np.array(p, dtype=np.float64)
        p /= np.sum(p)
        sampleIndices = np.random.choice(np.arange(len(pairs)), interactionN, p=p)
    else:
        sampleIndices = np.random.choice(np.arange(len(pairs)), interactionN)

    if self.decisionFunction != self.decisionFunctions[2]:
        warnings.warn("Animal Scores & Timeline only implemented for Elo Rating!", RuntimeWarning, stacklevel=3)

    # Sample from the graph
    k = 100

    for idx in sampleIndices:
        self.interactions.append(pairs[idx])
        indexI = np.where(self.animals == pairs[idx][0])[0][0]
        indexJ = np.where(self.animals == pairs[idx][1])[0][0]
        Rij = 1 / (1 + np.exp(-0.01 * (self.animalScores[indexI] - self.animalScores[indexJ])))

        if np.random.uniform() < dominanceMatrix[indexI][indexJ]:
            if self.decisionFunction == self.decisionFunctions[2]:
                self.animalScores[indexI] += k * (1 - Rij)
                self.animalScores[indexJ] -= k * (1 - Rij)
            self.winSequenceGlobal.append(pairs[idx])
        else:
            if self.decisionFunction == self.decisionFunctions[2]:
                self.animalScores[indexI] += k * (0 - Rij)
                self.animalScores[indexJ] -= k * (0 - Rij)
            self.winSequenceGlobal.append(pairs[idx][::-1])
        if self.decisionFunction == self.decisionFunctions[2]:
            self.animalScoresTimeline = np.vstack((self.animalScoresTimeline, self.animalScores))

## <Checkpoint>
