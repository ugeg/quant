import datetime

import backtrader as bt
import pandas as pd


class StrategyDefault(bt.Strategy):
    params = (('socket_name', ' '),
              ('printlog', True),)

    # 交易记录日志（可省略，默认不输出结果）
    def log(self, txt, dt=None, doprint=False):
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()},{txt}')

    # 记录交易执行情况（可省略，默认不输出结果）
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    f'买入:{order.data._name} 价格:{order.executed.price},成本:{order.executed.value},手续费:{order.executed.comm}')
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                self.log(
                    f'卖出:{order.data._name} 价格：{order.executed.price},成本: {order.executed.value},手续费{order.executed.comm}')
            # self.bar_executed = len(self)
        # 如果指令取消/交易失败, 报告结果
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log(order.data._name + '交易失败\t' + order.Status[order.status])
        self.order = None

    # 记录交易收益情况（可省略，默认不输出结果）
    def notify_trade(self, trade):
        if trade.isclosed:
            self.log(
                f'结算 {trade.data._name} 毛收益 {trade.pnl:.2f}, 净收益 {trade.pnlcomm:.2f},手续费{trade.commission:.2f}')

    # 回测结束后输出结果（可省略，默认输出结果）
    def stop(self):
        self.log('期末总资金 %.2f' % (self.broker.getvalue()), doprint=True)


class MyStrategy(StrategyDefault):
    params = (('maperiod', 20),
              ('printlog', True),)

    def __init__(self):
        # 指定价格序列
        # self.dataclose = self.datas[0].close

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
        if self.order:  # 检查是否有指令等待执行,
            return
        for i, data in enumerate(self.datas):
            position = self.getposition(data=data)
            name = data._name
            # 判断是否有持仓
            if not position:
                # 收盘价格大于20日均线
                if data.close[0] > self.sma[i][0]:
                    # 执行买入
                    upper_price = round(data.close[0] * 1.05, 2)
                    self.log('BUY %s CREATE,close_price:%.2f,upper_price:%.2f' % (name, data.close[0], upper_price))
                    # self.order = self.buy(data, exectype=bt.Order.Limit, price=upper_price,
                    #                       valid=bt.num2date(data.datetime[1]))
                    self.order = self.buy(data)
            else:
                # 执行卖出条件判断：收盘价格小于20日均线
                if data.close[0] < self.sma[i][0]:
                    self.log('SELL %s CREATE, %.2f' % (name, data.close[0]))
                    # 执行卖出
                    self.order = self.sell(data)


class StampDutyCommission(bt.CommInfoBase):
    """
    佣金及印花税
    """
    params = (
        ("stamp_duty", 0.001),  # 印花税
        ('commission', 0.00015),  # 佣金率
        ("percabs", True),  # 是否为股票模式
        ('stocklike', True),
        ('commtype', bt.CommInfoBase.COMM_PERC),
    )

    def _getcommission(self, size, price, pseudoexec):
        comm = round(abs(size) * price * self.p.commission, 2)
        comm = max(comm, 5)
        if size > 0:
            return comm
        else:
            duty = round(-size * price * self.p.stamp_duty, 2)
            return round(comm + duty, 2)


class ASharesSizer(bt.sizers.PercentSizerInt):
    """
    A股买卖最少100股
    """
    params = (
        ('percents', 100),
    )

    def _getsizing(self, comminfo, cash, data, isbuy):
        position = self.broker.getposition(data)
        current_prize = data.open[0]
        if not position:
            size = cash * (self.params.percents / 100) // (current_prize * 100) * 100
            if size == 0:
                if cash > data.close[0] * 100:
                    size = 100
                else:
                    print("cash :", cash, "not enough for prize:", current_prize)
        else:
            size = position.size

        if self.p.retint:
            size = int(size)

        return size


if __name__ == '__main__':
    # 初始化模型
    cerebro = bt.Cerebro()
    cerebro.addstrategy(MyStrategy)
    # 设定初始资金
    cerebro.broker.setcash(100000.0)
    # 手续费
    commission = StampDutyCommission(stamp_duty=0.001, commission=0.0005)
    cerebro.broker.addcommissioninfo(commission)
    # 每次交易买入的股数
    cerebro.addsizer(ASharesSizer, percents=98)
    # 读取历史数据
    df = pd.read_csv("E:\quant\AI炒股学习/002594.SZ.csv")
    df.drop(labels='ts_code', axis=1, inplace=True)
    df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')
    df.set_index('trade_date', inplace=True)
    # 设定回测周期
    start = datetime.datetime(2022, 1, 1)
    end = datetime.datetime(2023, 1, 1)
    data = bt.feeds.PandasDirectData(dataname=df, fromdate=start, todate=end, datetime=0, openinterest=-1)
    cerebro.adddata(data, name="002594.SZ")

    # 策略执行前的资金
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    results = cerebro.run()
    # 策略执行后的资金
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # 画图
    from btplotting import BacktraderPlotting
    from btplotting.schemes import Tradimo
    p = BacktraderPlotting(style='bar', scheme=Tradimo())
    cerebro.plot(p)
