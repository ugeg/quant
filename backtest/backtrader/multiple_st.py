from utils import global_operator

import backtrader as bt
import matplotlib as plt


# Create a Stratey
class St0(bt.SignalStrategy):
    def __init__(self):
        sma1, sma2 = bt.ind.SMA(period=10), bt.ind.SMA(period=30)
        crossover = bt.ind.CrossOver(sma1, sma2)
        self.signal_add(bt.SIGNAL_LONG, crossover)

# 策略St1
class St1(bt.SignalStrategy):
    def __init__(self):
        sma1 = bt.ind.SMA(period=10)
        crossover = bt.ind.CrossOver(self.data.close, sma1)
        self.signal_add(bt.SIGNAL_LONG, crossover)

# 策略选择类
class StFetcher(object):
    _STRATS = [St0, St1] # 注册策略

    def __new__(cls, *args, **kwargs):
        idx = kwargs.pop('idx') # 策略索引

        obj = cls._STRATS[idx](*args, **kwargs)
        return obj


if __name__ == '__main__':
    # 初始化模型
    cerebro = bt.Cerebro()
    # cerebro.addstrategy(TestStrategy)
    # cerebro.addstrategy(my_strategy1)
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
    cerebro.addanalyzer(bt.analyzers.Returns)
    cerebro.optstrategy(StFetcher, idx=[0, 1])
    results = cerebro.run(maxcpus=4)

    strats = [x[0] for x in results]  # 取得两个策略的运行结果
    for i, strat in enumerate(strats):
        rets = strat.analyzers.returns.get_analysis()  # 输出策略分析者结果
        print('Strat {} Name {}:\n  - analyzer: {}\n'.format(
            i, strat.__class__.__name__, rets))
    # cerebro.plot(volume=False)
