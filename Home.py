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

chart = context.asset_chart()
st.plotly_chart(chart, theme="streamlit", use_container_width=True)
