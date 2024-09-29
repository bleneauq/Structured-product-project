import streamlit as st

def dislay_info_page(selected_date):
    
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
    
    st.title("Product informations")
    st.write(f"Selected date: {selected_date}")
    st.write("""
    ### Product 3: Based on Yosemite
    - The formula depends on the performance of 4 indexs: **ASX 200**, **CAC 40**, **Nasdaq 100**, and **KOSPI 50**.
    - The management objective of the FCP is to enable the bearer to receive, at the Maturity Date ("Tc date"), the Reference Net Asset Value (i.e., €1000), excluding subscription fees, plus a Final Gain.
    - At each observation date ("T1 date" to "Tc date"), we calculate the performance of each of the 4 indexs relative to their initial value (value at "T0 date"). If this performance is:
        - Between -15% and +15%, we take a value Pi equal to the absolute value of this annual performance.
        - Greater than 15%, we take a value Pi equal to 15%.
        - Less than -15%, we take a value Pi equal to the performance itself.
    - We then average the 4 Pi values and take this average value as the Annual Performance of the Basket, if positive, 0% otherwise.
    - The Final Performance is the sum of the Annual Performances, and we pay out at the final date the Reference Net Asset Value increased by 25% of the Final Performance.
    - Additionally, at each Intermediate Observation Date ("T1 date" to "T4 date"), we pay the bearer a dividend equal to the "minimum of positive Pi values" x €50. For example, if at one of the T1, ..., T4 dates, the Pi values are -27%, 3%, 9%, 15%, we will pay a dividend of 50x3%=€1.5.
    """)