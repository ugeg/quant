import tushare as ts
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import mpl_finance as mpf
# import seaborn as sns
import talib as tl



df_300427  = ts.get_hist_data('300427',start='2018-04-01',end='2019-07-01')


fig = plt.figure(figsize=(24, 8))
ax = fig.add_subplot(1, 1, 1)
ax.set_xticks(range(0, len(df_300427.index), 10))
ax.set_xticklabels(df_300427.index[::10])
mpf.candlestick2_ochl(ax, df_300427['open'], df_300427['close'], df_300427['high'],
                      df_300427['low'], width=0.6, colorup='r', colordown='g', alpha=0.75);

#加均线
sma_10 = tl.SMA(np.array(df_300427['close']), 10)
sma_30 = tl.SMA(np.array(df_300427['close']), 30)

fig = plt.figure(figsize=(24, 8))
ax = fig.add_subplot(1, 1, 1)
ax.set_xticks(range(0, len(df_300427.index), 10))
ax.set_xticklabels(df_300427.index[::10])
mpf.candlestick2_ochl(ax, df_300427['open'], df_300427['close'], df_300427['high'],
                      df_300427['low'], width=0.6, colorup='r', colordown='g', alpha=0.75)
plt.rcParams['font.sans-serif']=['Microsoft JhengHei']
ax.plot(sma_10, label='10日均线')
ax.plot(sma_30, label='30日均线')
ax.legend();

#加成交量
sma_10 = tl.SMA(np.array(df_300427['close']), 10)
sma_30 = tl.SMA(np.array(df_300427['close']), 30)

fig = plt.figure(figsize=(24, 15))
ax = fig.add_axes([0,0.2,1,0.5])
ax2 = fig.add_axes([0,0,1,0.2])

ax.set_xticks(range(0, len(df_300427.index), 10))
ax.set_xticklabels(df_300427.index[::10])
mpf.candlestick2_ochl(ax, df_300427['open'], df_300427['close'], df_300427['high'],
                      df_300427['low'], width=0.6, colorup='r', colordown='g', alpha=0.75)
plt.rcParams['font.sans-serif']=['Microsoft JhengHei']
ax.plot(sma_10, label='10日均线')
ax.plot(sma_30, label='30日均线')

mpf.volume_overlay(ax2, df_300427['open'], df_300427['close'], df_300427['volume'], colorup='r', colordown='g', width=0.5, alpha=0.8)
ax2.set_xticks(range(0, len(df_300427.index), 10))
ax2.set_xticklabels(df_300427.index[::10])

ax.legend();

#加上kd值

sma_10 = tl.SMA(np.array(df_300427['close']), 10)
sma_30 = tl.SMA(np.array(df_300427['close']), 30)
df_300427['k'], df_300427['d'] = tl.STOCH(df_300427['high'], df_300427['low'], df_300427['close'])
df_300427['k'].fillna(value=0, inplace=True)
df_300427['d'].fillna(value=0, inplace=True)

fig = plt.figure(figsize=(24, 20))
ax = fig.add_axes([0,0.3,1,0.4])
ax2 = fig.add_axes([0,0.2,1,0.1])
ax3 = fig.add_axes([0,0,1,0.2])

ax.set_xticks(range(0, len(df_300427.index), 10))
ax.set_xticklabels(df_300427.index[::10])
mpf.candlestick2_ochl(ax, df_300427['open'], df_300427['close'], df_300427['high'],
                      df_300427['low'], width=0.6, colorup='r', colordown='g', alpha=0.75)
plt.rcParams['font.sans-serif']=['Microsoft JhengHei']
ax.plot(sma_10, label='10日均线')
ax.plot(sma_30, label='30日均线')

ax2.plot(df_300427['k'], label='K值')
ax2.plot(df_300427['d'], label='D值')
ax2.set_xticks(range(0, len(df_300427.index), 10))
ax2.set_xticklabels(df_300427.index[::10])

mpf.volume_overlay(ax3, df_300427['open'], df_300427['close'], df_300427['volume'], colorup='r', colordown='g', width=0.5, alpha=0.8)
ax3.set_xticks(range(0, len(df_300427.index), 10))
ax3.set_xticklabels(df_300427.index[::10])

ax.legend()
ax2.legend()

plt.show()