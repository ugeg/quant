# 导入相关模块和类
import matplotlib.pyplot
import pandas as pd
import pybroker
import pybroker as pb
import sqlalchemy
from pybroker import Strategy, StrategyConfig, ExecContext
from pybroker.data import DataSource
from pybroker.ext.data import AKShare
from sqlalchemy import text
from sqlalchemy.orm import Session

# 查看当前版本
print(pb.__version__)


class MysqlDataSource(DataSource):

    def __init__(self, mysql_url: str):
        super().__init__()
        self.engine: sqlalchemy.engine.Engine = sqlalchemy.create_engine(mysql_url, echo=False)
        # Register custom columns
        # pybroker.register_columns('rsi')

    def _fetch_data(self, symbols, start_date, end_date, _timeframe, _adjust):
        # 必须包含symbol、date、open、high、low 和 close
        query = f"""SELECT 代码 as symbol, 日期 as `date`, 开盘 as `open`, 最高 as high, 最低 as low, 收盘 as `close` 
        FROM stock_zh_a_hist where 代码 in({"'" + "','".join(symbols) + "'"})
        and 日期 between '{start_date}' and '{end_date}'"""
        df = pd.read_sql(query, self.engine)
        return df


# 策略配置
config = StrategyConfig(initial_cash=500_000)
strategy = Strategy(
    data_source=AKShare(),
    start_date='20220101',
    end_date='20230916',
    config=config
)


# 定义规则
def buy_low(ctx: ExecContext):
    # 如果当前已经持有仓位，则不再买入。
    if ctx.long_pos():
        return
    # 如果当前的收盘价小于前一天的最低价，则下单买入。
    if ctx.bars >= 2 and ctx.close[-1] < ctx.low[-2]:
        # 计算买入的股票数量，该数量为当前资金的 25%。
        ctx.buy_shares = ctx.calc_target_shares(0.25)
        # 设置买入的限价，该限价为当前收盘价减去 0.01。
        ctx.buy_limit_price = ctx.close[-1] - 0.01
        # 设置持有仓位的时间，该时间为 3 个交易日。
        ctx.hold_bars = 3


# 执行回测
strategy.add_execution(fn=buy_low, symbols=['000001', '600000'])
result = strategy.backtest()

# 查看结果
print(result.metrics_df)  # 查看绩效
print(result.orders)  # 查看订单
print(result.positions)  # 查看持仓
print(result.portfolio)  # 查看投资组合
print(result.trades)  # 查看交易
import matplotlib.pyplot as plt

chart = plt.subplot2grid((3, 2), (0, 0), rowspan=3, colspan=2)
chart.plot(result.portfolio.index, result.portfolio['market_value'])
matplotlib.pyplot.show()