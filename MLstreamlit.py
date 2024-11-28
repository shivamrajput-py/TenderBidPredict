import pandas as pd
import json
import difflib
import plotly_express as px
import datetime
import streamlit as st
from pathlib import Path
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

# Page Configuration
st.set_page_config(
    page_title="VVYSAI's Contractor Analysis",
    page_icon="👷🏻‍♂️",
    initial_sidebar_state="collapsed",
    layout="wide",
)

# Helper Functions
def currn_INR(value):
    try:
        value = int(value)
        if value >= 10**7:
            crore = value / 10**7
            return f"{crore:.2f} Cr."
        elif value >= 10**5:
            lakh = value / 10**5
            return f"{lakh:.2f} Lakh"
        else:
            return f"{value:,} INR"
    except:
        return value

def most_frequent_element(arr):
    if not arr:
        return None
    most_frequent = max(arr, key=arr.count)
    frequency = arr.count(most_frequent)
    return most_frequent, frequency

# Load Data
with open("BIDDERS_PROFILE_INSIGHTS_15TO24.json", "r") as f:
    biddersDf = json.load(f)

# Authentication
with open(".streamlit/config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
    config["preauthorized"],
)

name, authentication_status, username = authenticator.login("main", 3)

if authentication_status == False:
    st.error("Username/password is incorrect")

if authentication_status == None:
    st.warning("Please enter your Username and Password to Continue")

if authentication_status:
    authenticator.logout(location="sidebar")

    # Main Page Title
    st.markdown(
        """
        <style>
        .main-title { 
            font-family: 'Arial', sans-serif; 
            color: #1f77b4; 
            font-size: 2.5rem; 
            text-align: center; 
            margin-bottom: 20px; 
        }
        .section-title {
            font-size: 1.2rem;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .info-text {
            font-size: 1rem;
            color: #555;
            margin-bottom: 15px;
        }
        </style>
        <h1 class="main-title">VVYSAI's Contractor Analysis</h1>
        """,
        unsafe_allow_html=True,
    )

    # Search Section
    search_term = st.text_input(
        "Search Contractor Name", placeholder="Enter contractor name..."
    )

    if search_term:
        matched_contractors = difflib.get_close_matches(
            search_term, biddersDf.keys(), n=5, cutoff=0.5
        )
        dropbox = st.selectbox(
            label="Select the Probable Contractor",
            options=list(matched_contractors),
            key="contbut",
        )
        but = st.button("Get the Competitive Analysis NOW")

        if dropbox and but:
            # Contractor Analysis
            DATA = biddersDf[dropbox]
            district_data, district_dlist = {}, []
            total_bidwon = 0
            total_bidpercent = []
            bid_district_dept = [[], []]
            table_index = "| Tender Title | Department | District | Gov Price | Bid Won Price | Bid Percentage |\n"
            table_row = "|--------------|------------|-----------|-----------|----------------|----------------|\n"

            DATA = sorted(
                DATA,
                key=lambda x: datetime.datetime.strptime(
                    x["bid_submission_date"], "%d-%b-%Y %I:%M %p"
                ),
                reverse=True,
            )

            for tend in DATA:
                table_row += f"| {tend['tender_titile']} | {tend['org'].split('|')[0]} | {tend['district']} | {currn_INR(tend['gov_price'])} | {currn_INR(tend['bid_won_price'])} | {tend['bid_percentage']} |\n"

                district_data[tend["district"]] = district_data.get(tend["district"], 0) + 1

                if tend["l1_price"] != "NA":
                    total_bidwon += float(tend["l1_price"].replace(",", ""))

                if tend["bid_percentage"] != "NA":
                    total_bidpercent.append(float(tend["bid_percentage"]))

                bid_district_dept[0].append(tend["district"])
                bid_district_dept[1].append(tend["org"].split("|")[0])

            T_district, T_district_freq = most_frequent_element(bid_district_dept[0])
            T_dept, T_dept_freq = most_frequent_element(bid_district_dept[1])

            # Layout for Displaying Key Metrics
            left_col, right_col = st.columns(2)
            with left_col:
                st.markdown(
                    f"""
                    <h3>Contractor: {tend['l1_name']}</h3>
                    <ul>
                        <li><strong>Total Value of Awarded Tenders:</strong> {currn_INR(total_bidwon)}</li>
                        <li><strong>Total Tenders Won:</strong> {len(DATA)}</li>
                        <li><strong>Average Bid Percentage:</strong> {round(sum(total_bidpercent)/len(total_bidpercent), 2)}%</li>
                        <li><strong>Top Department:</strong> {T_dept} ({T_dept_freq} tenders won)</li>
                        <li><strong>Top District:</strong> {T_district} ({T_district_freq} tenders won)</li>
                    </ul>
                    """,
                    unsafe_allow_html=True,
                )

            # District Data Visualization
            for key, value in district_data.items():
                district_dlist.append({"District": key, "Tenders Won": value})

            df = pd.DataFrame(district_dlist)

            fig = px.pie(
                df,
                names="District",
                values="Tenders Won",
                title="Tenders Won by District",
                color_discrete_sequence=px.colors.qualitative.Dark2_r,
            )
            fig.update_traces(
                textinfo="percent+label",
                pull=[
                    0.1 if value == df["Tenders Won"].max() else 0
                    for value in df["Tenders Won"]
                ],
            )

            with right_col:
                st.plotly_chart(fig, use_container_width=True)

            # Table of Recent Tenders
            st.markdown("### Recent Won Tenders")
            st.markdown(table_index + table_row)

