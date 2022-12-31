import datetime
import time

import akshare as ak
import tushare as ts
from sqlalchemy import func
from utils.entity import Daily
import utils
from utils.logging_util import count_time
from utils.global_operator import save

time_format = '%Y-%m-%d %H:%M:%S'
pro = ts.pro_api(utils.conf.tushare_token)
mysql_connector = utils.mysql_connector
session = utils.session


def get_last_10000_news():
    """财联社-快讯最近的 10000 条数据"""
    stock_zh_a_alerts_cls_df = ak.stock_zh_a_alerts_cls()
    print(stock_zh_a_alerts_cls_df)
    stock_zh_a_alerts_cls_df.to_csv("D:/news.csv", encoding='gbk')


def get_recent_news(end_date: str = datetime.datetime.now().strftime(time_format)):
    df = pro.major_news(**{"src": "", "start_date": "", "end_date": end_date, "limit": "60", "offset": ""},
                        fields=["title", "pub_time", "src"])
    # print(df)
    save(df, "news")
    return df.iloc[59, 1]


def loop_get_recent_news():
    start_date = '2021-01-01 00:00:00'
    end_date = datetime.datetime.now().strftime(time_format)
    while start_date < end_date:
        end_date = (datetime.datetime.strptime(end_date, time_format) - datetime.timedelta(seconds=1)).strftime(
            time_format)
        end_date = get_recent_news(end_date)
        print('end_date:', end_date)
        time.sleep(30)


def get_news_js(forward=True):
    if forward:
        """从当前时间更新到表中最大时间"""
        start_date = session.execute("select cast(max(datetime) as char) from news_jin10").first()[0]
        end_date = datetime.datetime.now().strftime(time_format)
    else:
        """从表中最小时间更新到start_date"""
        start_date = '2016-01-01 00:00:00'
        end_date = session.execute("select cast(min(datetime) as char) from news_jin10").first()[0]
    print('end_date:', end_date)
    while start_date < end_date:
        end_date = (datetime.datetime.strptime(end_date, time_format) - datetime.timedelta(seconds=1)).strftime(
            time_format)
        js_news_df = ak.js_news(timestamp=end_date)
        js_news_df.dropna(inplace=True)
        js_news_df = js_news_df[js_news_df['datetime'] > start_date]
        js_news_df = js_news_df[js_news_df['content'] != '-']
        js_news_df = js_news_df[js_news_df['content'] != '']
        if len(js_news_df) == 0:
            continue
        save(js_news_df, "news_jin10")
        end_date = js_news_df.iloc[0, 0]
        print('end_date:', end_date)
        # time.sleep(3)


if __name__ == '__main__':
    # loop_get_recent_news()
    get_news_js()
