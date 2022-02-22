DROP TABLE IF EXISTS stock_basic;
CREATE TABLE `stock_basic` (
  `ts_code` varchar(9)  COMMENT 'TS代码',
  `symbol` varchar(6)  COMMENT '股票代码',
  `name` varchar(10)  COMMENT '股票名称',
  `area` varchar(10)  COMMENT '所在地域',
  `industry` varchar(10)  COMMENT '所属行业',
  `fullname` varchar(100)  COMMENT '	股票全称',
  `enname` varchar(100)  COMMENT '英文全称',
  `market` varchar(10)  COMMENT '市场类型 （主板/中小板/创业板/科创板/CDR）',
  `exchange` varchar(10)  COMMENT '交易所代码',
  `curr_type` varchar(10)  COMMENT '	交易货币',
  `list_status` varchar(1)  COMMENT '上市状态： L上市 D退市 P暂停上市',
  `list_date` varchar(8)  COMMENT '上市日期',
  `delist_date` varchar(8)  COMMENT '	退市日期',
  `is_hs` varchar(1)  COMMENT '是否沪深港通标的，N否 H沪股通 S深股通',
  PRIMARY KEY (`ts_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `daily`;
CREATE TABLE `daily` (
  `ts_code` varchar(9) COMMENT '股票代码',
  `trade_date` varchar(8) COMMENT '交易日期',
  `open` float COMMENT '开盘价',
  `high` float COMMENT '最高价',
  `low` float COMMENT '最低价',
  `close` float COMMENT '收盘价',
  `pre_close` float COMMENT '昨收价',
  `change` float COMMENT '涨跌额',
  `pct_chg` float COMMENT '涨跌幅 （未复权）',
  `vol` float COMMENT '成交量 （手）',
  `amount` float COMMENT '成交额 （千元）',
  PRIMARY KEY (`ts_code`,`trade_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `rps_indicator`;
CREATE TABLE `rps_indicator` (
  `ts_code` varchar(9) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `trade_date` varchar(8) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `period` int NOT NULL,
  `increase` float DEFAULT NULL,
  `rps` int DEFAULT NULL,
  PRIMARY KEY (`ts_code`,`trade_date`,`period`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;