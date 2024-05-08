import sys
import streamlit as st
import pandas as pd
sys.path.append("..")
from context import FinContext
context:FinContext = st.session_state['context']

keys = ["acc_cat_df_key", "acc_acc_toggle"]
def s_incre(s):
    st.session_state[s] = st.session_state[s] + 1

def k_incre_all():
    for key in keys:
        s_incre(key)

def k_init_all():
    for key in keys:
        if key not in st.session_state:
            st.session_state[key] = 0

k_init_all()

st.set_page_config(
    page_title="Account Management",
)
st.sidebar.header("Account Management")
st.header("Account Management")
st.subheader("Account Categories")

# category
cat_df = context.category_df()

# TODO - use list editor
df = st.data_editor(
    cat_df,
    hide_index=True,
    num_rows="dynamic",
    key = st.session_state['acc_cat_df_key']
)
col1, col2= st.columns([2,11])
with col1:
    st.button("Commit", on_click=FinContext.category_from_df, args=(context, df), type="primary", key="acc_cat_df_commit")
with col2:
    if st.button("Reset"):
        k_incre_all()
        st.rerun()


# Accounts
st.subheader("Accounts")

edit_on = st.toggle("Edit", key = st.session_state["acc_acc_toggle"])
if not edit_on:
    st.table(context.account_df())
else:
    df = st.data_editor (
        context.account_df(),
        hide_index=True,
        num_rows="dynamic"
    )
    st.button("Commit", on_click=FinContext.account_from_df, args=(context, df), type="primary", key="acc_acc_df_commit")