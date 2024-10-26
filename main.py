import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from tvdatafeed.tvDatafeed.main import *
from statsmodels.tsa.stattools import grangercausalitytests
import plotly.subplots as ms

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
    'Yếu tố': ['TPCP Mỹ 10 năm', 'TPCP VN 10 năm', 'Chỉ số USD', 'Chỉ số S&P500', 'LS liên ngân hàng VN'],
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
data = {
    "Yếu tố": data_input['Yếu tố'],
    "Hệ số tương quan": correlation,
    "Hệ số giải thích": coefficient,
    "Hệ số Granger": granger,
    "Trạng thái": status
}
df = pd.DataFrame(data)

st.title("WARNING MARKET SCREEN")

st.header('Biểu đồ nến chỉ số VNINDEX')
fig_vnindex = ms.make_subplots(rows=1, cols=1)
fig_vnindex.add_trace(go.Candlestick(x=df_vnindex.index, open=df_vnindex['open'], high=df_vnindex.high, low=df_vnindex.low, close=df_vnindex.close), row=1, col=1)
fig_vnindex.update_yaxes(fixedrange=False)
fig_vnindex.update_layout(xaxis_rangeslider_visible=False,
                            xaxis_range=['2022-01-01','2024-12-31'])
st.plotly_chart(fig_vnindex)

for i in range(0, len(symbol)):
    st.header(f'Biểu đồ nến {data_input["Yếu tố"][i]}')
    fig_i = ms.make_subplots(rows=1, cols=1)
    fig_i.add_trace(go.Candlestick(x=factor_data[symbol[i]].index, open=factor_data[symbol[i]]['open'], high=factor_data[symbol[i]].high, low=factor_data[symbol[i]].low, close=factor_data[symbol[i]].close), row=1, col=1)
    fig_i.update_yaxes(fixedrange=False)
    fig_i.update_layout(xaxis_rangeslider_visible=False,
                        xaxis_range=['2022-01-01','2024-12-31'])
    st.plotly_chart(fig_i)

st.header("Bảng thông tin")
st.dataframe(df.style)

# main()