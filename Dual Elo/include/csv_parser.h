#ifndef CSV_PARSER_H
#define CSV_PARSER_H

#include <iostream>
#include <sstream>
#include <fstream>
#include <string>
#include <vector>
#include <utility>

std::vector<std::pair<std::string, std::string>> parseCSV(const std::string& filePath);

#endif // CSV_PARSER_H
