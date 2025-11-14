"""
数据显示格式化工具
提供美观的表格显示功能
"""

import pandas as pd
from typing import Dict, List

def format_stock_realtime_table(realtime_data: Dict) -> str:
    """
    格式化实时股票数据为美观的表格
    
    Args:
        realtime_data: 实时数据字典
        
    Returns:
        格式化的表格字符串
    """
    if not realtime_data:
        return "暂无实时数据"
    
    # 表头
    header = f"{'股票代码':<8} {'名称':<10} {'最新价':<10} {'涨跌幅':<10} {'成交量(万)':<12} {'成交额(亿)':<10}"
    separator = "-" * 70
    
    # 数据行
    rows = []
    for code, data in realtime_data.items():
        volume_wan = data['volume'] / 10000  # 转换为万
        amount_yi = data['amount'] / 100000000  # 转换为亿
        change_str = f"{data['change']:+.2f}%"
        
        row = f"{code:<8} {data['name']:<10} {data['price']:<10.2f} {change_str:<10} {volume_wan:<12.2f} {amount_yi:<10.2f}"
        rows.append(row)
    
    return "\n".join([header, separator] + rows)

def format_historical_summary(hist_data: pd.DataFrame, days: int = 5) -> str:
    """
    格式化历史数据摘要显示
    
    Args:
        hist_data: 历史数据DataFrame
        days: 显示天数
        
    Returns:
        格式化的历史数据字符串
    """
    if hist_data is None or hist_data.empty:
        return "暂无历史数据"
    
    # 获取最近N天数据
    recent_data = hist_data.tail(days).copy()
    
    # 格式化显示
    result = []
    result.append(f"📊 最近{days}天交易数据:")
    result.append("-" * 80)
    
    # 表头
    header = f"{'日期':<12} {'开盘':<8} {'收盘':<8} {'最高':<8} {'最低':<8} {'涨跌幅':<10} {'成交量(万)':<12}"
    result.append(header)
    result.append("-" * 80)
    
    # 数据行
    for _, row in recent_data.iterrows():
        volume_wan = row['成交量'] / 10000
        change_str = f"{row['涨跌幅']:+.2f}%"
        
        # 确保日期格式正确显示
        date_str = str(row['日期'])
        if len(date_str) > 12:
            date_str = date_str[:12]
        
        data_row = f"{date_str:<12} {row['开盘']:<8.2f} {row['收盘']:<8.2f} {row['最高']:<8.2f} {row['最低']:<8.2f} {change_str:<10} {volume_wan:<12.1f}"
        result.append(data_row)
    
    return "\n".join(result)

def format_stock_info(info: Dict, code: str) -> str:
    """
    格式化股票基本信息显示
    
    Args:
        info: 股票信息字典
        code: 股票代码
        
    Returns:
        格式化的信息字符串
    """
    if not info:
        return f"未获取到 {code} 的基本信息"
    
    result = []
    result.append(f"🏢 {code} - {info.get('股票简称', 'N/A')} 基本信息:")
    result.append("-" * 50)
    
    # 格式化市值显示
    total_mv = info.get('总市值', 0)
    if isinstance(total_mv, (int, float)) and total_mv > 0:
        total_mv_yi = total_mv / 100000000
        result.append(f"  总市值: {total_mv_yi:.2f} 亿元")
    
    # 其他信息
    info_items = [
        ('流通市值', '流通市值'),
        ('市盈率', '市盈率-动态'),
        ('市净率', '市净率'),
        ('ROE', 'ROE'),
        ('每股收益', '每股收益'),
    ]
    
    for display_name, key in info_items:
        value = info.get(key, 'N/A')
        if isinstance(value, (int, float)) and display_name == '流通市值':
            value = f"{value / 100000000:.2f} 亿元"
        elif isinstance(value, (int, float)):
            value = f"{value:.2f}"
        result.append(f"  {display_name}: {value}")
    
    return "\n".join(result)

def format_multi_stock_comparison(data_dict: Dict[str, Dict]) -> str:
    """
    格式化多股票对比显示
    
    Args:
        data_dict: 多股票数据字典
        
    Returns:
        格式化的对比表格
    """
    if not data_dict:
        return "暂无对比数据"
    
    result = []
    result.append("📊 股票对比分析:")
    result.append("=" * 80)
    
    header = f"{'代码':<8} {'名称':<12} {'现价':<8} {'涨跌幅':<10} {'市值(亿)':<10} {'成交量(万)':<12}"
    result.append(header)
    result.append("-" * 80)
    
    for code, data in data_dict.items():
        if 'price' in data:  # 实时数据
            volume_wan = data.get('volume', 0) / 10000
            change_str = f"{data.get('change', 0):+.2f}%"
            
            # 简化市值显示
            mv_str = "N/A"
            
            row = f"{code:<8} {data.get('name', 'N/A'):<12} {data.get('price', 0):<8.2f} {change_str:<10} {mv_str:<10} {volume_wan:<12.1f}"
            result.append(row)
    
    return "\n".join(result)

if __name__ == "__main__":
    # 测试显示格式
    print("数据显示格式化工具测试")
    print("=" * 50)
    
    # 模拟数据测试
    test_realtime = {
        "000001": {
            "name": "平安银行",
            "price": 11.65,
            "change": 0.52,
            "volume": 1500000,
            "amount": 175000000
        }
    }
    
    print(format_stock_realtime_table(test_realtime))
