import datetime
import re

import pandas as pd
from pandas import DataFrame

import utils

code2name: dict = None
name2code: dict = None


def load_code2name(session):
    global code2name
    global name2code
    if name2code is None:
        try:
            result = session.execute('select ts_code,name from stock_basic').fetchall()
            code2name = dict([(a, b) for a, b in result])
            name2code = dict([(b, a) for a, b in result])
            print("code2name加载完成")
        except Exception as e:
            print(e)

def format_stock_code(src: str, format_type='tushare'):
    type_list = ['tushare', 'sina', 'name', 'code']
    if format_type not in type_list:
        raise Exception("not support type:", format_type)
    if re.match("s[h|z]\d{6}", src):
        market = src[:2].lower()
        code = src[2:]
    elif re.match("\d{6}\\.[A-Z]+", src):
        market = src[7:].lower()
        code = src[:6]
    elif len(src) == 6:
        market = 'sh' if src[0] == 6 else 'sz'
        code = src
    else:
        src = utils.global_operator.name2code[src]
        return format_stock_code(src, format_type)
    if format_type == 'code':
        return code
    elif format_type == 'sina':
        return market.lower() + code
    elif format_type == 'tushare':
        return code + '.' + market.upper()
    else:
        return utils.global_operator.code2name[code]


def save(df: DataFrame, table_name, db_type='mysql'):
    if db_type == 'mysql':
        try:
            print(datetime.datetime.now(), "save", len(df.index), "record to ", table_name)
            df.to_sql(table_name, utils.mysql_engine, if_exists="append", index=False, method=utils.mysql_util.mysql_replace_into)
        except Exception as e:
            print(e)
    else:
        print("Method [save] not implement! Please check")


def read(query_sql: str):
    # return pd.read_sql_query(query_sql, utils.mysql_engine, parse_dates={"trade_date": "%Y%m%d"},index_col="trade_date")
    return pd.read_sql_query(query_sql, utils.mysql_engine)

def get_last_trade_date(date:str=None):
    sql = "SELECT max(cal_date) FROM trade_cal WHERE cal_date<=DATE_FORMAT(CURDATE(),'%Y%m%d') and is_open=1"
    if date:
        sql = sql+" AND cal_date<="+date
    df = pd.read_sql_query(sql,utils.mysql_engine)
    return df.iloc[0,0]
def get_code_list(date='20220222'):
    # 默认2010年开始回测
    dd = read("SELECT * FROM `daily_basic` WHERE trade_date='{}'".format(date))
    # 收盘价小于100
    x1 = dd.close < 100
    # 流通市值低于300亿大于50亿
    x2 = dd.circ_mv > 500000
    x3 = dd.circ_mv < 3000000
    # 市盈率低于80
    x4 = dd.pe_ttm < 80
    # 股息率大于2%
    x5 = dd.dv_ttm > 3
    # 换手率大于1
    x6 = dd.turnover_rate_f>1
    x = x1 & x2 & x3 & x4 & x5 & x6
    stock_list = dd[x].ts_code.values
    return stock_list


if __name__ == '__main__':
    print(get_last_trade_date())