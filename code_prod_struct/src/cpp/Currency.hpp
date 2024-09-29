#pragma once
#include "RiskyAsset.hpp"

class Currency: public RiskyAsset {
public:
    double interestRate_;
    double domesticInterestRate_;

    Currency(double spot, double drift, PnlVect *volatilityVector, double interestRate, double domesticInterestRate);
};