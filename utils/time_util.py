# -*- coding: utf-8 -*-
# @Author  : pengj    <ugeg@163.com>
# @Time    : 2021/1/24 23:48
# @File    : time_util.py
from datetime import datetime, timedelta


def format_date(date_str, format_len=8):
    assert format_len == 8 or format_len == 10
    src_len = len(date_str)
    if src_len == format_len:
        return date_str
    if len(date_str) == 8:
        return date_str[:4] + "-" + date_str[4:6] + "-" + date_str[6:]
    else:
        return date_str[:4] + date_str[5:7] + date_str[8:]


def date_to_str(date: datetime = None):
    if date is None:
        date = datetime.today()
    return "{}{:0>2}{:0>2}".format(date.year, date.month, date.day)


def str_to_date(date_str: str):
    assert len(date_str) == 8
    return datetime(int(date_str[:4]), int(date_str[4:6]), int(date_str[6:]))


def get_latest_trading_day():
    today = datetime.today()
    if today.hour < 15:
        today -= timedelta(days=1)
    weekday = datetime.isoweekday(today)
    if weekday == 6 or weekday == 7:
        today -= timedelta(days=(weekday - 5))
    return today


if __name__ == '__main__':
    print(datetime.today())
    print(date_to_str(datetime.today()))
    print(str_to_date("20210101"))
    print(get_latest_trading_day())
