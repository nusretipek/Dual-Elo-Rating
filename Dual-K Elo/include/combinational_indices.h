#ifndef COMBINATIONAL_INDICES_H
#define COMBINATIONAL_INDICES_H

#include <vector>
#include <random>
#include <dlib/matrix.h>
#include "verbose.h"

// Define constants for optimization
const double LOSS_THRESHOLD = 9.99e-1;
const double ACCURACY_ACTIVATION = 5.0;
const double LOSS_ACTIVATION = 1.0;


class CombinationalIndices {
public:
    // Constructor
    CombinationalIndices(const std::vector<std::pair<int, int>>& data, 
                         const std::vector<double>& eloValues, 
                         const std::vector<double>& kValues, 
                         int permuteN = 100, 
                         int topN = 10, 
                         int verbose = 0);

    // Member functions
    std::vector<int> run();

private:
    // Data
    std::vector<std::pair<int, int>> data;
    dlib::matrix<int> d;
    std::vector<double> eloValues;
    const std::vector<double> kValues;

    // Parameters
    std::vector<int> players;
    int playerCount;
    int permuteN;
    int topN;
    int verbose;

    // Internal states
    dlib::matrix<double, 0, 1> eloScores;
		
	// Helper function (argsort - matrix)
    std::vector<int> argsortMatrix(const dlib::matrix<int>& v) {
        std::vector<int> idx(v.size());
        std::iota(idx.begin(), idx.end(), 0);
        std::sort(idx.begin(), idx.end(), [&v](int i1, int i2) {
            return v(i1) > v(i2);
        });

        return idx;
    }
};

#endif // COMBINATIONAL_INDICES_H