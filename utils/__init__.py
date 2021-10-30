# -*- coding: utf-8 -*-
# @Author  : pengj    <ugeg@163.com>
# @Time    : 2020/7/8 22:53
# @File    : __init__.py
from sqlalchemy.orm import Session
import utils.conf
import utils.mysql_util
import utils.global_operator
utils.conf.init_config()
mysql_config = utils.conf.mysql_config
mysql_connector = utils.mysql_util.MysqlConnector(mysql_config.ip, mysql_config.user, mysql_config.passwd,
                                                  mysql_config.db)
mysql_engine = mysql_connector.engine
session = Session(mysql_engine, autocommit=True)
utils.global_operator.load_code2name(session)
