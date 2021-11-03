from utils import global_operator

import backtrader as bt
import matplotlib as plt


# Create a Stratey
class TestStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        # To keep track of pending orders
        self.order = None

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
                self.order = self.buy(size=500)
        else:
            # 执行卖出条件判断：收盘价格跌破20日均线
            if self.dataclose[0] < self.sma[0]:
                # 执行卖出
                self.order = self.sell(size=500)


if __name__ == '__main__':
    # 初始化模型
    cerebro = bt.Cerebro()
    cerebro.addstrategy(TestStrategy)
    # 设定初始资金
    cerebro.broker.setcash(100000.0)
    # 手续费
    cerebro.broker.setcommission(0.005)
    # 每次交易买入的股数
    # cerebro.addsizer(bt.sizers.FixedSize, stake=500)
    # cerebro.addsizer(bt.sizers.PercentSizer, stake=50)
    cerebro.addsizer(bt.sizers.AllInSizer, percents=95)
    # 策略执行前的资金
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    df = global_operator.read(
        "select trade_date,open,high,low,close,vol as volume,0 from daily where ts_code='002049.SZ' and trade_date>'20171101'")
    # data = bt.feeds.PandasData(dataname=df,fromdate=datetime(2021,6,1),totime=datetime(2021,16,1))
    data = bt.feeds.PandasData(dataname=df)
    cerebro.adddata(data)
    cerebro.run()
    # 策略执行后的资金
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    # cerebro.plot(style='bar',tight=False,width=160,height=90)

    cerebro.plot(style='candlestick')
    # cerebro.plot(volume=False)
