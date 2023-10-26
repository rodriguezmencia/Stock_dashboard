#------------------------------
#------import libraries--------
#------------------------------
import streamlit as st
import pandas as pd
import sqlite3
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
from datetime import datetime
import time
import yfinance as yf

st.set_page_config(page_title="SQLite_Analysis", page_icon="📈")

st.markdown("**Data Analysis**")

conn = sqlite3.connect('stock.sqlite')
c = conn.cursor()
   
# Fxn Make Execution
def sql_executor(raw_code):
    c.execute(raw_code)
    data = c.fetchall()
    return data 
    
data_struc = ['Date','Open','High','Low','Close','Volume','Dividends','Stock Splits','MA_30','MA_15','MA_5']

col5,col6 = st.columns(2)
# query
with col5:
    with st.form(key='query_form'):
        raw_code = st.text_area("SQL Code Here")
        submit_code2 = st.form_submit_button("Execute")
    # Table of Info
    with st.expander("Table Info"):
        table_info = {'hist_price':data_struc}
        st.json(table_info)
# Results Layouts
with col6:
    if submit_code2:
        st.info("Query Submitted")
        st.code(raw_code)
        # Results 
        query_results = sql_executor(raw_code)
        with st.expander("Results"):
            st.write(query_results)
        with st.expander("Pretty Table"):
            query_df = pd.DataFrame(query_results)
            st.dataframe(query_df)
