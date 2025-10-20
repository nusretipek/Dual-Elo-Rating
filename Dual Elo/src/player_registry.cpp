#include "player_registry.h"
#include <exception>

int PlayerRegistry::registerPlayer(const std::string& label) {
    std::unordered_map<std::string, int>::const_iterator it = labelToIndex.find(label);
    if (it != labelToIndex.end()) {
        return it->second;
    }

    bool useNumericIndex = false;
    int numericIndex = 0;
    try {
        std::size_t consumed = 0;
        numericIndex = std::stoi(label, &consumed);
        if (consumed == label.size() && numericIndex >= 0) {
            useNumericIndex = true;
        }
    } catch (const std::exception&) {
        useNumericIndex = false;
    }

    int index = 0;
    if (useNumericIndex) {
        index = numericIndex;
        const std::size_t requiredSize = static_cast<std::size_t>(index) + 1;
        if (orderedLabels.size() < requiredSize) {
            orderedLabels.resize(requiredSize);
        }
        orderedLabels[static_cast<std::size_t>(index)] = label;
    } else {
        index = static_cast<int>(orderedLabels.size());
        orderedLabels.push_back(label);
    }

    labelToIndex[label] = index;
    return index;
}

const std::string& PlayerRegistry::labelForIndex(int index) const {
    return orderedLabels.at(static_cast<std::size_t>(index));
}
