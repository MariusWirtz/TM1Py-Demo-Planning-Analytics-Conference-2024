from datetime import datetime

import streamlit as st
from dateutil.relativedelta import relativedelta

from calculate_irr import calculate_irr
from deploy_file import deploy_file
from forecast import forecast, clear
from integrate import integrate

# streamlit run app.py
EMOJIS = {
    "Forecast": "📊",
    "Calculate IRR": "💰",
    "Load Salesforce": "📥",
    "Deploy File to PAoC": "🚀"
}

NAVIGATION_ENTRIES = {
    "🎯 Forecast",
    "📊 Calculate IRR",
    "📥 Load Customers From Salesforce",
    "🔁 Deploy File to PAoC"
}

INVESTMENTS = [
    "Investment " + str(i).zfill(4)
    for i
    in range(1, 10_000)]

REGIONS = [
    "Austria",
    "Belgium",
    "Germany",
    "France",
    "Netherlands"]

PRODUCTS = [
    "Belgian-Style Ale",
    "India Pale Ale",
    "Lager",
    "Pale Ale",
    "Wheat Beer"
]

# Sidebar navigation
nav_selection = st.sidebar.selectbox("Navigation", NAVIGATION_ENTRIES)
st.sidebar.markdown("---")
st.sidebar.markdown(
    '<h6>Made in &nbsp<img src="https://streamlit.io/images/brand/streamlit-mark-color.png" alt="Streamlit logo" height="16">&nbsp by <a href="https://github.com/MariusWirtz">@MariusWirtz</a></h6>',
    unsafe_allow_html=True,
)

st.image("logo-cubewise.png")
st.title("TM1py Analytics App 🚀")
st.markdown("---")

if nav_selection == "🎯 Forecast":

    start_date = datetime(2014, 1, 1)
    end_date = datetime(2021, 12, 1)

    # Generate the list of periods
    periods = []
    current_date = start_date
    while current_date <= end_date:
        periods.append(current_date.strftime("%Y%m"))
        current_date += relativedelta(months=1)

    # Period picker
    start_period = st.selectbox("Select Start Period", periods, index=0)
    end_period = st.selectbox("Select End Period", periods, index=len(periods) - 1)
    region = st.selectbox("Select Region", REGIONS)
    product = st.selectbox("Select Product", PRODUCTS)
    st.button(
        label="Clear",
        use_container_width=True,
        on_click=clear,
        args=[region, product])
    st.button(
        label="Forecast Sales",
        use_container_width=True,
        on_click=forecast,
        args=[start_period, end_period, region, product])

if nav_selection == "📥 Load Customers From Salesforce":
    st.button(label="Load Salesforce Accounts", use_container_width=True, on_click=integrate)

if nav_selection == "📊 Calculate IRR":
    st.button(label="Calculate IRR For All", use_container_width=True, on_click=calculate_irr, args=[None])
    investment = st.selectbox("Select Investment", INVESTMENTS)
    st.button(label="Calculate IRR For One", use_container_width=True, on_click=calculate_irr, args=[investment])

if nav_selection == "🔁 Deploy File to PAoC":
    file = st.file_uploader("Upload File")
    file_name = st.text_input("File Name in TM1")
    st.button(label="Deploy File to PAoC", use_container_width=True, on_click=deploy_file, args=[file_name, file])
