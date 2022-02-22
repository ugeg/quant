import akshare as ak

stock_zh_a_tick_tx_df = ak.stock_zh_a_tick_tx(code="sh600848", trade_date="20191011")
print(stock_zh_a_tick_tx_df)

# 当前交易日的分时数据可以通过下接口获取
stock_zh_a_tick_tx_js_df = ak.stock_zh_a_tick_tx_js(code="sz000001")
print(stock_zh_a_tick_tx_js_df)