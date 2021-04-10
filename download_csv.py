# -*- coding: utf-8 -*-
# @Author  : pengj    <ugeg@163.com>
# @Time    : 2019/6/24 23:58
# @File    : download_tushare.py
import os
import time

import pandas as pd
import tushare as ts

import utils.mysql_util

stock_index_file = "D:/QuantData/base/stock_base.csv"
daily_line_path = "D:/QuantData/day/"
download_start_date = "19940101"
pro = ts.pro_api("09bc9aa347e21a71a3c94fbcf0b6244276ff5dcc27e9e54328950d2c")
# mysql_engine = utils.mysql_util.MysqlConnector("localhost", "jing", "123456", "quant").create_engine()
mysql_connector = utils.mysql_connector
mysql_engine = mysql_connector.engine

def data_to_mysql(data: pd.DataFrame, table: str, engine):
    data.to_sql(table, engine, if_exists="append", index=False)


def download_stock_index():
    # data = pro.query('stock_basic', exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
    data = pro.query('stock_basic', exchange='', list_status='L',
                     fields='ts_code,symbol,name,area,industry,fullname,enname,market,exchange,curr_type,list_status,list_date,delist_date,is_hs')
    data.to_csv(stock_index_file, encoding='gbk', index=False)
    # data.to_sql()


def read_index_file_and_download():
    if not os.path.exists(stock_index_file):
        download_stock_index()
    index_data = pd.read_csv(stock_index_file, index_col='symbol', encoding='gbk', header=0)
    code_num = len(index_data['ts_code'])
    for i, code in enumerate(index_data['ts_code']):
        print(i + 1, "/", code_num, code)
        download_daily_data(code, daily_line_path, download_start_date)


def download_daily_data(code, path, start_date=None):
    file_name = path + code + ".csv"
    if not os.path.exists(file_name):
        while 1:
            try:
                df: pd.DataFrame = pro.daily(ts_code=code, start_date=start_date)
                df.to_csv(path + code + ".csv", encoding='gbk', index=False)
                # data_to_mysql(df, "daily", mysql_engine)
                break
            except Exception as e:
                print("超时")
                time.sleep(10)
        time.sleep(0.2)


def create_dir_if_not_exist():
    stock_index_dir = os.path.dirname(stock_index_file)
    if not os.path.exists(stock_index_dir):
        os.mkdir(stock_index_dir)
    if not os.path.exists(daily_line_path):
        os.mkdir(daily_line_path)


if __name__ == '__main__':
    # data = pro.query('stock_basic', exchange='', list_status='L',
    #                  fields='ts_code,symbol,name,area,industry,fullname,enname,market,exchange,curr_type,list_status,list_date,delist_date,is_hs')
    # mysql_util = utils.mysql_util.mysql_util("localhost", "jing", "123456", "quant")
    # data_to_mysql(data,"stock_basic", mysql_util.create_engine())
    create_dir_if_not_exist()
    read_index_file_and_download()
    print("下载结束")
