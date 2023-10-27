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


#st.set_page_config(page_title="Stock app")

#Streamlit app
#------------------------------------------------------------------------------------------
#-----------------------------------------SIDEBAR------------------------------------------
#------------------------------------------------------------------------------------------
with st.sidebar.form(key ='Form1'):
    st.title("Enter information")
    symbol = st.text_input('Stock symbol e.g. GOOG',help='write down the stock symbol that you want to search',value='GOOG')
    default_date = datetime(2023, 1, 1)
    init = st.date_input("Enter the start date [YYYY/MM/DD]:", value=default_date)
    finish=st.date_input("Enter the finish date [YYYY/MM/DD]:", )
    
    with st.expander(f"**Analytics**"):
        MA_30 = st.checkbox('MA-30',help='moving average 30 last periods')
        MA_15 = st.checkbox('MA-15',help='moving average 15 last periods')
        MA_5 = st.checkbox('MA-5',help='moving average 5 last periods')
        Mean_ = st.checkbox('Mean',help='mean of selected periods')
    
    submit_code = st.form_submit_button(label ="Execute")

#------------------------------------------------------------------------------------------
@st.cache
def lee(symbol,interval,start,end):
    stock = yf.Ticker(symbol)
    df = stock.history(interval=interval, start=start, end=end)
    # Calculate the 30/15/5-period moving average
    df['MA_30'] = df['Close'].rolling(window=30).mean()
    df['MA_15'] = df['Close'].rolling(window=15).mean()
    df['MA_5'] = df['Close'].rolling(window=5).mean()
    df['Mean'] = df['Close'].mean()
    return df

@st.cache
def lee_hoy(symbol):
    stock = yf.Ticker(symbol)
    new_stock = stock.history(period='1d')
    return new_stock

@st.cache_data
def recomend(symbol):
    stock = yf.Ticker(symbol)
    recom = stock.get_news()
    if recom is None:
        return pd.DataFrame()  # Return an empty DataFrame if there's no data
    return pd.DataFrame(recom)


#main page
tab1, tab2 = st.tabs(["General info", "Detailed info"])
with tab1:
    # title
    st.subheader("Stock Analytics")
    st.markdown("""---""")
    # plot
    if submit_code:
        if symbol:
            df=lee(symbol,'1d',init,finish)

            if not df.empty:
        
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
                if Mean_:
                    fig.add_trace(go.Scatter(x=df.index, y=df['Mean'], line=dict(color='blue', width=1), name='Mean'),
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
                new_stock=lee_hoy(symbol)

                if not new_stock.empty:
                    stock_now=new_stock.iloc[-1]["Close"] 
                    stock_beg=new_stock.iloc[-1]["Open"] 
                    vol_now=new_stock.iloc[-1]["Volume"] 
                    var=stock_now/stock_beg-1
                    
                    formatted_stock_now = "{:.2f}".format(stock_now)
                    formatted_vol_now = "{:.2f}".format(vol_now/1000000)
                    formatted_time = time.strftime("%Y-%m-%d, %H:%M:%S")
                    formatted_var = "{:.2%}".format(var)
                    text_color = "green" if var > 0 else "red"
        
                    recom=recomend(symbol)
                    
                    #-------------
                    #sql procedure
                    #-------------
                    #1.- drop data
                    conection = sqlite3.connect('stock.sqlite')
                    cursor = conection.cursor()
                    cursor.execute("DELETE FROM hist_price")
            
                    #2.-insert new dataset
                    columns_to_insert = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits', 'MA_30', 'MA_15', 'MA_5']
                    df.reset_index()[columns_to_insert].to_sql('hist_price', conection, if_exists='append', index=False)
            
                    conection.commit()
                    conection.close()
                    #-------------
            
                #-------------Part 1
                    st.subheader("Summary - Current market information")
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
                    st.subheader("Historical price evolution")
                    st.plotly_chart(fig,use_container_width=True)
                #-------------Part 2.1
                    st.subheader("News related with the company")
                    if not recom.empty:
                        table = "<table><tr><th>Publisher</th><th>Title</th></tr>"
                        for index, row in recom.iterrows():
                            publisher = row['publisher']
                            title = row['title']
                            link = row['link']
                            title_with_link = f'<a href="{link}" target="_blank">{title}</a>'
                            table += f"<tr><td>{publisher}</td><td>{title_with_link}</td></tr>"
                        table += "</table>"
                        st.markdown(table, unsafe_allow_html=True)
                
                    else:
                        st.write("No recommendation data available for this stock.")
                else:
                    st.write("No data available for this stock today.")
            else:
                st.write("No data available for this stock.")
        else:
            st.write("please enter a valid stock symbol")        
        #-------------Part 3
with tab2: 
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
                submit_code2 = st.form_submit_button("Submit")
                st.warning('when you press this button, general info will dissapear, so you have to run "Execute" buttom again', icon="⚠️")
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
                
        #----------------------------------------------------------------------------------------------
            

