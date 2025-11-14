"""
测试数据显示格式
验证表格对齐效果
"""

from data_fetcher import StockDataFetcher
from display_utils import format_historical_summary, format_stock_info

def test_display():
    print("📊 数据显示格式测试")
    print("=" * 60)
    
    fetcher = StockDataFetcher()
    
    # 测试历史数据显示
    print("\n1. 历史数据格式测试:")
    hist_data = fetcher.get_historical_data("000001")
    if hist_data is not None:
        print(format_historical_summary(hist_data, 7))  # 显示最近7天
    
    print("\n" + "=" * 60)
    
    # 测试股票信息显示
    print("\n2. 股票信息格式测试:")
    info = fetcher.get_stock_info("000001")
    if info:
        print(format_stock_info(info, "000001"))
    
    print("\n" + "=" * 60)
    
    # 测试不同股票的数据
    print("\n3. 多股票数据格式测试:")
    test_codes = ["000001", "002594"]
    for code in test_codes:
        print(f"\n{code} 数据:")
        hist = fetcher.get_historical_data(code)
        if hist is not None:
            print(format_historical_summary(hist, 3))  # 只显示3天
        print("-" * 40)

if __name__ == "__main__":
    test_display()
