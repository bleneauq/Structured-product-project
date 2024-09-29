import numpy as np
import streamlit as st
import pandas as pd  
import plotly.express as px
import plotly.graph_objects as go
from config import ASSETS, DATES_GRID, NUM_DAY_YEAR, PRECOMPUTED_PRICINGS, RATES, STR_DATES_GRID, PRICES, INDEX_DICT, SYMBOL_DICT, CURRENCIES_DICT
import plotly.graph_objs as go

def display_portfolio_compo(portfolio_compo, selected_date, title_graph):    
    
    deltas = portfolio_compo[portfolio_compo['Date'] == selected_date].Delta.values[0].strip('[]').split(', ')
    deltas = [float(element) for element in deltas]
    
    invested_cash = round(portfolio_compo[portfolio_compo['Date'] == selected_date].InvestedCash.values[0], 2)
    
    dayNumber = PRECOMPUTED_PRICINGS[st.session_state.selected_period].loc[PRECOMPUTED_PRICINGS[st.session_state.selected_period]['Date'] == selected_date, 'DayNumber'].values[0]
    spots = PRICES.loc[selected_date, :].to_list()
    for i in range(1, 4):
        spots[i] *= spots[i+3]
        spots[i+3] *= np.exp(RATES.loc[RATES.index==selected_date, ["RAUD", "RUSD", "RKRW"][i-1]].values[0]*dayNumber/NUM_DAY_YEAR)
    
    positions_d_int = [round(price * delta)for price, delta in zip(spots, deltas)] + [invested_cash]
    positions_d = [str(round(price * delta)) + " €" for price, delta in zip(spots, deltas)]
    positions_f = [round(price * delta) for price, delta in zip(spots, deltas)]
    

    aud_rate = PRICES[PRICES.index == selected_date]['AUD'].values[0]
    usd_rate = PRICES[PRICES.index == selected_date]['USD'].values[0]
    krw_rate = PRICES[PRICES.index == selected_date]['KRW'].values[0]
    
    positions_f[1] = round(positions_f[1] / aud_rate, 2)
    positions_f[2] = round(positions_f[2] / usd_rate, 2)
    positions_f[3] = round(positions_f[3] / krw_rate, 2)
    positions_f[4] = round(positions_f[4] / aud_rate, 2)
    positions_f[5] = round(positions_f[5] / usd_rate, 2)
    positions_f[6] = round(positions_f[6] / krw_rate, 2)
    
    positions_f += [invested_cash]
    
    positions_f = [str(e) for e in positions_f]
    positions_f[0] += " €"
    positions_f[1] += " AU$"
    positions_f[2] += " $"
    positions_f[3] += " ₩"
    positions_f[4] += " AU$"
    positions_f[5] += " $"
    positions_f[6] += " ₩"
    positions_f[7] += " €"

    modified_deltas = [round(d, 4) for d in deltas] + [0]
    
    df = pd.DataFrame({"Domestic": positions_d + ["0"], "Foreign": positions_f, "Deltas": modified_deltas,
                        "Domestic Int": positions_d_int}, index=ASSETS) 

    df["text"] = "Delta:<br>" + df["Deltas"].astype(str) + "<br>Domestic:<br>" + df["Domestic"].astype(str) \
        + "<br>Foreign:<br>" + df["Foreign"].astype(str)
    
    df.loc[ASSETS[-1], "text"] = f"Invested Cash:<br> {invested_cash} €"
    
    fig = px.bar(df, x=df.index, y='Domestic Int', text='text', 
                title=title_graph).update_layout(xaxis_title="Products invested in", yaxis_title="Investments in domestic currency (€)")
    fig.update_traces(textposition='outside')
    # Plot!
    st.plotly_chart(fig, use_container_width=True)

