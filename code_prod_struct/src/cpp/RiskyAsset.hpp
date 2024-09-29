#pragma once
#include "pnl/pnl_vector.h"

class RiskyAsset {
public:
    double spot_;
    double drift_;
    PnlVect *volatilityVector_;

    RiskyAsset(double spot, double drift, PnlVect *volatilityVector);
    RiskyAsset(const RiskyAsset &that);
    ~RiskyAsset();
};