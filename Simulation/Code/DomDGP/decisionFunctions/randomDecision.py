import numpy as np


def randomDecision(self, interactions: np.ndarray = None) -> None:
    # Assertions
    assert interactions is not None

    # Calculate Random
    winSequenceRound = []
    for i, j in interactions:
        Rij = np.random.choice([0, 1])
        if Rij:
            winSequenceRound.append([i, j])
        else:
            winSequenceRound.append([j, i])
    self.winSequenceGlobal.append(winSequenceRound)

## <Checkpoint>