# import numpy as np
# import streamlit as st
# import joblib  # To load saved models
# import warnings
# import pandas as pd
#
# warnings.filterwarnings('ignore')
#
# def currenc(value, currency_symbol="₹"):
#     return f"{currency_symbol}{value:,.2f}"
#
# # Custom CSS for styling the page
# def local_css(file_name):
#     with open(file_name) as f:
#         st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
#
# def set_custom_css():
#     st.markdown("""
#
# <style>
# /* Center the title */
# .title h1 {
#     text-align: center;
#     color: #0078D7;
#     font-size: 3em;
# }
#
#
# /* Style the input field */
# .stNumberInput input {
#     border-radius: 12px;
#     border: 2px solid #0078D7;
# }
#
# /* Customize the subheaders */
# .subheader {
#     font-weight: bold;
#     color: #0078D7;
#     text-align: center;
#     margin-bottom: 20px;
# }
#
# /* Make the columns content more appealing */
# .pred-container {
#     background-color: #526272;
#     border-radius: 10px;
#     padding: 20px;
#     box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1);
#     text-align: center;
# }
#
# /* Prediction text styling */
# .pred-container h3 {
#     color: #e5f9ff;  /* Set prediction text color to black */
# }
#
# /* Overall page styling */
# body {
#     background-color: #F0F2F6;
# }
#
#
# .css-15zrgzn {display: none}
# .css-eczf16 {display: none}
# .css-jn99sy {display: none}
#
# /* FOR REMOVING THE SIDE BAR COMPLETELY */
# [data-testid="collapsedControl"] {
#         display: none
#     }
# /* */
# #root > div:nth-child(1) > div.withScreencast > div > div > div > section:nth-child(2) {
#                     height: 3rem !important;
#                 }
# /* FOR ADJUSTING EXTRA SPACE AROUND THE WHOLE PAGE */
# .block-container {
#     padding-top: 23px;
#     padding-bottom: 5rem;
#     padding-left: 0rem;
#     padding-right: 0rem;
# }
#
#
# #MainMenu {visibility: hidden;}
# footer {visibility: hidden;}
# header {visibility: hidden;}
#
# [data-testid="stToolbar"] {visibility: hidden !important;}
# footer {visibility: hidden !important;}
#
# </style>
#     """, unsafe_allow_html=True)
#
# # Load pre-trained models
# @st.cache_resource
# def load_models():
#
#     # FOR BRIDGE
#     rfr = joblib.load('rfr_model.pkl')
#     lr = joblib.load('lr_model.pkl')
#
#     # FOR ELECTRICAL WORK
#     ee_model = joblib.load('linearElectrical_model.pkl')
#     return rfr, lr, ee_model
#
# def main():
#
#     set_custom_css()
#
#     # Page title
#     st.markdown("<div class='title'><h1>Bid Prediction Model By Vyvsai</h1></div>", unsafe_allow_html=True)
#
#     chosedcat = st.selectbox("SELECT CATEGORY OF THE WORK:", ['Electrical Work', 'Bridges'])
#
#     if chosedcat == 'Bridges':
#
#         rfr_model, lr_model, _ = load_models()
#
#         # st.markdown('---')
#         left, right = st.columns(2)
#
#         try:
#             with left:
#                 st.markdown('###### ')
#                 INPUT_GOV_PRICE = int(st.text_input("GOV ESTIMATED TENDER PRICE:", value='0'))
#             NOERROR = True
#         except:
#             st.error("ENTER INTEGER VALUED PRICE ONLY! NEEDS VALID INPUT TO PREDICT!")
#             NOERROR = False
#
#         with right:
#             st.markdown('#### ')
#             predict = st.button("Predict Bid Won Price")
#
#         if NOERROR and (INPUT_GOV_PRICE != 0) and predict:
#
#             # Prepare input data
#             input_data = np.array([[INPUT_GOV_PRICE, 0.0]])
#
#             # Predictions
#             rfr_prediction = rfr_model.predict(input_data)
#             percentage_rfr = round(((rfr_prediction[0] - INPUT_GOV_PRICE) / INPUT_GOV_PRICE) * 100, 2)
#             lr_prediction = lr_model.predict(input_data)
#             percentage_lrp = round(((lr_prediction[0] - INPUT_GOV_PRICE) / INPUT_GOV_PRICE) * 100, 2)
#
#             st.write(f'#### For Gov Estimated Price: {str(currenc(INPUT_GOV_PRICE))}')
#
#             st.markdown("---")
#
#             col1, col2 = st.columns(2)
#
#             with col1:
#                 st.markdown("<div class='subheader'> 1st Recommendation [RFR MODEL]</div>", unsafe_allow_html=True)
#                 st.markdown(
#                     f"<div class='pred-container'><h3>Price: {currenc(rfr_prediction[0])}<br>Bid% : {str(percentage_rfr) + '%'}</h3></div>",
#                     unsafe_allow_html=True)
#
#             with col2:
#                 st.markdown("<div class='subheader'>2nd Recommendation [LRP MODEL]</div>", unsafe_allow_html=True)
#                 st.markdown(
#                     f"<div class='pred-container'><h3>Price: {currenc((lr_prediction[0]))}<br>Bid% : {str(percentage_lrp) + '%'}</h3></div>",
#                     unsafe_allow_html=True)
#
#             # Add footer or additional info
#             st.markdown("""
#                     <br><hr>
#                     <p style='text-align: center; font-size: 0.8em; color: grey;'>
#                     Vyvsai Private Limited
#                     </p>
#                 """, unsafe_allow_html=True)
#
# #-----------------------------------------------------------------------------------------------------------
#
#     elif chosedcat == 'Electrical Work':
#         _, _ , model = load_models()
#
#         # st.markdown('---')
#         left, right = st.columns(2)
#
#         try:
#             with left:
#                 st.markdown('###### ')
#                 INPUT_GOV_PRICE = int(st.text_input("GOV ESTIMATED TENDER PRICE:", value='0'))
#             NOERROR = True
#         except:
#             st.error("ENTER INTEGER VALUED PRICE ONLY! NEEDS VALID INPUT TO PREDICT!")
#             NOERROR = False
#
#         with right:
#             st.markdown('#### ')
#             predict = st.button("Predict Bid Won Price")
#
#         # Button to trigger prediction
#         if NOERROR and (INPUT_GOV_PRICE != 0) and predict:
#
#             custom_re_df = pd.DataFrame(data={'bid_won_price': [INPUT_GOV_PRICE]})
#
#             # Make a prediction
#             custom_pred = model.predict(custom_re_df)
#
#             percentage_ee_model = round(((custom_pred[0] - INPUT_GOV_PRICE) / INPUT_GOV_PRICE) * 100, 2)
#
#             st.write(f'#### For Gov Estimated Price: {str(currenc(INPUT_GOV_PRICE))}')
#
#             st.markdown("---")
#
#             _ , col1, _ = st.columns([0.75, 1.5, 0.75])
#
#             with col1:
#                 st.markdown("<div class='subheader'>Model Recommendation Says:</div>", unsafe_allow_html=True)
#                 st.markdown(
#                     f"<div class='pred-container'><h3>Price: {currenc(round(custom_pred[0], 0))}<br>Bid% : {str(percentage_ee_model) + '%'}</h3></div>",
#                     unsafe_allow_html=True)
#
#
#             # Add footer or additional info
#             st.markdown("""
#                                 <br><hr>
#                                 <p style='text-align: center; font-size: 0.8em; color: grey;'>
#                                 Vyvsai Private Limited
#                                 </p>
#                             """, unsafe_allow_html=True)
#
# if __name__ == "__main__":
#     main()