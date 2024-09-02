import numpy as np
from typing import Optional, Union


def random(self, interactionN: int = 100, weights: Optional[Union[list, dict]] = None) -> None:
    weightsArr = None

    # Assert N type
    assert isinstance(interactionN, int) and interactionN > 0, "interactionN is not an integer > 0!"

    # Weight parameter typing assertions
    if weights is not None:
        assert (isinstance(weights, dict) or
                isinstance(weights, list)), "Weights is neither a dict, nor a list, nor an integer!"
        if isinstance(weights, dict) and self.nameList is not None:
            assert set(self.nameList) == set(weights.keys()), "The set of nameList is not equal to the set of dict keys."
        if isinstance(self.initialScores, list) and self.nameList is not None:
            assert len(self.nameList) == len(weights), "The length of nameList is not equal to length of weights."
        if isinstance(self.initialScores, list) and self.nameList is None:
            assert self.N == len(weights), "The group size (N) is not equal to length of initialScores."
        if isinstance(weights, dict):
            weightsArr = np.array([weights[animal] for animal in self.animals], dtype=np.float64)
        else:
            weightsArr = np.array(weights, dtype=np.float64)

        # Adjust to sum 1 for probability
        weightsArr /= np.sum(weightsArr)

    # Random DGP
    if weightsArr is None:
        for _ in range(interactionN):
            tempInteraction = np.sort(np.random.choice(self.animals, size=2, replace=False)).tolist()
            self.interactions.append(tempInteraction)
            if self.decisionFunction is not None:
                self.decisionRuleParser(interactions=[tempInteraction])
                self.winSequenceGlobal[-1] = self.winSequenceGlobal[-1][0]
    else:
        for _ in range(interactionN):
            tempInteraction = np.sort(np.random.choice(self.animals, size=2, replace=False, p=weightsArr)).tolist()
            self.interactions.append(tempInteraction)
            if self.decisionFunction is not None:
                self.decisionRuleParser(interactions=[tempInteraction])
                self.winSequenceGlobal[-1] = self.winSequenceGlobal[-1][0]

## <Checkpoint>
