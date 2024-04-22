import datetime
import sys
import time
import traceback

import akshare as ak
import sqlalchemy
from sqlalchemy import text
from sqlalchemy.orm import Session

import utils

mysql_config = utils.mysql_config
mysql_url_template = "mysql+pymysql://{}:{}@{}:{}/{}"
sqlalchemy_url = mysql_url_template.format(mysql_config.user, mysql_config.passwd, mysql_config.ip, mysql_config.port,
                                           mysql_config.db)
engine: sqlalchemy.engine.Engine = sqlalchemy.create_engine(sqlalchemy_url, echo=False)


def index_stock_info():
    """
    所有指数 index_code display_name publish_date
    """
    ak.index_stock_info().to_sql('index_stock_info', engine, if_exists='replace', index=False)


def stock_zh_index_daily_em(symbol: str = "sh000001"):
    """
    指数日k
    上证sh000001 深成sz399001
    """
    stock_zh_index_daily_em_df = ak.stock_zh_index_daily_em(symbol=symbol)
    stock_zh_index_daily_em_df["symbol"] = symbol
    stock_zh_index_daily_em_df.to_sql('stock_zh_index_daily_em', engine, if_exists='append', index=False)


def get_trade_date_list():
    with Session(engine) as session:
        result_list = session.execute(
            text("select `date` from stock_zh_index_daily_em where symbol='sh000001' order by `date` asc")).fetchall()
        if len(result_list) == 0:
            raise Exception("未获取到数据")
        return [result[0] for result in result_list]


def stock_zh_a_spot_em():
    """所有沪深京 A 股上市公司的实时行情数据"""
    stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
    stock_zh_a_spot_em_df.drop(columns=["序号"], inplace=True)
    stock_zh_a_spot_em_df.to_sql('stock_zh_a_spot_em', engine, if_exists='append', index=False)


def get_stock_list():
    with Session(engine) as session:
        result_list = session.execute(
            text("select `代码` from stock_zh_a_spot_em where 最新价 is not null")).fetchall()
        if len(result_list) == 0:
            raise Exception("未获取到数据")
        return [result[0] for result in result_list]

def stock_zh_a_hist(symbol: str = "000001", period: str = "daily", start_date: str = "20140101", adjust: str = "hfq"):
    current_date = datetime.datetime.now().strftime('%Y%m%d')
    stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol, period=period, start_date=start_date, end_date=current_date, adjust=adjust)
    stock_zh_a_hist_df["代码"] = symbol
    stock_zh_a_hist_df.to_sql('stock_zh_a_hist', engine, if_exists='append', index=False)
    print(f"symbol:{symbol} start_date:{start_date} records:{stock_zh_a_hist_df.shape[0]} 下载完成")

def get_all_daily_data():
    stock_list = get_stock_list()
    current_date = get_trade_date_list()[-1]
    with Session(engine) as session:
        max_date_dict = {record[0]: record[1] for record in session.execute(text("select 代码,max(`日期`) from stock_zh_a_hist group by 代码")).fetchall()}
        for index,stock in enumerate(stock_list):
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
                    print(f"{stock} 下载完成。总进度{index+1}/{len(stock_list)} ")
                    # time.sleep(0.01)
                    break
                except Exception as e:
                    traceback.print_exc()
                    time.sleep(10)



if __name__ == '__main__':
    get_all_daily_data()
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
