#include <cmath>
#include "GlobalModel.hpp"

GlobalModel::GlobalModel(std::vector<Asset> assets, std::vector<Currency> currencies, std::vector<double> dateGrid,
std::vector<int> assetCurrencyMapping): assets_(assets), currencies_(currencies), dateGrid_(dateGrid), assetCurrencyMapping_(assetCurrencyMapping) {
    nbModelRiskyAssets_ = assets.size() + currencies.size();
    matriceGauss_ = pnl_mat_create_from_zero(nbModelRiskyAssets_, dateGrid.size());
    colMatriceGaussian_ = pnl_vect_create_from_zero(nbModelRiskyAssets_);
}

void GlobalModel::sample(PnlMat* path, PnlRng *rng, int nextPathLine, double tDate){
    pnl_mat_rng_normal(matriceGauss_, nbModelRiskyAssets_, dateGrid_.size(), rng);
    double prix;
    double drift;
    double step;
    double lastDate;
    RiskyAsset *riskyAsset;

    for(unsigned int d = 0; d < nbModelRiskyAssets_; d++) {   
        if (d < assets_.size()) {
            riskyAsset = &assets_[d];
        } else {
            riskyAsset = &currencies_[d -  assets_.size()];
        }

        prix = riskyAsset->spot_;
        drift = riskyAsset->drift_;
        lastDate = tDate;
        for (int t = nextPathLine; t < dateGrid_.size(); t++) {
            step = dateGrid_[t] - lastDate;
            pnl_mat_get_col(colMatriceGaussian_, matriceGauss_, t);
            prix *= exp(drift * step + pnl_vect_scalar_prod(riskyAsset->volatilityVector_, colMatriceGaussian_) * std::sqrt(step));
            pnl_mat_set(path, t, d, prix);
            lastDate += step;
        }
    }
}

void GlobalModel::shiftAsset(PnlMat *shift_path, const PnlMat *path, int d, double h, int tInt) {
    pnl_mat_clone(shift_path, path);
    for (int i = tInt; i < dateGrid_.size(); i++) {
        pnl_mat_set(shift_path, i, d, pnl_mat_get(path, i, d) * (1 + h));
    }
}

void GlobalModel::updateSpots(PnlVect* newSpots) {
    for(unsigned int d = 0; d < nbModelRiskyAssets_; d++)
    {   
        if (d < assets_.size()) {
            assets_[d].spot_ = pnl_vect_get(newSpots, d);
        } else {
            currencies_[d-assets_.size()].spot_ = pnl_vect_get(newSpots, d);
        }
    }
}

GlobalModel::~GlobalModel() {
    pnl_mat_free(&matriceGauss_);
    pnl_vect_free(&colMatriceGaussian_);
}
