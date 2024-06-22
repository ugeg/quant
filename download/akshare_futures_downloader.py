import logging
from datetime import datetime
import pandas as pd
import akshare as ak
from sqlalchemy import text
from sqlalchemy.orm import Session

from utils import mysql_engine
from utils.logging_util import logger


def futures_code_info():
    df_futures_code_info = ak.futures_display_main_sina()
    df_futures_code_info.to_sql('futures_code_info', mysql_engine, if_exists='replace', index=False)


def futures_main_sina():
    current_date = datetime.now().strftime('%Y%m%d')
    futures_code_info = pd.read_sql('select * from futures_code_info', mysql_engine)
    # 查询futures_main_sina表每个symbol的最大日期
    # max_date = pd.read_sql(text("select symbol,DATE_FORMAT(MAX(`日期`), '%Y-%m-%d') from futures_main_sina group by symbol"), mysql_engine)
    max_date = pd.read_sql(text("select symbol,MAX(`日期`) from futures_main_sina group by symbol"), mysql_engine)
    max_date_dict = {x[0]: x[1] for x in max_date.values}
    start_date = "20080101"
    code_count = len(futures_code_info)
    for index, row in futures_code_info.iterrows():
        symbol = row['symbol']
        futures_main_sina_hist = ak.futures_main_sina(symbol=symbol, start_date=start_date, end_date=current_date)
        # 筛选日期大于futures_main_sina表中最大日期的数据
        futures_main_sina_hist = futures_main_sina_hist[futures_main_sina_hist['日期'] > max_date_dict.get(symbol, datetime.strptime(start_date, '%Y%m%d').date())]
        if len(futures_main_sina_hist)==0:
            logger.info(f"{index + 1}/{code_count} {symbol} skip")
            continue
        futures_main_sina_hist.insert(0, 'symbol', symbol)
        futures_main_sina_hist.to_sql('futures_main_sina', mysql_engine, if_exists='append', index=False)
        logger.info(f"{index + 1}/{code_count} {symbol} download success,records:{len(futures_main_sina_hist)}")


def futures_zh_minute_sina():
    with Session(mysql_engine) as session:
        exchange_codes = session.execute(text("select `code` from exchange_info")).all()
        exchange_code_list = [x[0].lower() for x in exchange_codes if x[0] != 'INE']
        max_datetime = session.execute(text("select symbol,DATE_FORMAT(MAX(`datetime`), '%Y-%m-%d %H:%i:%s') from futures_zh_minute_sina group by symbol")).all()
        # 转为dict
        max_datetime_dict = {x[0]: x[1] for x in max_datetime}
    for exchange_code in exchange_code_list:
        futures_codes_str = ak.match_main_contract(symbol=exchange_code)
        futures_codes = futures_codes_str.split(",")
        for futures_code in futures_codes:
            futures_zh_minute_sina_df = ak.futures_zh_minute_sina(symbol=futures_code, period="1")
            # 筛选日期大于futures_zh_minute_sina表中最大日期的数据
            if max_datetime_dict.get(futures_code):
                futures_zh_minute_sina_df = futures_zh_minute_sina_df[futures_zh_minute_sina_df['datetime'] > max_datetime_dict[futures_code]]
            if len(futures_zh_minute_sina_df) == 0:
                logger.info(f"futures_zh_minute_sina:{exchange_code}\t{futures_code} skip")
                continue
            futures_zh_minute_sina_df.insert(0, 'symbol', futures_code)
            futures_zh_minute_sina_df.insert(1, 'exchange', exchange_code)
            futures_zh_minute_sina_df.to_sql('futures_zh_minute_sina', mysql_engine, if_exists='append', index=False)
            logger.info(f"futures_zh_minute_sina:{exchange_code}\t{futures_code} download success")


if __name__ == '__main__':
    futures_main_sina()
    futures_zh_minute_sina()
