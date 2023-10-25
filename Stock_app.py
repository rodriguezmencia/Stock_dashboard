#------------------------------
#------import libraries--------
#------------------------------
import streamlit as st
import pandas as pd
#import sqlite3
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
    symbol = st.text_input('Stock symbol', 'e.g.AAPL')
    inter=st.selectbox('Enter the interval of time:',
    ('1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo'))
    init = st.date_input("Enter the start date [YYYY-MM-DD]:", ) #datetime.date(2019, 7, 6)
    finish=st.date_input("Enter the finish date [YYYY-MM-DD]:", )#datetime.date(2019, 7, 6)
    submit_code = st.form_submit_button(label ="Execute")

#main page
# title
st.subheader("Stock Analytics")
st.markdown("""---""")

# plot
if submit_code:
    if symbol:
        stock=yf.Ticker(symbol)
        df=stock.history(interval=inter, start=init, end=finish)
        st.write(df)
        
        # Calculate the 30/15/5-period moving average
        df['MA_30'] = df['Close'].rolling(window=30).mean()
        df['MA_15'] = df['Close'].rolling(window=15).mean()
        df['MA_5'] = df['Close'].rolling(window=5).mean()

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
    
        # Add the 30-period moving average line
        fig.add_trace(go.Scatter(x=df.index, y=df['MA_30'], line=dict(color='red', width=1), name='MA 30'),
                      row=1, col=1)
        
        # Add the 15-period moving average line
        fig.add_trace(go.Scatter(x=df.index, y=df['MA_15'], line=dict(color='purple', width=1), name='MA 15'),
                      row=1, col=1)
        
        # Add the 5-period moving average line
        fig.add_trace(go.Scatter(x=df.index, y=df['MA_5'], line=dict(color='blue', width=1), name='MA 5'),
                      row=1, col=1)
        
        fig.add_trace(go.Bar(x=df.index,
                             y=df['Volume'],
                             marker_color='blue'), row=2, col=1)
        
        fig.update_layout(
            title=symbol,
            xaxis_rangeslider_visible=False,
            showlegend=False)
        
        fig.update_yaxes(title_text="stock price", row=1, col=1)
        fig.update_yaxes(title_text="volumen", row=2, col=1)
        fig.update_xaxes(title_text='Date', row=2, col=1)
        
        # hide weekends without transactions
        fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"])])
        
        
        fig.show()
        
        
        # In[11]:
        
        
        from datetime import datetime
        import time
        
        
        # In[12]:
        
        
        ##Current price
        print(datetime.now())
        display(stock.history(period='1d'))
        time.sleep(60)
        print(datetime.now())
        display(stock.history(period='1d'))
        
        
        # In[ ]:
        
        
        #Major stakeholders
        stock.institutional_holders
        
        
        
        stock.mutualfund_holders
        
        
        stock.dividends.tail()
        
        
        # ### SQLite
        
        # In[ ]:
        
        
        # create a sql connection <---sólo 1 vez
        con = sqlite3.connect('stock.db')
        c = con.cursor()
        # create price table
        query1 = """CREATE TABLE IF NOT EXISTS prices (
        Date TEXT NOT NULL,
        ticker TEXT NOT NULL,
        price REAL,
        PRIMARY KEY(Date, ticker)
        )"""
        c.execute(query1.replace('\n',' '))
        # create volume table
        query2 = """CREATE TABLE IF NOT EXISTS volume (
        Date TEXT NOT NULL,
        ticker TEXT NOT NULL,
        volume REAL,
        PRIMARY KEY(Date, ticker)
        )"""
        c.execute(query2.replace('\n',' '))
        
        
        # In[ ]:
        
        
        #adjuntar información en sqlite
        adj_close_long.to_sql('prices', con, if_exists='append', index=False)
        volume_long.to_sql('volume', con, if_exists='append', index=False)
        
        
        # In[ ]:
        
        
        #borrar información de sqlite después del uso
        
        
        # In[ ]:
        
        
        #hacer una consulta en sqlite
        
        # backtest inputs
        bt_inputs = {'tickers': ['BA', 'UNH', 'MCD', 'HD'],
        'start_date': '2019-01-01',
        'end_date': '2021-06-01'}
            
        # create a sql connection
        con = sqlite3.connect('stock.db')
        c = con.cursor()
        # create price table
        query1 = """CREATE TABLE IF NOT EXISTS prices (
        Date TEXT NOT NULL,
        ticker TEXT NOT NULL,
        price REAL,
        PRIMARY KEY(Date, ticker)
        )"""
        c.execute(query1.replace('\n',' '))
        # create volume table
        query2 = """CREATE TABLE IF NOT EXISTS volume (
        Date TEXT NOT NULL,
        ticker TEXT NOT NULL,
        volume REAL,
        PRIMARY KEY(Date, ticker)
        )"""
        c.execute(query2.replace('\n',' '))
    
        def download(bt_inputs, proxy = None):
            data = yf.download(tickers= bt_inputs['tickers'],
                               start = bt_inputs['start_date'],   
                               end = bt_inputs['end_date'],
                               interval = '1d',
                               prepost = True,
                               threads = True,
                               proxy = proxy)
            return data
        
        test = download(bt_inputs)
        
        
        adj_close = test['Adj Close']
        volume = test['Volume']
        
        
        # convert wide to long
        adj_close_long = pd.melt(adj_close.reset_index(), id_vars='Date',
                                 value_vars=bt_inputs['tickers'], var_name ="ticker", value_name="price")
        volume_long = pd.melt(volume.reset_index(), id_vars='Date', value_vars=bt_inputs['tickers'],
                              var_name = "ticker", value_name = "volume")
        
        
        
        adj_close_long.to_sql('prices', con, if_exists='append', index=False)
        volume_long.to_sql('volume', con, if_exists='append', index=False)
        
    
