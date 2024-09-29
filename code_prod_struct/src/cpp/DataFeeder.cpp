#include "DataFeeder.hpp"

DataFeeder::DataFeeder(nlohmann::json &jsonParams): jsonParams_(jsonParams) {
    PnlMat* correlation;
    jsonParams.at("Correlation").get_to(correlation);
    pnl_mat_chol(correlation);
    
    jsonParams.at("Past").get_to(past_);
    jsonParams.at("Dates").get_to(mathDateGrid_);

    todayDate_ = jsonParams.at("TodayDate").get<double>();
    isTodayAFixingDate_ = jsonParams.at("isTodayAFixingDate");

    int riskyAssetNb = jsonParams.at("Correlation").size();

    std::string domesticCurrencyId;
    jsonParams.at("DomesticCurrencyId").get_to(domesticCurrencyId);
    assetNb_ = jsonParams.at("Assets").size();

    int currencyNb = jsonParams.at("Currencies").size();


    std::map<std::string, int> currencyToRankInCorrelMat;

    auto jsonCurrencies = jsonParams.at("Currencies");

    int indexCurrencyInCorrelMat = assetNb_;
    for (auto jsonCurrency : jsonCurrencies) {
        std::string currencyId(jsonCurrency.at("id").get<std::string>());

        if (currencyId == domesticCurrencyId) {
            domesticInterestRate_ = jsonCurrency.at("InterestRate").get<double>();
        } else {
            foreignInterestRates_.push_back(jsonCurrency.at("InterestRate").get<double>());
            currencyToRankInCorrelMat[currencyId] = indexCurrencyInCorrelMat;
            indexCurrencyInCorrelMat++;
        }
    }

    for (auto jsonCurrency : jsonCurrencies) {
        std::string currencyId(jsonCurrency.at("id").get<std::string>());
        if (currencyId != domesticCurrencyId) {
            double interestRate = foreignInterestRates_[currencyToRankInCorrelMat[currencyId]-assetNb_];
            double realVolatility = jsonCurrency.at("Volatility").get<double>();
            double spot = jsonCurrency.at("Spot").get<double>();

            PnlVect *volatilityVect = pnl_vect_create_from_zero(riskyAssetNb);
            pnl_vect_set(volatilityVect, currencyToRankInCorrelMat[currencyId], realVolatility);

            volatilityVect = pnl_mat_mult_vect(correlation, volatilityVect);
            double drift = domesticInterestRate_ - pow(pnl_vect_norm_two(volatilityVect), 2)/2;

            currencies_.push_back(Currency(spot, drift, volatilityVect, interestRate, domesticInterestRate_));
            pnl_vect_free(&volatilityVect);
        }
    }

    auto jsonAssets = jsonParams.at("Assets");
    int countAsset = 0;
    for (auto jsonAsset : jsonAssets) {
        std::string currencyId(jsonAsset.at("CurrencyId").get<std::string>());
        double realVolatility = jsonAsset.at("Volatility").get<double>();
        double spot = jsonAsset.at("Spot").get<double>();

        PnlVect *volatilityVect = pnl_vect_create_from_zero(riskyAssetNb);
        pnl_vect_set(volatilityVect, countAsset, realVolatility);
        if (currencyId != domesticCurrencyId) {
            spot *= currencies_[currencyToRankInCorrelMat[currencyId]-assetNb_].spot_; // initialize the X_i*S_f_i
            assetCurrencyMapping_.push_back(currencyToRankInCorrelMat[currencyId]-assetNb_+1);
            pnl_vect_plus_vect(volatilityVect, currencies_[currencyToRankInCorrelMat[currencyId]-assetNb_].volatilityVector_);
        } else {
            assetCurrencyMapping_.push_back(0);
        }
        volatilityVect = pnl_mat_mult_vect(correlation, volatilityVect);
        double drift = domesticInterestRate_ - pow(pnl_vect_norm_two(volatilityVect), 2)/2;

        assets_.emplace_back(spot, drift, volatilityVect, domesticInterestRate_);
        pnl_vect_free(&volatilityVect);
        countAsset++;
    }

    numberOfDaysPerYear_ = jsonParams.at("NumberOfDaysInOneYear").get<int>();
    
    sampleNb_ = jsonParams.at("SampleNb").get<int>();
    fdStep_ = jsonParams.at("RelativeFiniteDifferenceStep").get<double>();

    double maturity = mathDateGrid_[mathDateGrid_.size() - 1];
    option_ = new YosemiteOption(domesticInterestRate_, maturity, mathDateGrid_, foreignInterestRates_);
    globalModel_ = new GlobalModel(assets_, currencies_, mathDateGrid_, assetCurrencyMapping_);
    pnl_mat_free(&correlation);
}

DataFeeder::~DataFeeder() {
    delete globalModel_;
    delete option_;
}