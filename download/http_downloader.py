import datetime
import re
import time

import pandas as pd
import requests

# col_value = requests.get("http://hq.sinajs.cn/list=sz002594,sz002456").text.split("\"")[1].split(",")
from lxml import etree
from utils.global_operator import save, format_stock_code
import utils
import json
from utils.time_util import format_date


def get_realtime_detail(ts_code, src='sina'):
    if src == 'sina':
        col_name_list = ['股票名字', '今开价', '昨收价', '当前价格', '今日最高价', '今日最低价', '买一价', '卖一价', '成交量（股）', '成交额（元）', '买一量（股）',
                         '买一价',
                         '买二量（股）',
                         '买二价', '买三量（股）', '买三价', '买四量（股）', '买四价', '买五量（股）', '买五价', '卖一量（股）', '卖一价', '卖二量（股）', '卖二价',
                         '卖三量（股）',
                         '卖三价', '卖四量（股）', '卖四价', '卖五量（股）', '卖五价', '日期', '时间']
        index_name_dict = {'深成指': 'sz399001', '上证指': 'sh000001', '道琼斯': 'int_dji ', '纳斯达克': 'int_nasdaq',
                           '恒生指': 'int_hangseng', '日经指数': 'int_nikkei', '台湾加权': 'b_TWSE ', '新加坡': 'b_FSSTI '}
        url = 'http://hq.sinajs.cn/list='
        col_value = requests.get(url + ts_code).text.split("\"")[1].split(",")
        return dict(zip(col_name_list, col_value))
    elif src == 'tencent':
        url = 'http://qt.gtimg.cn/q='
        col_value = requests.get(url + ts_code).text.split("\"")[1].split("~")
        col_name_list = ['交易所', '股票名字', '股票代码', '当前价格', '昨收', '开盘', '成交量', '外盘', '内盘', '买一', '买一量', '买二', '买二量', '买三',
                         '买三量', '买四', '买四量', '买五', '买五量', '卖一', '卖一量', '卖二', '卖二量', '卖三', '买三量', '卖四', '卖四量', '卖五',
                         '卖五量', '最新逐笔成交', '请求时间', '涨跌', '涨跌%', '最高', '最低', '最新价/成交量（手）/成交额（元）', '成交量（手）', '成交额（元）',
                         '换手率%',
                         'ttm市盈率', '-', '最高', '最低', '振幅%', '流通市值(亿)', '总市值(亿)', 'lf市净率', '涨停价', '跌停价', '量比', '-', '均价',
                         '动态市盈率', '静态市盈率']
        market_dict = {'200': '美股（us）', '100': '港股（hk）', '51': '深圳（sz）', '1': '上海（sh）'}
        col_value[0] = market_dict[col_value[0]]
        return dict(zip(col_name_list, col_value))


def get_realtime_simple(ts_code, src='sina'):
    if src == 'sina':
        col_name_list = ['股票名字', '当前价', '涨跌额', '涨跌幅%', '成交量（手）', '成交额（万元）']
        url = 'http://hq.sinajs.cn/list=s_'
        col_value = requests.get(url + ts_code).text.split("\"")[1].split(",")
        return dict(zip(col_name_list, col_value))
    elif src == 'tencent':
        url = 'http://qt.gtimg.cn/q=s_'
        col_value = requests.get(url + ts_code).text.split("\"")[1].split("~")
        col_name_list = ['交易所', '股票名字', '股票代码', '当前价格', '涨跌', '涨跌%', '成交量（手）', '成交额（万元）', '-', '总市值（万元）', 'GP-A']
        market_dict = {'200': '美股（us）', '100': '港股（hk）', '51': '深圳（sz）', '1': '上海（sh）'}
        col_value[0] = market_dict[col_value[0]]
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


def download_all_price_his(ts_code):
    ts_code = format_stock_code(ts_code)
    start_date_list = utils.session.execute('SELECT max(start_date) FROM `price_his`').fetchall()
    if (len(start_date_list) == 0):
        sql = "SELECT trade_date FROM `daily` WHERE ts_code='{}' ORDER BY trade_date".format(ts_code)
    else:
        sql = "SELECT trade_date FROM `daily` WHERE ts_code='{}' and trade_date>'{}' ORDER BY trade_date".format(
            ts_code, start_date_list[0])
    result = utils.session.execute(sql).fetchall()
    i = 1
    for day in result:
        print(day[0], i, "/", len(result), round(i * 100 / len(result), 2), '%')
        i += 1
        while 1:
            try:
                download_price_his(ts_code, startdate=day[0], enddate=day[0])
                time.sleep(1)
                break
            except Exception as e:
                print(e)
                print(datetime.datetime.now(), "timeout")
                time.sleep(180)


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
    payload = {'symbol': ts_code, 'num': 60, 'sort': 'ticktime', 'asc': 0, 'volume': 0, 'amount': big_amount, 'type': 0,
               'day': day}
    result = requests.get(url, payload).text
    if result == '[]':
        return None
    return json.loads(result)[0]


def get_position_analysis(ts_code, src='tencent'):
    # 盘口分析
    url = 'http://qt.gtimg.cn/q=s_pk'
    col_value = requests.get(url + ts_code).text.split("\"")[1].split("~")
    col_name_list = ['买盘大单占比', '买盘小单占比', '卖盘大单占比', '卖盘小单占比']
    return dict(zip(col_name_list, col_value))


def get_realtime_capital_flow(ts_code, src='tencent'):
    # 实时资金流向
    url = 'http://qt.gtimg.cn/q=ff_'
    col_value = requests.get(url + ts_code).text.split("\"")[1].split("~")
    col_name_list = ['股票代码', '主力流入', '主力流出', '主力净流入', '主力净流入/资金流入流出总和', '散户流入', '散户流出', '散户净流入', '散户净流入/资金流入流出总和',
                     '资金流入流出总和1+2+5+6', '-1', '-2', '股票名称', '日期', '-3', '-4', '-5', '-6']
    return dict(zip(col_name_list, col_value))


def get_kline_data(ts_code, start_date, end_date, trade_day_count, kline_type='day', adjsutment='qfq', src='tencent'):
    # k线数据
    assert adjsutment == 'qfq' or adjsutment == 'hfq'
    # url = 'https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param=sz002594,day,2017-12-01,,2,qfq'
    url = 'https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param='
    param = ','.join([ts_code, kline_type, start_date, end_date, trade_day_count, adjsutment])
    url += param
    result_json = requests.get(url).content.decode('raw_unicode-escape')
    qfqday = ['交易日，开盘价，收盘价，最高价，最低价', '总手']
    return result_json


def get_minute_data(ts_code, src='tencent'):
    url = 'https://web.ifzq.gtimg.cn/appstock/app/minute/query?code=' + ts_code
    result_json = requests.get(url).text
    col_name_list = ['时间', '价格', '总手']
    return result_json


if __name__ == '__main__':
    # print(get_realtime_detail('sz002594'))
    # print(get_realtime_detail('sh000001'))
    print(get_minute_data('sz002594',src='tencent'))
    # print(format_stock_code('比亚迪', format_type='tushare'))
