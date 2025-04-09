#ifndef CSV_PARSER_H
#define CSV_PARSER_H

#include <iostream>
#include <sstream>
#include <fstream>
#include <string>
#include <vector>

std::vector<std::pair<int, int>> parseCSV(const std::string& filePath);

#endif // CSV_PARSER_H