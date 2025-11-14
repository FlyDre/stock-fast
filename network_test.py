"""
网络连接测试工具
用于检测网络状态和数据源可用性
"""

import requests
import akshare as ak
from data_fetcher import StockDataFetcher

def test_network():
    """测试网络连接"""
    print("🌐 网络连接测试...")
    
    # 测试基本网络连接
    try:
        response = requests.get("https://www.baidu.com", timeout=5)
        if response.status_code == 200:
            print("✅ 基本网络连接正常")
        else:
            print("❌ 基本网络连接异常")
            return False
    except Exception as e:
        print(f"❌ 基本网络连接失败: {str(e)}")
        return False
    
    return True

def test_akshare():
    """测试AkShare数据获取"""
    print("\n📊 AkShare数据源测试...")
    
    fetcher = StockDataFetcher()
    
    # 测试股票基本信息获取
    print("  测试1: 获取股票基本信息...")
    try:
        info = fetcher.get_stock_info("000001")
        if info:
            print(f"  ✅ 股票信息获取成功: {info.get('股票简称', 'N/A')}")
        else:
            print("  ❌ 股票信息获取失败")
    except Exception as e:
        print(f"  ❌ 股票信息获取异常: {str(e)}")
    
    # 测试历史数据获取
    print("  测试2: 获取历史数据...")
    try:
        hist_data = fetcher.get_historical_data("000001")
        if hist_data is not None and not hist_data.empty:
            print(f"  ✅ 历史数据获取成功: {len(hist_data)} 条记录")
            print(f"  📋 数据列: {list(hist_data.columns)}")
        else:
            print("  ❌ 历史数据获取失败")
    except Exception as e:
        print(f"  ❌ 历史数据获取异常: {str(e)}")
    
    # 测试实时数据获取
    print("  测试3: 获取实时价格...")
    try:
        price_data = fetcher.get_realtime_price("000001")
        if price_data:
            print(f"  ✅ 实时价格获取成功: {price_data['name']} - {price_data['price']}元")
        else:
            print("  ❌ 实时价格获取失败")
    except Exception as e:
        print(f"  ❌ 实时价格获取异常: {str(e)}")

def test_alternative_method():
    """测试替代获取方法"""
    print("\n🔄 测试替代数据获取方法...")
    
    try:
        # 使用不同的AkShare接口
        print("  测试A股实时行情接口...")
        df = ak.stock_zh_a_spot_em()
        if df is not None and not df.empty:
            print(f"  ✅ A股实时行情获取成功，共 {len(df)} 只股票")
            # 显示部分数据
            sample = df.head(3)
            print("  📋 样例数据:")
            for _, row in sample.iterrows():
                print(f"    {row['代码']} {row['名称']}: {row['最新价']}元")
        else:
            print("  ❌ A股实时行情获取失败")
    except Exception as e:
        print(f"  ❌ A股实时行情获取异常: {str(e)}")

if __name__ == "__main__":
    print("股票数据获取系统诊断工具")
    print("=" * 50)
    
    # 运行所有测试
    if test_network():
        test_akshare()
        test_alternative_method()
    
    print("\n🏁 诊断完成！")
    print("\n💡 如果遇到网络问题，请检查:")
    print("  1. 网络连接是否正常")
    print("  2. 是否使用了代理设置")
    print("  3. 防火墙是否阻止了连接")
    print("  4. 稍后重试，数据源可能暂时不可用")
