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
config_path = os.path.join(curr_dir, "config.json")
data_path = os.path.join(curr_dir, "data.csv")
db_path = os.path.join(curr_dir, "db")
db_path = os.path.join(db_path, "test.db")

context = FinContext(config_path, db_path)
st.session_state['context'] = context
#context.init_db_from_csv(data_path)

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
