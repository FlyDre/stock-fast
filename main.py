"""
股票数据获取主程序
支持实时价格获取、历史数据获取和数据导出功能
"""

import argparse
import sys
from datetime import datetime
from data_fetcher import StockDataFetcher
from config import STOCK_CODES

def main():
    """主程序入口"""
    parser = argparse.ArgumentParser(description='股票数据获取工具')
    parser.add_argument('--mode', choices=['realtime', 'historical', 'both'], 
                       default='realtime', help='数据获取模式')
    parser.add_argument('--codes', nargs='*', 
                       help='股票代码列表（空格分隔），不指定则使用配置文件中的默认列表')
    parser.add_argument('--start', help='历史数据开始日期 (YYYYMMDD)')
    parser.add_argument('--end', help='历史数据结束日期 (YYYYMMDD)')
    parser.add_argument('--save', action='store_true', help='保存数据到文件')
    
    args = parser.parse_args()
    
    # 确定要获取的股票代码
    stock_codes = args.codes if args.codes else STOCK_CODES
    
    print(f"开始获取股票数据...")
    print(f"目标股票: {', '.join(stock_codes)}")
    print(f"获取模式: {args.mode}")
    print("-" * 50)
    
    # 初始化数据获取器
    fetcher = StockDataFetcher()
    
    if args.mode in ['realtime', 'both']:
        print("\n📈 获取实时价格数据...")
        realtime_data = fetcher.get_multiple_stocks_realtime(stock_codes)
        
        if realtime_data:
            print("\n实时价格信息:")
            print(f"{'股票代码':<8} {'股票名称':<12} {'最新价':<10} {'涨跌幅':<10} {'成交量':<15}")
            print("-" * 65)
            for code, data in realtime_data.items():
                volume_str = f"{data['volume']:,.0f}"
                change_str = f"{data['change']:+.2f}%"
                print(f"{code:<8} {data['name']:<12} {data['price']:<10.2f} {change_str:<10} {volume_str:<15}")
                
            if args.save:
                # 保存实时数据
                import pandas as pd
                df = pd.DataFrame(list(realtime_data.values()))
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                fetcher.save_to_csv(df, f'realtime_data_{timestamp}.csv')
        else:
            print("❌ 未获取到实时数据")
    
    if args.mode in ['historical', 'both']:
        print("\n📊 获取历史数据...")
        historical_data = fetcher.get_multiple_stocks_historical(stock_codes)
        
        if historical_data:
            print("\n历史数据获取完成:")
            for code, df in historical_data.items():
                print(f"- {code}: {len(df)} 条记录")
                
                if args.save:
                    # 保存历史数据
                    fetcher.save_to_csv(df, f'{code}_historical_data.csv')
        else:
            print("❌ 未获取到历史数据")
    
    print("\n✅ 数据获取完成！")

def demo():
    """演示函数，展示各种功能的使用方法"""
    print("股票数据获取工具演示")
    print("=" * 50)
    
    # 初始化数据获取器
    fetcher = StockDataFetcher()
    
    # 演示1: 获取单只股票实时价格（网络环境可能不支持）
    print("\n1. 获取单只股票实时价格示例:")
    print("  ⚠️  注意：实时价格功能可能因网络代理设置而不可用")
    print("  💡 跳过实时价格获取，展示其他可用功能...")
    
    # 演示2: 获取股票基本信息
    print("\n2. 获取股票基本信息示例:")
    info = fetcher.get_stock_info("601127")
    if info:
        print(f"  股票简称: {info.get('股票简称', 'N/A')}")
        print(f"  总市值: {info.get('总市值', 'N/A')}")
    
    # 演示3: 获取历史数据
    print("\n3. 获取历史数据示例:")
    hist_data = fetcher.get_historical_data("601127")
    if hist_data is not None:
        print(f"  历史数据记录数: {len(hist_data)}")
        print("  最近5天数据:")
        # 选择主要列并格式化显示
        display_data = hist_data.tail()[['日期', '开盘', '收盘', '最高', '最低', '涨跌幅', '成交量']].copy()
        # 格式化数值显示
        display_data['开盘'] = display_data['开盘'].apply(lambda x: f"{x:.2f}")
        display_data['收盘'] = display_data['收盘'].apply(lambda x: f"{x:.2f}")
        display_data['最高'] = display_data['最高'].apply(lambda x: f"{x:.2f}")
        display_data['最低'] = display_data['最低'].apply(lambda x: f"{x:.2f}")
        display_data['涨跌幅'] = display_data['涨跌幅'].apply(lambda x: f"{x:+.2f}%")
        display_data['成交量'] = display_data['成交量'].apply(lambda x: f"{x:,.0f}")
        
        print(display_data.to_string(index=False, justify='center'))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 带参数：走命令行数据获取流程
        main()
    else:
        # 无参数：启动统一 UI
        import tkinter as tk
        from unified_ui import UnifiedStockApp

        root = tk.Tk()
        app = UnifiedStockApp(root)
        root.mainloop()
