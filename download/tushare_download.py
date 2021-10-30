import datetime
import time

import tushare as ts
from sqlalchemy import func
from sqlalchemy.orm import Session

from utils.entity import Daily, StockBasic
import utils
from utils.logging_util import count_time

pro = ts.pro_api(utils.conf.tushare_token)
stock_basic_table = 'stock_basic'
daily_table_name = "daily"
mysql_connector = utils.mysql_connector
mysql_engine = mysql_connector.engine
session = Session(mysql_connector.engine, autocommit=True)


def download_stock_basic_to_mysql():  # 下载stock_basic到mysql
    # 查询本地stock_basic数据量
    local_stock_count = session.query(func.count(StockBasic.ts_code)).one()[0]
    print("local_stock_count:", local_stock_count)
    # 查询远程stock_basic数据量并保存到mysql
    base_data = pro.query(
        stock_basic_table, exchange='', list_status='L',
        fields='ts_code,symbol,name,area,industry,fullname,enname,market,exchange,curr_type,list_status,list_date,delist_date,is_hs')
    remote_stock_count = len(base_data.index)
    print("remote_stock_count:", remote_stock_count)
    if local_stock_count != len(base_data.index):
        print("stock_basic save to mysql")
        mysql_connector.truncate(stock_basic_table)
        base_data.to_sql(stock_basic_table, mysql_engine, if_exists="append", index=False)
        # stock_basic_df.to_csv("D:/QuantData/base/stock_base.csv", encoding='gbk', index=False)


def get_daily(ts_code='', trade_date='', start_date='', end_date=''):
    while 1:
        try:
            if trade_date:
                df = pro.daily(ts_code=ts_code, trade_date=trade_date)
            else:
                df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        except Exception as e:
            print(e)
            if e.args[0] == "type object 'object' has no attribute 'dtype'":
                print("no more data")
                break
            print("ERROR: download daily data timeout")
            time.sleep(1)
        else:
            return df


@count_time
def download_daily_by_day():
    start_day = session.query(func.max(Daily.trade_date)).scalar()
    if start_day:
        start_day = (datetime.datetime.strptime(start_day, "%Y%m%d") + datetime.timedelta(days=1)).strftime("%Y%m%d")
    else:
        start_day = '19940101'
    current_time = datetime.datetime.now()
    if current_time.hour > 15:
        current_day = current_time.strftime("%Y%m%d")
    else:
        current_day = (current_time + datetime.timedelta(days=-1)).strftime("%Y%m%d")
    df = pro.trade_cal(exchange='SSE', is_open='1', start_date=start_day, end_date=current_day, fields='cal_date')
    download_day_count = len(df.index)
    for i, date in enumerate(df['cal_date']):
        daily_data_df = get_daily(trade_date=date)
        daily_data_df.to_sql(daily_table_name, mysql_engine, if_exists="append", index=False)
        print("Downloading daily data:", date, "count:", len(daily_data_df.index), "\tcurrent progress:[", i + 1, "/",
              download_day_count, "]", (i + 1) * 100 // download_day_count, "%")


if __name__ == '__main__':
    print("Downloading start.", datetime.datetime.now())
    download_stock_basic_to_mysql()
    # download_daily_by_day()
