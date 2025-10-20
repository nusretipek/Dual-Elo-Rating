#ifndef OPTIMIZED_ELO_H
#define OPTIMIZED_ELO_H

#include <vector>
#include <limits>
#include <unordered_map>
#include <dlib/optimization.h>
#include <dlib/matrix.h>
#include "calculation.h"
#include "convert.h"
#include "player_registry.h"

// Define constants for optimization
const double INITIAL_K_VALUE = 5.0;
const double INITIAL_ELO_VALUE = 0.0;
const double LOWER_BOUND_INITIAL = -10.0;
const double UPPER_BOUND_INITIAL = 10.0;
const double BOUND_INF = std::numeric_limits<double>::infinity();
const double LOG_PROBABILITY_EPSILON = 1e-10;

class OptimizedElo {
public:
    // Constructor
    OptimizedElo(const std::vector<std::pair<int, int>>& data, const PlayerRegistry& registry, int verbose = 0);

    // Member functions
    std::tuple<double, dlib::matrix<double,0,1>, std::vector<double>, double, double> run();

private:
    std::vector<std::pair<int, int>> data;
    std::vector<int> players;
    std::unordered_map<int, int> playerIndexMap;
    int playerCount;
    int verbose;
    const PlayerRegistry& registry;
};
#endif // OPTIMIZED_ELO_H
