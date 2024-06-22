import datetime
import sys
import time
import traceback

import akshare as ak
import pandas as pd
import sqlalchemy
from sqlalchemy import text
from sqlalchemy.orm import Session

import utils
from utils.logging_util import logger

mysql_config = utils.mysql_config
mysql_url_template = "mysql+pymysql://{}:{}@{}:{}/{}"
sqlalchemy_url = mysql_url_template.format(mysql_config.user, mysql_config.passwd, mysql_config.ip, mysql_config.port,
                                           mysql_config.db)
engine: sqlalchemy.engine.Engine = sqlalchemy.create_engine(sqlalchemy_url, echo=False)


def index_stock_info():
    """
    所有指数 index_code display_name publish_date
    """
    df = ak.index_stock_info()
    df.to_sql('index_stock_info', engine, if_exists='replace', index=False)


def stock_zh_index_daily_em(symbol: str = "sh000001"):
    """
    指数日k
    上证sh000001 深成sz399001
    """
    stock_zh_index_daily_em_df = ak.stock_zh_index_daily_em(symbol=symbol)
    stock_zh_index_daily_em_df["symbol"] = symbol
    with Session(engine) as session:
        session.execute(text("truncate table stock_zh_index_daily_em"))
        session.commit()
    stock_zh_index_daily_em_df.to_sql('stock_zh_index_daily_em', engine, if_exists='append', index=False)
    logger.info("保存指数日k数据")


def get_trade_date_list():
    with Session(engine) as session:
        result_list = session.execute(
            text("select `date` from stock_zh_index_daily_em where symbol='sh000001' order by `date`")).fetchall()
        if len(result_list) == 0:
            raise Exception("未获取到数据")
        return [result[0] for result in result_list]


def get_max_trade_date_time():
    with Session(engine) as session:
        result_list = session.execute(
            text("select max(`date`) from stock_zh_index_daily_em where symbol='sh000001'")).fetchall()
        if len(result_list) == 0:
            raise Exception("未获取到数据")
        return str(result_list[0][0]) + " 15:00:00"


def stock_zh_a_spot_em():
    """所有沪深京 A 股上市公司的实时行情数据"""
    stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
    stock_zh_a_spot_em_df.drop(columns=["序号"], inplace=True)
    with Session(engine) as session:
        session.execute(text("truncate table stock_zh_a_spot_em"))
        session.commit()
    stock_zh_a_spot_em_df.to_sql('stock_zh_a_spot_em', engine, if_exists='append', index=False)
    logger.info("保存沪深京 A 股上市公司的实时行情数据")


def get_stock_list():
    with Session(engine) as session:
        result_list = session.execute(
            text("select `代码` from stock_zh_a_spot_em where 最新价 is not null")).fetchall()
        if len(result_list) == 0:
            raise Exception("未获取到数据")
        return [result[0] for result in result_list]


def stock_zh_a_hist(symbol: str = "000001", period: str = "daily", start_date: str = "20140101", adjust: str = "hfq"):
    current_date = datetime.datetime.now().strftime('%Y%m%d')
    stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol, period=period, start_date=start_date, end_date=current_date,
                                            adjust=adjust)
    stock_zh_a_hist_df.to_sql('stock_zh_a_hist', engine, if_exists='append', index=False)
    logger.info(f"symbol:{symbol} start_date:{start_date} records:{stock_zh_a_hist_df.shape[0]} 下载完成")


