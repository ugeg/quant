import pandas as pd

from utils import global_operator, session
from utils.global_operator import save
from utils.logging_util import count_time


@count_time
def RPS_indicator(period: int = 250):
    table_name = 'rps_indicator'
    start_day = session.execute('select max(trade_date) as trade_date from {}'.format(table_name)).scalar()
    if start_day is None:
        start_day = '20060101'
    trade_cal_sql = "SELECT cal_date FROM trade_cal WHERE '20060101'<cal_date and cal_date<=DATE_FORMAT(CURDATE(),'%%Y%%m%%d') and is_open=1 ORDER BY cal_date"
    df1 = global_operator.read(trade_cal_sql)

    df = pd.concat([df1, df1.shift(period)], axis=1).dropna()
    df = df.reset_index().drop('index', axis=1)
    df.columns = ["max_date", "min_date"]
    for index, row in df.iterrows():
        if row['max_date'] <= start_day:
            continue
        print(row['max_date'])
        min_date = df.iloc[index, 1]
        max_date = df.iloc[index, 0]
        increase_sql = '''select a.ts_code,b.trade_date,{} as period,(b.pre_close-a.pre_close)/abs(a.pre_close) as increase from 
                (SELECT ts_code,trade_date,pre_close from daily where trade_date='{}')a inner JOIN 
                (SELECT ts_code,trade_date,pre_close from daily where trade_date ='{}')b 
                on a.ts_code=b.ts_code ORDER BY increase'''.format(period, min_date, max_date)
        df2 = global_operator.read(increase_sql)
        df2['rps'] = df2.reset_index().apply(lambda x: x['index'] * 100 // len(df2), axis=1)
        save(df2, table_name)


if __name__ == '__main__':
    RPS_indicator(250)
