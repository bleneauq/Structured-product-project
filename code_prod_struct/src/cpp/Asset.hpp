#pragma once
#include "RiskyAsset.hpp"

class Asset: public RiskyAsset {
public:
    double domesticInterestRate_;

    Asset(double spot, double drift, PnlVect *volatilityVector, double domesticInterestRate);
};