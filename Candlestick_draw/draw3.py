# -*- coding: utf-8 -*-
# @Author  : pengj    <ugeg@163.com>
# @Time    : 2021/2/1 20:41
# @File    : draw3.py
import talib
import numpy as np
import tushare as ts
from pyecharts.charts  import Grid, Bar, Line, Kline, Overlap

# data = ts.get_k_data('399300', index=True, start='2017-01-01', end='2017-06-31')
# ochl = data[['open', 'close', 'high', 'low']]
# ochl_tolist = [ochl.ix[i].tolist() for i in range(len(ochl))]
#
# sma_10 = talib.SMA(np.array(data['close']), 10)
# sma_30 = talib.SMA(np.array(data['close']), 30)
#
# kline = Kline()
# kline.add("日K", data['date'], ochl_tolist, is_datazoom_show=True)
#
# line = Line()
# line.add('10 日均线', data['date'], sma_10, is_fill=False, line_opacity=0.8, is_smooth=True)
# line.add('30 日均线', data['date'], sma_30, is_fill=False, line_opacity=0.8, is_smooth=True)
#
# overlap = Overlap()
# overlap.add(kline)
# overlap.add(line)
# overlap
