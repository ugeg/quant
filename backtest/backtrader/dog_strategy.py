# https://zhuanlan.zhihu.com/p/268584873
import backtrader as bt
import datetime
import pandas as pd
import numpy as np
import os, sys


# 我们使用的时候，直接用我们新的类读取数据就可以了。
class test_divdend_rate_strategy(bt.Strategy):
    params = (('window', 200),)

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('{}, {}'.format(dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.bar_num = 0
        self.stock_divdend_info = pd.read_csv("/home/yun/data/股票历史股息率数据.csv", index_col=0)
        self.buy_list = []
        self.value_list = []
        self.trade_list = []
        self.order_list = []

    def prenext(self):

        self.next()

    def next(self):
        # 假设有100万资金，每次成份股调整，每个股票使用1万元
        self.bar_num += 1
        self.log(self.bar_num)
        # 需要调仓的时候
        pre_current_date = self.datas[0].datetime.date(-1).strftime("%Y-%m-%d")
        current_date = self.datas[0].datetime.date(0).strftime("%Y-%m-%d")
        total_value = self.broker.get_value()
        self.value_list.append([current_date, total_value])
        # 如果是8月的第一个交易日
        if current_date[5:7] == '08' and pre_current_date[5:7] != '08':
            # 获取当前股息率前30的股票
            divdend_info = self.stock_divdend_info[self.stock_divdend_info['tradeDate'] == current_date]
            divdend_info = divdend_info.sort_values("divRate", ascending=False)
            divdend_info = divdend_info.drop_duplicates("secID")
            divdend_stock_list = [i.split('.')[0] for i in list(divdend_info['secID'])]
            if len(divdend_stock_list) > 10:
                stock_list = divdend_stock_list[:10]
            else:
                stock_list = divdend_stock_list
            self.log(stock_list)
            # 平掉原来的仓位
            for stock in self.buy_list:
                data = self.getdatabyname(stock)
                if self.getposition(data).size > 0:
                    self.close(data)
            # 取消所有未成交的订单
            for order in self.order_list:
                self.cancel(order)
                # self.log(order)
            self.buy_list = stock_list

            value = 0.90 * self.broker.getvalue() / len(stock_list)
            # 开新的仓位，按照90%的比例开
            for stock in stock_list:
                data = self.getdatabyname(stock)
                # 没有把手数设定为100的倍数
                lots = value / data.close[0]
                order = self.buy(data, size=lots)
                self.log(f"symbol:{data._name},price:{data.close[0]}")
                self.order_list.append(order)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # order被提交和接受
            return
        if order.status == order.Rejected:
            self.log(f"order is rejected : order_ref:{order.ref}  order_info:{order.info}")
        if order.status == order.Margin:
            self.log(f"order need more margin : order_ref:{order.ref}  order_info:{order.info}")
        if order.status == order.Cancelled:
            self.log(f"order is concelled : order_ref:{order.ref}  order_info:{order.info}")
        if order.status == order.Partial:
            self.log(f"order is partial : order_ref:{order.ref}  order_info:{order.info}")
        # Check if an order has been completed
        # Attention: broker could reject order if not enougth cash
        if order.status == order.Completed:
            if order.isbuy():
                self.log("buy result : buy_price : {} , buy_cost : {} , commission : {}".format(
                    order.executed.price, order.executed.value, order.executed.comm))

            else:  # Sell
                self.log("sell result : sell_price : {} , sell_cost : {} , commission : {}".format(
                    order.executed.price, order.executed.value, order.executed.comm))

    def notify_trade(self, trade):
        # 一个trade结束的时候输出信息
        if trade.isclosed:
            self.log('closed symbol is : {} , total_profit : {} , net_profit : {}'.format(
                trade.getdataname(), trade.pnl, trade.pnlcomm))
            self.trade_list.append([self.datas[0].datetime.date(0), trade.getdataname(), trade.pnl, trade.pnlcomm])

        if trade.isopen:
            self.log('open symbol is : {} , price : {} '.format(
                trade.getdataname(), trade.price))

    def stop(self):

        value_df = pd.DataFrame(self.value_list)
        value_df.columns = ['datetime', 'value']
        value_df.to_csv("股息率value结果.csv")

        trade_df = pd.DataFrame(self.trade_list)
        # trade_df.columns =['datetime','name','pnl','net_pnl']
        trade_df.to_csv("股息率-trade结果.csv")


# 初始化cerebro,获得一个实例
cerebro = bt.Cerebro()
# cerebro.broker = bt.brokers.BackBroker(shortcash=True)  # 0.5%
data_root = "/home/yun/data/stock/day/"
file_list = sorted(os.listdir(data_root))
params = dict(

    fromdate=datetime.datetime(2006, 1, 4),
    todate=datetime.datetime(2019, 12, 31),
    timeframe=bt.TimeFrame.Days,
    dtformat=("%Y-%m-%d"),
    compression=1,
    datetime=0,
    open=1,
    high=2,
    low=3,
    close=4,
    volume=5,
    openinterest=-1)

# 读取数据
for file in file_list:
    feed = bt.feeds.GenericCSVData(dataname=data_root + file, **params)
    # 添加数据到cerebro
    cerebro.adddata(feed, name=file.split('.')[0])
print("加载数据完毕")
# 添加手续费，按照万分之二收取
cerebro.broker.setcommission(commission=0.0002, stocklike=True)
# 设置初始资金为100万
cerebro.broker.setcash(1000000.0)
# 添加策略
cerebro.addstrategy(test_divdend_rate_strategy)
cerebro.addanalyzer(bt.analyzers.TotalValue, _name='_TotalValue')
# 运行回测
results = cerebro.run()