#include "csv_parser.h"

#include <algorithm>
#include <cctype>

namespace {

std::string trim(const std::string& value) {
    std::string::const_iterator begin = value.begin();
    while (begin != value.end() && std::isspace(static_cast<unsigned char>(*begin))) {
        ++begin;
    }

    std::string::const_iterator end = value.end();
    while (end != begin && std::isspace(static_cast<unsigned char>(*(end - 1)))) {
        --end;
    }

    return std::string(begin, end);
}

bool isBlank(const std::string& value) {
    return std::all_of(value.begin(), value.end(), [](unsigned char ch) {
        return std::isspace(ch);
    });
}

} // namespace

std::vector<std::pair<std::string, std::string>> parseCSV(const std::string& filePath) {
    std::vector<std::pair<std::string, std::string>> data;

    std::ifstream file(filePath);
    if (!file.is_open()) {
        std::cerr << "Error opening file: " << filePath << std::endl;
        return data;
    }

    std::string headerLine;
    if (std::getline(file, headerLine)) {
    }

    std::string line;
    while (std::getline(file, line)) {
        if (line.empty() || isBlank(line)) {
            continue;
        }

        std::istringstream lineStream(line);
        std::string cell;
        std::vector<std::string> cells;
        while (std::getline(lineStream, cell, ',')) {
            cells.push_back(trim(cell));
        }

        if (cells.size() != 2 || cells[0].empty() || cells[1].empty()) {
            std::cerr << "Error parsing line: " << line << std::endl;
            data.clear();
            return data;
        }

        data.emplace_back(cells[0], cells[1]);
    }

    file.close();

    return data;
}
