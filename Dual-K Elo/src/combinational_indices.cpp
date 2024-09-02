#include "combinational_indices.h"

CombinationalIndices::CombinationalIndices(const std::vector<std::pair<int, int>>& data, 
                                           const std::vector<double>& eloValues, 
                                           const std::vector<double>& kValues, 
                                           int permuteN, 
                                           int topN, 
                                           int verbose)
    : data(data), eloValues(eloValues), kValues(kValues), permuteN(permuteN), topN(topN), verbose(verbose) {

        // Initialize players and playerCount
        std::set<int> playersSet;
        for (const auto& pair : data) {
            playersSet.insert(pair.first);
            playersSet.insert(pair.second);
        }

        players = std::vector<int>(playersSet.begin(), playersSet.end());
        playerCount = players.size();

        // Parse Interactions
        d.set_size(data.size(), 2);
        for (size_t i = 0; i < data.size(); ++i) {
            d(i, 0) = data[i].first;
            d(i, 1) = data[i].second;
        }

        // Initialize eloScores
        eloScores.set_size(playerCount);
        for (int i = 0; i < playerCount; ++i) {
            eloScores(i) = eloValues[i];
        }
}

std::vector<int> CombinationalIndices::run() {

    // Benchmark run
    double tempTrainLoss = 0; 
    double tempTrainAcc = 0;
    for (int i = 0; i < d.nr(); ++i) {
        double eloDifference = eloScores(d(i, 0)) - eloScores(d(i, 1));
        double probabilityWin = 1 / (1 + exp(-0.01 * eloDifference));
        eloScores(d(i, 0)) += kValues[0] * (1 - probabilityWin);
        eloScores(d(i, 1)) -= kValues[0] * (1 - probabilityWin);
        tempTrainLoss += log(probabilityWin);
        if (probabilityWin >= 0.5) {
            tempTrainAcc += 1;
        }
    }
    tempTrainAcc /= d.nr();

    // Parameters & Temporary results
    dlib::matrix<int> activatedKeys(d.nr(), 1);
    for (int i = 0; i < d.nr(); ++i) {
        activatedKeys(i, 0) = 0;
    }    
            
    std::vector<int> iL(d.nr());
    std::iota(iL.begin(), iL.end(), 0);
    for (int idy = 0; idy < permuteN; idy++) {
        double optimizedLoss = tempTrainLoss;
        double optimizedAcc = tempTrainAcc;
        dlib::matrix<double, 0, 1> Kt(d.nr());
        for (int i = 0; i < d.nr(); ++i) {
            Kt(i) = kValues[0];
        }
                    
        std::default_random_engine rng;
        std::shuffle(iL.begin(), iL.end(), rng);
        for (auto i : iL) {
            Kt(i) = Kt(i) == kValues[0] ? kValues[1] : kValues[0];
            double iterationTrainLoss = 0;
            double iterationTrainAcc = 0;
            dlib::matrix<double, 0, 1> tempEloScores(eloValues.size());
                            for (int idx = 0; idx < playerCount; ++idx) {
                                tempEloScores(idx) = eloValues[idx];
                            }     
            for (int j = 0; j < d.nr(); ++j) {
                double eloDifference = tempEloScores(d(j, 0)) - tempEloScores(d(j, 1));
                double probabilityWin = 1 / (1 + exp(-0.01 * eloDifference));
                tempEloScores(d(j, 0)) += Kt(j) * (1 - probabilityWin);
                tempEloScores(d(j, 1)) -= Kt(j) * (1 - probabilityWin);
                iterationTrainLoss += log(probabilityWin);
                if (probabilityWin >= 0.5) {
                    iterationTrainAcc += 1;
                }
            }
            iterationTrainAcc /= d.nr();
            if (iterationTrainAcc > optimizedAcc && iterationTrainLoss > optimizedLoss) {
                activatedKeys(i, 0) += ACCURACY_ACTIVATION;
                optimizedLoss = iterationTrainLoss;
                optimizedAcc = iterationTrainAcc;
            }
            else if (iterationTrainAcc == optimizedAcc && iterationTrainLoss - optimizedLoss > LOSS_THRESHOLD) {
                activatedKeys(i, 0) += LOSS_ACTIVATION;
                optimizedLoss = iterationTrainLoss;
                optimizedAcc = iterationTrainAcc; 
            }
            else {
                Kt(i) = Kt(i) == kValues[0] ? kValues[1] : kValues[0];
            }
        }
    }

    std::vector<int> indices = argsortMatrix(activatedKeys);
    if (int(indices.size()) > topN) {
            indices.resize(topN);
    }
    
    // printVector(indices); CHECK / DELETE
    //std::cout << std::endl;
    return indices;
}