# -*- coding: utf-8 -*-
# @Author  : pengj    <ugeg@163.com>
# @Time    : 2019/6/25 22:25
# @File    : read_stock_data.py
import pandas as pd
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
import mpl_finance
import mplfinance
register_matplotlib_converters()
data_path = r"D:/QuantData/"


def read_data_and_show(stock_name):
    code_str = name2code(stock_name)
    stock_data = pd.read_csv(data_path + "\\day\\" + code_str + '.csv', encoding='gbk', parse_dates=['trade_date'],
                             index_col='trade_date')
    # stock_data = pd.read_csv(data_path + "\\day\\" + code_str + '.csv', encoding='gbk')
    # fig, ax = plt.subplots(figsize=(10,5))
    # mpl_finance.candlestick_ochl(ax=ax,
    #                              quotes=stock_data[['trade_date', 'open', 'close', 'high', 'low']].values,
    #                              width=0.7,
    #                              colorup='r',
    #                              colordown='g',
    #                              alpha=0.7)
    # ax.xaxis_date()
    # plt.xticks(rotation=30);
    print(stock_data.head())
    plt.plot(stock_data['close'])
    plt.show()


def name2code(stock_name):
    code_df = pd.read_csv(data_path + r"\base\stock_base.csv", encoding='gbk')
    # print(code_df.head())
    code = code_df[code_df['name'] == stock_name]["ts_code"]
    code_str = code[code.index[0]]
    return code_str


if __name__ == "__main__":
    temp_stock_name = "中兴通讯"
    read_data_and_show(temp_stock_name)
