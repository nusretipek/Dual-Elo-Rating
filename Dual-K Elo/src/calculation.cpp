#include "calculation.h"

std::vector<std::vector<std::vector<int>>> generateCombinations(const std::vector<int>& indices) {
    std::vector<std::vector<std::vector<int>>> allCombinations;
		
    for (size_t r = 1; r <= indices.size(); ++r) {
        std::vector<bool> v(indices.size());
        std::fill(v.begin(), v.begin() + r, true);
        std::vector<std::vector<int>> r_combinations;

        do {
            std::vector<int> combo;
            for (size_t i = 0; i < indices.size(); ++i) {
                if (v[i]) {
                    combo.push_back(indices[i]);
                }
            }
            r_combinations.push_back(combo);
        } while (std::prev_permutation(v.begin(), v.end()));
        
        allCombinations.push_back(r_combinations);
    }
    allCombinations.push_back({{}});
    
    return allCombinations;
}

double calculateRelativeDifference(double loss1, double loss2) {
    return std::abs(loss2 - loss1) / std::abs(loss1);
}

std::vector<double> calculateRelativeDifferences(const std::vector<std::tuple<double, double, std::vector<int>>>& combLoss) {
    std::vector<double> relative_differences;
    for (size_t i = 1; i < combLoss.size(); ++i) {
        double abs_loss = std::get<0>(combLoss[i]);
        double prev_abs_loss = std::get<0>(combLoss[i - 1]);
        double relative_difference = (calculateRelativeDifference(abs_loss, prev_abs_loss)) * 1e2;
        /*BALANCED DIFFERENCE BY INTERACTION N -> double relative_difference = (calculateRelativeDifference(abs_loss, prev_abs_loss) / n) * 1e6;*/ 
        relative_differences.push_back(relative_difference);
    }

    return relative_differences;
}

std::vector<double> calculateRelativeDifferencesFullModel(const std::vector<std::tuple<double, double, std::vector<int>>>& combLoss) {
    std::vector<double> relative_differences;
    std::vector<double> ratios;

    for (const auto& tuple : combLoss) {
        double first = std::get<0>(tuple);
        double second = std::get<1>(tuple);
        double ratio = first / second;
        ratios.push_back(ratio);
    }
    
    for (size_t i = 1; i < ratios.size(); ++i) {
        double relative_difference = (calculateRelativeDifference(ratios[i], ratios[i-1])) * 1e2;
        relative_differences.push_back(relative_difference);
    }

    return relative_differences;
}

std::vector<double> calculateRelativeAccuracy(const std::vector<std::tuple<double, double, std::vector<int>>>& combLoss) {
    std::vector<double> relative_accuracies;
    for (size_t i = 1; i < combLoss.size(); ++i) {
        double acc = std::get<1>(combLoss[i]);
        double prev_acc = std::get<1>(combLoss[i - 1]);
        double relative_accuracy = acc-prev_acc;
        relative_accuracies.push_back(relative_accuracy);
    }

    return relative_accuracies;
}

std::vector<int> argsort(const std::vector<double>& vec) {
    std::vector<int> indices(vec.size());
    for (size_t i = 0; i < vec.size(); ++i) {
        indices[i] = i;
    }

    std::sort(indices.begin(), indices.end(), [&vec](int i1, int i2) {
        return vec[i1] > vec[i2];
    });

    return indices;
}

std::vector<int> calculateChangeType(const std::vector<int>& vec1, const std::vector<int>& vec2){
    std::unordered_set<int> set1(vec1.begin(), vec1.end());
    std::unordered_set<int> set2(vec2.begin(), vec2.end());
    std::vector<int> difference;
     
    for (int num : set2) {
        if (set1.find(num) == set1.end()) {
            difference.push_back(num);
        }
    }

    return difference;
}