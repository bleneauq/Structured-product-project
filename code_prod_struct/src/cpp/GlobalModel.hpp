#pragma once
#include <vector>
#include "Asset.hpp"
#include "Currency.hpp"
#include "pnl/pnl_random.h"
#include "pnl/pnl_vector.h"
#include "pnl/pnl_matrix.h"


class GlobalModel {
public:
    std::vector<Asset> assets_;
    std::vector<Currency> currencies_;
    std::vector<double> dateGrid_;
    std::vector<int> assetCurrencyMapping_;
    int nbModelRiskyAssets_;
    PnlMat *matriceGauss_;
    PnlVect *colMatriceGaussian_;

    GlobalModel(std::vector<Asset> assets, std::vector<Currency> currencies, std::vector<double> dateGrid, std::vector<int> assetCurrencyMapping);
    void sample(PnlMat* path, PnlRng *rng, int nextPathLine, double tDate);
    void shiftAsset(PnlMat *shift_path, const PnlMat *path, int d, double h, int tInt);
    void updateSpots(PnlVect* newSpots);
    ~GlobalModel();
};