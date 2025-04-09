// Standard Input/Output and File Handling
#include <iostream>

// Containers
#include <vector>
#include <string>

// Time and Random Number Generation
#include <chrono>
#include <ctime>
#include <cstdlib>

// Calculations
#include <set>
#include <algorithm>

// Headers
#include "verbose.h"
#include "calculation.h"
#include "convert.h"
#include "csv_parser.h"
#include "optimized_elo.h"
#include "combinational_indices.h"
#include "combinational_spikes.h"
#include "k2_optimizer.h"
#include "full_optimizer.h"

// Namespaces
using namespace std;

/**************************************** 
***************  Main method  ***********
*****************************************/

std::vector<int> mergedIndices(const std::vector<int>& indicesOptimizedAccuracy, const std::vector<int>& indicesOptimizedLoss) {
    // Merging and removing duplicates in one line
    std::vector<int> merged(indicesOptimizedAccuracy.begin(), indicesOptimizedAccuracy.end());
    merged.insert(merged.end(), indicesOptimizedLoss.begin(), indicesOptimizedLoss.end());
    std::set<int> uniqueSet(merged.begin(), merged.end());
    return std::vector<int>(uniqueSet.begin(), uniqueSet.end());
}


int main(int argc, char *argv[]) {
    
    // Timer & Default parameters
    auto totalTimeBegin = std::chrono::high_resolution_clock::now();
    std::string filePath;             
    int optimizationLevel = 0;         
    double initialK2 = 5.298317366548; 
    int topN = 10;
    int permuteN = 100;                 
    int verbose = 0;

    // Parse the arguments
    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if ((arg == "-f" || arg == "--file") && i + 1 < argc) {
            filePath = argv[++i];
        } else if ((arg == "-opt" || arg == "--optimization-level") && i + 1 < argc) {
            try {
                optimizationLevel = std::stoi(argv[++i]);
                if (optimizationLevel < 0 || optimizationLevel > 2) {
                    throw std::out_of_range("Optimization level out of valid range");
                }
            } catch (const std::invalid_argument& e) {
                std::cerr << "Invalid argument for --optimization-level: " << argv[i] << std::endl;
                return 1;
            } catch (const std::out_of_range& e) {
                std::cerr << "Argument for --optimization-level must be 0, 1, or 2" << std::endl;
                return 1;
            }
        } else if ((arg == "-k2" || arg == "--initial-k2") && i + 1 < argc) {
            try {
                initialK2 = std::stod(argv[++i]);
                if (initialK2 >= 10) {
                    throw std::out_of_range("Initial K₂ must be less than 10");
                }
            } catch (const std::invalid_argument& e) {
                std::cerr << "Invalid argument for --initial-k2: " << argv[i] << std::endl;
                return 1;
            } catch (const std::out_of_range& e) {
                std::cerr << "Initial K₂ must be less than 10" << std::endl;
                return 1;
            }
        } else if ((arg == "-t" || arg == "--top-n") && i + 1 < argc) {
            try {
                topN = std::stoi(argv[++i]);
                if (topN >= 20) {
                    throw std::out_of_range("Top n must be less than 20 (2^n) combinations exceed 1M");
                }
                else if (topN < 5){
                    throw std::out_of_range("Top n must be at least 5");
                }
            } catch (const std::invalid_argument& e) {
                std::cerr << "Invalid argument for --top-n: " << argv[i] << std::endl;
                return 1;
            } catch (const std::out_of_range& e) {
                std::cerr << "top-n must be 5 <= top-n < 20" << std::endl;
                return 1;
            }
        } else if ((arg == "-n" || arg == "--n-random") && i + 1 < argc) {
            try {
                permuteN = std::stoi(argv[++i]);
                if (permuteN <= 0) {
                    throw std::out_of_range("Number of random permutations must be greater than 0");
                }
            } catch (const std::invalid_argument& e) {
                std::cerr << "Invalid argument for --n-random: " << argv[i] << std::endl;
                return 1;
            } catch (const std::out_of_range& e) {
                std::cerr << "Number of random permutations must be greater than 0" << std::endl;
                return 1;
            }
        } else if ((arg == "-v" || arg == "--verbose") && i + 1 < argc) {
            try {
                verbose = std::stoi(argv[++i]);
                if (verbose < 0 || verbose > 2) {
                    throw std::out_of_range("Verbose level out of valid range");
                }
            } catch (const std::invalid_argument& e) {
                std::cerr << "Invalid argument for --verbose: " << argv[i] << std::endl;
                return 1;
            } catch (const std::out_of_range& e) {
                std::cerr << "Verbose level must be 0, 1, or 2" << std::endl;
                return 1;
            }
        } else if (arg == "-h" || arg == "--help") {
            std::cout << "Usage: "
                      << "./my_program -f <file-path> [--optimization-level <level>] [--initial-k2 <value>]"
                      << " [--n-random <number>] [--verbose <level>]" << std::endl;
            std::cout << "  -f, --file <file-path>       Path to the file (string, mandatory)." << std::endl;
            std::cout << "  -opt, --optimization-level <level> Set the optimization level (integer: 0, 1, or 2)." << std::endl;
            std::cout << "  -k2, --initial-k2 <value>      Set the initial K₂ parameter (double, less than 10)." << std::endl;
            std::cout << "  -n, --n-random <number>        Set the number of random permutations for T (positive integer)." << std::endl;
            std::cout << "  -t, --top-n <number>           Set the number of maximum elements in combinations" << std::endl;
            std::cout << "  -v, --verbose <level>          Set the verbosity level (integer: 0, 1, or 2)." << std::endl;
            std::cout << "  -h, --help                 Print this help message." << std::endl;
            return 0;
        } else {
            std::cerr << "Unknown argument: " << arg << std::endl;
            std::cerr << "Usage: "
                      << "./my_program -f <file-path> [--optimization-level <level>] [--initial-k2 <value>]"
                      << " [--n-random <number>] [--verbose <level>]" << std::endl;
            std::cout << "  -f, --file <file-path>       Path to the file (string, mandatory)." << std::endl;
            std::cout << "  -opt, --optimization-level <level> Set the optimization level (integer: 0, 1, or 2)." << std::endl;
            std::cout << "  -k2, --initial-k2 <value>      Set the initial K₂ parameter (double, less than 10)." << std::endl;
            std::cout << "  -n, --n-random <number>        Set the number of random permutations for T (positive integer)." << std::endl;
            std::cout << "  -t, --top-n <number>           Set the number of maximum elements in combinations" << std::endl;
            std::cout << "  -v, --verbose <level>          Set the verbosity level (integer: 0, 1, or 2)." << std::endl;
            std::cout << "  -h, --help                 Print this help message." << std::endl;
            return 1;
        }
    }

    if (filePath.empty()) {
        std::cerr << "CSV file must be provided, use -h or --help" << std::endl;
        return 1;
    }
	
    std::ifstream file(filePath);
    if (!file.is_open()) {
        std::cerr << "Error opening file: " << filePath << std::endl;
        std::cerr << "File not found. Exiting the program." << std::endl;
        std::exit(EXIT_FAILURE);
    }

    // Parse CSV data into a vector of pairs
    std::vector<std::pair<int, int>> data = parseCSV(filePath);

    // Run Optimized Elo (Default)
    printHeaders(0);
    OptimizedElo elo(data, verbose);
    auto [time, params, finalElo, trainLoss, trainAcc] = elo.run();
    std::vector<double> eloValues = matrixToVector(subFirstElement(params));
    std::vector<double> kValues = {std::exp(params(0)), std::exp(initialK2)};

    // Run Optimized Elo K₂ parameter
    std::vector<double> kValuesOptimized;
    std::vector<double> kValuesOptimizedAccuracy;
    std::vector<double> kValuesOptimizedLoss;
    std::vector<int> indicesOptimized;
    std::vector<int> indicesOptimizedAccuracy;
    std::vector<int> indicesOptimizedLoss;

    if (optimizationLevel >= 1) {
        // Accuracy-oriented
        printHeaders(1); 
        K2Optimizer eloK2Accuracy(data, eloValues, kValues, true, permuteN, topN, verbose);
        std::tie(kValuesOptimizedAccuracy, indicesOptimizedAccuracy) = eloK2Accuracy.run();

        // Loss-oriented
        printHeaders(2); 
        K2Optimizer eloK2Loss(data, eloValues, kValues, false, permuteN, topN, verbose);
        std::tie(kValuesOptimizedLoss, indicesOptimizedLoss) = eloK2Loss.run();    
    }

    // Run Optimize Full Model
    if (optimizationLevel == 2) {
        if (indicesOptimizedAccuracy.empty() && indicesOptimizedLoss.empty()) {
            std::cout << "Result: K2 optimization yielded empty lists indication 0 hierarchy changes." << std::endl;
        }
        else {
            printHeaders(3); 
            kValuesOptimized = kValuesOptimizedAccuracy < kValuesOptimizedLoss ? kValuesOptimizedAccuracy : kValuesOptimizedLoss;
            indicesOptimized = mergedIndices(indicesOptimizedAccuracy, indicesOptimizedLoss);
            FullOptimizer eloFull(data, eloValues, kValuesOptimized, indicesOptimized, verbose);
            eloFull.run();
        }
    }
    
    // Runtime verbose
    auto totalTimeEnd = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> totalTimeTaken = totalTimeEnd - totalTimeBegin;
    std::cout << "\nTotal Time (s): "<< totalTimeTaken.count() << std::endl;
		
	// Exit
    return 0;
}

/*CHANGELOG: NEED optimize the results with and without gradual change, The k2 optimizer changed to take all indices through the code, find_max_single parameters adjusted.*/


        /*kValues = {params(0), optimziedK2};
        CombinationalIndices optimizerInT(data, eloValues, kValues, permuteN, topN, 0);
        std::vector<int> indicesT2 = optimizerInT.run();
        CombinationalSpikes optimizerC(data, eloValues, kValues, indicesT2, 0, true, true);
        std::tuple<double, double, std::vector<int>> combination = optimizerC.run();*/
