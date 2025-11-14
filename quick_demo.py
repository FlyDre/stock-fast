"""
快速演示程序 - 展示核心功能
重点演示已验证可以正常工作的功能
"""

from data_fetcher import StockDataFetcher
from config import STOCK_CODES
from display_utils import format_historical_summary, format_stock_info, format_stock_realtime_table
import pandas as pd

def demo_basic_info():
    """演示获取股票基本信息"""
    print("🏢 股票基本信息获取演示")
    print("-" * 40)
    
    fetcher = StockDataFetcher()
    
    # 获取几只主要股票的基本信息
    demo_codes = ["000001", "600036", "600519"]
    
    for code in demo_codes:
        info = fetcher.get_stock_info(code)
        if info:
            print(format_stock_info(info, code))
            print()

def demo_historical_data():
    """演示获取历史数据"""
    print("📈 历史数据获取演示")
    print("-" * 40)
    
    fetcher = StockDataFetcher()
    
    # 获取平安银行近期历史数据
    hist_data = fetcher.get_historical_data("000001")
    if hist_data is not None:
        print(f"📋 获取到 {len(hist_data)} 条历史数据")
        print()
        print(format_historical_summary(hist_data, 5))
        
        # 保存数据示例
        fetcher.save_to_csv(hist_data, "demo_historical_data_formatted.csv")
        print(f"\n💾 数据已保存到 data/demo_historical_data_formatted.csv")

def demo_batch_historical():
    """演示批量获取历史数据"""
    print("\n🔄 批量获取历史数据演示")
    print("-" * 40)
    
    fetcher = StockDataFetcher()
    
    # 批量获取配置文件中的股票历史数据
    demo_codes = STOCK_CODES[:3]  # 只获取前3只股票以节省时间
    print(f"正在获取股票: {', '.join(demo_codes)}")
    
    historical_data = fetcher.get_multiple_stocks_historical(demo_codes)
    
    if historical_data:
        print("\n📊 批量获取结果:")
        for code, df in historical_data.items():
            if df is not None:
                print(f"  {code}: {len(df)} 条记录")
                # 保存每只股票的数据
                fetcher.save_to_csv(df, f"{code}_batch_demo.csv")
        
        print(f"\n💾 所有数据已保存到 data/ 目录")

def demo_data_analysis():
    """演示简单的数据分析"""
    print("\n🔍 数据分析演示")
    print("-" * 40)
    
    fetcher = StockDataFetcher()
    
    # 获取数据并进行简单分析
    hist_data = fetcher.get_historical_data("000001")
    if hist_data is not None:
        # 计算一些基本统计信息
        recent_data = hist_data.tail(30)  # 最近30天
        
        avg_price = recent_data['收盘'].mean()
        max_price = recent_data['收盘'].max()
        min_price = recent_data['收盘'].min()
        total_volume = recent_data['成交量'].sum()
        
        print("📊 平安银行 (000001) 近30天数据分析:")
        print(f"  平均收盘价: {avg_price:.2f} 元")
        print(f"  最高价: {max_price:.2f} 元")
        print(f"  最低价: {min_price:.2f} 元")
        print(f"  总成交量: {total_volume:,.0f}")
        
        # 找出涨幅最大的交易日
        max_gain_day = recent_data.loc[recent_data['涨跌幅'].idxmax()]
        print(f"  最大涨幅日: {max_gain_day['日期']} (+{max_gain_day['涨跌幅']:.2f}%)")

if __name__ == "__main__":
    print("股票数据获取工具 - 功能演示")
    print("=" * 50)
    print("✅ 注意：此演示展示已验证可以正常工作的功能")
    print("❗ 实时价格功能可能因网络环境而无法使用")
    print()
    
    try:
        # 运行各个演示
        demo_basic_info()
        demo_historical_data()
        demo_batch_historical()
        demo_data_analysis()
        
        print("\n🎉 演示完成！")
        print("\n📁 查看 data/ 目录可以看到保存的CSV文件")
        print("💡 这些数据可以用于后续的分析和处理工作")
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {str(e)}")
        print("💡 请检查网络连接或稍后重试")
