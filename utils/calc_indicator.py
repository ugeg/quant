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


@count_time
def calc_qfq(init=False):
    calc_sql_tmp = '''
        replace into daily_qfq 
        SELECT a.`ts_code`, a.`trade_date`, 
        round(`open`*b.adj_factor/c.adj_factor,2), round(`high`*b.adj_factor/c.adj_factor,2),
        round(`low`*b.adj_factor/c.adj_factor,2), round(`close`*b.adj_factor/c.adj_factor,2),
        round(`pre_close`*b.adj_factor/c.adj_factor,2), `change`, `pct_chg`, `vol`, `amount` 
        from (SELECT * from daily where ts_code='{}') a 
        INNER JOIN (SELECT * from adj_factor where ts_code='{}') b on a.ts_code=b.ts_code and a.trade_date=b.trade_date 
        LEFT JOIN (SELECT * from adj_factor where ts_code='{}' and trade_date='{}') c on a.ts_code=c.ts_code;'''
    # 计算全量数据
    if init:
        end_date = session.execute("select max(trade_date) from adj_factor").first()[0]
        # 查询未计算前复权的股票
        df_code = global_operator.read(
            '''SELECT a.ts_code from (SELECT DISTINCT ts_code from daily WHERE trade_date>20070101) a 
            LEFT JOIN (SELECT DISTINCT ts_code from daily_qfq)b on a.ts_code = b.ts_code WHERE b.ts_code is null''')
        code_list = df_code.iloc[:, 0].values.tolist()
        for ts_code in code_list:
            insert_sql = calc_sql_tmp.format(ts_code, ts_code, ts_code, end_date)
            insert_count = session.execute(insert_sql).rowcount
            print("ts_code:{},insert count:{}".format(ts_code, insert_count))
    # 计算增量数据
    dates_to_calc = global_operator.read(
        '''SELECT a.trade_date from (SELECT DISTINCT trade_date from adj_factor) a 
           LEFT JOIN (SELECT DISTINCT trade_date from daily_qfq)b on a.trade_date = b.trade_date 
           WHERE b.trade_date is null ORDER BY a.trade_date ASC''').iloc[:, 0].values.tolist()
    for date in dates_to_calc:
        insert_count = session.execute(
            "insert into daily_qfq select * from daily where trade_date={}".format(date)).rowcount
        print("trade_date:{},insert count:{}".format(date, insert_count))
        # 当天除权的股票需要重新计算
        code_list = global_operator.read(
            '''SELECT a.ts_code from 
            (SELECT * FROM adj_factor WHERE trade_date=(select max(trade_date) from adj_factor where trade_date<{}))a
            LEFT JOIN (SELECT * FROM adj_factor WHERE trade_date={}) b on a.ts_code=b.ts_code 
            WHERE a.adj_factor<>b.adj_factor'''
            .format(date, date)).iloc[:, 0].values.tolist()
        for ts_code in code_list:
            insert_sql = calc_sql_tmp.format(ts_code, ts_code, ts_code, date)
            insert_count = session.execute(insert_sql).rowcount
            print('ts_code:{},insert count:{}'.format(ts_code, insert_count))


if __name__ == '__main__':
    # RPS_indicator(250)
    calc_qfq()
