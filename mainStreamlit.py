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

#CONSTANTS
IS_AUTHENTICATION = True

# Page Configuration
st.set_page_config(
    page_title="VVYSAI's Contractor Analysis",
    page_icon="👷🏻‍♂️",
    initial_sidebar_state="collapsed",
    layout="wide",
)

# CURRENCY IDEA!
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

# MOST APPREARED ELEMENT !
def most_frequent_element(arr):
    if not arr:
        return None
    most_frequent = max(arr, key=arr.count)
    frequency = arr.count(most_frequent)
    return most_frequent, frequency

with open("BIDDERS_PROFILE_INSIGHTS_15TO24.json", "r") as f:
    biddersDf = json.load(f)

with open('style.css', 'r') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Main Page Title
st.markdown(
    """<h1 class="main-title">VVYSAI's Contractor Analysis</h1>""",
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
            st.markdown("# ")
            st.markdown(
                f"""
                <h3 style="font-size: 45px;">Contractor: {tend['l1_name']}</h3>
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
        st.markdown(f"""<h6 style="font-size: 11px;">[Use Desktop mode to see the table & Charts Properly""", unsafe_allow_html=True)

        st.markdown("### Recent Won Tenders")
        st.markdown(table_index + table_row)