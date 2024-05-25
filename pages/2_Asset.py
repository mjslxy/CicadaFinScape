import sys
import streamlit as st
import pandas as pd
import re

sys.path.append("..")
from context import FinContext
from finsql import ASSET_TABLE
import fwidgets as fw
import finutils as fu

context: FinContext = st.session_state['context']

st.set_page_config(page_title="Account")
st.sidebar.header("Account")
st.header("Account")

acc_name_list = [v.name for k, v in context.acc.items()]
tabs = st.tabs(acc_name_list)
for index, tab in enumerate(tabs):
    with tab:
        acc_name = acc_name_list[index]
        acc = context.acc[acc_name]
        assets_name = [x.name for x in acc.asset_list]

        if not assets_name:
            st.write(f"### You don't have any asset under account {acc_name}.")
            if st.button("Add asset", type="primary", key="ass_add_asset"):
                fw.add_asset()
            st.stop()

        sub_name = st.radio("Choose your subaccount", assets_name, key=f"Choose-asset-{acc}-{index}", label_visibility="collapsed")
        account_and_sub = f"{acc_name}-{sub_name}"
        asset_df = context.asset_df(acc_name, sub_name)
        asset_df.sort_values("DATE", ascending=False, inplace=True)

        col_configs = {k: st.column_config.TextColumn(k, disabled=True) for k in asset_df.columns}
        asset_df["Select"] = False
        check_col_config = st.column_config.CheckboxColumn("Select", default=False)
        col_configs["Select"] = check_col_config

        df = st.data_editor(asset_df, hide_index=True, key=account_and_sub + "-df", use_container_width=True, column_config=col_configs)
        date_list = df.loc[df["Select"]]["DATE"]

        # TODO - use https://github.com/victoryhb/streamlit-option-menu
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Add/Update record", key=f"{account_and_sub}-add", type="primary"):
                fw.insert_or_update_record_dia(acc_name, sub_name)
        with col2:
            if st.button("Delete Selected", key=f"asset-{account_and_sub}-delete"):
                fw.delete_selected_data_dia(acc_name, sub_name, date_list)

        # if st.button("DELETE SUBACCOUNT", key=account_and_sub + "-delete"):
        #     delete_asset_dia(acc_name, sub_name)
