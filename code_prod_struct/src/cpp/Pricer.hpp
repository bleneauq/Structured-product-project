#pragma once
#include "pnl/pnl_vector.h"
#include "Position.hpp"
#include "DataFeeder.hpp"

class Pricer {
public:
    Position *position_;
    PnlMat *currentPath_;
    PnlMat *past_;
    PnlVect* lastPrices_;
    PnlRng *rng_;
    MonteCarlo *monteCarlo_;
    int currentPathLine_;
    int numberOfDaysPerYear_;
    int isTodayAFixingDate_;
    std::vector<int> realDaysGrid_;
    std::vector<double> foreignInterestRates_;
    std::vector<double> mathDateGrid_;
    PnlVect *delta_;
    PnlVect *deltaStdDev_;
    double price_;
    double price_std_dev_;
    int isFixingDate_;

    Pricer(DataFeeder *dataFeeder, PnlRng *rng);
    double getFlowAtFixingDate(const PnlMat *path); 
    void getPricing(double dayNb);
    void writeResults(char *resultFile);
    ~Pricer();
};