import numpy as np


def eloRating(self, interactions: np.ndarray = None, **kwargs) -> None:
    # Assertions
    assert interactions is not None

    # Arguments
    k = kwargs['k'] if 'k' in kwargs else 100

    # Calculate Elo Model
    winSequenceRound = []
    for i, j in interactions:
        indexI = np.where(self.animals == i)[0]
        indexJ = np.where(self.animals == j)[0]
        Rij = 1 / (1 + np.exp(-0.01 * (self.animalScores[indexI] - self.animalScores[indexJ])))

        if np.random.uniform() < Rij:
            winSequenceRound.append([i, j])
            self.animalScores[indexI] += k * (1 - Rij)
            self.animalScores[indexJ] -= k * (1 - Rij)
        else:
            winSequenceRound.append([j, i])
            self.animalScores[indexI] += k * (0 - Rij)
            self.animalScores[indexJ] -= k * (0 - Rij)

    self.winSequenceGlobal.append(winSequenceRound)

## <Checkpoint>
