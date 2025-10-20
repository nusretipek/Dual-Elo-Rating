#include "full_optimizer.h"

void writeRankingToFile(const std::string& fileName, int step, const std::vector<int>& ranking) {
    std::ofstream file(fileName, std::ios::app);
    if (file.is_open()) {
        file << step << " - ";
        for (size_t i = 0; i < ranking.size(); ++i) {
            file << ranking[i];
            if (i != ranking.size() - 1) {
                file << " ";
            }
        }
        file << "\n";
    }
    file.close();
}

void writeEloToFile(const std::string& fileName, const std::vector<double>& data) {
    std::ofstream file(fileName, std::ios::app);
    if (file.is_open()) {
        file << "[";  
        for (size_t i = 0; i < data.size(); ++i) {
            file << data[i];
            if (i != data.size() - 1) {
                file << ", ";  
            }
        }
        file << "]\n";
        file.close();
    } 
}

// Constructor definition
FullOptimizer::FullOptimizer(const std::vector<std::pair<int, int>>& data, 
                             const std::vector<double>& eloValues, 
                             const std::vector<double>& initialKValues, 
                             std::vector<int> indices, 
                             const PlayerRegistry& registry,
                             int verbose)
    : data(data), players(), eloValues(eloValues), kValues(initialKValues), indices(indices), playerIndexMap(), d(), playerCount(0), verbose(verbose), registry(registry) {
            
        // Initialize players and count
        std::set<int> playerSet;
        for (const auto& interaction : data) {
            playerSet.insert(interaction.first);
            playerSet.insert(interaction.second);
        }
                
        players.assign(playerSet.begin(), playerSet.end());
        playerCount = players.size();

        // Initialize player index map
        for (size_t i = 0; i < players.size(); ++i) {
            playerIndexMap[players[i]] = i;
        }

        // Parse Interactions
        d.set_size(data.size(), 2);
        for (size_t i = 0; i < data.size(); ++i) {
            d(i, 0) = data[i].first;
            d(i, 1) = data[i].second;
        }
}

void FullOptimizer::FullOptimizerResultVerbose(dlib::matrix<double,0,1> params, dlib::matrix<double, 0, 1> scores) {
    dlib::matrix<double, 0, 1> initialScores = subFirstElement(subFirstElement(params));
    std::vector<double> finalEloScores = matrixToVector(scores);
    double k2Adjusted = params(1) > K2_UPPER_BOUND_EXP ? K2_UPPER_BOUND_EXP : params(1);
    const double kgNatural = std::exp(params(0));
    const double kcNatural = std::exp(k2Adjusted);
    std::cout << "\nOptimized Full Model Elo: Results\n ---------------" << std::endl;
    std::cout << "Optimal k(g): " << kgNatural << " (log(k(g)) = " << params(0) << ")" << std::endl;
    std::cout << "Optimal k(c): " << kcNatural << " (log(k(c)) = " << k2Adjusted << ")" << std::endl;
    std::vector<double> initialScoreVector = matrixToVector(initialScores);
    printLabeledScores("Optimal Initial Elo Scores:", initialScoreVector, players, registry);
    printLabeledScores("Final Elo Scores:", finalEloScores, players, registry);
    std::vector<int> rankingIndices = argsort(finalEloScores);
    std::vector<std::string> rankingLabels;
    rankingLabels.reserve(rankingIndices.size());
    for (int idx : rankingIndices) {
        int playerId = players[idx];
        rankingLabels.push_back(registry.labelForIndex(playerId));
    }
    std::cout << "Final Ranking: " << vectorToString(rankingLabels) << std::endl;
}


