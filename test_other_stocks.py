from data_fetcher import StockDataFetcher

fetcher = StockDataFetcher()

# 测试其他股票代码
codes = ["002594", "300750"]
names = ["比亚迪", "宁德时代"]

for code, expected_name in zip(codes, names):
    info = fetcher.get_stock_info(code)
    if info:
        print(f"{code}: {info.get('股票简称', 'N/A')} - 总市值: {info.get('总市值', 'N/A')}")
    else:
        print(f"{code}: 获取信息失败")
