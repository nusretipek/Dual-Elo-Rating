#ifndef K2_OPTIMIZER_H
#define K2_OPTIMIZER_H

#include <tuple>
#include <vector>
#include <limits>
#include <dlib/optimization.h>
#include "combinational_indices.h"
#include "combinational_spikes.h"
#include "player_registry.h"


// Define constants for optimization
const double LOWEST_LOSS = std::numeric_limits<double>::infinity();
const double INITIAL_K2_VALUE = 0.0;
const double SEARCH_STEP = 0.25;
const double SEARCH_UPPER_BOUND = 7.0;
const double LOG_PROBABILITY_EPSILON_K2_OPTIMIZER = 1e-1;
const double MAX_ITERATION = 20;
const double SEARCH_PERIMETER = 0.1;
const int MAX_STEP_TRIALS = 10;


class K2Optimizer {
public:
    // Constructor
    K2Optimizer(const std::vector<std::pair<int, int>>& data, 
                const std::vector<double>& eloValues, 
                const std::vector<double>& initialKValues, 
                const PlayerRegistry& registry,
                bool sortAccuracyFirst,
                int permuteN = 100, 
                int topN = 10,
                int verbose = 0);
    
    // Member functions
    void K2OptimizerStepVerbose(double, std::tuple<double, double, std::vector<int>>);
    void K2OptimizerResultVerbose();
    std::tuple<std::vector<double>, std::vector<int>> run();

private:
    std::vector<std::pair<int, int>> data;
    std::vector<double> eloValues;
    std::vector<double> initialKValues;
    std::vector<double> kValues;
    bool sortAccuracyFirst;
    int permuteN;
    int topN;
    int verbose;
    const PlayerRegistry& registry;

    // Parameters
    double searchLowerBound = std::log(kValues[0]);
    double searchParameterAdjusted = searchLowerBound > 0 ? (searchLowerBound >= 7 ? 5 : searchLowerBound) : 1;
    double bestInitialParameter = INITIAL_K2_VALUE;
    double bestLoss = -LOWEST_LOSS;
    double tempParameter;
    double tempLoss;
};

#endif // K2_OPTIMIZER_H
