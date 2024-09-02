#ifndef FULL_OPTIMIZER_H
#define FULL_OPTIMIZER_H

#include <string>
#include <tuple>
#include <vector>
#include <limits>
#include <dlib/matrix.h>
#include <dlib/optimization.h>
#include "convert.h"
#include "calculation.h"
#include "combinational_indices.h"
#include "combinational_spikes.h"


// Define constants for optimization
const double K2_UPPER_BOUND_EXP = 8.0;
const double HIGHER_K1_LOSS_PENALTY = 9999.9;
const double LOG_PROBABILITY_EPSILON_FULL_MODEL_OPTIMIZER = 1e-8;

void writeRankingToFile(const std::string& fileName, int step, const std::vector<int>& ranking);
void writeEloToFile(const std::string& fileName, const std::vector<double>& data);

class FullOptimizer {
public:
    // Constructor
    FullOptimizer(const std::vector<std::pair<int, int>>& data, 
                  const std::vector<double>& eloValues, 
                  const std::vector<double>& initialKValues, 
                  std::vector<int> indices, 
                  int verbose = 0);

    // Member functions
    void FullOptimizerResultVerbose(dlib::matrix<double,0,1>, dlib::matrix<double, 0, 1>);
    void run();

private:
    std::vector<std::pair<int, int>> data;
    std::vector<int> players;
    std::vector<double> eloValues;
    std::vector<double> kValues;
    std::vector<int> indices;
    std::unordered_map<int, size_t> playerIndexMap;
    dlib::matrix<long> d;
    int playerCount;
    int verbose;

    // Parameters
    std::vector<double> finalElo;
    dlib::matrix<double, 0, 1> Kt;
};

#endif // FULL_OPTIMIZER_H