#include "csv_parser.h"

std::vector<std::pair<int, int>> parseCSV(const std::string& filePath) {
    std::vector<std::pair<int, int>> data;

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
        std::istringstream lineStream(line);
        std::string cell;
        int values[2];
        int i = 0;

        while (std::getline(lineStream, cell, ',')) {
            std::istringstream cellStream(cell);
            if (!(cellStream >> values[i++])) {
                std::cerr << "Error parsing line: " << line << std::endl;
                data.clear();
                return data;
            }
        }

        if (i == 2) {
            data.emplace_back(values[0], values[1]);
        } else {
            std::cerr << "Error parsing line: " << line << std::endl;
            data.clear();
            return data;
        }
    }
    file.close();

    return data;
}