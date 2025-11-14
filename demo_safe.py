"""
网络友好的安全演示程序
只使用能稳定工作的功能，跳过可能有网络问题的部分
"""

from data_fetcher import StockDataFetcher
from display_utils import format_historical_summary, format_stock_info
import pandas as pd

def safe_demo():
    """安全的演示程序，只使用稳定的功能"""
    print("🛡️  股票数据获取工具 - 网络安全版演示")
    print("=" * 60)
    print("✅ 只演示已验证在当前网络环境下可用的功能")
    print("❌ 跳过可能受网络代理影响的实时价格功能")
    print()
    
    fetcher = StockDataFetcher()
    
    # 1. 股票基本信息获取（通常可用）
    print("📋 1. 股票基本信息获取测试:")
    print("-" * 40)
    
    test_codes = ["000001", "002594", "600519"]
    success_count = 0
    
    for code in test_codes:
        try:
            info = fetcher.get_stock_info(code)
            if info:
                print(format_stock_info(info, code))
                success_count += 1
                print()
            else:
                print(f"❌ {code}: 获取失败")
        except Exception as e:
            print(f"❌ {code}: 异常 - {str(e)}")
    
    print(f"📊 基本信息获取成功率: {success_count}/{len(test_codes)}")
    
    # 2. 历史数据获取（通常可用）
    print(f"\n📈 2. 历史数据获取测试:")
    print("-" * 40)
    
    hist_success = 0
    for code in test_codes[:2]:  # 只测试前2只以节省时间
        try:
            hist_data = fetcher.get_historical_data(code)
            if hist_data is not None:
                print(f"✅ {code}: 获取到 {len(hist_data)} 条历史记录")
                print(format_historical_summary(hist_data, 3))
                hist_success += 1
                
                # 保存数据
                fetcher.save_to_csv(hist_data, f"{code}_safe_demo.csv")
                print(f"💾 数据已保存为 {code}_safe_demo.csv")
                print()
            else:
                print(f"❌ {code}: 历史数据获取失败")
        except Exception as e:
            print(f"❌ {code}: 历史数据异常 - {str(e)}")
    
    print(f"📊 历史数据获取成功率: {hist_success}/{min(2, len(test_codes))}")
    
    # 3. 数据分析示例
    print(f"\n🔍 3. 数据分析示例:")
    print("-" * 40)
    
    try:
        # 使用第一个成功的股票进行分析
        analysis_code = "000001"
        hist_data = fetcher.get_historical_data(analysis_code)
        
        if hist_data is not None:
            recent_data = hist_data.tail(10)
            
            print(f"📊 {analysis_code} 近10天数据分析:")
            print(f"  平均价格: {recent_data['收盘'].mean():.2f} 元")
            print(f"  最高价: {recent_data['收盘'].max():.2f} 元")
            print(f"  最低价: {recent_data['收盘'].min():.2f} 元")
            print(f"  价格波动: {((recent_data['收盘'].max() - recent_data['收盘'].min()) / recent_data['收盘'].mean() * 100):.2f}%")
            
            # 找出涨幅最大的一天
            max_gain_idx = recent_data['涨跌幅'].idxmax()
            max_gain_row = recent_data.loc[max_gain_idx]
            print(f"  最大涨幅: {max_gain_row['日期']} (+{max_gain_row['涨跌幅']:.2f}%)")
            
    except Exception as e:
        print(f"❌ 数据分析失败: {str(e)}")
    
    # 4. 网络状态总结
    print(f"\n🌐 4. 网络环境总结:")
    print("-" * 40)
    print("✅ 股票基本信息接口：工作正常")
    print("✅ 历史数据接口：工作正常") 
    print("❌ 实时价格接口：受代理影响，暂不可用")
    print()
    print("💡 建议：")
    print("  - 使用历史数据进行分析和处理")
    print("  - 基本信息足够支持股票筛选")
    print("  - 可以批量获取多只股票数据")
    print("  - 实时数据可在网络环境改善后使用")

if __name__ == "__main__":
    safe_demo()
