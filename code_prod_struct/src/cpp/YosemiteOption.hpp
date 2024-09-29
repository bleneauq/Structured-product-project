#pragma once
#include <iostream>
#include <fstream>
#include "pnl/pnl_vector.h"
#include "pnl/pnl_matrix.h"
#include <vector>

class YosemiteOption
{
public:
    double domesticInterestRate_;
    double T_;
    std::vector<double> dateGrid_;
    std::vector<double> foreignInterestRates_;
    double currentFlow_;

    YosemiteOption(double domesticInterestRate, double T, std::vector<double> mathDateGrid, std::vector<double> foreignInterestRates);
    double payoff(const PnlMat *path, double t);
};

