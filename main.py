# -*- coding: utf-8 -*-
"""
Created on Wed Apr 21 08:08:49 2021

@author: visha
"""

import streamlit as st
import pybase64
import pandas as pd
from nsepy import get_history
from prophet import Prophet
from prophet.plot import plot_plotly
from plotly import graph_objs as go
from datetime import date

start = "2016-01-01"
today = date.today().strftime("%Y-%m-%d")

bg_image = '''
<style>
.reportview-container{
background: url("https://unsplash.com/photos/R401qwThw7w")     
}
</style>
'''
st.markdown(bg_image,unsafe_allow_html=True)
st.title("Stock Price Predictor Web App")

stock_df = pd.read_csv(r"C:\Users\visha\Downloads\EQUITY_L.csv")
for index,row in stock_df.iterrows():
    if int(row[' DATE OF LISTING'][-4:])>2015:
        stock_df = stock_df.drop(index)
stock_df = stock_df[['SYMBOL','NAME OF COMPANY']]
company_names = list(stock_df['NAME OF COMPANY'])
tickers = list(stock_df['SYMBOL'])
stock_dict = {}
for i in range(len(company_names)):
    stock_dict[company_names[i]] = tickers[i]

selected_ticker = st.selectbox("Select a stock to predict its trend",tickers)

n = st.slider("Select number of years to predict", 1, 4)
period = n * 365

@st.cache
def load_data(tick):
    data = get_history(symbol=tick,start=date(2016,1,1),end=date(2021,4,21))
    data.to_csv('stock.csv')
    data = pd.read_csv('stock.csv')
    return data

data_load_state = st.text("Loading data...PLEASE WAIT")
data = load_data(selected_ticker)
data_load_state.text("Loading data.....DONE!")

st.subheader("Raw Data - "+ selected_ticker)
st.write(data.tail())

def plot_raw_data():
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['Date'],y=data['Open'],name="stock_open"))
    fig.add_trace(go.Scatter(x=data['Date'],y=data['Close'],name="stock_close"))
    fig.layout.update(title_text='Time Series data with Range Slider', xaxis_rangeslider_visible=True)
    st.plotly_chart(fig)

plot_load_state = st.text("Plotting graph....PLEASE WAIT")    
plot_raw_data()
plot_load_state.text("Plotting graph....DONE!")

#PREDICTION
predict_load_state = st.text("PREDICTING STOCK PRICE.....Please Wait")
train_data = data[['Date','Close']]
train_data = train_data.rename(columns={'Date':'ds','Close':'y'})
m = Prophet()
m.fit(train_data)
future = m.make_future_dataframe(periods=period)
forecast = m.predict(future)

st.subheader('Predicted Stock Price for '+selected_ticker)
st.write(forecast.tail(5))
predict_load_state.text("PREDICTION DONE!")

plot2_load_state = st.text("Plotting FORECAST chart....Please Wait")
st.subheader(f'Forecast plot for {n} years')
fig1 = plot_plotly(m, forecast)
st.plotly_chart(fig1)
plot2_load_state.text("Forecast Chart Plotted....Plotting Foreecast Components....")

st.subheader('Forecast Components')
fig2 = m.plot_components(forecast)
st.write(fig2)
plot2_load_state.text("Forecast Components Plotted!")
    