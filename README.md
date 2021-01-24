# quant
使用pyalgotrade进行回测 使用tushare获取数据

# 注意事项
1. mysql8.0需要在连接串上加auth_plugin=mysql_native_password
2. 表需COLLATE=utf8mb4_general_ci，utf8mb4_bin会出现TypeError: unhashable type: 'bytearray'