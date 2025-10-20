#include "verbose.h"
#include <cctype>
#include <exception>

namespace {
bool isIntegerLabel(const std::string& label) {
    if (label.empty()) {
        return false;
    }
    std::size_t start = (label.front() == '-' || label.front() == '+') ? 1 : 0;
    if (start >= label.size()) {
        return false;
    }
    return std::all_of(label.begin() + start, label.end(), [](unsigned char ch) {
        return std::isdigit(ch) != 0;
    });
}

bool naturalLabelLess(const std::string& lhs, const std::string& rhs) {
    const bool lhsIsInt = isIntegerLabel(lhs);
    const bool rhsIsInt = isIntegerLabel(rhs);
    if (lhsIsInt && rhsIsInt) {
        try {
            long long lhsValue = std::stoll(lhs);
            long long rhsValue = std::stoll(rhs);
            if (lhsValue != rhsValue) {
                return lhsValue < rhsValue;
            }
            if (lhs.size() != rhs.size()) {
                return lhs.size() < rhs.size();
            }
        }
        catch (const std::exception&) {
            // Fall through to lexicographical ordering when conversion fails.
        }
    }
    return lhs < rhs;
}
} // namespace

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
                     "*** Optimized Elo (k(c) Parameter - Accuracy-oriented) ***\n"
                     "********************************************************" << std::endl;
    }
    else if (idx == 2){
        std::cout << "****************************************************\n"
                     "*** Optimized Elo (k(c) Parameter - Loss-oriented) ***\n"
                     "****************************************************" << std::endl;
    }
    else{
        std::cout << "**********************************\n"
                     "*** Optimized Elo (Full Model) ***\n"
                     "**********************************" << std::endl;
    }
}

void printLabeledScores(const std::string& title,
                        const std::vector<double>& scores,
                        const std::vector<int>& players,
                        const PlayerRegistry& registry) {
    std::cout << title << std::endl;
    if (scores.empty() || players.empty()) {
        std::cout << "  (no players)" << std::endl;
        return;
    }

    std::vector<std::pair<std::string, double>> labeledScores;
    std::size_t limit = std::min(players.size(), scores.size());
    labeledScores.reserve(limit);
    for (std::size_t i = 0; i < limit; ++i) {
        const std::string& label = registry.labelForIndex(players[i]);
        labeledScores.emplace_back(label, scores[i]);
    }

    std::sort(labeledScores.begin(), labeledScores.end(),
              [](const std::pair<std::string, double>& lhs, const std::pair<std::string, double>& rhs) {
                  return naturalLabelLess(lhs.first, rhs.first);
              });

    for (const auto& entry : labeledScores) {
        std::cout << "  " << entry.first << ": " << entry.second << std::endl;
    }
}
