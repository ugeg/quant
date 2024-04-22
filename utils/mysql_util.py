# -*- coding: utf-8 -*-
# @Author  : pengj    <ugeg@163.com>
# @Time    : 2020/7/8 21:55
# @File    : mysql_util.py

import pymysql
import sqlalchemy
from sqlalchemy import func
from sqlalchemy.orm import Session
from utils import entity
from utils.entity import Daily

# mysql_sqlalchemy_url = "mysql+mysqlconnector://{}:{}@{}:{}/{}?auth_plugin=mysql_native_password"
mysql_sqlalchemy_url = "mysql+pymysql://jing:123456@127.0.0.1:3306/test"
mysql_sqlalchemy_url = "mysql+pymysql://{}:{}@{}:{}/{}"


class MysqlConnector:
    def __init__(self, host: str, user: str, passwd: str, db: str, port: int = 3306, charset: str = 'utf8'):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.db = db
        self.host = host
        self.port = port
        self.charset = charset
        # mysql8.0以上默认加密方式变了，需要执行 ALTER USER 'jing'@'*' IDENTIFIED WITH mysql_native_password BY '123456';
        self.sqlalchemy_url = mysql_sqlalchemy_url.format(user, passwd, host, port, db)
        self.engine = sqlalchemy.create_engine(self.sqlalchemy_url, echo=False,
                                               )  # type: sqlalchemy.engine.Engine

    def create_connect(self):
        self.connect = pymysql.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, db=self.db,
                                       charset=self.charset)

    def query(self, sql):
        cursor = self.connect.cursor()
        cursor.execute(sql)
        data = cursor.fetchall()
        return data

    def insert(self, sql):
        cursor = self.connect.cursor()
        cursor.execute(sql)

    def insert(self, sql, param):
        cursor = self.connect.cursor()
        cursor.executemany(sql, param)

    def query_count(self, table_name):
        cursor = self.connect.cursor()
        cursor.execute("select count(1) as cnt from " + table_name)
        data = cursor.fetchone()
        return data[0]

    def truncate(self, table_name):
        with self.engine.connect() as connect:
            connect.execute("truncate " + table_name)

    def close(self):
        self.connect.close()


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
    mysql_util = MysqlConnector("localhost", "jing", "123456", "quant")
    # with mysql_util.engine.connect() as conn:
    #     conn.execute("truncate stock_basic")
    print("gg")
    session = Session(mysql_util.engine)
    # query = session.query(entity.StockBasic)
    # query = session.query(entity.Daily).filter(entity.Daily.trade_date == 20200103).first()
    # # clause = select(entity.StockBasic)
    # print(query)
    # print(select(Daily.amount))
    result = session.execute("select max(trade_date) as trade_date from daily").scalar()
    print(result)
    count = session.query(func.count(entity.StockBasic.ts_code)).one()
    print(count[0])
    date_all = session.query(Daily.ts_code, func.max(Daily.trade_date)).group_by(Daily.ts_code).all()
    dict(date_all)
    for row in date_all:
        print(row)
    # conn = mysql_util.create_connect()
    # print(mysql_util.query("select * from user"))
    # # 创建一个 dataframe格式 数据
    # df_data = pd.DataFrame([[1.2, '54513', 116.47, 39.8069, 31.3, 'LC']],
    #                        columns=['file_version', 'station_id', 'lon', 'lat', 'alt', 'radar_type'])
    #
    # # 写入数据库，如果已存在该表，则追加写入数据，不加索引
    # df_data.to_sql(name="test1", con=mysql_util.engine.connect(), if_exists='append', index=False)
