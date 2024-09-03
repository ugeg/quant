# -*- coding: utf-8 -*-
# @Author  : pengj    <ugeg@163.com>
# @Time    : 2020/7/8 21:55
# @File    : mysql_util.py

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

import config

# mysql_sqlalchemy_url = "mysql+mysqlconnector://{}:{}@{}:{}/{}?auth_plugin=mysql_native_password"
# mysql_sqlalchemy_url = "mysql+pymysql://jing:123456@127.0.0.1:3306/test"
# mysql_sqlalchemy_url = "mysql+pymysql://{}:{}@{}:{}/{}"

engine = create_engine(config.mysql_url, echo=False,pool_pre_ping=True,pool_recycle=1800)
session = sessionmaker(bind=engine,expire_on_commit=False,class_=Session)
# async_session = sessionmaker(bind=engine,expire_on_commit=False,class_=AsyncSession)


def mysql_replace_into(table, conn, keys, data_iter):
    from sqlalchemy.ext.compiler import compiles
    from sqlalchemy.sql.expression import Insert

    @compiles(Insert)
    def replace_string(insert, compiler, **kw):
        s = compiler.visit_insert(insert, **kw)
        s = s.replace("INSERT INTO", "REPLACE INTO")
        return s

    data = [dict(zip(keys, row)) for row in data_iter]

    conn.execute(table.table.insert(), data)


if __name__ == '__main__':
    with session() as sess:
        result = sess.execute(text("select 1")).first()
        print(result)
    # mysql_util = MysqlConnector("localhost", "jing", "123456", "quant")
    # # with mysql_util.engine.connect() as conn:
    # #     conn.execute("truncate stock_basic")
    # print("gg")
    # session = Session(mysql_util.engine)
    # # query = session.query(entity.StockBasic)
    # # query = session.query(entity.Daily).filter(entity.Daily.trade_date == 20200103).first()
    # # # clause = select(entity.StockBasic)
    # # print(query)
    # # print(select(Daily.amount))
    # result = session.execute("select max(trade_date) as trade_date from daily").scalar()
    # print(result)
    # count = session.query(func.count(entity.StockBasic.ts_code)).one()
    # print(count[0])
    # date_all = session.query(Daily.ts_code, func.max(Daily.trade_date)).group_by(Daily.ts_code).all()
    # dict(date_all)
    # for row in date_all:
    #     print(row)
    # conn = mysql_util.create_connect()
    # print(mysql_util.query("select * from user"))
    # # 创建一个 dataframe格式 数据
    # df_data = pd.DataFrame([[1.2, '54513', 116.47, 39.8069, 31.3, 'LC']],
    #                        columns=['file_version', 'station_id', 'lon', 'lat', 'alt', 'radar_type'])
    #
    # # 写入数据库，如果已存在该表，则追加写入数据，不加索引
    # df_data.to_sql(name="test1", con=mysql_util.engine.connect(), if_exists='append', index=False)