def display_portfolio_page(selected_date, portfolio_compo):
    
    st.markdown("""
        <style>
               .block-container {
                    padding-top: 1rem;
                    padding-bottom: 0rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
        </style>
        """, unsafe_allow_html=True)
    
    # Titre de l'application
    st.title(f"Structured Product Management - Period {st.session_state.selected_period+1}")
    st.write("")

    # Ajouter des cases avec un fond bleu sous le titre
    portfolio, price, pnl = st.columns(3)
    portfolio_value = round(portfolio_compo[portfolio_compo['Date'] == selected_date].PortfolioValue.values[0], 2)
    product_price = round(portfolio_compo[portfolio_compo['Date'] == selected_date].Price.values[0], 2)
    relative_pnl = round(100* (portfolio_value - product_price) / product_price, 2)

    with portfolio:
        st.markdown("<h2 style='text-align:center; font-weight:bold; font-size:20px;'>Today's portfolio value</h2>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='background-color:#21B1CD; color:white; padding:10px; border-radius:10px; text-align:center'>{portfolio_value} €</h2>", unsafe_allow_html=True)
        
    with price:
        st.markdown("<h2 style='text-align:center; font-weight:bold; font-size:20px;'>Today's product value</h2>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='background-color:#21B1CD; color:white; padding:10px; border-radius:10px; text-align:center'>{product_price} €</h2>", unsafe_allow_html=True)

    with pnl:
        st.markdown("<h2 style='text-align:center; font-weight:bold; font-size:20px;'>Total PnL</h2>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='background-color:#21B1CD; color:white; padding:10px; border-radius:10px; text-align:center'>{relative_pnl} %</h2>", unsafe_allow_html=True)

    # Définition du style des bordures
    st.markdown(
        """
        <style>
        .css-1tflvku {
            border-top: 2px solid black;
            border-left: 2px solid black;
            border-right: 2px solid black;
            border-bottom: 2px solid black;
            border-collapse: collapse;
        }
        .css-1bnyegb {
            border-top: 2px solid cyan;
            border-left: 2px solid cyan;
            border-right: 2px solid cyan;
            border-bottom: 2px solid cyan;
            border-collapse: collapse;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # List of dates T0 to T5
    date_lines = [date for date in STR_DATES_GRID[st.session_state.selected_period] if pd.to_datetime(date) <= selected_date]

    # Create traces for PortfolioValue and Price
    trace_portfolio_value = go.Scatter(x=portfolio_compo['Date'], y=portfolio_compo['PortfolioValue'], mode='lines', name='PortfolioValue')
    trace_price = go.Scatter(x=portfolio_compo['Date'], y=portfolio_compo['Price'], mode='lines', name='Price')

    # Create a figure with both traces
    fig = go.Figure([trace_portfolio_value, trace_price])

    # Add vertical lines for T0 to T5
    for i, date_line in enumerate(date_lines):
        fig.add_vline(x=pd.to_datetime(date_line, format="%d/%m/%Y"), line=dict(color="#e2e2e2", width=1, dash='dot'))
        fig.add_annotation(x=pd.to_datetime(date_line, format="%d/%m/%Y"), y=1400, text=f'T{i} - {date_lines[i]}', showarrow=True, 
                        font=dict(family="Courier New, monospace", size=10, color="#000"))

    # Update layout for better appearance
    fig.update_layout(
        title="Portfolio and Product values history (in €)",
        xaxis=dict(title='Date'),
        yaxis=dict(title='Prices in domestic currency (€)'),
        hovermode="x",
        hoverlabel=dict(bgcolor="white", font_size=12),
        showlegend=True
    )
    # Afficher le graphique
    st.plotly_chart(fig, use_container_width=True)
    
    
    deltas = portfolio_compo[portfolio_compo['Date'] == selected_date].Delta.values[0].strip('[]').split(', ')
    deltas = [float(element) for element in deltas]
            
    if selected_date != DATES_GRID[st.session_state.selected_period][0]:
        if "portfolio" in st.session_state and st.session_state.portfolio.iloc[-1]["DayNumber"]!=portfolio_compo.iloc[-1]["DayNumber"]:
            previous_date = pd.to_datetime(portfolio_compo.iloc[-2]["Date"])
            display_portfolio_compo(portfolio_compo, previous_date, "Current Portfolio composition:")
        else:
            st.sidebar.markdown("<h2 style='text-align:center; font-weight:bold; font-size:20px;'>Portfolio rebalanced today!</h2><br>", 
                        unsafe_allow_html=True)
    if "portfolio" in st.session_state and st.session_state.portfolio.iloc[-1]["DayNumber"]!=portfolio_compo.iloc[-1]["DayNumber"]:
        display_portfolio_compo(portfolio_compo, selected_date, "New suggested Portfolio composition:")
    else:
        display_portfolio_compo(portfolio_compo, selected_date, "Current Portfolio composition:")

    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("<h2 style='text-align:center; font-weight:bold; font-size:20px;'>Cash history</h2>", 
            unsafe_allow_html=True)
        st.plotly_chart(
            px.line(st.session_state.portfolio, x="Date", y="InvestedCash").update_layout(
                                                                    xaxis_title="Date", yaxis_title="Invested Cash in domestic ZC (€)"
                                                                ),
            use_container_width=True)
    if selected_date != DATES_GRID[st.session_state.selected_period][0]:
        with col4:
            if "portfolio" in st.session_state and st.session_state.portfolio.iloc[-1]["DayNumber"]!=portfolio_compo.iloc[-1]["DayNumber"]:
                st.markdown("<h2 style='text-align:center; font-weight:bold; font-size:20px;'>Rebalancing transactions</h2><br>", 
                            unsafe_allow_html=True)
                
                previous_deltas = portfolio_compo[portfolio_compo['Date'] == previous_date].Delta.values[0].strip('[]').split(', ')
                previous_deltas = [float(element) for element in previous_deltas]
                
                transactions = []

                for asset, delta, previous_delta in zip(ASSETS, deltas, previous_deltas):

                    transaction = {
                        'Asset': asset,
                        'Quantities to buy/ sell': delta - previous_delta
                    }
                    transactions.append(transaction)

                # Affichage des transactions
                st.write("Transactions to do to rebalance your portfolio", previous_date.date(), "to", selected_date.date(), ":")
                st.write(pd.DataFrame(transactions).set_index("Asset").transpose())
