import re

import pandas as pd
import requests

# col_value = requests.get("http://hq.sinajs.cn/list=sz002594,sz002456").text.split("\"")[1].split(",")
from lxml import etree
from utils.global_operator import save, format_stock_code
import utils
import json
from utils.time_util import format_date


def get_realtime_detail(ts_code, src='sina'):
    col_name_list = ['股票名字', '今开价', '昨收价', '当前价格', '今日最高价', '今日最低价', '买一价', '卖一价', '成交量（股）', '成交额（元）', '买一量（股）', '买一价',
                     '买二量（股）',
                     '买二价', '买三量（股）', '买三价', '买四量（股）', '买四价', '买五量（股）', '买五价', '卖一量（股）', '卖一价', '卖二量（股）', '卖二价',
                     '卖三量（股）',
                     '卖三价', '卖四量（股）', '卖四价', '卖五量（股）', '卖五价', '日期', '时间']
    index_name_dict = {'深成指': 'sz399001', '上证指': 'sh000001', '道琼斯': 'int_dji ', '纳斯达克': 'int_nasdaq',
                       '恒生指': 'int_hangseng', '日经指数': 'int_nikkei', '台湾加权': 'b_TWSE ', '新加坡': 'b_FSSTI '}
    url = 'http://hq.sinajs.cn/list='
    col_value = requests.get(url + ts_code).text.split("\"")[1].split(",")
    return dict(zip(col_name_list, col_value))


def get_realtime_simple(ts_code, src='sina'):
    col_name_list = ['股票名字', '当前价', '涨跌额', '涨跌幅%', '成交量（手）', '成交额（万元）']
    url = 'http://hq.sinajs.cn/list=s_'
    col_value = requests.get(url + ts_code).text.split("\"")[1].split(",")
    return dict(zip(col_name_list, col_value))


def download_price_his(ts_code, startdate, enddate):
    """获取一段时间内的历史分价表"""
    # col_name_list = ['成交价(元)', '成交量(股)', '占比']
    # http://market.finance.sina.com.cn/pricehis.php?symbol=sh600900&startdate=2011-08-17&enddate=2011-08-19
    price = []
    volume = []
    percentage = []
    url = 'http://market.finance.sina.com.cn/pricehis.php?'
    payload = {'symbol': ts_code, 'startdate': format_date(startdate, format_len=10),
               'enddate': format_date(enddate, format_len=10)}
    result = requests.get(url, payload).content.decode('gbk')
    trs = etree.HTML(result).xpath("//tbody/tr")
    for tr in trs:
        tds = tr.xpath("./td")
        price.append(tds[0].text)
        volume.append(tds[1].text)
        percentage.append(tds[2].text)
    ts_code = format_stock_code(ts_code, 'tushare')
    ts_code_list = [ts_code for i in range(len(price))]
    startdate_tushare = format_date(startdate, format_len=8)
    enddate_tushare = format_date(enddate, format_len=8)
    start_date_list = [startdate_tushare for i in range(len(price))]
    end_date_list = [enddate_tushare for i in range(len(price))]
    df = pd.DataFrame(
        {"ts_code": ts_code_list, "start_date": start_date_list, "end_date": end_date_list, "price": price,
         "volume": volume,
         "percentage": percentage})
    save(df, "price_his")


def get_kline_gif_url(ts_code, type='min'):
    type_list = ['min', 'daily', 'weekly', 'monthly']
    if type not in type_list:
        raise Exception('type must in ', type_list)
    # http://image.sinajs.cn/newchart/min/n/sh000001.gif
    return "http://image.sinajs.cn/newchart/" + type + "/n/" + ts_code + ".gif"


def get_big_bill_sum(ts_code: str, day: str, big_amount=1000000):
    """大单统计,只能获取到最近15天的"""
    # big_amount：大单阈值
    dict = {
        "symbol": "股票代码",
        "name": "股票名称",
        "opendate": "2021-10-29",
        "minvol": "0",
        "voltype": "12",
        "totalvol": "大单总成交量",
        "totalvolpct": "大单成交量占比",
        "totalamt": "大单总成交额",
        "totalamtpct": "大单成交额占比",
        "avgprice": "305.006",
        "kuvolume": "主买量（股）",
        "kuamount": "主买额（元）",
        "kevolume": "中性量（股）",
        "keamount": "中性额（元）",
        "kdvolume": "主卖量（股）",
        "kdamount": "主卖额（元）",
        "stockvol": "总成交量（股）",
        "stockamt": "总成交额（元）"
    }
    # https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_Bill.GetBillSum?symbol=sz002594&num=60&sort=ticktime&asc=0&volume=0&amount=1000000&type=0&day=2021-10-29
    url = 'https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_Bill.GetBillSum'
    payload = {'symbol': ts_code, 'num': 60, 'sort': 'ticktime', 'asc': 0, 'volume': 0, 'amount': amount, 'type': 0,
               'day': day}
    result = requests.get(url, payload).text
    if result == '[]':
        return None
    return json.loads(result)[0]


if __name__ == '__main__':
    # print(get_realtime_detail('sz002594'))
    # print(get_realtime_detail('sh000001'))
    # print(get_realtime_simple('sz002594'))
    # print(stock_code_adjust('比亚迪', format_type='tushare'))
    result = utils.session.execute(
        "SELECT trade_date FROM `daily` WHERE ts_code='002594.SZ' and trade_date>='20120105' ORDER BY trade_date").fetchall()
    i = 1
    for day in result:
        print(day[0], i, "/", len(result), round(i / len(result), 2), '%')
        i += 1
        download_price_his('sz002594', startdate=day[0], enddate=day[0])
