# -*- coding: utf-8 -*-
# @Author  : pengj    <ugeg@163.com>
# @Time    : 2019/6/28 23:21
# @File    : tusharefeed.py
from pyalgotrade.barfeed import csvfeed
from pyalgotrade import bar


class Feed(csvfeed.GenericBarFeed):

    def __init__(self, frequency=bar.Frequency.DAY, timezone=None, maxLen=None):
        if frequency not in [bar.Frequency.DAY, bar.Frequency.WEEK]:
            raise Exception("Invalid frequency")

        super(Feed, self).__init__(frequency, timezone, maxLen)

        self.setDateTimeFormat("%Y%m%d")
        self.setColumnName("datetime", "trade_date")
        self.setColumnName("open", "open")
        self.setColumnName("high", "high")
        self.setColumnName("low", "low")
        self.setColumnName("close", "close")
        self.setColumnName("volume", "vol")
        self.setColumnName("adj_close", "pre_close")
