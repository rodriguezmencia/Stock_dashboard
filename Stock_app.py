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

#Streamlit app
# sidebar
with st.sidebar.form(key ='Form1'):
    st.title("Enter information")
    symbol = st.text_input('Stock symbol e.g. GOOG')
    inter=st.selectbox('Enter the interval of time:',
    ('1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo'))
    init = st.date_input("Enter the start date [YYYY-MM-DD]:", ) #datetime.date(2019, 7, 6)
    finish=st.date_input("Enter the finish date [YYYY-MM-DD]:", )#datetime.date(2019, 7, 6)
    
    with st.expander(f"**Analytics**"):
        MA_30 = st.checkbox('MA-30 d')
        MA_15 = st.checkbox('MA-15 d')
        MA_5 = st.checkbox('MA-5 d')
    
    submit_code = st.form_submit_button(label ="Execute")

#main page
# title
st.subheader("Stock Analytics")
st.markdown("""---""")

# plot
if submit_code:
    if symbol:
        stock = yf.Ticker(symbol)
        df = stock.history(interval=inter, start=init, end=finish)

        # Calculate the 30/15/5-period moving average
        df['MA_30'] = df['Close'].rolling(window=30).mean()
        df['MA_15'] = df['Close'].rolling(window=15).mean()
        df['MA_5'] = df['Close'].rolling(window=5).mean()

        # Main plot
        fig = make_subplots(rows=2, cols=1,
                                shared_xaxes=True,
                                vertical_spacing=0.1,
                                subplot_titles=("Stock Price","Volumen"),
                                row_heights=[0.5,0.2])
        
        fig.add_trace(go.Candlestick(x=df.index,
              open=df['Open'],
              high=df['High'],
              low=df['Low'],
              close=df['Close']),row=1,col=1)
            
        fig.add_trace(go.Bar(x=df.index,
                             y=df['Volume'],
                             marker_color='blue'), row=2, col=1)
        
        # Add the 30/15/5-period moving average line
        if MA_30:
            fig.add_trace(go.Scatter(x=df.index, y=df['MA_30'], line=dict(color='red', width=1), name='MA 30'),
                          row=1, col=1)
        if MA_15:
            fig.add_trace(go.Scatter(x=df.index, y=df['MA_15'], line=dict(color='purple', width=1), name='MA 15'),
                          row=1, col=1)
        if MA_5:
            fig.add_trace(go.Scatter(x=df.index, y=df['MA_5'], line=dict(color='blue', width=1), name='MA 5'),
                          row=1, col=1)
        
        fig.update_layout(
                title=symbol,
                xaxis_rangeslider_visible=False,
                showlegend=False)
            
        fig.update_yaxes(title_text="stock price", row=1, col=1)
        fig.update_yaxes(title_text="volumen", row=2, col=1)
        fig.update_xaxes(title_text='Date', row=2, col=1)
            
        # hide weekends without transactions
        fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"])])
        
        time=datetime.now()
        new_stock=stock.history(period='1d')
        
        stock_now=new_stock.iloc[-1]["Close"] #stock.history(period='1d').iloc[-1]["Close"]
        stock_beg=new_stock.iloc[-1]["Open"] #stock.history(period='1d').iloc[-1]["Open"]
        vol_now=new_stock.iloc[-1]["Volume"] #stock.history(period='1d').iloc[-1]["Volume"]
        var=stock_now/stock_beg-1
        
        formatted_stock_now = "{:.2f}".format(stock_now)
        formatted_vol_now = "{:.2f}".format(vol_now/1000000)
        formatted_time = time.strftime("%Y-%m-%d, %H:%M:%S")
        formatted_var = "{:.2%}".format(var)
        text_color = "green" if var > 0 else "red"

        #-------------
        #sql procedure
        #-------------
        #1.- drop data
        conection = sqlite3.connect('stock.sqlite')
        cursor = conection.cursor()
        cursor.execute("DELETE FROM hist_price")

        #2.-insert new dataset
        df2=df.reset_index()
	df2=df2.to_records(index=False)
	df2.to_sql('hist_price', conection, if_exists='append', index=False)

        conection.commit()
        conection.close()
        #-------------

	#-------------Part 1
        st.markdown("**Summary - Current market information**")
        col1,col2,col3,col4 = st.columns([0.25,0.25,0.25,0.25])
        with col1:
            #st.plotly_chart(fig,use_container_width=True)
            st.markdown(f"**Price (USD)**")
            st.write(f'<p style="color:black">{formatted_stock_now}</p>', unsafe_allow_html=True)
        with col2:
            st.markdown(f"**Intraday var.(%)**")
            st.write(f'<p style="color:{text_color}">{formatted_var}</p>', unsafe_allow_html=True)
        with col3:
            st.markdown(f"**Volume (MM$)**")
            st.write(f'<p style="color:black">{formatted_vol_now}</p>', unsafe_allow_html=True)
        with col4:
            st.markdown(f"**Date**")
            st.write(f'<p style="color:black">{formatted_time}</p>', unsafe_allow_html=True)

    #-------------Part 2
        st.markdown("**Historical price evolution**")
        st.plotly_chart(fig,use_container_width=True)
    
    #-------------Part 3
        st.markdown("**Data Analysis**")
        conn = sqlite3.connect('stock.sqlite')
        c = conn.cursor()
        
    # Fxn Make Execution
        def sql_executor(raw_code):
            c.execute(raw_code)
            data = c.fetchall()
            return data 
        data_struc = ['Date','Open','High','Low','Close','Volume','Dividends','Stock Splits']

        col5,col6 = st.columns(2)
    # query
        with col5:
            with st.form(key='query_form'):
                raw_code = st.text_area("SQL Code Here")
                submit_code = st.form_submit_button("Execute")
            # Table of Info
            with st.expander("Table Info"):
                table_info = {'Stock infor':data_struc}
                st.json(table_info)
        # Results Layouts
        with col6:
            if submit_code:
                st.info("Query Submitted")
                st.code(raw_code)
                # Results 
                query_results = sql_executor(raw_code)
                with st.expander("Results"):
                    st.write(query_results)
                with st.expander("Pretty Table"):
                    query_df = pd.DataFrame(query_results)
                    st.dataframe(query_df)
        #----------------------------------------------------------------------------------------------
        
    else:
        st.write("please enter a valid stock symbol")
