# Tournament format models to generate data for pair-wise interactions

# Libraries
import typing
import math
import pprint
import itertools
import numpy as np
import pandas as pd


# DomDGP class
class DGP:
    def __init__(self,
                 N: int = None,
                 nameList: list = None,
                 decisionFunction: typing.Union[str, None] = None,
                 initialScores: typing.Union[int, dict, list] = 100,
                 seed: int = 68,
                 **kwargs) -> None:

        # Parsed parameters
        self.N = N
        self.nameList = nameList
        self.decisionFunction = decisionFunction
        self.initialScores = initialScores
        self.seed = seed
        self.kwargs = kwargs

        # Set seed
        np.random.seed(self.seed)

        # Internal parameters
        self.decisionFunctions = ["random", "bradleyterry", "elo"]
        self.interactions = []
        self.winSequenceGlobal = []
        self.animals = None
        self.animalScores = None
        self.animalScoresTimeline = None

        # Assertions
        ## Minimum group size
        assert self.N >= 2, "Minimum group size is 2!"

        ## Namelist length & uniqueness
        if self.nameList:
            assert self.N == len(self.nameList), "Name list doesn't match with group size!"
            assert len(set(self.nameList)) == len(self.nameList), "Repeated names present in the name list!"

        ## Initial scores typing
        assert isinstance(self.initialScores, dict) or isinstance(self.initialScores, list) \
               or isinstance(self.initialScores, int), "Initial scores is neither a dict, nor a list, nor an integer!"
        if isinstance(self.initialScores, dict) and self.nameList is not None:
            # Assert if the set of nameList is equal to the set of dict keys
            assert set(self.nameList) == set(self.initialScores.keys()), \
                "The set of nameList is not equal to the set of dict keys."
        if isinstance(self.initialScores, list) and self.nameList is not None:
            assert len(self.nameList) == len(self.initialScores), \
                "The length of nameList is not equal to length of initialScores."
        if isinstance(self.initialScores, list) and self.nameList is None:
            assert self.N == len(self.initialScores), "The group size (N) is not equal to length of initialScores."

        ## Decision function
        assert self.decisionFunction is None or self.decisionFunction.lower() in self.decisionFunctions, \
            "Decision function is not implemented choose from " + str(self.decisionFunctions) + "!"

        # Combine nameList and initial scores
        if isinstance(self.initialScores, dict):
            self.animals = np.array(list(self.initialScores.keys()))
            self.animalScores = np.array(list(self.initialScores.values()), dtype=np.float32)
        elif isinstance(self.initialScores, list) and nameList is None:
            self.animals = np.arange(self.N)
            self.animalScores = np.array(self.initialScores, dtype=np.float32)
        elif isinstance(self.initialScores, list) and nameList is not None:
            self.animals = np.array(self.nameList)
            self.animalScores = np.array(self.initialScores, dtype=np.float32)
        elif isinstance(self.initialScores, int) and nameList is None:
            self.animals = np.arange(self.N)
            self.animalScores = np.full(self.N, self.initialScores, dtype=np.float32)
        elif isinstance(self.initialScores, int) and nameList is not None:
            self.animals = np.array(self.nameList)
            self.animalScores = np.full(self.N, self.initialScores, dtype=np.float32)
        else:
            raise ValueError("Error in parsing nameList and initialScores!")

        # Animal scores timeline / Evolution of scores
        self.animalScoresTimeline = np.expand_dims(self.animalScores.copy(), axis=0)

    # Import Data generating Process (DGP) methods
    from .tournaments.knockout import knockout
    from .tournaments.doubleElimination import doubleElimination
    from .tournaments.roundRobin import roundRobin
    from .tournaments.swiss import swiss
    from .random.random import random
    from .graph.directedGraph import directedGraph

    # Decision function
    from .decisionFunctions.randomDecision import randomDecision
    from .decisionFunctions.BradleyTerry import BradleyTerry
    from .decisionFunctions.eloRating import eloRating

    # Plotting
    from .plots.animalScoresTimeline import plotAnimalScoreTimeline

    def decisionRuleParser(self, interactions: np.ndarray = None):
        if self.decisionFunction.lower() == self.decisionFunctions[0]:
            self.randomDecision(interactions)
        elif self.decisionFunction.lower() == self.decisionFunctions[1]:
            self.BradleyTerry(interactions, **self.kwargs)
        elif self.decisionFunction.lower() == self.decisionFunctions[2]:
            self.eloRating(interactions, **self.kwargs)

        # Collect current animal scores after each round
        self.animalScoresTimeline = np.vstack((self.animalScoresTimeline, self.animalScores))

    def plotTimeline(self):
        fig = self.plotAnimalScoreTimeline()
        fig.show()

    def toCSV(self, filename):
        interactionsDataFrame = pd.DataFrame(self.winSequenceGlobal, columns=["Initiator", "Receiver"])
        interactionsDataFrame.to_csv(filename, index=False, header=True)

    ## <Class Checkpoint>


if __name__ == "__main__":
    DGP = DomDGP(N=8,
                 nameList=["a", "b", "c", "d", "e", "f", "g", "h"],
                 decisionFunction="random",
                 S=20,
                 swissRoundN=10)
    DGP.knockout()
    pprint.pprint(DGP.__dict__)

# initialScores

## <Main Checkpoint>
