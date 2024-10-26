import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from tvdatafeed.tvDatafeed.main import *
from statsmodels.tsa.stattools import grangercausalitytests

# ------------------------------------------------------------------------------ #
# Granger Causality test
def granger_causality_test(data_1, data_2, maxlag: int=10):
    df_1 = data_1.copy()
    df_2 = data_2.copy()
    bars = pd.DataFrame()

    df_1['percent_change'] = df_1.close.pct_change()
    df_2['percent_change'] = df_2.close.pct_change()
    bars = pd.concat([bars, df_1, df_2]).reset_index()
    bars['datetime'] = bars.datetime.dt.date
    bars = bars.set_index('datetime')
    df_test = bars.pivot_table(values='percent_change', index='datetime', columns='symbol').dropna()
    df_granger = grangercausalitytests(df_test[[df_1.symbol.unique()[0], df_2.symbol.unique()[0]]], maxlag=[maxlag])
    df_granger = df_granger[maxlag][0]['ssr_ftest'][1]
    return df_granger

# ------------------------------------------------------------------------------ #
# Import Data
USERNAME = 'tradingpro.112233@gmail.com'
PASSWORD = 'Vuatrochoi123'
tv = TvDatafeed(USERNAME, PASSWORD)

data_input = {
    'Yếu tố': ['TPCP Mỹ 10 năm', 'TPCP VN 10 năm', 'Chỉ số US', 'Chỉ số S&P500', 'LS liên ngân hàng VN'],
    'symbol' : ['US10Y', 'VN10Y', 'DXY', 'SPX', 'VNINBR'],
    'exchange' : ['TVC', 'TVC', 'TVC', 'SP', 'ECONOMICS']
}

# VNINDEX index data
df_vnindex = tv.get_hist(symbol='VNINDEX', exchange='HOSE', interval=Interval.in_daily, n_bars=20000)
df_vnindex.index = df_vnindex.index.normalize()

# Factors data
symbol = data_input['symbol']
exchange = data_input['exchange']
factor_data = {}
for i in range(0, len(symbol)):
    df_temp = tv.get_hist(symbol=symbol[i], exchange=exchange[i], interval=Interval.in_daily, n_bars=20000)
    df_temp.index = df_temp.index.normalize()
    factor_data[symbol[i]] = df_temp

# ------------------------------------------------------------------------------ #
# Calculation
correlation, granger, status = [], [], []
coefficient = [''] * len(symbol)
corr_length = 30
back = 5
for i in range(0, len(symbol)):
    df_corr = pd.concat([df_vnindex.close, factor_data[symbol[i]].close], axis=1)
    df_corr = df_corr.dropna()
    df_corr.columns = ['VNINDEX', symbol[i]]
    correlation.append((df_corr['VNINDEX'].rolling(corr_length).corr(df_corr[symbol[i]])).iloc[-1])
    granger.append(granger_causality_test(df_vnindex, factor_data[symbol[i]]))
    if ((factor_data[symbol[i]].close / factor_data[symbol[i]].close.shift(back) > 0.05).iloc[-1] and (correlation[i] > 0)) | \
          ((factor_data[symbol[i]].close / factor_data[symbol[i]].close.shift(back) < -0.05).iloc[-1] and (correlation[i] < 0)):
        status.append('Tích cực')
    elif ((factor_data[symbol[i]].close / factor_data[symbol[i]].close.shift(back) > 0.05).iloc[-1] and (correlation[i] < 0)) | \
          ((factor_data[symbol[i]].close / factor_data[symbol[i]].close.shift(back) < -0.05).iloc[-1] and (correlation[i] > 0)):
        status.append('Tiêu cực')
    else:
        status.append('Trung tính')

# ------------------------------------------------------------------------------ #
# def main():
st.title("WARNING MARKET SCREEN")
data = {
    "Yếu tố": data_input['Yếu tố'],
    "Hệ số tương quan": correlation,
    "Hệ số giải thích": coefficient,
    "Hệ số Granger": granger,
    "Trạng thái": status
}
df = pd.DataFrame(data)
st.dataframe(df.style)

# main()