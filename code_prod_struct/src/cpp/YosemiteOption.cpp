#include "YosemiteOption.hpp"
#include <cmath>

YosemiteOption::YosemiteOption(double domesticInterestRate, double maturity, std::vector<double> mathDateGrid,
    std::vector<double> foreignInterestRates){
    T_ = maturity;
    domesticInterestRate_ = domesticInterestRate;
    dateGrid_ = mathDateGrid;
    currentFlow_ = 0;
    foreignInterestRates_ = foreignInterestRates;
}

double getPnlVectMinPositive(const PnlVect *v) {
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

double YosemiteOption::payoff(const PnlMat *path, double t) {
    int nbDates = path -> m;
    double price = 0;
    double finalReturn = 0;
    double returnYear = 0;
    int nbDateMet = 0;
    double convert_currency_factor_init = 1;
    double convert_currency_factor_t = 1;

    PnlVect *returnRates = pnl_vect_create_from_zero(4);
    for (int i = 1; i < nbDates; i++) {
        double returnRate = 0;
        int countPositiveReturns = 0;
        double annualPerf = 0;
        
        for (int j = 0; j < 4 ; j++) {
            convert_currency_factor_init = 1;
            convert_currency_factor_t = 1;
            if(j>0) {
                convert_currency_factor_init = pnl_mat_get(path, 0, j+3);
                convert_currency_factor_t = pnl_mat_get(path, i, j+3) * exp(-foreignInterestRates_[j-1] * dateGrid_[i]);
            }
            returnYear = log((pnl_mat_get(path, i, j)/convert_currency_factor_t) / (pnl_mat_get(path, 0, j)/convert_currency_factor_init));
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
            annualPerf += returnRate;
        }

        annualPerf /= 4;
        double dividend = 0;
        if (t < dateGrid_[i]) {
            dividend = (countPositiveReturns > 0) ? 50 * getPnlVectMinPositive(returnRates) : 0;
            price += dividend;
        }
        
        finalReturn += (annualPerf > 0) ? annualPerf : 0;
    }
    
    price += (1000 * (1 + 0.25*finalReturn));

    pnl_vect_free(&returnRates);

    return price;
}
