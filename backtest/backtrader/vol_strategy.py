import datetime
import math

import utils.backtrader_util
import backtrader as bt


class VolStrategy(utils.backtrader_util.StrategyDefault):
    params = (('maperiod', 30),
              ('printlog', True),)

    def __init__(self):
        self.order = None
        self.sma_vol = bt.indicators.SimpleMovingAverage(
            self.datas[0].volume, period=self.params.maperiod)
        self.sma_close = bt.indicators.SimpleMovingAverage(
            self.datas[0].close, period=self.params.maperiod)
    def next(self):
        # 记录收盘价
        # self.log(f'收盘价, {dataclose[0]}')
        if self.order:  # 检查是否有指令等待执行,
            return
        # 检查是否持仓
        if not self.position:  # 没有持仓
            # close-low>2(close-open)
            # 执行买入条件判断：收盘价格上涨突破15日均线
            close_open_min = min(self.datas[0].close[0],self.datas[0].open[0])
            if close_open_min - self.datas[0].low[0] > 2 * (self.datas[0].high[0] - close_open_min) \
                and self.datas[0].volume[0] < self.sma_vol*0.8 and self.datas[0].close[-1]>self.datas[0].close[-2]:
                self.log('BUY CREATE, %.2f' % self.datas[0].close[0])
                self.order = self.buy(data=self.datas[0])
        else:
            # 执行卖出条件判断：收盘价格跌破15日均线
            if self.datas[0].close[0] < self.sma_close[0]:
                self.log('SELL CREATE, %.2f' % self.datas[0].close[0])
                # 执行卖出
                self.order = self.sell(self.datas[0])


if __name__ == '__main__':
    # 初始化模型
    cerebro = bt.Cerebro()
    # Add a strategy
    # strats = cerebro.optstrategy(
    #     TestStrategy,
    #     maperiod=range(10, 31))
    cerebro.addstrategy(VolStrategy)
    # 设定初始资金
    cerebro.broker.setcash(100000.0)
    # cerebro.broker.set_coc(True)  # 设置以当日收盘价成交
    # 手续费
    # cerebro.broker.setcommission(0.0005)
    comminfo = utils.backtrader_util.StampDutyCommission(stamp_duty=0.001, commission=0.0005)
    cerebro.broker.addcommissioninfo(comminfo)
    # 每次交易买入的股数
    # cerebro.addsizer(bt.sizers.FixedSize, stake=500)
    # cerebro.addsizer(bt.sizers.PercentSizer, stake=50)
    # cerebro.addsizer(bt.sizers.AllInSizerInt, percents=95)
    cerebro.addsizer(utils.backtrader_util.ASharesSizer, percents=10)

    # socket_list = ['比亚迪','紫光国微']
    socket_list = ['康华生物']
    # socket_list = ['比亚迪']
    # socket_list = ['紫光国微',]
    # 回测期间
    start = datetime.datetime(2020, 6, 11)
    end = datetime.datetime(2022, 1, 1)
    use_direct_data = False
    for socket in socket_list:
        df = utils.backtrader_util.get_stock_daily_data(socket, '20200101')
        if use_direct_data:
            data = bt.feeds.PandasDirectData(dataname=df, fromdate=start, todate=end, datetime=0, openinterest=-1)
        else:
            data = bt.feeds.PandasData(dataname=df, fromdate=start, todate=end, openinterest=None)
        cerebro.adddata(data, name=socket)
    cerebro.addanalyzer(bt.analyzers.Returns)
    cerebro.addanalyzer(utils.backtrader_util.TotalValue, _name='_TotalValue')

    # 策略执行前的资金
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    results = cerebro.run(maxcpus=16)
    # 策略执行后的资金
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    # cerebro.plot(style='bar',tight=False,width=160,height=90)mei
    rets = results[0].analyzers.returns.get_analysis()
    totalValue = results[0].analyzers._TotalValue.get_analysis()
    print(rets)
    print('totalValue:', totalValue)
    from backtrader_plotting import Bokeh
    from backtrader_plotting.schemes import Tradimo

    # 其它回测代码
    # ...
    # 设置回测结果中不显示数据K线
    # for d in cerebro.datas:
    #     d.plotinfo.plot = False
    b = Bokeh(style='bar', plot_mode='single', scheme=Tradimo())
    cerebro.plot(b)