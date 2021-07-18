# -*- coding: utf-8 -*-
# @Author  : pengj    <ugeg@163.com>
# @Time    : 2019/6/24 23:58
# @File    : download_tushare.py
import time

import pandas as pd
import tushare as ts
from sqlalchemy import func
from sqlalchemy.orm import Session

import utils.mysql_util
from utils import time_util
from utils.entity import Daily, StockBasic

download_start_date = 19940101
tushare_pro = ts.pro_api(utils.conf.tushare_token)
stock_basic_table = 'stock_basic'
daily_table_name = "daily"


def download_daily_data_to_mysql(ts_code, start_date=None):

    if start_date is not None:
        if start_date > time_util.date_to_str(time_util.get_latest_trading_day()):
            print(ts_code, "data is up to date,skip...")
            return
    while 1:
        try:
            df: pd.DataFrame = tushare_pro.daily(ts_code=ts_code, start_date=start_date)
            df.to_sql(daily_table_name, mysql_engine, if_exists="append", index=False)
            # df.to_csv("D:/QuantData/base/day/"+ts_code+".csv",encoding='gbk', index=False)
            break
        except Exception as e:
            print(e)
            if e.args[0] == "type object 'object' has no attribute 'dtype'":
                print("code:", ts_code, "\tno more data")
                break
            print("ERROR: download daily data timeout")
            time.sleep(3)
    time.sleep(0.2)


def stock_basic_save_to_mysql(stock_basic_df: pd.DataFrame, if_truncate: bool):  # 下载stock_basic到mysql
    if if_truncate:
        mysql_connector.truncate(stock_basic_table)
        stock_basic_df.to_sql(stock_basic_table, mysql_engine, if_exists="append", index=False)
        # stock_basic_df.to_csv("D:/QuantData/base/stock_base.csv", encoding='gbk', index=False)


if __name__ == '__main__':
    # mysql_config = utils.conf.mysql_config
    # mysql_util = utils.mysql_util.MysqlUtil(mysql_config.ip, mysql_config.user, mysql_config.passwd, mysql_config.db)
    mysql_connector = utils.mysql_connector
    mysql_engine = mysql_connector.engine
    session = Session(mysql_connector.engine, autocommit=True)
    print("Downloading start.")
    # 查询本地stock_basic数据量
    local_stock_count = session.query(func.count(StockBasic.ts_code)).one()[0]
    print("local_stock_count:", local_stock_count)
    # 查询远程stock_basic数据量并保存到mysql
    base_data = tushare_pro.query(
        stock_basic_table, exchange='', list_status='L',
        fields='ts_code,symbol,name,area,industry,fullname,enname,market,exchange,curr_type,list_status,list_date,delist_date,is_hs')
    remote_stock_count = len(base_data.index)
    print("remote_stock_count:", remote_stock_count)
    stock_basic_save_to_mysql(base_data, local_stock_count != len(base_data.index))
    # 查询本地数据库中每个股票已下载的最新日期
    max_date_list = session.query(Daily.ts_code, func.max(Daily.trade_date)).group_by(Daily.ts_code).all()
    max_date_dict = dict(max_date_list)
    for i, code in enumerate(base_data['ts_code']):
        start_time = int(max_date_dict[code]) + 1 if max_date_dict.get(code) is not None else download_start_date
        print("Downloading daily data: ", code, "start_date:", start_time, "\tcurrent progress:[", i + 1, "/",
              remote_stock_count, "]")
        download_daily_data_to_mysql(code, str(start_time))
    print("Downloading end.")
