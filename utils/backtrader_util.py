from collections import OrderedDict

import backtrader as bt
import pandas as pd
from matplotlib import pyplot as plt

from utils import global_operator, time_util

from pylab import mpl

mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False


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
        comm = round(size * price * self.p.commission, 2)
        comm = max(comm, 5)
        if size > 0:
            return comm
        else:
            duty = round(size * price * self.p.stamp_duty, 2)
            return round(-comm - duty, 2)


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


class TotalValue(bt.Analyzer):
    """
    记录每天账户资产
    """
    def __init__(self):
        self.rets = OrderedDict()

    def start(self):
        super(TotalValue, self).start()

    def next(self):
        super(TotalValue, self).next()
        self.rets[self.datas[0].datetime.datetime()] = self.strategy.broker.getvalue()

    def get_analysis(self):
        return self.rets


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
            self.log('交易失败')
        self.order = None

    # 记录交易收益情况（可省略，默认不输出结果）
    def notify_trade(self, trade):
        if trade.isclosed:
            self.log(
                f'结算 {trade.data._name} 毛收益 {trade.pnl:.2f}, 净收益 {trade.pnlcomm:.2f},手续费{trade.commission:.2f}')

    # 回测结束后输出结果（可省略，默认输出结果）
    def stop(self):
        self.log('期末总资金 %.2f' % (self.broker.getvalue()), doprint=True)


def get_stock_daily_data(code, start_date, end_date=None):
    if not end_date:
        end_date = time_util.date_to_str()
    start_date = time_util.format_date(start_date)
    end_date = time_util.format_date(end_date)
    socket_code = global_operator.format_stock_code(code)
    df = global_operator.read(
        "select trade_date,open,high,low,close,vol as volume from daily where ts_code='{}' and trade_date>='{}' and trade_date<{}".format(
            socket_code, start_date, end_date))
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    df.set_index('trade_date', inplace=True)
    return df


def plot_stock(code, title, start, end=None):
    dd = get_stock_daily_data(code, start, end)
    trade_date_count = len(dd.index)
    print('trade_date_count:{}', trade_date_count)
    dd.close.plot(figsize=(14, 6), color='r')
    plt.title(title + '价格走势\n' + start + ':' + end, size=15)
    plt.annotate(f'期间累计涨幅:{(dd.close[-1] / dd.close[0] - 1) * 100:.2f}%',
                 xy=(dd.index[-trade_date_count // 2], dd.close.mean()),
                 xytext=(dd.index[-trade_date_count // 4], dd.close.min()), bbox=dict(boxstyle='round,pad=0.5',
                                                                                      fc='yellow', alpha=0.5),
                 arrowprops=dict(facecolor='green', shrink=0.05), fontsize=12)
    plt.show()


if __name__ == '__main__':
    plot_stock('比亚迪', '比亚迪', start="20210101")
