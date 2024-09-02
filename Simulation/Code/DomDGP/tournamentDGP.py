# Tournament format models to generate data for pair-wise interactions

# Libraries
import sys
import numpy as np
import pandas as pd
import typing
import math
import pprint
import itertools
import argparse


# Tournament class
class Tournament:
    def __init__(self,
                 N: int = None,
                 nameList: list = None,
                 tournamentFormat: str = None,
                 decisionFunction: str = "random",
                 DtDict: dict = None,
                 seed: int = 68,
                 **kwargs) -> None:

        # Parsed parameters
        self.N = N
        self.nameList = nameList
        self.tournamentFormat = tournamentFormat
        self.seed = seed
        self.decisionFunction = decisionFunction
        self.DtDict = DtDict
        self.kwargs = kwargs

        # Set seed
        np.random.seed(self.seed)

        # Internal parameters
        self.tournamentFormats = ["knockout", "round-robin", "swiss"]
        self.decisionFunctions = ["random", "mirror"]
        self.winSequenceGlobal = []
        self.animals = None

        if self.nameList:
            self.animals = np.array(nameList)
        else:
            self.animals = np.arange(self.N)
        if not self.DtDict:
            self.DtDict = {i: 100 for i in self.animals}  # np.random.randint(50,100)

        # Assertions
        assert self.N >= 2, "Minimum group size is 2!"
        if self.nameList:
            assert self.N == len(self.nameList), "Name list doesn't match with group size!"
            assert len(set(self.nameList)) == len(self.nameList), "Repeated names present in the name list!"
        assert self.tournamentFormat.lower() in self.tournamentFormats, \
            "Tournament type is not implemented choose from " + str(self.tournamentFormats) + "!"
        assert self.decisionFunction.lower() in self.decisionFunctions, \
            "Decision function is not implemented choose from " + str(self.decisionFunctions) + "!"

        # Tournaments
        if self.tournamentFormat.lower() == self.tournamentFormats[0]:
            assert math.log2(self.N).is_integer(), \
                "Knockout tournaments not implemented for group size not equal to 2^N!"
            self.__knockout()
            flattenedWinSequenceGlobal = np.array([item for sublist in self.winSequenceGlobal for item in sublist])
            self.pairsDataFrame = pd.DataFrame(flattenedWinSequenceGlobal,
                                               columns=["Initiator", "Receiver"])

        elif self.tournamentFormat.lower() == self.tournamentFormats[1]:
            self.__roundRobin()
            flattenedWinSequenceGlobal = np.array([item for sublist in self.winSequenceGlobal for item in sublist])
            self.pairsDataFrame = pd.DataFrame(flattenedWinSequenceGlobal,
                                               columns=["Initiator", "Receiver"])

        elif self.tournamentFormat.lower() == self.tournamentFormats[2]:
            self.__swiss(**self.kwargs)
            flattenedWinSequenceGlobal = np.array([item for sublist in self.winSequenceGlobal for item in sublist])
            self.pairsDataFrame = pd.DataFrame(flattenedWinSequenceGlobal,
                                               columns=["Initiator", "Receiver"])

    ###################################
    ### Tournament implementations  ###
    ###################################

    # Pairing Function
    @staticmethod
    def _generateRoundRobinRound(pairs, prevWP):
        possiblePlayersRound = list(set(pairs.flatten().tolist()))

        nextWP = None
        if len(possiblePlayersRound) % 2 != 0 and len(pairs) > 1:
            if prevWP:
                possiblePlayersRound.remove(prevWP)
            print(possiblePlayersRound, np.random.choice(possiblePlayersRound))
            nextWP = np.random.choice(possiblePlayersRound)
            pairs = np.array([pair for pair in pairs if nextWP not in pair])

        np.random.shuffle(pairs)
        roundPairs = []
        pairedPlayers = set()

        # Randomly select pairs ensuring each player plays only once
        for pair in pairs:
            if not pairedPlayers.intersection(pair):
                roundPairs.append(pair)
                pairedPlayers.update(pair)

        return nextWP, np.array(roundPairs)

    @staticmethod
    def _generateSwissRound(pairs, vectorD):

        possiblePlayersRoundTemp = list(set(pairs.flatten().tolist()))
        possibleMatches = int(math.floor(len(possiblePlayersRoundTemp) / 2))

        # Calculate probability vector where closer score animals has more chance to play
        probabilityVector = np.array([abs(vectorD[i] - vectorD[j] + 1e-3) for i, j in pairs])
        probabilityVector = 1 / np.array(probabilityVector)
        probabilityVector = np.divide(probabilityVector, np.sum(probabilityVector))

        # Randomly select pairs ensuring each player plays only once
        roundPairs = []
        pairedPlayers = set()
        while len(roundPairs) < possibleMatches:
            pairIndex = np.random.choice(np.arange(len(pairs)), p=probabilityVector)
            pair = pairs[pairIndex]
            if not pairedPlayers.intersection(pair):
                roundPairs.append(pair)
                pairedPlayers.update(pair)
                pairs = [_ for _ in pairs if pair not in _]

                probabilityVector = np.array([abs(vectorD[i] - vectorD[j] + 1e-3) for i, j in pairs])
                probabilityVector = 1 / np.array(probabilityVector)
                probabilityVector = np.divide(probabilityVector, np.sum(probabilityVector))

        return np.array(roundPairs)

    def __knockout(self) -> None:
        # Shuffle animals
        np.random.shuffle(self.animals)

        # Knockout loop
        while len(self.animals) > 1:

            # Call decision rule
            self.decisionRuleParser(interactions=self.animals.reshape(-1, 2))

            # Update based on single elimination structure
            self.animals = np.array(self.winSequenceGlobal[-1])[:, 0]

    def __roundRobin(self) -> None:
        # Generate combinations
        pairings = np.array(list(itertools.combinations(self.animals, 2)))
        waitingPlayer = None

        # Round-Robin loop
        while len(pairings) > 0:
            possiblePlayersRoundTemp = list(set(pairings.flatten().tolist()))
            possibleMatches = int(math.floor(len(possiblePlayersRoundTemp) / 2))
            roundPairings = []
            waitingPlayerTemp = None
            counter = 0

            while len(roundPairings) < possibleMatches:
                waitingPlayerTemp, roundPairings = self._generateRoundRobinRound(pairings, prevWP=waitingPlayer)
                counter += 1
                if counter > possibleMatches ** 2 and possibleMatches != 1:
                    possibleMatches -= 1

            waitingPlayer = waitingPlayerTemp
            print(waitingPlayer, "\n---\n", roundPairings, "\n---\n", pairings)

            pairings = pairings[~np.all(pairings == roundPairings[:, None], axis=-1).any(axis=0)]
            # print(waitingPlayer, "\n---\n", roundPairings, "\n---\n", pairings)
            print("\n---\n")

            # Call decision rule
            self.decisionRuleParser(interactions=roundPairings)

    def __swiss(self, **kwargs) -> None:
        # Generate first random round
        pairings = np.array(list(itertools.combinations(self.animals, 2)))
        pairingsRoundRobin = pairings.copy()

        # Arguments
        roundCount = kwargs['swissRoundN'] if 'swissRoundN' in kwargs else 10

        # Swiss loop
        for _ in range(roundCount):
            roundPairings = self._generateSwissRound(pairings, self.DtDict)
            pairingsRoundRobin = pairingsRoundRobin[
                ~np.all(pairingsRoundRobin == roundPairings[:, None], axis=-1).any(axis=0)]

            # Call decision rule
            self.decisionRuleParser(interactions=roundPairings)

            # If Round-Robin condition satisfied exit gracefully
            if pairingsRoundRobin.shape[0] == 0:
                print("All pairings matched already. Exiting at round " + str(_ + 1) + "!")
                break

    ###################################
    ## Decision rule implementations ##
    ###################################

    def decisionRuleParser(self, interactions: np.ndarray = None):
        if self.decisionFunction.lower() == "mirror":
            self.MIRROR(interactions, **self.kwargs)
        elif self.decisionFunction.lower() == "random":
            self.Random(interactions)

    def MIRROR(self, interactions: np.ndarray = None, **kwargs) -> None:
        # Assertions
        assert interactions is not None

        # Arguments
        S = kwargs['S'] if 'S' in kwargs else 15

        # Calculate MIRROR
        winSequenceRound = []
        for i, j in interactions:
            Rij = self.DtDict[i] / (self.DtDict[i] + self.DtDict[j])
            if np.random.uniform() < Rij:
                winSequenceRound.append([i, j])
                self.DtDict[i] += S * (1 - Rij)
                self.DtDict[j] -= S * (1 - Rij)
            else:
                winSequenceRound.append([j, i])
                self.DtDict[i] += S * (0 - Rij)
                self.DtDict[j] -= S * (0 - Rij)

        self.winSequenceGlobal.append(winSequenceRound)

    def Random(self, interactions: np.ndarray = None) -> None:
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


if __name__ == "__main__":

    tournament = Tournament(N=8,
                            nameList=["a", "b", "c", "d", "e", "f", "g", "h"],
                            tournamentFormat="knockout",
                            decisionFunction="random",
                            S=20,
                            swissRoundN=10)

    pprint.pprint(tournament.__dict__)
