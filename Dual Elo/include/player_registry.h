#ifndef PLAYER_REGISTRY_H
#define PLAYER_REGISTRY_H

#include <string>
#include <vector>
#include <unordered_map>

class PlayerRegistry {
public:
    int registerPlayer(const std::string& label);
    const std::string& labelForIndex(int index) const;

private:
    std::vector<std::string> orderedLabels;
    std::unordered_map<std::string, int> labelToIndex;
};

#endif // PLAYER_REGISTRY_H
