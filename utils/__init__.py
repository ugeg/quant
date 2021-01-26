# -*- coding: utf-8 -*-
# @Author  : pengj    <ugeg@163.com>
# @Time    : 2020/7/8 22:53
# @File    : __init__.py
import utils.conf
import utils.mysql_util
utils.conf.init_config()
mysql_config = utils.conf.mysql_config
mysql_connector = utils.mysql_util.MysqlConnector(mysql_config.ip, mysql_config.user, mysql_config.passwd, mysql_config.db)