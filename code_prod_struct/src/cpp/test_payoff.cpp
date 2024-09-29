#include "ForeignPerfBasket.hpp"
#include <iostream>
#include <vector>
#include <pnl/pnl_matrix.h> // Assuming you have pnl installed

int main() {
    double strike = 10;
    int assetCurrencyMapping[] = {1,2,0}; // Assuming it's an array of correct size
    std::vector<double> foreignInterestRates = {0.05,0.04}; // Assuming correct size and values
    double domesticInterestRate = 0.03;
    double T = 1.0;
    int assetNb_ = 3;

    ForeignPerfBasket call = ForeignPerfBasket(strike, assetCurrencyMapping, foreignInterestRates, domesticInterestRate, T, assetNb_);

    // Assuming you have pnl_mat initialized properly
    PnlMat *path = pnl_mat_create_from_double(3, 5, 20); // Example exchange rate
    for (int i = 0; i < 3; i++) {
        pnl_mat_set(path, i, 1, 10); 
        pnl_mat_set(path, i, 3, 10);
        pnl_mat_set(path, i, 2, 9);

    }
    
    double payoff = call.payoff(path);
    
    std::cout << "Payoff: " << payoff << std::endl;

    pnl_mat_free(&path); // Free memory allocated for path

    return 0;
}