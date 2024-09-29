#include <cmath>
#include "MonteCarlo.hpp"

MonteCarlo::MonteCarlo(YosemiteOption *option, GlobalModel *model, int sampleNb, double fdStep)
    : option_(option), model_(model), sampleNb_(sampleNb), fdStep_(fdStep) {
    }

void MonteCarlo::priceAndDelta(PnlMat *path, double t, double T,double &prix, double &prix_std_dev,  PnlVect *delta, PnlVect *delta_std_dev,
PnlRng *rng, double nbSamples, double fdStep, int tInt, int isTodayAFixingDate){
    double sum_prix = 0;
    double sum2_pstdev = 0;
    double payoff;
    double actuFactor = exp(-(option_->domesticInterestRate_) * (T - t));

    int nRiskyAssets = path->n;
    double delta_diff;

    PnlMat *path_shift = pnl_mat_create(path->m, nRiskyAssets);
    PnlVect *temp_std_dev = pnl_vect_create_from_zero(nRiskyAssets);
    PnlVect *sumPrice = pnl_vect_create_from_zero(nRiskyAssets);
    for (int i = 0; i < nbSamples; i++) {
        model_->sample(path, rng, tInt, t);
        payoff = option_->payoff(path, t);
        sum_prix += payoff;
        sum2_pstdev += pow(payoff, 2);
        for (int d = 0; d <nRiskyAssets; d++) {
            model_->shiftAsset(path_shift, path, d, fdStep, tInt);
            delta_diff = option_->payoff(path_shift, t);
            model_->shiftAsset(path_shift, path, d, -fdStep, tInt);
            delta_diff -= option_->payoff(path_shift, t);
            pnl_vect_set(sumPrice, d, pnl_vect_get(sumPrice, d) + delta_diff);
            pnl_vect_set(temp_std_dev, d, pnl_vect_get(temp_std_dev, d) + delta_diff * delta_diff);
        }
    }
    prix = actuFactor * sum_prix / nbSamples;
    sum2_pstdev = pow(actuFactor, 2) * (sum2_pstdev / nbSamples) - pow(prix, 2);
    prix_std_dev = sqrt(abs(sum2_pstdev) / nbSamples);
    double factor;
    for (int d = 0; d < nRiskyAssets; d++) {
        if (d < model_->assets_.size()) {
            factor = exp(-option_->domesticInterestRate_* (T-t)) / (nbSamples * 2 * fdStep * (model_->assets_[d].spot_));
        } else {
            factor = exp(-option_->domesticInterestRate_* (T-t)) / (nbSamples * 2 * fdStep * (model_->currencies_[d - model_->assets_.size()].spot_));
        }
        pnl_vect_set(delta, d, pnl_vect_get(sumPrice, d) * factor);
        pnl_vect_set(delta_std_dev, d,
                sqrt(abs((factor * factor) * (pnl_vect_get(temp_std_dev, d) - pnl_vect_get(sumPrice, d) * pnl_vect_get(sumPrice, d) / nbSamples))));
    }
    pnl_mat_free(&path_shift);
    pnl_vect_free(&temp_std_dev);
    pnl_vect_free(&sumPrice);
}