#include "verbose.h"

template <typename T>
void printVector(const std::vector<T>& vec) {
    // Sort vector
    std::vector<T> sortedVec = vec;
    std::sort(sortedVec.begin(), sortedVec.end());
    
    // Print vector
    std::cout << "{";
    for (size_t i = 0; i < sortedVec.size(); ++i) {
        std::cout << sortedVec[i];
        if (i != sortedVec.size() - 1) {
            std::cout << ", ";
        }
    }
    std::cout << "}";
}

void printCombLoss(const std::vector<std::tuple<double, double, std::vector<int>>>& combLoss) {
    for (const auto& elem : combLoss) {
        double first;
        double second;
        std::vector<int> third;
        std::tie(first, second, third) = elem;
        std::cout << "(" << first << ", " << second << ", ";
        printVector(third);
        std::cout << ")" << std::endl;
    }
}

void printBestCombination(const std::vector<std::tuple<double, double, std::vector<int>>>& combLoss, int idx) {
    if (!combLoss.empty()) {
        const auto& tuple = combLoss[idx];
        double loss = std::get<0>(tuple);
        double accuracy = std::get<1>(tuple);
        const std::vector<int>& indices = std::get<2>(tuple);

        std::cout << "Loss: " << loss << std::endl;
        std::cout << "Accuracy: " << accuracy << std::endl;
        std::cout << "Indices: {";
        if (indices.size() > 0) {
            for (size_t i = 0; i < indices.size(); ++i) {
                std::cout << indices[i];
                if (i < indices.size() - 1) {
                    std::cout << ", ";
                }
            }
        }
        std::cout << "}" << std::endl;
    }
}

void printHeaders(int idx) {
    if (idx == 0) {
        std::cout << "*******************************\n"
                     "*** Optimized Elo (Default) ***\n"
                     "*******************************" << std::endl;
    }
    else if (idx == 1){
        std::cout << "********************************************************\n"
                     "*** Optimized Elo (K₂ Parameter - Accuracy-oriented) ***\n"
                     "********************************************************" << std::endl;
    }
    else if (idx == 2){
        std::cout << "****************************************************\n"
                     "*** Optimized Elo (K₂ Parameter - Loss-oriented) ***\n"
                     "****************************************************" << std::endl;
    }
    else{
        std::cout << "**********************************\n"
                     "*** Optimized Elo (Full Model) ***\n"
                     "**********************************" << std::endl;
    }
}
