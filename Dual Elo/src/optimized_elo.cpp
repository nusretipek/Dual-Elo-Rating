#include "optimized_elo.h"

// Constructor definition
OptimizedElo::OptimizedElo(const std::vector<std::pair<int, int>>& data, int verbose)
    : data(data), verbose(verbose) {
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
}

// Run function
std::tuple<double, dlib::matrix<double,0,1>, std::vector<double>, double, double> OptimizedElo::run() {
    // Start timer
    auto start = std::chrono::high_resolution_clock::now();

    // Define the objective function
    auto eloModel = [this](const dlib::matrix<double,0,1>& parameters) {
        double K = parameters(0);
        double expK = std::exp(K);

        std::vector<double> currentElo(parameters.size() - 1);
        for (long i = 1; i < parameters.size(); ++i) {
            currentElo[i - 1] = parameters(i);
        }

        
        double loss = 0;
        for (const auto& interaction : data) {
            int initiatorID = interaction.first;
            int receiverID = interaction.second;
            double eloDifference = currentElo[playerIndexMap[initiatorID]] - currentElo[playerIndexMap[receiverID]];
            double probabilityWin = 1 / (1 + std::exp(-0.01 * eloDifference));
            currentElo[playerIndexMap[initiatorID]] += expK * (1 - probabilityWin);
            currentElo[playerIndexMap[receiverID]] -= expK * (1 - probabilityWin);
            loss += std::log(probabilityWin);
        }

        return -loss;
    };

    // Initial parameters
    dlib::matrix<double,0,1> initialParameters(playerCount + 1);
    initialParameters = INITIAL_K_VALUE;
    for (int i = 1; i <= playerCount; ++i) {
        initialParameters(i) = INITIAL_ELO_VALUE;
    }

    // Optimize
    if (verbose == 1 || verbose == 2) {
        try {
            std::cout << "\nOptimized Elo: Iterations\n-------------------" << std::endl;
            find_min(dlib::bfgs_search_strategy(),
                     dlib::objective_delta_stop_strategy(LOG_PROBABILITY_EPSILON).be_verbose(),
                     eloModel,
                     dlib::derivative(eloModel),
                     initialParameters, -1);
        }
        catch (const std::exception& e) {
            dlib::matrix<double,0,1> lower_bound(playerCount + 1);
            dlib::matrix<double,0,1> upper_bound(playerCount + 1);
            initialParameters = INITIAL_K_VALUE;
            lower_bound(0) = LOWER_BOUND_INITIAL;
            upper_bound(0) = UPPER_BOUND_INITIAL;
            for (int i = 1; i <= playerCount; ++i) {
                initialParameters(i) = INITIAL_ELO_VALUE;
                lower_bound(i) = -BOUND_INF;
                upper_bound(i) = BOUND_INF;
            }
            std::cout << "Optimized Elo unbounded optimization failed: " << e.what() << ".\nUsing find min box constrained method..." << std::endl;
            std::cout << "\nOptimized Elo: Iterations \n --------------- \n" << std::endl;
            find_min_box_constrained(dlib::bfgs_search_strategy(),
                    dlib::objective_delta_stop_strategy(LOG_PROBABILITY_EPSILON).be_verbose(),
                    eloModel,
                    dlib::derivative(eloModel),
                    initialParameters, lower_bound, upper_bound);
        }
    }
    else {
        try {
            find_min(dlib::bfgs_search_strategy(),
                    dlib::objective_delta_stop_strategy(LOG_PROBABILITY_EPSILON),
                    eloModel,
                    dlib::derivative(eloModel),
                    initialParameters, -1);
        }
        catch (const std::exception& e) {
            dlib::matrix<double,0,1> lower_bound(playerCount + 1);
            dlib::matrix<double,0,1> upper_bound(playerCount + 1);
            initialParameters = INITIAL_K_VALUE;
            lower_bound(0) = LOWER_BOUND_INITIAL;
            upper_bound(0) = UPPER_BOUND_INITIAL;
            for (int i = 1; i <= playerCount; ++i) {
                initialParameters(i) = 0;
                lower_bound(i) = -BOUND_INF;
                upper_bound(i) = BOUND_INF;
            }
            std::cout << "Optimized Elo unbounded optimization failed: " << e.what() << ".\nUsing find min box constrained method..." << std::endl;
            find_min_box_constrained(dlib::bfgs_search_strategy(),
                    dlib::objective_delta_stop_strategy(LOG_PROBABILITY_EPSILON),
                    eloModel,
                    dlib::derivative(eloModel),
                    initialParameters, lower_bound, upper_bound);
        }
    }

    // Fit optimized Elo model with best parameters
    double K = initialParameters(0);
    double expK = std::exp(K);
    double trainLoss = 0, trainAcc = 0;

    std::vector<double> finalElo(playerCount);
    for (int i = 1; i <= playerCount; ++i) {
        finalElo[i - 1] = initialParameters(i);
    }

    for (const auto& interaction : data) {
        int initiatorID = interaction.first;
        int receiverID = interaction.second;
        double eloDifference = finalElo[playerIndexMap[initiatorID]] - finalElo[playerIndexMap[receiverID]];
        double probabilityWin = 1 / (1 + std::exp(-0.01 * eloDifference));
        finalElo[playerIndexMap[initiatorID]] += expK * (1 - probabilityWin);
        finalElo[playerIndexMap[receiverID]] -= expK * (1 - probabilityWin);
        trainLoss += std::log(probabilityWin);
        if (probabilityWin >= 0.5) {
            trainAcc += 1;
        }
    }

    trainAcc /= data.size();
    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed = end - start;

    // Verbose
    dlib::matrix<double, 0, 1> initialScores = subFirstElement(initialParameters);
    std::cout << "\nOptimized Elo: Results \n ---------------" << std::endl;
    std::cout << "Loss: " << trainLoss << std::endl;
    std::cout << "Accuracy: " << trainAcc << std::endl;
    std::cout << "Optimal K₁: " << initialParameters(0) << std::endl;
    std::cout << "Optimal Initial Elo Scores: " << matrixToString(initialScores) << std::endl;
    std::cout << "Final Elo Scores: " << vectorToString(finalElo) << std::endl;
    std::cout << "Final Ranking: " << vectorToString(argsort(finalElo)) << std::endl;
    std::cout << "Time (s): " << elapsed.count() << "\n" <<std::endl;

    return std::make_tuple(elapsed.count(), initialParameters, finalElo, trainLoss, trainAcc);
}