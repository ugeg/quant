# -*- coding: utf-8 -*-
# @Author  : pengj    <ugeg@163.com>
# @Time    : 2019/6/27 23:09
# @File    : backtesting.py
import itertools

import matplotlib.pyplot as plts
from pyalgotrade import strategy, plotter
from pyalgotrade.optimizer import local
from pyalgotrade.stratanalyzer import returns, sharpe, drawdown, trades
from pyalgotrade.technical import ma

import tusharefeed
from read_stock_data import name2code


class MyStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, sma_period, cash):
        """
        :param feed: 数据来源
        :param instrument: 股票标记
        :param sma_period: 周期
        """
        super(MyStrategy, self).__init__(feed, cash)  # 设置初始资金
        self.__position = None
        self.__instrument = instrument
        # 使用调整后的收盘价
        self.setUseAdjustedValues(True)
        self.__sma = ma.SMA(feed[instrument].getPriceDataSeries(), sma_period)

    def getSMA(self):
        return self.__sma

    def onEnterOk(self, position):
        """
        买入成功时触发
        :param position: 当前仓位(头寸),这是对下的订单的更高级别的抽象,本质是一对多单和空单
        """
        execInfo = position.getEntryOrder().getExecutionInfo()
        # 价格
        price = execInfo.getPrice()
        # 股数
        shares = execInfo.getQuantity()
        # 佣金(费用)
        commission = execInfo.getCommission()
        # 执行时间
        dateTime = execInfo.getDateTime()
        self.info("买入 %.0f手 价格￥%.2f" % (shares / 100, price))

    def onEnterCanceled(self, position):
        """
        多单被取消时触发
        """
        self.__position = None

    def onExitOk(self, position):
        """
        卖出成功时触发
        """
        execInfo = position.getExitOrder().getExecutionInfo()
        price = execInfo.getPrice()
        shares = execInfo.getQuantity()
        self.info("卖出 %.0f手 价格￥%.2f" % (shares / 100, price))
        self.__position = None

    def onExitCanceled(self, position):
        """
        卖单取消时触发
        :param position:
        """
        # 如果卖单取消掉了,重新挂卖单
        self.__position.exitMarket()

    def onBars(self, bars):
        """
        具体执行策略的逻辑,不能为空
        """
        # 如果调整收盘价，高于SMA(15)：15日均线价格，输入多头位置（下单买进）。
        # 如果调整收盘价，低于SMA(15)：15日均线价格，退出多头位置（空头，下单卖出）。
        # 等有足够的数据计算出SMA再执行后面的逻辑
        if self.__sma[-1] is None:
            return

        bar = bars[self.__instrument]
        # 如果还没开仓,检查该不该买
        if self.__position is None:
            if bar.getPrice() > self.__sma[-1]:
                # Broker相当于帮你买卖的经纪人,可以设置佣金
                broker = self.getBroker()
                current_cash = broker.getCash()
                current_price = bars[self.__instrument].getPrice()
                # A股交易中以1手(100股)为单位
                shares = int(current_cash * 0.9 / current_price / 100) * 100
                # enterLong 挂买单, 如果只成交一部分,第二天继续挂着,除非手动取消
                self.__position = self.enterLong(self.__instrument, shares, True)
        # 判断是否要卖
        elif bar.getPrice() < self.__sma[-1] and not self.__position.exitActive():
            # exitMarket(None)按照当前多单的仓位来卖,如果当前还挂了多单,会把多单取消
            self.__position.exitMarket()


def analyze_and_draw(feed, instrument, period, cash=10000):
    my_strategy = MyStrategy(feed, instrument, period, cash)
    # 在执行前添加不同的分析器
    ret_analyzer = returns.Returns()
    my_strategy.attachAnalyzer(ret_analyzer)
    sharpe_ratio_analyzer = sharpe.SharpeRatio()
    my_strategy.attachAnalyzer(sharpe_ratio_analyzer)
    draw_down_analyzer = drawdown.DrawDown()
    my_strategy.attachAnalyzer(draw_down_analyzer)
    trades_analyzer = trades.Trades()
    my_strategy.attachAnalyzer(trades_analyzer)
    # 设置中文等线字体以显示中文
    plts.rcParams['font.sans-serif'] = ['DengXian']
    plt = plotter.StrategyPlotter(my_strategy, True, False, True)
    plt.getInstrumentSubplot(instrument).addDataSeries("SMA", my_strategy.getSMA())
    # 开始执行策略
    my_strategy.run()
    plt.plot()
    # 现金+有价证券
    print("最终资产价值 Final portfolio value: ￥%.2f" % my_strategy.getBroker().getEquity())
    print("最终资产价值 Final portfolio value: ￥%.2f" % my_strategy.getResult())
    print("累计回报率 Cumulative returns: %.2f %%" % (ret_analyzer.getCumulativeReturns()[-1] * 100))
    print("夏普比率 Sharpe ratio: %.2f" % (sharpe_ratio_analyzer.getSharpeRatio(0.05)))
    print("最大回撤率 Max. drawdown: %.2f %%" % (draw_down_analyzer.getMaxDrawDown() * 100))
    print("最长回撤时间 Longest drawdown duration: %s" % (draw_down_analyzer.getLongestDrawDownDuration()))


def test_for_best_parameter(dest_instrument, feed):
    """
    多线程测试指定范围里的最佳参数
    """

    def parameters_generator():
        instrument = [dest_instrument]
        SMA = range(5, 30)
        return itertools.product(instrument, SMA, [10000])

    local.run(MyStrategy, feed, parameters_generator())


if __name__ == '__main__':
    instrument = "贵州茅台"
    code = name2code(instrument)
    cash = 100000
    feed = tusharefeed.Feed()
    feed.addBarsFromCSV(instrument, "D:/QuantData/day/" + code + ".csv")
    # test_for_best_parameter(instrument,feed)
    analyze_and_draw(feed, instrument, 30, cash)
