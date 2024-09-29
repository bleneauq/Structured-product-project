#include "Asset.hpp"

Asset::Asset(double spot, double drift, PnlVect *volatilityVector, double domesticInterestRate)
    : RiskyAsset(spot, drift, volatilityVector), domesticInterestRate_(domesticInterestRate){}
