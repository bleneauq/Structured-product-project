#include "Pricer.hpp"

Pricer::Pricer(DataFeeder *dataFeeder, PnlRng *rng): rng_(rng) {
    monteCarlo_ = new MonteCarlo(dataFeeder->option_, dataFeeder->globalModel_, dataFeeder->sampleNb_, dataFeeder->fdStep_);
    currentPath_ = pnl_mat_create_from_zero(dataFeeder->mathDateGrid_.size(), dataFeeder->globalModel_->nbModelRiskyAssets_);
    lastPrices_ = pnl_vect_create_from_zero(dataFeeder->globalModel_->nbModelRiskyAssets_);
    past_ = dataFeeder->past_;
    currentPathLine_ = past_->m - 1;
    isFixingDate_ = dataFeeder->isTodayAFixingDate_;
    numberOfDaysPerYear_ = dataFeeder->numberOfDaysPerYear_;
    foreignInterestRates_ = dataFeeder->foreignInterestRates_;
    mathDateGrid_ = dataFeeder->mathDateGrid_;

    pnl_mat_get_row(lastPrices_, past_, past_->m - 1);
    monteCarlo_->model_->updateSpots(lastPrices_);
    for (int i = 0; i < past_->m - 1 ; i++ ) {
        PnlVect *currentLine = pnl_vect_create_from_zero(past_->n);
        pnl_mat_get_row(currentLine, past_, i);
        pnl_mat_set_row(currentPath_, currentLine, i);
    }
    if (isFixingDate_) {
        pnl_mat_set_row(currentPath_, lastPrices_, past_->m - 1);
        currentPathLine_++;
    }
    
    getPricing(dataFeeder->todayDate_);
}

double getVectMinPositive(const PnlVect *v) {
    double minValue = std::numeric_limits<double>::infinity();
    int size = v->size;
    
    for (int i = 0; i < size; ++i) {
        double currentValue = pnl_vect_get(v, i);
        if (currentValue > 0 && currentValue < minValue) {
            minValue = currentValue;
        }
    }
    
    // if no positive value
    if (minValue == std::numeric_limits<double>::infinity()) {
        return 0; 
    }
    
    return minValue;
}

double Pricer::getFlowAtFixingDate(const PnlMat *path) {
    double returnYear = 0;
    double dividend = 0;
    double returnRate = 0;
    int countPositiveReturns = 0;
    double convert_currency_factor_init = 1;
    double convert_currency_factor_t = 1;

    PnlVect *returnRates = pnl_vect_create_from_zero(4);

    for (int j = 0; j < 4 ; j++) {
        convert_currency_factor_init = 1;
        convert_currency_factor_t = 1;
        if(j>0) {
            convert_currency_factor_init = pnl_mat_get(path, 0, j+3);
            convert_currency_factor_t = pnl_mat_get(path, currentPathLine_-1, j+3) * exp(-foreignInterestRates_[j-1] * mathDateGrid_[currentPathLine_-1]);
        }
        returnYear = log((pnl_mat_get(path, currentPathLine_-1, j)/convert_currency_factor_t) / (pnl_mat_get(path, 0, j)/convert_currency_factor_init));
        if (returnYear >= -0.15 && returnYear<=0.15) {
            returnRate = abs(returnYear);
        }
        else if(returnYear > 0.15) {
            returnRate = 0.15;
        } else {
            returnRate = returnYear;
        }
        
        pnl_vect_set(returnRates, j, returnRate);

        if (returnRate > 0) {
            countPositiveReturns++;
        }
    }

    dividend = (countPositiveReturns > 0) ? 50 * getVectMinPositive(returnRates) : 0;    
    
    return dividend;
}

void Pricer::getPricing(double day){

    price_;
    price_std_dev_;
    delta_ = pnl_vect_create_from_zero(monteCarlo_->model_->nbModelRiskyAssets_);
    deltaStdDev_ = pnl_vect_create_from_zero(monteCarlo_->model_->nbModelRiskyAssets_);
    monteCarlo_->priceAndDelta(currentPath_, day, monteCarlo_->option_->T_, price_, price_std_dev_,  delta_,
        deltaStdDev_, rng_, monteCarlo_->sampleNb_, monteCarlo_->fdStep_, currentPathLine_, isFixingDate_);
    if (isFixingDate_ && day>0) {
        double flux = getFlowAtFixingDate(currentPath_);
        position_ = new Position(price_, price_std_dev_, delta_, deltaStdDev_, flux);
    } else {
        position_ = new Position(price_, price_std_dev_, delta_, deltaStdDev_, 0);
    }
}

void Pricer::writeResults(char *resultFile) {
    nlohmann::json jsonPortfolio = position_->print();
    std::ofstream ifout(resultFile, std::ios_base::out);
    if (!ifout.is_open()) {
        std::cout << "Unable to open file " << resultFile << std::endl;
        std::exit(1);
    }
    ifout << jsonPortfolio.dump(4);
    ifout.close();
}

Pricer::~Pricer() {
    pnl_mat_free(&currentPath_);
    pnl_vect_free(&lastPrices_);
    delete monteCarlo_;
}