def get_all_daily_data():
    stock_list = get_stock_list()
    current_date = get_trade_date_list()[-1]
    with Session(engine) as session:
        max_date_dict = {record[0]: record[1] for record in
                         session.execute(text("select `股票代码`,max(`日期`) from stock_zh_a_hist group by `股票代码`")).fetchall()}
        for index, stock in enumerate(stock_list):
            # 查询该代码在数据库中的最新日期
            max_date = max_date_dict.get(stock)
            while True:
                try:
                    if max_date:
                        if max_date == current_date:
                            print(f"{stock} 数据已最新，跳过")
                            break
                        # 加一天
                        star_date = max_date + datetime.timedelta(days=1)
                        stock_zh_a_hist(stock, start_date=star_date.strftime("%Y%m%d"))
                    else:
                        stock_zh_a_hist(stock)
                    session.commit()
                    logger.info(f"{stock} 下载完成。总进度{index + 1}/{len(stock_list)} ")
                    # time.sleep(0.01)
                    break
                except Exception as e:
                    traceback.print_exc()
                    time.sleep(10)


def get_all_stock_minute_data(period="1", adjust: str = "hfq"):
    logger.info(f"get_all_stock_minute_data(period={period})")
    """
    获取所有股票分钟数据，只能获取到最近7个交易日的
    '1', '5', '15', '30', '60'
    """
    max_trade_date_time = get_max_trade_date_time()
    stock_list = get_stock_list()
    with Session(engine) as session:
        max_day_dict = {record[0]: record[1] for record in session.execute(
            text(f"select symbol,max(`day`) from stock_zh_{period}_minute group by symbol order by symbol")).fetchall()}
        for index, symbol in enumerate(stock_list):
            # 查询该代码在数据库中的最新日期
            max_day = max_day_dict.get(symbol)
            if max_day is not None and max_day.strftime("%Y-%m-%d %H:%M:%S") == max_trade_date_time:
                logger.info(f"symbol:{symbol}已最新，跳过")
                continue
            # 上交所主板 60 深交所主板 00 深交所创业板 30 上交所科创板68 北交所基础层 43 创新层 83、精选层 87、新上北交所 88,92
            if symbol[0] in ["0", "3"]:
                query_symbol = "sz" + symbol
            elif symbol[0] in ["6"]:
                query_symbol = "sh" + symbol
            elif symbol[0] in ["4", "8","9"]:
                query_symbol = "bj" + symbol
            else:
                raise NotImplementedError("未处理的代码：" + symbol)
            while True:
                try:
                    df = ak.stock_zh_a_minute(query_symbol, period=period, adjust=adjust)
                    if max_day:
                        df['day'] = pd.to_datetime(df['day'])
                        # 筛选day大于max_day的数据,防止写入报错
                        df = df[df["day"] > max_day]
                    df["symbol"] = symbol
                    df.to_sql(f'stock_zh_{period}_minute', engine, if_exists='append', index=False)
                    logger.info(f"symbol:{symbol} records:{df.shape[0]}下载完成。总进度{index + 1}/{len(stock_list)}")
                    break
                except Exception as e:
                    traceback.print_exc()
                    logger.error(e)
                    time.sleep(60)


if __name__ == '__main__':
    # # 获取上证指数历史数据（用于判断是否交易日）
    stock_zh_index_daily_em()
    # # 获取所有股票代码
    stock_zh_a_spot_em()
    # # 获取所有股票日k数据
    get_all_daily_data()

    get_all_stock_minute_data("5")
    # get_all_stock_minute_data("15")
    # get_all_stock_minute_data("30")
    # get_all_stock_minute_data("60")
# stock_zh_index_daily_df = ak.stock_zh_index_daily()
# print(stock_zh_index_daily_df)
# stock_zh_a_tick_tx_df = ak.stock_zh_a_tick_tx(code="sh600848", trade_date="20191011")
# print(stock_zh_a_tick_tx_df)
#
# # 当前交易日的分时数据可以通过下接口获取
# stock_zh_a_tick_tx_js_df = ak.stock_zh_a_tick_tx_js(code="sz000001")
# print(stock_zh_a_tick_tx_js_df)

# 实时行情
# stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
# print(stock_zh_a_spot_em_df)
# 分红配送

# stock_fhps_em_df = ak.stock_fhps_em(date="20211231")
# print(stock_fhps_em_df)


# js_news_df = ak.js_news(timestamp="2022-12-08 21:57:18")
# print(js_news_df)