// Optimization function
void FullOptimizer::run() {
    // Start timer
    auto start = std::chrono::high_resolution_clock::now();

    // Objective function
    auto FullModel = [this](const dlib::matrix<double,0,1>& parameters) {
        
        // K Values
        kValues[0] = parameters(0) > K2_UPPER_BOUND_EXP ? std::exp(K2_UPPER_BOUND_EXP) : std::exp(parameters(0));
        kValues[1] = parameters(1) > K2_UPPER_BOUND_EXP ? std::exp(K2_UPPER_BOUND_EXP) : std::exp(parameters(1));
        // Scores
        std::vector<double> currentElo(parameters.size() - 2);
        for (int i = 2; i < parameters.size(); ++i) {
            currentElo[i - 2] = parameters(i);
        }

        // Fit Combinational Spikes
        CombinationalSpikes spikesConstruct(data, currentElo, kValues, indices, true, 0, true, false, registry); // CHECK
        std::tuple<double, double, std::vector<int>> combination = spikesConstruct.run();
        
        // Return loss
        return kValues[0] >= kValues[1] ? (std::get<0>(combination) - HIGHER_K1_LOSS_PENALTY) : std::get<0>(combination);
    };
    
    // Initial parameters
    dlib::matrix<double,0,1> initialParameters(playerCount + 2);
    initialParameters(0) = kValues[0] < 1e-10 ? -100 : std::log(kValues[0]);
    initialParameters(1) = std::log(kValues[1]);
    for (int i = 2; i <= playerCount+1; ++i) {
        initialParameters(i) = eloValues[i-2];
    }
                    
    // Optimize
    if (verbose == 1 || verbose == 2) {
        std::cout << "\nOptimized Full model: Iterations\n-------------------" << std::endl;
        find_max(dlib::bfgs_search_strategy(),
                 dlib::objective_delta_stop_strategy(LOG_PROBABILITY_EPSILON_FULL_MODEL_OPTIMIZER).be_verbose(),
                 FullModel,
                 dlib::derivative(FullModel),
                 initialParameters,
                 -1);
    }
    else {
        find_max(dlib::bfgs_search_strategy(),
                 dlib::objective_delta_stop_strategy(LOG_PROBABILITY_EPSILON_FULL_MODEL_OPTIMIZER),
                 FullModel,
                 dlib::derivative(FullModel),
                 initialParameters, 
                 -1);
    }

    // Get metrics (combinational)
    std::vector<double> finalElo(initialParameters.size() - 2);
    kValues[0] = initialParameters(0) > K2_UPPER_BOUND_EXP ? std::exp(K2_UPPER_BOUND_EXP) : std::exp(initialParameters(0));
    kValues[1] = initialParameters(1) > K2_UPPER_BOUND_EXP ? std::exp(K2_UPPER_BOUND_EXP) : std::exp(initialParameters(1));
    for (int i = 2; i < initialParameters.size(); ++i) {
            finalElo[i - 2] = initialParameters(i);
    }

    CombinationalSpikes spikesConstructSubcall(data, finalElo, kValues, indices, true, 0, true, true, registry);
    std::tuple<double, double, std::vector<int>> combination = spikesConstructSubcall.run();
    
    // Get scores (optimized Elo)
    dlib::matrix<double, 0, 1> Kt(d.nr());
    dlib::matrix<double, 0, 1> EloScores(eloValues.size()); 

    for (int i = 0; i < d.nr(); ++i) {
        Kt(i) = kValues[0];
    }

    for (int i : std::get<2>(combination)){
        Kt(i) = kValues[1];
    }
    
    for (int idx = 0; idx < playerCount; ++idx) {
        EloScores(idx) = initialParameters(idx + 2);
    }     

    /*
    std::string fileName = "results/eloCam10.txt";

    //Initial ranking based on Elo scores
    std::vector<double> EloScoresVectorInitial(EloScores.begin(), EloScores.end());
    std::vector<int> prevRanking(EloScoresVectorInitial.size());
    std::iota(prevRanking.begin(), prevRanking.end(), 0); 
    std::sort(prevRanking.begin(), prevRanking.end(), [&](int a, int b) { return EloScoresVectorInitial[a] > EloScoresVectorInitial[b]; });
    writeRankingToFile(fileName, 0, prevRanking);
    */ 

    double trainLoss = 0;
    double trainAcc = 0;
    for (int j = 0; j < d.nr(); ++j) {
        //std::vector<double> EloScoresVector = matrixToVector(EloScores);
        //writeEloToFile(fileName, EloScoresVector);
        double eloDifference = EloScores(d(j, 0)) - EloScores(d(j, 1));
        double probabilityWin = 1 / (1 + exp(-0.01 * eloDifference));
        EloScores(d(j, 0)) += Kt(j) * (1 - probabilityWin);
        EloScores(d(j, 1)) -= Kt(j) * (1 - probabilityWin);
        trainLoss += log(probabilityWin);
        if (probabilityWin >= 0.5) {
            trainAcc += 1;
        }

        /*
        std::vector<double> EloScoresVector(EloScores.begin(), EloScores.end());
        std::vector<int> tempRanking(EloScoresVector.size());
        std::iota(tempRanking.begin(), tempRanking.end(), 0);
        std::sort(tempRanking.begin(), tempRanking.end(), [&](int a, int b) { return EloScoresVector[a] > EloScoresVector[b]; });

        if (tempRanking != prevRanking) {
            writeRankingToFile(fileName, j, tempRanking);
        }
        prevRanking = tempRanking;
        */

    }


    trainAcc /= d.nr();

    // Verbose
    FullOptimizerResultVerbose(initialParameters, EloScores);

    // Best combination
    CombinationalSpikes spikesConstruct(data, finalElo, kValues, indices, true, verbose, false, true, registry);
    combination = spikesConstruct.run();

    // Verbose runtime
    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed = end - start;
    std::cout << "Time (s): " << elapsed.count() << "\n" <<std::endl;
}

