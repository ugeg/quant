import backtrader as bt
import pandas as pd
from matplotlib import pyplot as plt

from utils import global_operator, time_util

from pylab import mpl
mpl.rcParams['font.sans-serif']=['SimHei']
mpl.rcParams['axes.unicode_minus']=False
class StampDutyCommission(bt.CommInfoBase):
    params = (
        ("stamp_duty", 0.001),  # 印花税
        ("percabs", True)  # 是否为股票模式
    )

    def _getcommission(self, size, price, pseudoexec):
        comm = round(size * price * self.p.commission,2)
        comm = max(comm, 5)
        if size > 0:
            return comm
        else:
            duty = round(size * price * self.p.stamp_duty,2)
            return round(-comm - duty,2)
class StrategyDefault(bt.Strategy):
    params = (('socket_name',' '),
        ('printlog', True),)

    # 交易记录日志（可省略，默认不输出结果）
    def log(self, txt, dt=None, doprint=False):
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()},{txt}')
    #记录交易执行情况（可省略，默认不输出结果）
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'买入:{list(self.dnames.keys())[0]} 价格:{order.executed.price},成本:{order.executed.value},手续费:{order.executed.comm}')
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                self.log(f'卖出:{list(self.dnames.keys())[0]} 价格：{order.executed.price},成本: {order.executed.value},手续费{order.executed.comm}')
            self.bar_executed = len(self)
        # 如果指令取消/交易失败, 报告结果
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('交易失败')
        self.order = None

    #记录交易收益情况（可省略，默认不输出结果）
    def notify_trade(self,trade):
        if trade.isclosed:
            self.log(f'结算 {list(self.dnames.keys())[0]} 毛收益 {trade.pnl:.2f}, 净收益 {trade.pnlcomm:.2f},手续费{trade.commission:.2f}')

    #回测结束后输出结果（可省略，默认输出结果）
    def stop(self):
        self.log('期末总资金 %.2f' %( self.broker.getvalue()), doprint=True)
def get_stock_daily(code, start_date, end_date=None):
    if not end_date:
        end_date = time_util.date_to_str()
    start_date = time_util.format_date(start_date)
    end_date = time_util.format_date(end_date)
    socket_code = global_operator.format_stock_code(code)
    df = global_operator.read(
        "select trade_date,open,high,low,close,vol as volume,0 from daily where ts_code='{}' and trade_date>='{}' and trade_date<{}".format(
            socket_code,start_date,end_date))
    df.index = pd.to_datetime(df.trade_date)
    return df
def plot_stock(code,title,start,end=None):
    dd = get_stock_daily(code,start,end)
    trade_date_count = len(dd.index)
    print('trade_date_count:{}',trade_date_count)
    dd.close.plot(figsize=(14,6),color='r')
    plt.title(title+'价格走势\n'+start+':'+end,size=15)
    plt.annotate(f'期间累计涨幅:{(dd.close[-1]/dd.close[0]-1)*100:.2f}%', xy=(dd.index[-trade_date_count//2],dd.close.mean()),
             xytext=(dd.index[-trade_date_count//4],dd.close.min()), bbox = dict(boxstyle = 'round,pad=0.5',
            fc = 'yellow', alpha = 0.5),
             arrowprops=dict(facecolor='green', shrink=0.05),fontsize=12)
    plt.show()
if __name__ == '__main__':
    plot_stock('比亚迪','比亚迪',start="20210101")