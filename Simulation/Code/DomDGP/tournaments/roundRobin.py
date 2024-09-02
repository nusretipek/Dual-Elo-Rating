import numpy as np
import itertools
import warnings
import math


def roundRobin(self, roundN=1) -> None:
    #vAssert
    assert self.decisionFunction is not None, \
        "Tournaments require a decision function, available options: " + str(self.decisionFunctions)
    if self.winSequenceGlobal:
        warnings.warn("Tournament data already generated, new tournament override interactions and win sequence!",
                      RuntimeWarning, stacklevel=3)
        self.interactions = []
        self.winSequenceGlobal = []

    # Pairing function
    def _generateRoundRobinRound(pairs):
        roundPairs = []
        pairedPlayers = set()

        # Select pairs ensuring each player plays only once
        for pair in pairs:
            if not pairedPlayers.intersection(pair):
                roundPairs.append(pair)
                pairedPlayers.update(pair)

        return np.array(roundPairs)

    for _ in range(roundN):
        # Generate combinations
        pairings = np.array(list(itertools.combinations(self.animals, 2)))

        # Round-Robin loop
        while len(pairings) > 0:
            possiblePlayersRoundTemp = list(set(pairings.flatten().tolist()))
            possibleMatches = int(math.floor(len(possiblePlayersRoundTemp) / 2))
            roundPairings = []
            counter = 0

            while len(roundPairings) < possibleMatches:
                np.random.shuffle(pairings)
                roundPairings = _generateRoundRobinRound(pairings)
                counter += 1
                if counter > possibleMatches**3 and possibleMatches != 1:
                    possibleMatches -= 1

            pairings = pairings[~np.all(pairings == roundPairings[:, None], axis=-1).any(axis=0)]

            # Call decision rule
            self.decisionRuleParser(interactions=roundPairings.tolist())

    # Parse interactions from winner sequence
    self.interactions = [sorted(item) for sublist in self.winSequenceGlobal for item in sublist]

## <Checkpoint>
