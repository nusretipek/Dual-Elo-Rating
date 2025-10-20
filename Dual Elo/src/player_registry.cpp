#include "player_registry.h"

int PlayerRegistry::registerPlayer(const std::string& label) {
    std::unordered_map<std::string, int>::const_iterator it = labelToIndex.find(label);
    if (it != labelToIndex.end()) {
        return it->second;
    }

    int index = static_cast<int>(orderedLabels.size());
    orderedLabels.push_back(label);
    labelToIndex[label] = index;
    return index;
}

const std::string& PlayerRegistry::labelForIndex(int index) const {
    return orderedLabels.at(static_cast<std::size_t>(index));
}
