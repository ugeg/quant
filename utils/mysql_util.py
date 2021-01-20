# -*- coding: utf-8 -*-
# @Author  : pengj    <ugeg@163.com>
# @Time    : 2020/7/8 21:55
# @File    : mysql_util.py
import pymysql
from sqlalchemy import create_engine
import pandas as pd

class MysqlUtil:
    def __init__(self, host: str, user: str, passwd: str, db: str, port: int = 3306, charset: str = 'utf8'):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.db = db
        self.host = host
        self.port = port
        self.charset = charset
        # mysql8.0以上默认加密方式变了，需要执行 ALTER USER 'jing'@'*' IDENTIFIED WITH mysql_native_password BY '123456';
        self.sqlalchemy_url = "mysql+mysqlconnector://{}:{}@{}:{}/{}?auth_plugin=mysql_native_password".format(user, passwd, host, port, db)

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
        cursor.execute("select count(1) as cnt from "+table_name)
        data = cursor.fetchone()
        return data[0]
    def truncate(self, table_name):
        cursor = self.connect.cursor()
        cursor.execute("truncate "+table_name)
    def create_engine(self):
        engine = create_engine(self.sqlalchemy_url)
        return engine

    def close(self):
        self.connect.close()


if __name__ == '__main__':
    mysql_util = MysqlUtil("localhost", "jing", "123456", "test")
    conn = mysql_util.create_connect()
    print(mysql_util.query("select * from user"))
    # 创建一个 dataframe格式 数据
    df_data = pd.DataFrame([[1.2, '54513', 116.47, 39.8069, 31.3, 'LC']],
                           columns=['file_version', 'station_id', 'lon', 'lat', 'alt', 'radar_type'])

    # 写入数据库，如果已存在该表，则追加写入数据，不加索引
    df_data.to_sql(name="test1", con=mysql_util.create_engine(), if_exists='append', index=False)