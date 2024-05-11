import csv
import pandas as pd
import streamlit as st
import os

import finsql as finsql
from context import FinContext

import streamlit as st

st.set_page_config(
    page_title="Monthly Financial Dashboard",
    page_icon="👋"
)

st.write("# Welcome to Monthly Financial Dashboard!")
st.sidebar.success("Sidebar")

curr_path = __file__
curr_dir = os.path.dirname(curr_path)
data_dir = os.path.join(curr_dir, "data")
if not os.path.exists(data_dir):
    os.makedirs(data_dir, mode=0o777, exist_ok = True)
    os.chmod(data_dir, 0o777)

config_path = os.path.join(data_dir, "config.json")
csv_path = os.path.join(data_dir, "data.csv")
db_path = os.path.join(data_dir, "test.db")

# Init context
context = FinContext(config_path, db_path)
st.session_state['context'] = context

@st.experimental_dialog("Your database is not valid")
def init_db():
    st.write("# Initialize your database? All of the data in database will be reset and can not recover")
    if st.button("Confirm", key = "initial_reset_dia_confirm"):
        context:FinContext = st.session_state['context']
        context.init_db()
        st.rerun()

if not context.validate_db():
    init_db()
    st.stop()

@st.experimental_dialog("RESET DATA TO SAMPLE DATA")
def reset_sample_data_dia():
    st.write("# WARNING: All of your data will be reset and can not recover")
    if st.button("Confirm", key = "side_bar_reset_dia_confirm"):
        context:FinContext = st.session_state['context']
        context.initialize_with_sample_data()
        st.rerun()

with st.sidebar:
    if st.button("Reset to Sample data", key="side_bar_reset_button"):
        reset_sample_data_dia()

chart = context.asset_chart()
st.plotly_chart(chart, theme="streamlit", use_container_width=True)
