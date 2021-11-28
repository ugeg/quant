import datetime
import time

import tushare as ts
from sqlalchemy import func
from utils.entity import Daily
import utils
from utils.logging_util import count_time
from utils.global_operator import save
pro = ts.pro_api(utils.conf.tushare_token)
mysql_connector = utils.mysql_connector
session = utils.session


@count_time
def download_basic_to_mysql(basic_type):
    mysql_connector.truncate(basic_type)
    print("download", basic_type, "and save to mysql")
    if basic_type == 'index_basic':
        market_dict = {'MSCI': 'MSCI指数', 'CSI': '中证指数', 'SSE': '上交所指数', 'SZSE': '深交所指数', 'CICC': '中金指数', 'SW': '申万指数',
                       'OTH': '其他指数'}
        for market in market_dict.keys():
            print("download index_basic for market", market)
            df = pro.index_basic(market=market,
                                 fields=["ts_code", "name", "market", "publisher", "category", "base_date",
                                         "base_point", "list_date", "index_type", "fullname", "weight_rule", "desc",
                                         "exp_date"])
            save(df, basic_type)
    elif basic_type == 'stock_basic':
        df = pro.stock_basic(
            fields=["ts_code", "symbol", "name", "area", "industry", "market", "list_date", "fullname", "enname",
                    "cnspell", "exchange", "curr_type", "list_status", "delist_date", "is_hs"])
        save(df, basic_type)


@count_time
def download_index_daily_to_mysql():
    table = "index_daily"
    mysql_connector.truncate(table)
    index_dict = {'000001.SH': '上证指数', '000016.SH': '上证50', '000300.SH': '沪深300', '000688.SH': '科创50',
                  '399001.SZ': '深证成指',
                  '399006.SZ': '创业板指'}
    for k in index_dict.keys():
        print("download ", index_dict[k])
        df = pro.index_daily(ts_code=k, start_date='19940101',
                             fields=["ts_code", "trade_date", "close", "open", "high", "low", "pre_close", "change",
                                     "pct_chg", "vol", "amount"])
        save(df, table)


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
def download_stock_daily_delta():
    daily_table_name = "daily"
    # start_day = session.execute('select max(trade_date) as trade_date from daily').scalar()
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
        save(daily_data_df, daily_table_name)
        print("Downloading stock daily data:", date, "count:", len(daily_data_df.index), "\tcurrent progress:[", i + 1, "/",
              download_day_count, "]", (i + 1) * 100 // download_day_count, "%")


if __name__ == '__main__':
    download_basic_to_mysql('stock_basic')
    # download_basic_to_mysql('index_basic')
    # download_index_daily_to_mysql()
    download_stock_daily_delta()
