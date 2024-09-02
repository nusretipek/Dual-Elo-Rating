#include "k2_optimizer.h"

// Constructor definition
K2Optimizer::K2Optimizer(const std::vector<std::pair<int, int>>& data, 
                         const std::vector<double>& eloValues, 
                         const std::vector<double>& initialKValues, 
                         bool sortAccuracyFirst,
                         int permuteN, 
                         int topN,
                         int verbose)
    : data(data), eloValues(eloValues), kValues(initialKValues), sortAccuracyFirst(sortAccuracyFirst), permuteN(permuteN), topN(topN), verbose(verbose) {}

void K2Optimizer::K2OptimizerStepVerbose(double parameter, std::tuple<double, double, std::vector<int>> combination) {
    if (verbose == 1 || verbose == 2) {
        std::cout << std::left << std::setw(10) << "Trying k2: " 
                  << std::setw(8) << parameter 
                  << std::setw(6) << "(" + std::to_string(int(std::round(std::exp(parameter)))) + ")" 
                  << " - Loss: " 
                  << std::setw(10) << std::get<0>(combination) 
                  << std::endl;
    }
}

void K2Optimizer::K2OptimizerResultVerbose() {
    std::cout << "\nK₂ Parameter: Results\n ---------------" << std::endl;
    std::cout << "Optimized K₂: " << bestInitialParameter << std::endl;
    kValues[1] = std::exp(bestInitialParameter);
    CombinationalIndices indicesConstruct(data, eloValues, kValues, permuteN, topN, 0);
    std::vector<int> indicesStep = indicesConstruct.run();
    CombinationalSpikes spikesConstructVerbose(data, eloValues, kValues, indicesStep, sortAccuracyFirst, verbose, false, false); //CHECK
    std::tuple<double, double, std::vector<int>> combination = spikesConstructVerbose.run();
}

// Optimization function
std::tuple<std::vector<double>, std::vector<int>> K2Optimizer::run() {
    // Start timer
    auto start_t = std::chrono::high_resolution_clock::now();
    
    if (verbose == 1 || verbose == 2) {
        std::cout << "\nOptimizing K₂ Parameter\n ---------------" << std::endl;
    }

    // Objective function
    auto K2Model = [this](double parameter) {
            kValues[1] = std::exp(parameter);
            CombinationalIndices indicesConstruct(data, eloValues, kValues, permuteN, topN, 0);
            std::vector<int> indicesStep = indicesConstruct.run();
            CombinationalSpikes spikesConstructK2Model(data, eloValues, kValues, indicesStep, sortAccuracyFirst, 0, true, false); //CHECK
            std::tuple<double, double, std::vector<int>> combination = spikesConstructK2Model.run();
            K2OptimizerStepVerbose(parameter, combination);
            return std::get<0>(combination);
    };


    // Initial search
    int improvementTracker = 0;
    for (double searchParameter=searchParameterAdjusted; searchParameter < (SEARCH_UPPER_BOUND-SEARCH_STEP); searchParameter=(searchParameter+SEARCH_STEP)) {
        tempParameter = searchParameter + SEARCH_STEP;
        tempLoss = K2Model(tempParameter);
        if (tempLoss > bestLoss) {
            bestInitialParameter = tempParameter;
            bestLoss = tempLoss;
            improvementTracker = 0;
        } 
        else {
            improvementTracker++;
        }
        if (improvementTracker >= MAX_STEP_TRIALS) {
            std::cout << "Stopping search due to no improvement for " << MAX_STEP_TRIALS << " trials. \n" << std::endl;
            return std::make_tuple(kValues, std::vector<int>{}); 
        }       
    }

    // Local optimization
    try{ 
        dlib::find_max_single_variable(K2Model, bestInitialParameter, searchParameterAdjusted, SEARCH_UPPER_BOUND, 
                                       LOG_PROBABILITY_EPSILON_K2_OPTIMIZER, MAX_ITERATION, SEARCH_PERIMETER);
    }
    catch (const dlib::optimize_single_variable_failure& e) {
        std::cerr << "Optimization failed: " << e.what() << std::endl;
        std::cerr << "Last value value taken: " << bestInitialParameter << std::endl;
    }

    // Verbose
    K2OptimizerResultVerbose();

    // Best combination
    kValues[1] = std::exp(bestInitialParameter);
    CombinationalIndices indicesConstruct(data, eloValues, kValues, permuteN, topN, 0);
    std::vector<int> bestIndices = indicesConstruct.run();
    CombinationalSpikes spikesConstruct(data, eloValues, kValues, bestIndices, sortAccuracyFirst, 0, true, false);
    std::tuple<double, double, std::vector<int>> combination = spikesConstruct.run();

    // Verbose runtime
    auto end_t = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed = end_t - start_t;
    std::cout << "Time (s): "<< elapsed.count() << "\n" << std::endl;

    // Return statement
    return std::make_tuple(kValues, std::get<2>(combination)); 
}
