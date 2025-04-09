#ifndef COMBINATIONAL_SPIKES_H
#define COMBINATIONAL_SPIKES_H

#include <vector>
#include <dlib/matrix.h>
#include "verbose.h"
#include "calculation.h"

// Define constants for optimization
const double THRESHOLD_ACC_SUBCALL_1 = 1.0;
const double THRESHOLD_ACC_SUBCALL_2 = 2.0;
const double THRESHOLD_FULL_STRONG = 7.5;
const double THRESHOLD_NON_FULL_STRONG = 1.0;

// Best parameter selection Shared Parameters
const double THRESHOLD_INDEX_0_LOSS_DIFFERENCE = 1.0;
const double THRESHOLD_INDEX_0_ACCURACY_DIFFERENCE = 0.000;

// KValueOptimizer SubCall Parameters
const double THRESHOLD_SUBCALL_NON_FULL_LOSS_DIFFERENCE = 0.5;
const double THRESHOLD_SUBCALL_NON_FULL_LOSS_DIFFERENCE_LOWER_BOUND = 0.75;
const double THRESHOLD_SUBCALL_NON_FULL_ACCURACY_DIFFERENCE_LOWER_BOUND = 0.0;

// Full Model Final Call Parameters
const double THRESHOLD_FULL_INDEX_0_LOSS_DIFFERENCE = 1.0;
const double THRESHOLD_FULL_INDEX_0_ACCURACY_DIFFERENCE = 0.001;
const double THRESHOLD_FULL_LOSS_DIFFERENCE = 3; //switched from 5
const double THRESHOLD_FULL_LOSS_DIFFERENCE_LOWER_BOUND = 7.5;
const double THRESHOLD_FULL_ACCURACY_DIFFERENCE_LOWER_BOUND = 0.0;

// Other Call Parameters
const double THRESHOLD_OTHER_LOSS_DIFFERENCE = 0.5;
const double THRESHOLD_OTHER_LOSS_DIFFERENCE_LOWER_BOUND = 0.75;
const double THRESHOLD_OTHER_ACCURACY_DIFFERENCE_LOWER_BOUND = 0.0;



class CombinationalSpikes {
public:
    // Constructor
    CombinationalSpikes(const std::vector<std::pair<int, int>>& data, 
                        const std::vector<double>& eloValues,
                        const std::vector<double>& kValues, 
                        std::vector<int> indices, 
                        bool sortAccuracyFirst,
                        int verbose = 0, 
                        bool subcall = false, 
                        bool fullModel = false);

    // Member functions
    void getCombinations();
    void getBestIndex();
    void printResults(std::unordered_map<int, int>);
    std::tuple<double, double, std::vector<int>> run();

private:
    // Data
    std::vector<std::pair<int, int>> data;
    dlib::matrix<int> d;
    std::vector<double> eloValues;
    const std::vector<double> kValues;
    std::vector<int> indices;
    std::vector<std::vector<int>> flattenedCombinations;
    std::vector<std::tuple<double, double, std::vector<int>>> sortedCombinationLoss;
    std::vector<double> relativeDifference;
    std::vector<double> relativeAccuracies;
    std::vector<std::tuple<double, double, std::vector<int>>> CombinationLoss;
    int bestCombIndex = 0;

    // Parameters
    std::vector<int> players;
    int playerCount;
    bool sortAccuracyFirst;
    int verbose;
    bool subcall;
    bool fullModel;
    // Internal states

    dlib::matrix<double, 0, 1> eloScores;
};

#endif // COMBINATIONAL_SPIKES_H