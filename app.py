import streamlit as st

from calculate_irr import calculate_irr
from deploy_file import deploy_file
from forecast import forecast
from integrate import integrate
from prod_to_dev import prod_to_dev

# streamlit run app.py


st.title("TM1py Demo with Streamlit")
forecast_expander = st.expander("DEMO 1", expanded=True)
with forecast_expander:
    st.button(label="Forecast Sales", use_container_width=True, on_click=forecast)

integration_expander = st.expander("DEMO 2", expanded=True)
with integration_expander:
    st.button(label="Load Salesforce Customers", use_container_width=True, on_click=integrate)

automation_expander = st.expander("DEMO 3", expanded=True)
with automation_expander:
    col1, col2 = st.columns([1, 1])
    with col1:
        cube_name = st.selectbox(label="Cube", options=["Investments", "Sales"], )
    with col2:
        dimension_name = st.selectbox(label="Anonymize Dimension", options=["Customer"])
    st.button(label="Replicate cube PROD to DEV", use_container_width=True, on_click=prod_to_dev,
              args=(cube_name, dimension_name))

calculation_expander = st.expander("DEMO 4", expanded=True)
with calculation_expander:
    st.button(label="Calculate IRR", use_container_width=True, on_click=calculate_irr)

file_expander = st.expander("DEMO 5", expanded=True)
with file_expander:
    st.button(label="Deploy File to PAoC", use_container_width=True, on_click=deploy_file)
