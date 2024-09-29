import numpy as np
from config import NUM_DAY_YEAR

def get_asset_position_value(currentAssetQuantities, assetValues):
    return np.dot(currentAssetQuantities, assetValues)

def get_bond_value(dateToCapitalizeTo, lastRebalancingDate, investedCash, domestic_interest_rate):
    day_difference = dateToCapitalizeTo - lastRebalancingDate
    capitalization_factor = np.exp(domestic_interest_rate * (day_difference / NUM_DAY_YEAR))
    return investedCash * capitalization_factor

def calculate_portfolio_value(currentAssetQuantities, assetValues, currentDate, lastRebalancingDate, investedCash, domestic_interest_rate):
    return get_asset_position_value(currentAssetQuantities, assetValues) + get_bond_value(currentDate, lastRebalancingDate,
                                                                                          investedCash, domestic_interest_rate)

def update_portfolio_composition(currentAssetQuantities, assetValues, newAssetComposition, currentDate, lastRebalancingDate,
                                 investedCash, domestic_interest_rate, flux):
    share_prices_before_rebalancing = get_asset_position_value(currentAssetQuantities, assetValues)
    share_prices_after_rebalancing = get_asset_position_value(newAssetComposition, assetValues)
    investedCash = get_bond_value(currentDate, lastRebalancingDate, investedCash, domestic_interest_rate) + \
        (share_prices_before_rebalancing - share_prices_after_rebalancing) - flux

    return investedCash
