import numpy as np
from ortools.linear_solver import pywraplp
import itertools


def minimizeSwissCost(scores: np.ndarray, possiblePairings: np.ndarray):
    # Create cost matrix
    M = 99999.9
    pairings = np.array(list(itertools.combinations(np.arange(len(scores)), 2)))
    costs = np.full((len(scores), len(scores)), M, dtype=np.float64)
    vectorD = scores[pairings]
    differenceVector = np.abs(vectorD[:, 0] - vectorD[:, 1])
    costs[pairings[:, 0], pairings[:, 1]] = differenceVector
    costLowerIndices = np.tril_indices(len(scores), -1)
    costs[costLowerIndices] = costs.T[costLowerIndices]
    num_workers = len(costs)
    num_tasks = len(costs[0])

    possiblePairings = set(tuple(item) for item in possiblePairings)
    for pair in pairings:
        if tuple(pair) not in possiblePairings:
            costs[pair[0], pair[1]] = M
            costs[pair[1], pair[0]] = M

    # Create solver SCIP
    solver = pywraplp.Solver.CreateSolver("SCIP")
    if not solver:
        return None

    # Variables
    x = {}
    for i in range(num_workers):
        for j in range(num_tasks):
            x[i, j] = solver.IntVar(0, 1, "")

    # Constraints
    for i in range(num_workers):
        animalConstraint = []
        for j in range(num_tasks):
            if i != j:
                animalConstraint.append(x[i, j])
                animalConstraint.append(x[j, i])
            else:
                animalConstraint.append(x[i, j])
        solver.Add(solver.Sum(animalConstraint) == 1)

    # Objective
    objective_terms = []
    for i in range(num_workers):
        for j in range(num_tasks):
            objective_terms.append(costs[i][j] * x[i, j])
    solver.Minimize(solver.Sum(objective_terms))
    # Solve
    status = solver.Solve()

    # Get solution
    solution = []
    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
        for i in range(num_workers):
            for j in range(num_tasks):
                if x[i, j].solution_value() > 0.5 and costs[i][j] < M and costs[j][i] < M:
                    solution.append([i, j])
    else:
        return None

    # Return statement
    return solution


if __name__ == "__main__":
    scoreArr = np.array([7.6, 13.4, 15.8, 13.2, 22.8, 22.2], dtype=np.float64)
    pairingArr = np.array([[0, 2], [0, 3], [0, 4], [0, 5], [1, 2], [1, 3],
                           [1, 4], [1, 5], [2, 4], [2, 5], [3, 4], [3, 5]])
    minimizeSwissCost(scoreArr, pairingArr)

## <Checkpoint>
