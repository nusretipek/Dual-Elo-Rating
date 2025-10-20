#ifndef VERBOSE_H
#define VERBOSE_H

#include <vector>
#include <tuple>
#include <iostream>
#include <algorithm>
#include <string>
#include "player_registry.h"

template <typename T>
void printVector(const std::vector<T>& vec);

void printCombLoss(const std::vector<std::tuple<double, double, std::vector<int>>>& combLoss);

void printBestCombination(const std::vector<std::tuple<double, double, std::vector<int>>>& combLoss, int idx);

void printHeaders(int idx);

void printLabeledScores(const std::string& title,
                        const std::vector<double>& scores,
                        const std::vector<int>& players,
                        const PlayerRegistry& registry);

#endif // VERBOSE_H
