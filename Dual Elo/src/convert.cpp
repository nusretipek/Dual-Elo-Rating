#include "convert.h"



std::vector<double> matrixToVector(const dlib::matrix<double, 0, 1>& mat) {
    std::vector<double> vec(mat.begin(), mat.end());
    return vec;
}

std::string matrixToString(const dlib::matrix<double>& mat) {
    std::stringstream ss;
    ss << "{";
    for (long r = 0; r < mat.nr(); ++r) {
        for (long c = 0; c < mat.nc(); ++c) {
            ss << mat(r, c);
            if (!(r == mat.nr() - 1 && c == mat.nc() - 1)) {
                ss << ", ";
            }
        }
    }
    ss << "}";
    return ss.str();
}

dlib::matrix<double, 0, 1> subFirstElement(const dlib::matrix<double, 0, 1>& mat) {
    if (mat.size() <= 1) {
        return dlib::matrix<double, 0, 1>();
    }
    dlib::matrix<double, 0, 1> result(mat.size() - 1);
    for (long i = 1; i < mat.size(); ++i) {
        result(i - 1) = mat(i);
    }
    return result;
}
