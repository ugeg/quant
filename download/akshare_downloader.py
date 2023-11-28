import akshare as ak

# stock_zh_a_tick_tx_df = ak.stock_zh_a_tick_tx(code="sh600848", trade_date="20191011")
# print(stock_zh_a_tick_tx_df)
#
# # 当前交易日的分时数据可以通过下接口获取
# stock_zh_a_tick_tx_js_df = ak.stock_zh_a_tick_tx_js(code="sz000001")
# print(stock_zh_a_tick_tx_js_df)

# 实时行情
# stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
# print(stock_zh_a_spot_em_df)
#分红配送

# stock_fhps_em_df = ak.stock_fhps_em(date="20211231")
# print(stock_fhps_em_df)


js_news_df = ak.js_news(timestamp="2022-12-08 21:57:18")
print(js_news_df)