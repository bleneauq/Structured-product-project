#pragma once
#include "YosemiteOption.hpp"
#include "GlobalModel.hpp"

class MonteCarlo {
public:
    YosemiteOption *option_;
    GlobalModel *model_;
    int sampleNb_;
    double fdStep_;

    MonteCarlo(YosemiteOption *option, GlobalModel *model, int sampleNb, double fdStep);
    void priceAndDelta(PnlMat *path, double t, double T,double &prix, double &prix_std_dev,  PnlVect *delta, PnlVect *delta_std_dev, PnlRng *rng, double nbSamples, double fdStep, int tInt, int isTodayAFixingDate);
};