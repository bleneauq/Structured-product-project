import numpy as np
import streamlit as st
import pandas as pd
from ast import literal_eval
from utils.rebalancing_portfolio import calculate_portfolio_value, update_portfolio_composition
import tabs.info_page as info_page
import tabs.portfolio_page as portfolio_page
import tabs.underlying_indexs_page as underlying_indexs_page
from config import CORRS, COVS, DATES_GRID, FINIT_DIF_STEP, LIST_DATES, MATHS_DATES_GRID, PAST, PRECOMPUTED_PRICINGS, NUM_DAY_YEAR, PRICES, RATES, SAMPLE_NB
from utils.cpp_pricing_utils import get_price_and_deltas

st.set_page_config(layout="wide")

st.markdown("""
            <style>
                div.st-emotion-cache-16txtl3 {
                    padding: 3rem 1.5rem;
                }
            </style>
            """, unsafe_allow_html=True)

if 'selected_period' not in st.session_state:
    _, col1, col2, col3 = st.columns([0.8, 2, 2, 2])
    m = st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: #f8f8f8;
        width: 300px;
    }
    </style>""", unsafe_allow_html=True)
    with col1:
        if st.button("Period 1"):
            st.session_state.selected_period = 0
            st.rerun()
    with col2:
        if st.button("Period 2"):
            st.session_state.selected_period = 1
            st.rerun()
    with col3:
        if st.button("Period 3"):
            st.session_state.selected_period = 2
            st.rerun()
elif 'init_date' not in st.session_state:
    st.markdown("<h1>Please choose an initial date</h1> <br><br>", unsafe_allow_html=True)
    first_date = DATES_GRID[st.session_state.selected_period][0]
    last_date = DATES_GRID[st.session_state.selected_period][-1]
    i_date = pd.Timestamp(st.date_input(
            "Select an initial date", first_date, min_value=first_date, max_value=last_date
        ))
    if st.button("Confirm"):
        st.session_state.init_date = i_date
        st.session_state.selected_date = st.session_state.init_date
        st.rerun()
else:
    if st.sidebar.button("Change Period"):
        del st.session_state["selected_period"]
        del st.session_state["selected_date"]
        del st.session_state["init_date"]
        del st.session_state["portfolio"]
        st.rerun() 
    if st.sidebar.button("Change Initial Date"):
        del st.session_state["selected_date"]
        del st.session_state["init_date"]
        del st.session_state["portfolio"]
        st.rerun()
        
    st.sidebar.title("Menu")

    # Fonction pour passer au jour suivant
    def next_day():
        sd = pd.Timestamp(st.session_state.selected_date)
        
        # Incrémenter la date sélectionnée jusqu'au prochain jour
        st.session_state.selected_date = PRECOMPUTED_PRICINGS[st.session_state.selected_period].loc[PRECOMPUTED_PRICINGS[st.session_state.selected_period]['Date'] > sd, 'Date'].iloc[0]

    # Bouton "Next Day"
    if st.sidebar.button("Next Day"):
        next_day()

    last_date = DATES_GRID[st.session_state.selected_period][-1]
    # Widget de date
    selected_date = pd.Timestamp(st.sidebar.date_input("Select the next rebalancing date",
                                                       st.session_state.selected_date,
                                                       min_value=st.session_state.selected_date,
                                                       max_value=last_date,
                                                       key="test_key"))
    st.session_state.selected_date = selected_date
    if selected_date not in LIST_DATES[st.session_state.selected_period]:
        st.markdown("<h1>Unavaible date : weekend</h1>", unsafe_allow_html=True)
    else:
        position_current_date = len([date for date in DATES_GRID[st.session_state.selected_period] if date <= selected_date])
        
        dayNumber = PRECOMPUTED_PRICINGS[st.session_state.selected_period].loc[PRECOMPUTED_PRICINGS[st.session_state.selected_period]['Date'] == selected_date, 'DayNumber'].values[0]
        t = dayNumber / NUM_DAY_YEAR
        
        spots = PRICES.loc[selected_date, :].to_list()
        for i in range(1, 4):
            spots[i] *= spots[i+3]
            spots[i+3] *= np.exp(RATES.loc[RATES.index==selected_date, ["RAUD", "RUSD", "RKRW"][i-1]].values[0]*dayNumber/NUM_DAY_YEAR)
            
        dates = MATHS_DATES_GRID[st.session_state.selected_period]
        rates = RATES.loc[selected_date, :].to_list()
        today_date = dayNumber / NUM_DAY_YEAR
        is_today_a_fixing_date = selected_date in DATES_GRID[st.session_state.selected_period]
        covar_mat = COVS.loc[selected_date, :].values.tolist()
        correl_mat = CORRS.loc[selected_date, :].values.tolist()

        past_matrix = PAST[st.session_state.selected_period][:position_current_date]
        if not is_today_a_fixing_date:
            past_matrix.append(spots)

        price, price_std_dev, delta, delta_std_dev, flux = get_price_and_deltas(
            spots, past_matrix, rates, dates, today_date, is_today_a_fixing_date,
            NUM_DAY_YEAR, covar_mat, correl_mat, SAMPLE_NB, FINIT_DIF_STEP
        )

        if selected_date == DATES_GRID[st.session_state.selected_period][0]:
            current_portfolio_value = 1000
            investedCash = 1000 - np.dot(delta, spots)
            l_new_row = [selected_date, dayNumber, price, price_std_dev, str(delta), str(delta_std_dev), current_portfolio_value, investedCash]

            # Convert the list to a DataFrame with a single row
            current_portfolio_compo = pd.DataFrame({k:v for k,v in zip(list(PRECOMPUTED_PRICINGS[st.session_state.selected_period].columns), l_new_row)}, index=[0])
        elif st.session_state.selected_date == st.session_state.init_date:
            current_portfolio_compo = PRECOMPUTED_PRICINGS[st.session_state.selected_period][PRECOMPUTED_PRICINGS[st.session_state.selected_period]['Date'] < selected_date]
            currentAssetQuantities = literal_eval(current_portfolio_compo.iloc[-1]['Delta'])
            assetValues = spots
            newAssetComposition = delta
            lastRebalancingDate = current_portfolio_compo.iloc[-1]['DayNumber']
            investedCash = current_portfolio_compo.iloc[-1]['InvestedCash']
            domestic_interest_rate = RATES.loc[RATES.index==selected_date, 'REUR'].values[0]

            investedCash = update_portfolio_composition(currentAssetQuantities, assetValues, newAssetComposition, dayNumber, lastRebalancingDate,
                                                        investedCash, domestic_interest_rate, flux)
            
            current_portfolio_value = calculate_portfolio_value(newAssetComposition, assetValues, dayNumber, dayNumber,
                                                                investedCash, domestic_interest_rate)
            l_new_row = [selected_date, dayNumber, price, price_std_dev, str(delta), str(delta_std_dev), current_portfolio_value, investedCash]

            # Convert the list to a DataFrame with a single row
            new_row_df = pd.DataFrame({k:v for k,v in zip(current_portfolio_compo.columns, l_new_row)}, index=[current_portfolio_compo.index[-1]+1])
            
            # Append the new row to the DataFrame
            current_portfolio_compo = pd.concat([current_portfolio_compo, new_row_df])
        else:       
            current_portfolio_compo = st.session_state.portfolio
            currentAssetQuantities = literal_eval(current_portfolio_compo.iloc[-1]['Delta'])
            assetValues = spots
            newAssetComposition = delta
            lastRebalancingDate = current_portfolio_compo.iloc[-1]['DayNumber']
            investedCash = current_portfolio_compo.iloc[-1]['InvestedCash']
            domestic_interest_rate = RATES.loc[RATES.index==selected_date, 'REUR'].values[0]

            investedCash = update_portfolio_composition(currentAssetQuantities, assetValues, newAssetComposition, dayNumber, lastRebalancingDate,
                                                        investedCash, domestic_interest_rate, flux)
            
            current_portfolio_value = calculate_portfolio_value(newAssetComposition, assetValues, dayNumber, dayNumber,
                                                                investedCash, domestic_interest_rate)
            l_new_row = [selected_date, dayNumber, price, price_std_dev, str(delta), str(delta_std_dev), current_portfolio_value, investedCash]

            # Convert the list to a DataFrame with a single row
            new_row_df = pd.DataFrame({k:v for k,v in zip(current_portfolio_compo.columns, l_new_row)}, index=[current_portfolio_compo.index[-1]+1])
            # Append the new row to the DataFrame
            current_portfolio_compo = pd.concat([current_portfolio_compo, new_row_df])
        
        # Sélection de la page à afficher
        selected_page = st.sidebar.radio("Select a page", ["Portfolio", "Underlying Indexs", "Product Informations"])
        
        if "portfolio" in st.session_state and st.session_state.portfolio.iloc[-1]["DayNumber"]!=current_portfolio_compo.iloc[-1]["DayNumber"]:
            if st.sidebar.button("Rebalance portfolio today", key="button_rebal"):
                st.session_state.portfolio = current_portfolio_compo
        if "portfolio" not in st.session_state:
            st.session_state.portfolio = current_portfolio_compo

        if selected_page == "Product Informations":
            info_page.dislay_info_page(selected_date)
        elif selected_page == "Underlying Indexs":
            underlying_indexs_page.display_underlying_indexs_page(selected_date)
        elif selected_page == "Portfolio":
            portfolio_page.display_portfolio_page(selected_date, current_portfolio_compo)
