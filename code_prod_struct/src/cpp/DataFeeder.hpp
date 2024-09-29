#pragma once
#include <iostream>
#include <fstream>
#include "json_reader.hpp"
#include "Currency.hpp"
#include "Asset.hpp"
#include "GlobalModel.hpp"
#include "MonteCarlo.hpp"

class DataFeeder {
public:
    nlohmann::json &jsonParams_;
    double strike_;
    std::vector<int> assetCurrencyMapping_;
    std::vector<double> foreignInterestRates_;
    YosemiteOption *option_;
    double domesticInterestRate_;
    int assetNb_;
    GlobalModel *globalModel_;
    std::vector<Asset> assets_;
    std::vector<Currency> currencies_;
    std::vector<double> mathDateGrid_;
    int numberOfDaysPerYear_;
    int sampleNb_;
    int maturityInDays_;
    double fdStep_;
    double todayDate_;
    int isTodayAFixingDate_;
    PnlMat *past_;

    DataFeeder(nlohmann::json &jsonParams);
    ~DataFeeder();
};
