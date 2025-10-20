#include "combinational_spikes.h"

CombinationalSpikes::CombinationalSpikes(const std::vector<std::pair<int, int>>& data, 
                                         const std::vector<double>& eloValues,
                                         const std::vector<double>& kValues, 
                                         std::vector<int> indices, 
                                         bool sortAccuracyFirst,
                                         int verbose, 
                                         bool subcall, 
                                         bool fullModel,
                                         const PlayerRegistry& registry)
    : data(data), eloValues(eloValues), kValues(kValues), indices(indices), sortAccuracyFirst(sortAccuracyFirst), verbose(verbose), subcall(subcall), fullModel(fullModel), registry(registry) {
            
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

void CombinationalSpikes::getCombinations() {
    // Get all combinations of most activated interactions (t)
    std::vector<std::vector<std::vector<int>>> allCombinations = generateCombinations(indices);
    flattenedCombinations.clear();
    for (const auto& rCombinations : allCombinations) {
        for (const auto& combo : rCombinations) {
            flattenedCombinations.push_back(combo);
        }
    }
}

void CombinationalSpikes::getBestIndex() {
    // Calculate relative decrease in loss values by adding extra elements
    if (fullModel) {
        relativeDifference = calculateRelativeDifferencesFullModel(sortedCombinationLoss);
    }
    else {
        relativeDifference = calculateRelativeDifferences(sortedCombinationLoss);

    }
    relativeAccuracies = calculateRelativeAccuracy(sortedCombinationLoss);

    // Find best combination based on relative loss decrease // CHECK THIS TO IMPROVE
    const double thresholdAccSubCall1 = THRESHOLD_ACC_SUBCALL_1/(d.nr()+1);
    const double thresholdAccSubCall2 = THRESHOLD_ACC_SUBCALL_2/(d.nr()+1);
    if (!fullModel) {
        for (size_t i = 0; i < relativeDifference.size(); ++i) {
            if (i == 0 && relativeDifference[0] < THRESHOLD_INDEX_0_LOSS_DIFFERENCE && relativeAccuracies[0] <= THRESHOLD_INDEX_0_ACCURACY_DIFFERENCE) {
                break;
            }
            else if (i == 0) {
                bestCombIndex = i + 1;
            }
            else if (relativeDifference[i] < THRESHOLD_SUBCALL_NON_FULL_LOSS_DIFFERENCE){
                break;
            }
            else if ((relativeDifference[i] >= THRESHOLD_SUBCALL_NON_FULL_LOSS_DIFFERENCE_LOWER_BOUND) || 
                     (relativeAccuracies[i] >= thresholdAccSubCall2) || 
                     (relativeAccuracies[i] >= thresholdAccSubCall1 && relativeDifference[i] >= THRESHOLD_SUBCALL_NON_FULL_ACCURACY_DIFFERENCE_LOWER_BOUND)) {
                bestCombIndex = i + 1;
            }
            else {
                break;
            }
        }
    }
    else if (fullModel) {
        for (size_t i = 0; i < relativeDifference.size(); ++i) {
            if (i == 0 && (relativeDifference[0] < THRESHOLD_FULL_INDEX_0_LOSS_DIFFERENCE || relativeAccuracies[0] <= THRESHOLD_FULL_INDEX_0_ACCURACY_DIFFERENCE)) {
                break;
            }
            else if (i == 0) {
                bestCombIndex = i + 1;
            }
            else if (relativeDifference[i] < THRESHOLD_FULL_LOSS_DIFFERENCE){
                break;
            }
            else if ((relativeDifference[i] >= THRESHOLD_FULL_LOSS_DIFFERENCE_LOWER_BOUND) || 
                     (relativeAccuracies[i] >= thresholdAccSubCall2) || 
                     (relativeAccuracies[i] >= thresholdAccSubCall1 && relativeDifference[i] >= THRESHOLD_FULL_ACCURACY_DIFFERENCE_LOWER_BOUND)) {
                bestCombIndex = i + 1;
            }
            else {
                break;
            }
        }
    }
    else {
        for (size_t i = 0; i < relativeDifference.size(); ++i) {
            if (i == 0 && relativeDifference[0] < THRESHOLD_INDEX_0_LOSS_DIFFERENCE && relativeAccuracies[0] <= THRESHOLD_INDEX_0_ACCURACY_DIFFERENCE) {
                break;
            }
            else if (i == 0) {
                bestCombIndex = i + 1;
            }
            else if (relativeDifference[i] < THRESHOLD_OTHER_LOSS_DIFFERENCE){
                break;
            }
            else if ((relativeDifference[i] >= THRESHOLD_OTHER_LOSS_DIFFERENCE_LOWER_BOUND) || 
                     (relativeAccuracies[i] >= thresholdAccSubCall2) || 
                     (relativeAccuracies[i] >= thresholdAccSubCall1 && relativeDifference[i] >= THRESHOLD_OTHER_ACCURACY_DIFFERENCE_LOWER_BOUND)) {
                bestCombIndex = i + 1;
            }
            else {
                break;
            }
        }
    }
}

void CombinationalSpikes::printResults(std::unordered_map<int, int> importanceMap) {
    static_cast<void>(importanceMap);
    if (verbose == 2) {
        std::cout << "\nCombinations Elo Spikes \n ---------------" << std::endl;
        printCombLoss(CombinationLoss);
    }

    if (verbose == 1 || verbose == 2) {
        std::cout << "\nBest Combination Candidates (length-wise) \n<Loss, Accuracy, Index (t)>\n--------------- " << std::endl;
        printCombLoss(sortedCombinationLoss);
    }

    if (verbose == 2) {		
        // Print the relative differences vector for verification
        std::cout << "\nRelative Loss Differences: \n ---------------" << std::endl;
        for (const auto& diff : relativeDifference) {
                std::cout << diff << std::endl;
        }
    }

    if (!subcall) {
        // Verbose the interactions from the best combination
        std::cout << "\nBest Combinational k(g) and k(c) Elo Model\n --------------- " << std::endl;
        printBestCombination(sortedCombinationLoss, bestCombIndex);
        
        for (int idx : std::get<2>(sortedCombinationLoss[bestCombIndex])) {
            std::cout << "          " << idx << ": ("
                      << registry.labelForIndex(d(idx, 0)) << ", "
                      << registry.labelForIndex(d(idx, 1)) << ")" << std::endl;
        }						
    }
}

std::tuple<double, double, std::vector<int>> CombinationalSpikes::run() {
    // Get all combinations
    getCombinations();

    // Iterate through the combinations
    for (const auto& combo : flattenedCombinations) {
        double iterationTrainLoss = 0;
        double iterationTrainAcc = 0;
        dlib::matrix<double, 0, 1> Kt(d.nr());
        for (int i = 0; i < d.nr(); ++i) {
                Kt(i) = kValues[0];
        }
        
        for (auto idx : combo) {
                Kt(idx) = kValues[1];
        }
        
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
        CombinationLoss.push_back(std::make_tuple(iterationTrainLoss, iterationTrainAcc, combo));
    }
    
    // Sort CombinationLoss - First Loss then size then accuracy!!!
    if (sortAccuracyFirst) {
        std::sort(CombinationLoss.begin(), CombinationLoss.end(), [](const auto& lhs, const auto& rhs) {
                if (std::get<1>(lhs) != std::get<1>(rhs))
                        return std::get<1>(lhs) > std::get<1>(rhs); // Highest accuracy first
                if (std::get<2>(lhs).size() != std::get<2>(rhs).size())
                        return std::get<2>(lhs).size() < std::get<2>(rhs).size(); // Lowest number of elements next
                return std::get<0>(lhs) > std::get<0>(rhs); // Highest loss last
        });
    }
    else{
        std::sort(CombinationLoss.begin(), CombinationLoss.end(), [](const auto& lhs, const auto& rhs) {
                if (std::get<0>(lhs) != std::get<0>(rhs))
                        return std::get<0>(lhs) > std::get<0>(rhs); // Highest accuracy first
                if (std::get<2>(lhs).size() != std::get<2>(rhs).size())
                        return std::get<2>(lhs).size() < std::get<2>(rhs).size(); // Lowest number of elements next
                return std::get<1>(lhs) > std::get<1>(rhs); // Highest loss last
        });
  }

    // Combine the loss and the accuracy for the final model
   if (fullModel) {
        std::sort(CombinationLoss.begin(), CombinationLoss.end(),[](const auto& lhs, const auto& rhs) {
                return (std::get<0>(lhs) / std::get<1>(lhs)) > (std::get<0>(rhs) / std::get<1>(rhs));
            });
    }

    // Iterate over sorted CombinationLoss and add tuples with different sizes to sortedCombinationLoss
    std::vector<size_t> addedSizes;
    for (const auto& tuple : CombinationLoss) {
            size_t size = std::get<2>(tuple).size();
            if (std::find(addedSizes.begin(), addedSizes.end(), size) == addedSizes.end()) {
                    sortedCombinationLoss.push_back(tuple);
                    addedSizes.push_back(size);
            }
            std::sort(sortedCombinationLoss.begin(), sortedCombinationLoss.end(), [](const auto& lhs, const auto& rhs) {
                    return std::get<2>(lhs).size() < std::get<2>(rhs).size(); // Lowest number of elements next		
            });
    }

    // Get best combination
    getBestIndex();

    // Strong & Subtle assignment to the changes 
    std::unordered_map<int, int> importanceMap;
    std::vector<int> temp;
    auto updateMap = [&importanceMap](int key, int value) {
        importanceMap[key] = value;
    };

    for (size_t i = 0; i < sortedCombinationLoss.size() - 1; ++i) {
        temp = calculateChangeType(std::get<2>(sortedCombinationLoss[i]), std::get<2>(sortedCombinationLoss[i+1]));
        
        for (int e : temp) {
            if (fullModel && relativeDifference[i] >= THRESHOLD_FULL_STRONG) {
                updateMap(e, 1);
            }
            else if (!fullModel && relativeDifference[i] >= THRESHOLD_NON_FULL_STRONG){
                updateMap(e, 1);
            }
            else {
                updateMap(e, 0);
            }
        }
    }

    // Verbose
    printResults(importanceMap);

    // Return statement
    std::tuple<double, double, std::vector<int>> results = sortedCombinationLoss[bestCombIndex];
    return results;
}
