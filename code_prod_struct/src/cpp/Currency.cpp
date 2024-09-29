#include "Currency.hpp"

Currency::Currency(double spot, double drift, PnlVect *volatilityVector, double interestRate, double domesticInterestRate)
    : RiskyAsset(spot, drift, volatilityVector), interestRate_(interestRate), domesticInterestRate_(domesticInterestRate){}
