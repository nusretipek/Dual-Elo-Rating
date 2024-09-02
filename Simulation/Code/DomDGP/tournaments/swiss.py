import numpy as np
import itertools
import warnings
import math
from ..optimizers import swissOptimizer


def swiss(self, swissRoundN: int = 10, pairingType: str = "deterministic") -> None:
    # Argument Assert
    pairingTypes = ["probabilistic", "deterministic", "optimized"]
    assert pairingType.lower() in pairingTypes, "Pairing type not supported, choose from " + str(pairingTypes) + "!"
    assert self.decisionFunction is not None, \
        "Tournaments require a decision function, available options: " + str(self.decisionFunctions)
    if self.winSequenceGlobal:
        warnings.warn("Tournament data already generated, new tournament override interactions and win sequence!",
                      RuntimeWarning, stacklevel=3)
        self.interactions = []
        self.winSequenceGlobal = []

    def _generateSwissRoundProbabilistic(pairs):
        possiblePlayersRoundProbabilistic = list(set(pairs.flatten().tolist()))
        possibleMatchesProbabilistic = int(math.floor(len(possiblePlayersRoundProbabilistic) / 2))
        pairingIndices = np.vectorize(lambda ps: np.where(self.animals == ps)[0])(pairs)
        vectorD = self.animalScores[pairingIndices]

        # Calculate probability vector where closer score animals has more chance to play
        probabilityVector = np.abs(vectorD[:, 0] - vectorD[:, 1] + 1e-3)
        probabilityVector = 1 / np.array(probabilityVector)
        probabilityVector = np.divide(probabilityVector, np.sum(probabilityVector))

        # Randomly select pairs ensuring each player plays only once
        roundPairs = []
        pairedPlayers = set()
        while len(roundPairs) < possibleMatchesProbabilistic:
            pairIndex = np.random.choice(np.arange(len(pairs)), p=probabilityVector)
            pair = pairs[pairIndex]
            if not pairedPlayers.intersection(pair):
                roundPairs.append(pair)
                pairedPlayers.update(pair)
                pairs = [_ for _ in pairs if not set(_) & set(pair)]
                if len(pairs) > 0:
                    pairingIndices = np.vectorize(lambda ps: np.where(self.animals == ps)[0])(pairs)
                    vectorD = self.animalScores[pairingIndices]
                    probabilityVector = np.abs(vectorD[:, 0] - vectorD[:, 1] + 1e-3)
                    probabilityVector = 1 / np.array(probabilityVector)
                    probabilityVector = np.divide(probabilityVector, np.sum(probabilityVector))
                else:
                    break

        return np.array(roundPairs)

    def _generateSwissRoundDeterministic(pairs):
        possiblePlayersRoundTempDeterministic = list(set(pairs.flatten().tolist()))
        possibleMatchesDeterministic = int(math.floor(len(possiblePlayersRoundTempDeterministic) / 2))
        pairingIndices = np.vectorize(lambda ps: np.where(self.animals == ps)[0])(pairs)
        vectorD = self.animalScores[pairingIndices]

        # Calculate probability vector where closer score animals has more chance to play
        differenceVector = np.abs(vectorD[:, 0] - vectorD[:, 1])

        # Deterministic selection of pairs ensuring each player plays only once
        roundPairs = []
        pairedPlayers = set()
        while len(roundPairs) < possibleMatchesDeterministic:
            pairIndex = np.where(differenceVector == differenceVector.min())[0][0]
            pair = pairs[pairIndex]
            if not pairedPlayers.intersection(pair):
                roundPairs.append(pair)
                pairedPlayers.update(pair)
                mask = ~(np.isin(pairs[:, 0], pair) | np.isin(pairs[:, 1], pair))
                pairs = pairs[mask]

                if len(pairs) > 0:
                    pairingIndices = np.vectorize(lambda ps: np.where(self.animals == ps)[0])(pairs)
                    vectorD = self.animalScores[pairingIndices]
                    differenceVector = np.abs(vectorD[:, 0] - vectorD[:, 1])
                else:
                    break

        return np.array(roundPairs)

    def _generateSwissRoundOptimized(pairs):
        pairingsIndices = np.vectorize(lambda ps: np.where(self.animals == ps)[0])(pairs)
        roundPairs = swissOptimizer.minimizeSwissCost(self.animalScores, pairingsIndices)
        return np.array(roundPairs)

    # Generate first random round
    pairings = np.array(list(itertools.combinations(self.animals, 2)))
    pairingsSwiss = pairings.copy()
    roundPairings = None

    # Swiss loop
    for _ in range(swissRoundN):
        # Generate probabilistic Swiss tournament
        if pairingType.lower() == pairingTypes[0]:
            possiblePlayersRoundTemp = list(set(pairingsSwiss.flatten().tolist()))
            possibleMatches = int(math.floor(len(possiblePlayersRoundTemp) / 2))
            roundPairings = _generateSwissRoundProbabilistic(pairingsSwiss)
            # In probabilistic, suboptimal solutions might exist with fewer matches than possible per round
            for i in range(10):
                if len(roundPairings) < possibleMatches:
                    roundPairings = _generateSwissRoundProbabilistic(pairingsSwiss)
                else:
                    break

        # Generate deterministic Swiss tournament (heuristics)
        elif pairingType.lower() == pairingTypes[1]:
            roundPairings = _generateSwissRoundDeterministic(pairingsSwiss)

        # Generate optimized Swiss tournament
        elif pairingType.lower() == pairingTypes[2]:
            roundPairings = _generateSwissRoundOptimized(pairingsSwiss)
            roundPairings = self.animals[roundPairings]

        # Update not matched pairings and decide round pairings
        if roundPairings is not None:
            # Remove round pairings from the tournament
            pairingsSwiss = pairingsSwiss[~np.all(pairingsSwiss == roundPairings[:, None], axis=-1).any(axis=0)]

            # Call decision rule
            self.decisionRuleParser(interactions=roundPairings.tolist())

        # If Round-Robin condition satisfied exit gracefully
        if pairingsSwiss.shape[0] == 0:
            print("All pairings matched already. Exiting at round " + str(_ + 1) + "!")
            break

    # Parse interactions from winner sequence
    self.interactions = [sorted(item) for sublist in self.winSequenceGlobal for item in sublist]

## <Checkpoint>
