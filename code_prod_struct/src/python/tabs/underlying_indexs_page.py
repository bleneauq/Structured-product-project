import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from datetime import timedelta
from config import PRICES, INDEX_DICT, SYMBOL_DICT, CURRENCIES_DICT

def get_performance_data(selected_date, prices_df):    
    performance_data = pd.DataFrame(columns=['Index', 'Today', 'Last 6 Months', 'Last Year', 'All Time'])
    today_return = (prices_df.iloc[-1] - prices_df.iloc[-2]) / prices_df.iloc[-2] * 100
    six_months_ago_date = min(prices_df.index, key=lambda x: abs(x - (selected_date - timedelta(days=180))))
    last_6_months_returns = (prices_df.loc[selected_date, :] - prices_df.loc[six_months_ago_date, :]) \
        / prices_df.loc[six_months_ago_date, :] * 100
    one_year_ago_date = min(prices_df.index, key=lambda x: abs(x - (selected_date - timedelta(days=365))))
    last_year_returns = (prices_df.loc[selected_date, :] - prices_df.loc[one_year_ago_date, :]) \
        / prices_df.loc[one_year_ago_date, :] * 100
    all_time_returns = (prices_df.loc[selected_date, :] - prices_df.iloc[0]) / prices_df.iloc[0] * 100
    
    index_performance = {
        'Index': prices_df.columns,
        'Today': (round(today_return, 2).astype(str) + " %").to_list(),
        'Last 6 Months': (round(last_6_months_returns, 2).astype(str) + " %").to_list(),
        'Last Year': (round(last_year_returns, 2).astype(str) + " %").to_list(),
        'All Time': (round(all_time_returns, 2).astype(str) + " %").to_list()
    }
    performance_data = pd.concat([performance_data, pd.DataFrame(index_performance)], ignore_index=True)
    return performance_data

def display_underlying_indexs_page(selected_date):
    
    prices_df = PRICES.loc[PRICES.index <= selected_date, :]
    
    performance_data = get_performance_data(selected_date, prices_df.iloc[:, 0:4])
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Widget pour sélectionner l'indice à afficher
        selected_index = st.selectbox("Select the index you want to see", INDEX_DICT.keys())
    
    # Vérifier si l'indice est le CAC40 ou un autre index
    if selected_index == 'CAC40':
        selected_currency = '€'
    else:
        with col2:
            selected_currency = st.selectbox("Select currency",
                                             {"€": "€ (Domestic)", SYMBOL_DICT[selected_index]: SYMBOL_DICT[selected_index] + " (Foreign)"})

    # Create a trace for the selected index
    if selected_currency == SYMBOL_DICT[selected_index]:
        # If selected currency matches the index currency, no conversion needed
        currency_factor = 1
    else:
        # Otherwise, adjust by currency conversion factor
        currency_factor = prices_df.loc[:, CURRENCIES_DICT[SYMBOL_DICT[selected_index]]].to_list()
        
    trace_price = go.Scatter(x=prices_df.index, y=prices_df.loc[:, INDEX_DICT[selected_index]] * currency_factor, mode='lines', 
                            name=selected_index + ' Price' + ' (' + selected_currency + ')')

    # Create a figure with the trace
    fig = go.Figure(trace_price)

    # Update layout for better appearance
    fig.update_layout(
        title=f'Underlying Index: {selected_index}',
        xaxis=dict(title='Date'),
        yaxis=dict(title=f'Price ({selected_currency})'),
        height=600,
        width=800,
        hovermode="x",
        hoverlabel=dict(bgcolor="white", font_size=12),
        showlegend=True
    )

    # Afficher le graphique en utilisant Streamlit
    st.plotly_chart(fig, use_container_width=True)

    # Convertir les données de performance en DataFrame
    performance_data_df = pd.DataFrame(performance_data)
    
    st.markdown("<h2 style='text-align:center; font-weight:bold; font-size:20px;'>Index Returns History</h2>", unsafe_allow_html=True)
    st.dataframe(performance_data_df.set_index("Index"), use_container_width=True)


