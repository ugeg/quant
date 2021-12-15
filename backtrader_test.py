import time
from datetime import datetime

import pandas as pd

import utils.backtrader_util
from utils import global_operator
from matplotlib import pyplot as plt
import backtrader as bt
# 正常显示画图时出现的中文和负号
from pylab import mpl

mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False


# import matplotlib as mpl
# mpl.rcParams['font.sans-serif'] = ['KaiTi', 'SimHei', 'FangSong']  # 汉字字体,优先使用楷体，如果找不到楷体，则使用黑体
# mpl.rcParams['font.size'] = 12  # 字体大小
# mpl.rcParams['axes.unicode_minus'] = False  # 正常显示负号
# Create a Stratey

class MyStrategy(utils.backtrader_util.StrategyDefault):
    params = (('maperiod', 15),
              ('printlog', True),)

    def __init__(self):
        # 指定价格序列
        self.dataclose = self.datas[0].close

        # 初始化交易指令、买卖价格和手续费
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # 添加移动均线指标
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.maperiod)

    # 策略核心，根据条件执行买卖交易指令（必选）
    def next(self):
        # 记录收盘价
        # self.log(f'收盘价, {dataclose[0]}')
        if self.order:  # 检查是否有指令等待执行,
            return
        # 检查是否持仓
        if not self.position:  # 没有持仓
            # 执行买入条件判断：收盘价格上涨突破15日均线
            if self.dataclose[0] > self.sma[0]:
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                # 执行买入
                self.order = self.buy()
        else:
            # 执行卖出条件判断：收盘价格跌破15日均线
            if self.dataclose[0] < self.sma[0]:
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                # 执行卖出
                self.order = self.sell()


class MyStrategy1(utils.backtrader_util.StrategyDefault):
    params = (('maperiod', 15),
              ('printlog', True),)

    def __init__(self):
        # 指定价格序列
        self.dataclose = self.datas[0].close

        # 初始化交易指令、买卖价格和手续费
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # 添加移动均线指标
        self.sma = [bt.indicators.SimpleMovingAverage(
            self.datas[i], period=self.params.maperiod) for i in range(len(self.datas))]

    # 策略核心，根据条件执行买卖交易指令（必选）
    def next(self):
        # 记录收盘价
        # self.log(f'收盘价, {dataclose[0]}')
        if self.order:  # 检查是否有指令等待执行,
            return
        for i in range(len(self.datas)):
            data = self.datas[i]
            position = self.getpositions()[i]
            name = data._name
            if not position:
                if data.close[0] > self.sma[i][0]:
                    self.log('BUY %s CREATE, %.2f' % (name, self.dataclose[0]))
                    # 执行买入
                    self.order = self.buy(data)
            else:
                # 执行卖出条件判断：收盘价格跌破15日均线
                if data.close[0] < self.sma[i][0]:
                    self.log('SELL %s CREATE, %.2f' % (name, self.dataclose[0]))
                    # 执行卖出
                    self.order = self.sell(data)


class TestStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.sizer.setsizing(10)
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        # To keep track of pending orders
        self.order = None
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=10)
        # Indicators for the plotting show
        bt.indicators.ExponentialMovingAverage(self.datas[0], period=25)
        bt.indicators.WeightedMovingAverage(self.datas[0], period=25,
                                            subplot=True)
        bt.indicators.StochasticSlow(self.datas[0])
        bt.indicators.MACDHisto(self.datas[0])
        rsi = bt.indicators.RSI(self.datas[0])
        bt.indicators.SmoothedMovingAverage(rsi, period=10)
        bt.indicators.ATR(self.datas[0], plot=False)

    def notify(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enougth cash
        if order.status in [order.Completed, order.Canceled, order.Margin]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f' % order.executed.price)
            elif order.issell():
                self.log('SELL EXECUTED, %.2f' % order.executed.price)

            self.bar_executed = len(self)

        # Write down: no pending order
        self.order = None

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:

            # Not yet ... we MIGHT BUY if ...
            if self.dataclose[0] < self.dataclose[-1]:
                # current close less than previous close

                if self.dataclose[-1] < self.dataclose[-2]:
                    # previous close less than the previous close

                    # BUY, BUY, BUY!!! (with default parameters)
                    self.log('BUY CREATE, %.2f' % self.dataclose[0])

                    # Keep track of the created order to avoid a 2nd order
                    self.order = self.buy()

        else:

            # Already in the market ... we might sell
            if len(self) >= (self.bar_executed + 5):
                # SELL, SELL, SELL!!! (with all possible default parameters)
                self.log('SELL CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()


class my_strategy1(bt.Strategy):
    # 全局设定交易策略的参数
    params = (
        ('maperiod', 20),
    )

    def __init__(self):
        # 指定价格序列
        self.dataclose = self.datas[0].close
        # 初始化交易指令、买卖价格和手续费
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # 添加移动均线指标，内置了talib模块
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.maperiod)

    def next(self):
        if self.order:  # 检查是否有指令等待执行,
            return
        # 检查是否持仓
        if not self.position:  # 没有持仓
            # 执行买入条件判断：收盘价格上涨突破20日均线
            if self.dataclose[0] > self.sma[0]:
                # 执行买入
                self.order = self.buy()
        else:
            # 执行卖出条件判断：收盘价格跌破20日均线
            if self.dataclose[0] < self.sma[0]:
                # 执行卖出
                self.order = self.sell()


class mySizer(bt.sizers.AllInSizerInt):
    def _getsizing(self, comminfo, cash, data, isbuy):
        position = self.broker.getposition(data)
        if not position:
            size = cash * (self.params.percents / 100) // (data.close[0] * 100) * 100
        else:
            size = position.size

        if self.p.retint:
            size = int(size)

        return size


if __name__ == '__main__':
    # 初始化模型
    cerebro = bt.Cerebro()
    # Add a strategy
    # strats = cerebro.optstrategy(
    #     TestStrategy,
    #     maperiod=range(10, 31))
    # cerebro.addstrategy(MyStrategy1)
    cerebro.addstrategy(TestStrategy)
    # cerebro.addstrategy(my_strategy1)
    # 设定初始资金
    cerebro.broker.setcash(100000.0)
    # 手续费
    # cerebro.broker.setcommission(0.0005)
    comminfo = utils.backtrader_util.StampDutyCommission(stamp_duty=0.001, commission=0.0005)
    cerebro.broker.addcommissioninfo(comminfo)
    # 每次交易买入的股数
    # cerebro.addsizer(bt.sizers.FixedSize, stake=500)
    # cerebro.addsizer(bt.sizers.PercentSizer, stake=50)
    # cerebro.addsizer(bt.sizers.AllInSizerInt, percents=95)
    cerebro.addsizer(mySizer, percents=95)

    # socket_list = ['比亚迪','紫光国微']
    socket_list = ['比亚迪']
    # socket_list = ['王府井',]
    # 回测期间
    start = datetime(2021, 1, 1)
    end = datetime(2021, 12, 1)
    use_direct_data = False
    for socket in socket_list:
        df = utils.backtrader_util.get_stock_daily_data(socket, '20200628')
        if use_direct_data:
            data = bt.feeds.PandasDirectData(dataname=df, fromdate=start, todate=end, datetime=0, openinterest=-1)
        else:
            data = bt.feeds.PandasData(dataname=df, fromdate=start, todate=end, openinterest=None)
    cerebro.adddata(data, name=socket)
    cerebro.addanalyzer(bt.analyzers.Returns)
    # 策略执行前的资金
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    results = cerebro.run(maxcpus=8)
    # 策略执行后的资金
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    # cerebro.plot(style='bar',tight=False,width=160,height=90)
    rets = results[0].analyzers.returns.get_analysis()
    print(rets)
    # rets = results[1].analyzers.returns.get_analysis()
    # print(rets)
    # cerebro.plot(style='candlestick')
    # cerebro.plot(volume=False)
    cerebro.plot()
    # plt.show()
