#ifndef CALCULATION_H
#define CALCULATION_H

#include <vector>
#include <algorithm>
#include <set>
#include <unordered_set>

std::vector<std::vector<std::vector<int>>> generateCombinations(const std::vector<int>& indices);

double calculateRelativeDifference(double loss1, double loss2);

std::vector<double> calculateRelativeDifferences(const std::vector<std::tuple<double, double, std::vector<int>>>& combLoss);

std::vector<double> calculateRelativeDifferencesFullModel(const std::vector<std::tuple<double, double, std::vector<int>>>& combLoss);

std::vector<double> calculateRelativeAccuracy(const std::vector<std::tuple<double, double, std::vector<int>>>& combLoss);

std::vector<int> argsort(const std::vector<double>& vec);

std::vector<int> calculateChangeType(const std::vector<int>&, const std::vector<int>&);

#endif // CALCULATION_H