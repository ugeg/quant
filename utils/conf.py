# -*- coding: utf-8 -*-
# @Author  : pengj    <ugeg@163.com>
# @Time    : 2021/1/20 22:06
# @File    : conf.py
import os

import yaml


class MysqlConfig:

    def __repr__(self) -> str:
        return "MsqlConfig:[ip:%s,port:%s]" % (self.ip, self.port)

    def __init__(self, ip, port, user, passwd, db):
        self.ip = ip
        self.port = port
        self.user = user
        self.passwd = passwd
        self.db = db


mysql_config: MysqlConfig = None
tushare_token: str = None


def init_config():
    global mysql_config
    global tushare_token
    if mysql_config is not None:
        print("mysql_config is already set")
        return
    file_path = os.path.abspath(__file__)[:-13] + 'conf.yaml'
    root_conf = load_yaml_config(file_path)
    mysql = root_conf.get("mysql")
    mysql_config = MysqlConfig(mysql.get("ip"), mysql.get("port"), mysql.get("user"), mysql.get("passwd"),
                               mysql.get("db"))
    tushare = root_conf.get("tushare")
    tushare_token = tushare.get("token")


def load_yaml_config(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as f:  # 打开yaml文件
        cfg = f.read()
        return yaml.load(cfg, Loader=yaml.FullLoader)  # 将数据转换成python字典行驶输出，存在多个文件时，用load_all，单个的时候load就可以


if __name__ == '__main__':
    print(os.path.abspath(__file__)[:-13] + 'conf.yaml')
    # init_config()
    # print(mysql_config)
    # print(tushare_token)
