import datetime

import utils
from utils import backtrader_util, global_operator
import backtrader as bt


# 多股策略，从股票池中取涨幅前10的股票，均线金叉时买入。每周调仓
class MyStrategy(backtrader_util.StrategyDefault):
    # 策略参数
    params = dict(
        period=20,  # 均线周期
        look_back_days=30,
        printlog=True
    )

    def __init__(self):
        self.mas = dict()
        # 遍历所有股票,计算20日均线
        for data in self.datas:
            self.mas[data._name] = bt.ind.SMA(data.close, period=self.p.period)

    def next(self):
        # 每周五判断，周一调仓
        # todo 这里应该确保第0个股票不停牌，否则停牌的时候无法调仓了
        today = self.datas[0].datetime.date(0)
        week = today.weekday()
        if week != 4:
            return
        # 计算截面收益率
        rate_list = []
        for data in self.datas:
            if len(data) > self.p.look_back_days:
                p0 = data.close[0]
                pn = data.close[-self.p.look_back_days]
                rate = (p0 - pn) / pn
                rate_list.append([data._name, rate])

        sorted_rate = sorted(rate_list, key=lambda x: x[1], reverse=True)
        # 股票池,取30天涨幅前10
        long_list = [i[0] for i in sorted_rate[:10]]

        # 得到当前的账户价值
        total_value = self.broker.getvalue()
        p_value = total_value * 0.9 / 10
        for data in self.datas:
            # 获取仓位
            pos = self.getposition(data).size
            # 在股票池中，且股价高于均线，买入
            if not pos and data._name in long_list and \
                    self.mas[data._name][0] < data.close[0]:
                size = int(p_value / 100 / data.close[0]) * 100
                self.buy(data=data, size=size)

            if pos != 0 and data._name not in long_list or \
                    self.mas[data._name][0] > data.close[0]:
                self.close(data=data)


if __name__ == '__main__':
    # 初始化模型
    cerebro = bt.Cerebro()
    # 回测期间
    start = datetime.datetime(2021, 1, 1)
    end = datetime.datetime(2022, 2, 21)
    start_date = global_operator.get_last_trade_date('20210101')
    socket_list = global_operator.get_code_list(start_date)
    use_direct_data = True
    for socket in socket_list:
        scoket_name = global_operator.code2name[socket]
        df = utils.backtrader_util.get_stock_daily_data(None, socket, start_date)
        if use_direct_data:
            data = bt.feeds.PandasDirectData(dataname=df, fromdate=start, todate=end, datetime=0, openinterest=-1)
        else:
            data = bt.feeds.PandasData(dataname=df, fromdate=start, todate=end, openinterest=None)
            # data = PandasData_Extend(dataname=df, fromdate=start, todate=end, openinterest=None)
        cerebro.adddata(data, name=scoket_name)
    # Add a strategy
    cerebro.addstrategy(MyStrategy)
    # 设定初始资金
    cerebro.broker.setcash(1000000.0)
    # cerebro.broker.set_coc(True)  # 设置以当日收盘价成交
    # 手续费
    # cerebro.broker.setcommission(0.0005)
    comminfo = utils.backtrader_util.StampDutyCommission(stamp_duty=0.001, commission=0.0005)
    cerebro.broker.addcommissioninfo(comminfo)
    # 每次交易买入的股数
    # cerebro.addsizer(bt.sizers.FixedSize, stake=500)
    # cerebro.addsizer(bt.sizers.PercentSizer, stake=50)
    cerebro.addsizer(bt.sizers.AllInSizerInt, percents=95)

    cerebro.addanalyzer(bt.analyzers.Returns)
    cerebro.addanalyzer(utils.backtrader_util.TotalValue, _name='_TotalValue')

    # 策略执行前的资金
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    results = cerebro.run(maxcpus=16)
    # 策略执行后的资金
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    # cerebro.plot(style='bar',tight=False,width=160,height=90)
    rets = results[0].analyzers.returns.get_analysis()
    totalValue = results[0].analyzers._TotalValue.get_analysis()
    print(rets)
    print('totalValue:', totalValue)
    # rets = results[1].analyzers.returns.get_analysis()
    # print(rets)
    # cerebro.plot(style='candlestick')
    # cerebro.plot(volume=False)
    print('gg')

    from backtrader_plotting import Bokeh
    from backtrader_plotting.schemes import Tradimo

    # 其它回测代码
    # ...
    # 设置回测结果中不显示数据K线
    for d in cerebro.datas:
        d.plotinfo.plot = False
    b = Bokeh(style='bar', plot_mode='single', scheme=Tradimo())
