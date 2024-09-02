import numpy as np


def BradleyTerry(self, interactions: np.ndarray = None, **kwargs) -> None:
    # Assertions
    assert interactions is not None

    # Arguments
    BradleyTerryUpdateC = kwargs['BradleyTerryUpdateC'] if 'BradleyTerryUpdateC' in kwargs else 15

    # Calculate Bradley-Terry Model
    winSequenceRound = []
    for i, j in interactions:
        indexI = np.where(self.animals == i)[0]
        indexJ = np.where(self.animals == j)[0]

        Rij = self.animalScores[indexI] / (self.animalScores[indexI] + self.animalScores[indexJ])
        if np.random.uniform() < Rij:
            winSequenceRound.append([i, j])
            self.animalScores[indexI] += BradleyTerryUpdateC * (1 - Rij)
            self.animalScores[indexJ] -= BradleyTerryUpdateC * (1 - Rij)
        else:
            winSequenceRound.append([j, i])
            self.animalScores[indexI] += BradleyTerryUpdateC * (0 - Rij)
            self.animalScores[indexJ] -= BradleyTerryUpdateC * (0 - Rij)

    self.winSequenceGlobal.append(winSequenceRound)

## <Checkpoint>
