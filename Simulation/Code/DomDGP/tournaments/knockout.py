import numpy as np
import warnings


def knockout(self) -> None:
    # Assert
    assert self.N & (self.N - 1) == 0, "Knockout tournament is only implemented for 2^N!"
    assert self.decisionFunction is not None, \
        "Tournaments require a decision function, available options: " + str(self.decisionFunctions)

    if self.winSequenceGlobal:
        warnings.warn("Tournament data already generated, new tournament override interactions and win sequence!",
                      RuntimeWarning, stacklevel=3)
        self.interactions = []
        self.winSequenceGlobal = []

    # Local animals
    localAnimals = self.animals.copy()

    # Shuffle animals
    np.random.shuffle(localAnimals)

    # Knockout loop
    while len(localAnimals) > 1:
        # Call decision rule
        self.decisionRuleParser(interactions=localAnimals.reshape(-1, 2).tolist())

        # Update based on single elimination structure
        localAnimals = np.array(self.winSequenceGlobal[-1])[:, 0]

    # Parse interactions from winner sequence
    self.interactions = [sorted(item) for sublist in self.winSequenceGlobal for item in sublist]

## <Checkpoint>
