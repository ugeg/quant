# 导入相关模块和类
import matplotlib.pyplot
import pandas as pd
import pybroker as pb
import sqlalchemy
from pybroker import Strategy, StrategyConfig, ExecContext, PriceType
from pybroker.data import DataSource
from pybroker.ext.data import AKShare

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
        query = f"""SELECT symbol, trade_date as `date`, `open`,  high, low,`close` 
        FROM stock_zh_a_hist where symbol in({"'" + "','".join(symbols) + "'"})
        and trade_date between '{start_date}' and '{end_date}'"""
        df = pd.read_sql(query, self.engine)
        df['date'] = pd.to_datetime(df['date'])
        return df



# 定义规则
def buy_low(ctx: ExecContext):
    # 如果当前已经持有仓位，则不再买入。
    if ctx.long_pos():
        return
    # 如果当前的收盘价小于前一天的最低价，则下单买入。
    if ctx.bars >= 2 and ctx.close[-1] < ctx.low[-2]:
        # 计算买入的股票数量，该数量为当前资金的 25%。
        ctx.buy_shares = ctx.calc_target_shares(1)
        # 设置买入的限价，该限价为当前收盘价减去 0.01。
        # ctx.buy_limit_price = ctx.close[-1] - 0.01
        ctx.buy_fill_price = ctx.close[-1]
        ctx.sell_fill_price = PriceType.CLOSE
        # 设置持有仓位的时间，该时间为 3 个交易日。
        ctx.hold_bars = 3


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    symbols = ['002594']
    start_date = '20230101'
    end_date = '20230601'

    # 策略配置
    config = StrategyConfig(initial_cash=500_000)
    from config import mysql_url
    data_source = MysqlDataSource(mysql_url)
    df = data_source.query(symbols, start_date, end_date)
    print(df.head(10))
    strategy = Strategy(
        data_source=data_source,
        start_date=start_date,
        end_date=end_date,
        config=config
    )
    # 执行回测
    strategy.add_execution(fn=buy_low, symbols=symbols)
    result = strategy.backtest()
    # 查看结果
    print("metrics_df\n",result.metrics_df)  # 查看绩效
    print("orders\n",result.orders)  # 查看订单
    print("positions\n",result.positions)  # 查看持仓
    print("portfolio\n",result.portfolio)  # 查看投资组合
    print("trades\n",result.trades)  # 查看交易
    # plt.plot(df['date'],df['close'])
    # plt.show()
    chart = plt.subplot2grid((3, 2), (0, 0), rowspan=3, colspan=2)
    chart.plot(df['date'], df['close'])
    orders = result.orders
    buy_orders = result.orders[result.orders['type']=='buy']
    sell_orders = result.orders[result.orders['type']=='sell']
    chart.plot(buy_orders['date'], buy_orders['fill_price'], 'r^', markersize=4, label="Buy")
    chart.plot(sell_orders['date'], sell_orders['fill_price'], 'gv', markersize=4, label="Sell")
    matplotlib.pyplot.show()
    chart2 = plt.subplot2grid((3, 2), (0, 0), rowspan=3, colspan=2)
    chart2.plot(result.portfolio.index, result.portfolio['market_value'])
    matplotlib.pyplot.show()
    print("")
