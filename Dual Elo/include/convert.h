#ifndef CONVERT_H
#define CONVERT_H

#include <sstream>
#include <iostream>
#include <string>
#include <vector>
#include <dlib/matrix.h>

template <typename T>
std::string vectorToString(const std::vector<T>& vec) {
    std::ostringstream oss;
    oss << "{";
    for (size_t i = 0; i < vec.size(); ++i) {
        oss << vec[i];
        if (i != vec.size() - 1) {
            oss << ", ";
        }
    }
    oss << "}";
    return oss.str();
}

std::vector<double> matrixToVector(const dlib::matrix<double, 0, 1>& mat);

std::string matrixToString(const dlib::matrix<double>& mat);

dlib::matrix<double, 0, 1> subFirstElement(const dlib::matrix<double, 0, 1>& mat);

#endif // CONVERT_H