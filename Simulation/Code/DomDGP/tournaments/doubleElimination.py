import numpy as np
import warnings


def doubleElimination(self) -> None:
    # Assert
    assert self.N & (self.N - 1) == 0, "Double elimination tournament is only implemented for 2^N!"
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

    # First round
    self.decisionRuleParser(interactions=localAnimals.reshape(-1, 2).tolist())
    winnerLeagueAnimals = np.array(self.winSequenceGlobal[-1])[:, 0]
    loserLeagueAnimals = np.array(self.winSequenceGlobal[-1])[:, 1]

    # Winners league
    while len(winnerLeagueAnimals) > 1:
        self.decisionRuleParser(interactions=winnerLeagueAnimals.reshape(-1, 2).tolist())
        winnerLeagueAnimals = np.array(self.winSequenceGlobal[-1])[:, 0]
        downgradeLosers = np.array(self.winSequenceGlobal[-1])[:, 1]
        self.decisionRuleParser(interactions=loserLeagueAnimals.reshape(-1, 2).tolist())
        loserLeagueWinnerAnimals = np.array(self.winSequenceGlobal[-1])[:, 0]
        self.winSequenceGlobal = self.winSequenceGlobal[:-2] + [self.winSequenceGlobal[-2] + self.winSequenceGlobal[-1]]

        while ((len(downgradeLosers) + len(loserLeagueWinnerAnimals)) / 2) % 2 != 0 and len(loserLeagueWinnerAnimals) > 1:
            self.decisionRuleParser(interactions=loserLeagueWinnerAnimals.reshape(-1, 2).tolist())
            loserLeagueWinnerAnimals = np.array(self.winSequenceGlobal[-1])[:, 0]

        loserLeagueAnimals = np.hstack((downgradeLosers,
                                        loserLeagueWinnerAnimals)).reshape(2, -1).reshape(-1, order='F')

        if len(winnerLeagueAnimals) == 1:
            # Last loser round
            self.decisionRuleParser(interactions=loserLeagueAnimals.reshape(-1, 2).tolist())
            loserLeagueAnimals = np.array(self.winSequenceGlobal[-1])[:, 0]

            # Final round
            finalAnimals = np.array([loserLeagueAnimals[0], winnerLeagueAnimals[0]])
            self.decisionRuleParser(interactions=finalAnimals.reshape(-1, 2).tolist())
            # Second game given loser branch winner wins the final round
            if self.winSequenceGlobal[-1][0][0] == loserLeagueAnimals[0]:
                self.decisionRuleParser(interactions=finalAnimals.reshape(-1, 2).tolist())

    # Parse interactions from winner sequence
    self.interactions = [sorted(item) for sublist in self.winSequenceGlobal for item in sublist]

## <Checkpoint>
