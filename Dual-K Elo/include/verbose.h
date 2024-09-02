#ifndef VERBOSE_H
#define VERBOSE_H

#include <vector>
#include <tuple>
#include <iostream>
#include <algorithm>

template <typename T>
void printVector(const std::vector<T>& vec);

void printCombLoss(const std::vector<std::tuple<double, double, std::vector<int>>>& combLoss);

void printBestCombination(const std::vector<std::tuple<double, double, std::vector<int>>>& combLoss, int idx);

void printHeaders(int idx);

#endif // VERBOSE_H