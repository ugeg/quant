/*
 Navicat Premium Data Transfer

 Source Server         : wsl
 Source Server Type    : MySQL
 Source Server Version : 80029
 Source Host           : localhost:3306
 Source Schema         : quant

 Target Server Type    : MySQL
 Target Server Version : 80029
 File Encoding         : 65001

 Date: 27/08/2022 14:34:24
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for adj_factor
-- ----------------------------
DROP TABLE IF EXISTS `adj_factor`;
CREATE TABLE `adj_factor`  (
  `ts_code` varchar(9) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '股票代码',
  `trade_date` varchar(8) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '交易日期',
  `adj_factor` float NULL DEFAULT NULL COMMENT '复权因子',
  PRIMARY KEY (`ts_code`, `trade_date`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for daily
-- ----------------------------
DROP TABLE IF EXISTS `daily`;
CREATE TABLE `daily`  (
  `ts_code` varchar(9) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '股票代码',
  `trade_date` varchar(8) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '交易日期',
  `open` float NULL DEFAULT NULL COMMENT '开盘价',
  `high` float NULL DEFAULT NULL COMMENT '最高价',
  `low` float NULL DEFAULT NULL COMMENT '最低价',
  `close` float NULL DEFAULT NULL COMMENT '收盘价',
  `pre_close` float NULL DEFAULT NULL COMMENT '昨收价',
  `change` float NULL DEFAULT NULL COMMENT '涨跌额',
  `pct_chg` float NULL DEFAULT NULL COMMENT '涨跌幅 （未复权）',
  `vol` float NULL DEFAULT NULL COMMENT '成交量 （手）',
  `amount` float NULL DEFAULT NULL COMMENT '成交额 （千元）',
  PRIMARY KEY (`ts_code`, `trade_date`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for daily_basic
-- ----------------------------
DROP TABLE IF EXISTS `daily_basic`;
CREATE TABLE `daily_basic`  (
  `ts_code` varchar(9) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT 'TS股票代码',
  `trade_date` varchar(8) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '交易日期',
  `close` float NULL DEFAULT NULL COMMENT '当日收盘价',
  `turnover_rate` float NULL DEFAULT NULL COMMENT '换手率（%）',
  `turnover_rate_f` float NULL DEFAULT NULL COMMENT '换手率（自由流通股）',
  `volume_ratio` float NULL DEFAULT NULL COMMENT '量比',
  `pe` float NULL DEFAULT NULL COMMENT '市盈率（总市值/净利润， 亏损的PE为空）',
  `pe_ttm` float NULL DEFAULT NULL COMMENT '市盈率（TTM，亏损的PE为空）',
  `pb` float NULL DEFAULT NULL COMMENT '市净率（总市值/净资产）',
  `ps` float NULL DEFAULT NULL COMMENT '市销率',
  `ps_ttm` float NULL DEFAULT NULL COMMENT '市销率（TTM）',
  `dv_ratio` float NULL DEFAULT NULL COMMENT '股息率 （%）',
  `dv_ttm` float NULL DEFAULT NULL COMMENT '股息率（TTM）（%）',
  `total_share` float NULL DEFAULT NULL COMMENT '总股本 （万股）',
  `float_share` float NULL DEFAULT NULL COMMENT '流通股本 （万股）',
  `free_share` float NULL DEFAULT NULL COMMENT '自由流通股本 （万）',
  `total_mv` float NULL DEFAULT NULL COMMENT '总市值 （万元）',
  `circ_mv` float NULL DEFAULT NULL COMMENT '流通市值（万元）',
  `limit_status` bigint NULL DEFAULT NULL,
  PRIMARY KEY (`ts_code`, `trade_date`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for futures_comm_info
-- ----------------------------
DROP TABLE IF EXISTS `futures_comm_info`;
CREATE TABLE `futures_comm_info`  (
  `交易所名称` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL,
  `合约名称` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL,
  `合约代码` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL,
  `现价` double NULL DEFAULT NULL,
  `涨停板` double NULL DEFAULT NULL,
  `跌停板` double NULL DEFAULT NULL,
  `保证金-买开` double NULL DEFAULT NULL,
  `保证金-卖开` double NULL DEFAULT NULL,
  `保证金-每手` double NULL DEFAULT NULL,
  `手续费标准-开仓-万分之` double NULL DEFAULT NULL,
  `手续费标准-开仓-元` double NULL DEFAULT NULL,
  `手续费标准-平昨-万分之` double NULL DEFAULT NULL,
  `手续费标准-平昨-元` double NULL DEFAULT NULL,
  `手续费标准-平今-万分之` double NULL DEFAULT NULL,
  `手续费标准-平今-元` double NULL DEFAULT NULL,
  `每跳毛利` bigint NULL DEFAULT NULL,
  `手续费` double NULL DEFAULT NULL,
  `每跳净利` double NULL DEFAULT NULL,
  `备注` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL,
  `手续费更新时间` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL,
  `价格更新时间` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for futures_daily
-- ----------------------------
DROP TABLE IF EXISTS `futures_daily`;
CREATE TABLE `futures_daily`  (
  `symbol` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL,
  `date` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL,
  `open` double NULL DEFAULT NULL,
  `high` double NULL DEFAULT NULL,
  `low` double NULL DEFAULT NULL,
  `close` double NULL DEFAULT NULL,
  `volume` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL,
  `open_interest` double NULL DEFAULT NULL,
  `turnover` double NULL DEFAULT NULL,
  `settle` double NULL DEFAULT NULL,
  `pre_settle` double NULL DEFAULT NULL,
  `variety` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for futures_diff
-- ----------------------------
DROP TABLE IF EXISTS `futures_diff`;
CREATE TABLE `futures_diff`  (
  `symbol2symbol` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL,
  `diffopen` double NULL DEFAULT NULL,
  `diffclose` double NULL DEFAULT NULL,
  `diffhigh` double NULL DEFAULT NULL,
  `difflow` double NULL DEFAULT NULL
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for index_basic
-- ----------------------------
DROP TABLE IF EXISTS `index_basic`;
CREATE TABLE `index_basic`  (
  `ts_code` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT 'TS代码',
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT '简称',
  `fullname` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT '指数全称',
  `market` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT '市场',
  `publisher` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT '发布方',
  `index_type` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT '指数风格',
  `category` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT '指数类别',
  `base_date` varchar(8) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT '基期',
  `base_point` float NULL DEFAULT NULL COMMENT '基点',
  `list_date` varchar(8) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT '发布日期',
  `weight_rule` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT '加权方式',
  `desc` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL COMMENT '描述',
  `exp_date` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT '终止日期',
  PRIMARY KEY (`ts_code`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for index_daily
-- ----------------------------
DROP TABLE IF EXISTS `index_daily`;
CREATE TABLE `index_daily`  (
  `ts_code` varchar(9) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT 'TS指数代码',
  `trade_date` varchar(8) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '交易日',
  `open` float NULL DEFAULT NULL COMMENT '开盘点位',
  `high` float NULL DEFAULT NULL COMMENT '最高点位',
  `low` float NULL DEFAULT NULL COMMENT '最低点位',
  `close` float NULL DEFAULT NULL COMMENT '收盘点位',
  `pre_close` float NULL DEFAULT NULL COMMENT '昨日收盘点',
  `change` float NULL DEFAULT NULL COMMENT '涨跌点',
  `pct_chg` float NULL DEFAULT NULL COMMENT '涨跌幅（%）',
  `vol` float NULL DEFAULT NULL COMMENT '成交量 （手）',
  `amount` float NULL DEFAULT NULL COMMENT '成交额 （千元）',
  PRIMARY KEY (`ts_code`, `trade_date`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for price_his
-- ----------------------------
DROP TABLE IF EXISTS `price_his`;
CREATE TABLE `price_his`  (
  `ts_code` varchar(9) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '股票代码',
  `start_date` varchar(8) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '开始日期',
  `end_date` varchar(8) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '开始日期',
  `price` float NOT NULL COMMENT '成交价',
  `volume` float NULL DEFAULT NULL COMMENT '成交量（股）',
  `percentage` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT '占比',
  PRIMARY KEY (`ts_code`, `start_date`, `end_date`, `price`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for rps_indicator
-- ----------------------------
DROP TABLE IF EXISTS `rps_indicator`;
CREATE TABLE `rps_indicator`  (
  `ts_code` varchar(9) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `trade_date` varchar(8) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `period` int NOT NULL,
  `increase` float NULL DEFAULT NULL,
  `rps` int NULL DEFAULT NULL,
  PRIMARY KEY (`ts_code`, `trade_date`, `period`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for stk_holdernumber
-- ----------------------------
DROP TABLE IF EXISTS `stk_holdernumber`;
CREATE TABLE `stk_holdernumber`  (
  `ts_code` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '股票代码',
  `ann_date` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT '公告日期',
  `end_date` varchar(8) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '截止日期',
  `holder_nums` int NULL DEFAULT NULL COMMENT '股东户数',
  `holder_num` int NULL DEFAULT NULL COMMENT '股东总户数（A+B）',
  PRIMARY KEY (`ts_code`, `end_date`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for stock_basic
-- ----------------------------
DROP TABLE IF EXISTS `stock_basic`;
CREATE TABLE `stock_basic`  (
  `ts_code` varchar(9) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'TS代码',
  `symbol` varchar(6) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '股票代码',
  `name` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '股票名称',
  `area` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '所在地域',
  `industry` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '所属行业',
  `fullname` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '	股票全称',
  `enname` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '英文全称',
  `cnspell` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '拼音缩写',
  `market` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '市场类型 （主板/中小板/创业板/科创板/CDR）',
  `exchange` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '交易所代码',
  `curr_type` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '	交易货币',
  `list_status` varchar(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '上市状态： L上市 D退市 P暂停上市',
  `list_date` varchar(8) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '上市日期',
  `delist_date` varchar(8) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '	退市日期',
  `is_hs` varchar(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '是否沪深港通标的，N否 H沪股通 S深股通',
  PRIMARY KEY (`ts_code`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for trade_cal
-- ----------------------------
DROP TABLE IF EXISTS `trade_cal`;
CREATE TABLE `trade_cal`  (
  `exchange` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `cal_date` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `is_open` bigint NULL DEFAULT NULL,
  `pretrade_date` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- View structure for rps
-- ----------------------------
DROP VIEW IF EXISTS `rps`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `rps` AS select `c`.`name` AS `name`,`c`.`industry` AS `industry`,`b`.`ts_code` AS `ts_code`,`b`.`rps_max` AS `rps_max`,`b`.`rps_min` AS `rps_min` from (((select `rps_indicator`.`ts_code` AS `ts_code`,max(`rps_indicator`.`rps`) AS `rps_max`,min(`rps_indicator`.`rps`) AS `rps_min` from `rps_indicator` where ((`rps_indicator`.`trade_date` > date_format((curdate() - interval 2 month),'%Y%m%d')) and (`rps_indicator`.`trade_date` <= date_format((curdate() - interval 1 month),'%Y%m%d'))) group by `rps_indicator`.`ts_code` having ((`rps_max` <= 90) and (`rps_min` >= 80))) `a` join (select `rps_indicator`.`ts_code` AS `ts_code`,max(`rps_indicator`.`rps`) AS `rps_max`,min(`rps_indicator`.`rps`) AS `rps_min` from `rps_indicator` where ((`rps_indicator`.`trade_date` > date_format((curdate() - interval 1 month),'%Y%m%d')) and (`rps_indicator`.`trade_date` <= curdate())) group by `rps_indicator`.`ts_code` having ((`rps_max` > 90) and (`rps_min` >= 85))) `b` on((`a`.`ts_code` = `b`.`ts_code`))) left join `stock_basic` `c` on((`a`.`ts_code` = `c`.`ts_code`)));

SET FOREIGN_KEY_CHECKS = 1;
