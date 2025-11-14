"""
股票数据获取核心模块
基于AkShare实现股票数据的获取、处理和存储
"""

import akshare as ak
import pandas as pd
import time
import logging
from datetime import datetime, date
from typing import List, Dict, Optional
import os
from config import *

class StockDataFetcher:
    """股票数据获取器"""
    
    def __init__(self):
        """初始化数据获取器"""
        self.setup_logging()
        self.ensure_directories()
        
    def setup_logging(self):
        """设置日志"""
        os.makedirs(LOG_DIR, exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'{LOG_DIR}/stock_fetcher.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def ensure_directories(self):
        """确保必要的目录存在"""
        os.makedirs(DATA_DIR, exist_ok=True)
        os.makedirs(LOG_DIR, exist_ok=True)
        
    def get_stock_info(self, stock_code: str) -> Optional[Dict]:
        """
        获取股票基本信息
        
        Args:
            stock_code: 股票代码
            
        Returns:
            股票信息字典或None
        """
        for attempt in range(RETRY_TIMES):
            try:
                # 获取股票信息
                stock_info = ak.stock_individual_info_em(symbol=stock_code)
                if stock_info is not None and not stock_info.empty:
                    result = {}
                    for _, row in stock_info.iterrows():
                        result[row['item']] = row['value']
                    
                    self.logger.info(f"成功获取股票 {stock_code} 基本信息")
                    return result
                    
            except Exception as e:
                self.logger.warning(f"获取股票 {stock_code} 信息失败，第 {attempt + 1} 次尝试: {str(e)}")
                if attempt < RETRY_TIMES - 1:
                    time.sleep(RETRY_DELAY)
                    
        self.logger.error(f"获取股票 {stock_code} 信息最终失败")
        return None
        
    def get_realtime_price(self, stock_code: str) -> Optional[Dict]:
        """
        获取股票实时价格
        
        Args:
            stock_code: 股票代码
            
        Returns:
            实时价格信息字典或None
        """
        for attempt in range(RETRY_TIMES):
            try:
                # 获取实时行情
                df = ak.stock_zh_a_spot_em()
                stock_data = df[df['代码'] == stock_code]
                
                if not stock_data.empty:
                    row = stock_data.iloc[0]
                    result = {
                        'code': stock_code,
                        'name': row['名称'],
                        'price': float(row['最新价']),
                        'change': float(row['涨跌幅']),
                        'change_amount': float(row['涨跌额']),
                        'volume': float(row['成交量']),
                        'amount': float(row['成交额']),
                        'high': float(row['最高']),
                        'low': float(row['最低']),
                        'open': float(row['今开']),
                        'yesterday_close': float(row['昨收']),
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    self.logger.info(f"成功获取股票 {stock_code} 实时价格: {result['price']}")
                    return result
                    
            except Exception as e:
                self.logger.warning(f"获取股票 {stock_code} 实时价格失败，第 {attempt + 1} 次尝试: {str(e)}")
                if attempt < RETRY_TIMES - 1:
                    time.sleep(RETRY_DELAY)
                    
        self.logger.error(f"获取股票 {stock_code} 实时价格最终失败")
        return None
        
    def get_historical_data(self, stock_code: str, period: str = "daily", 
                          start_date: str = None, end_date: str = None) -> Optional[pd.DataFrame]:
        """
        获取股票历史数据
        
        Args:
            stock_code: 股票代码
            period: 时间周期 ('daily', 'weekly', 'monthly')
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            
        Returns:
            历史数据DataFrame或None
        """
        for attempt in range(RETRY_TIMES):
            try:
                # 设置默认日期
                if not end_date:
                    end_date = datetime.now().strftime('%Y%m%d')
                if not start_date:
                    # 默认获取近一年数据
                    start_date = (datetime.now().replace(year=datetime.now().year-1)).strftime('%Y%m%d')
                
                # 获取历史数据
                df = ak.stock_zh_a_hist(
                    symbol=stock_code,
                    period=period,
                    start_date=start_date,
                    end_date=end_date,
                    adjust=""
                )
                
                if df is not None and not df.empty:
                    # 根据实际列数动态设置列名
                    column_names = ['日期', '开盘', '收盘', '最高', '最低', '成交量', '成交额', '振幅', '涨跌幅', '涨跌额', '换手率']
                    # 只使用与实际列数相匹配的列名
                    if len(df.columns) <= len(column_names):
                        df.columns = column_names[:len(df.columns)]
                    df['股票代码'] = stock_code
                    
                    self.logger.info(f"成功获取股票 {stock_code} 历史数据，共 {len(df)} 条记录")
                    return df
                    
            except Exception as e:
                self.logger.warning(f"获取股票 {stock_code} 历史数据失败，第 {attempt + 1} 次尝试: {str(e)}")
                if attempt < RETRY_TIMES - 1:
                    time.sleep(RETRY_DELAY)
                    
        self.logger.error(f"获取股票 {stock_code} 历史数据最终失败")
        return None
        
    def save_to_csv(self, data: pd.DataFrame, filename: str):
        """
        保存数据到CSV文件
        
        Args:
            data: 要保存的DataFrame
            filename: 文件名
        """
        try:
            filepath = os.path.join(DATA_DIR, filename)
            data.to_csv(filepath, index=False, encoding='utf-8-sig')
            self.logger.info(f"数据已保存到 {filepath}")
        except Exception as e:
            self.logger.error(f"保存数据到 {filename} 失败: {str(e)}")
            
    def get_multiple_stocks_realtime(self, stock_codes: List[str]) -> Dict[str, Dict]:
        """
        批量获取多只股票的实时价格
        
        Args:
            stock_codes: 股票代码列表
            
        Returns:
            股票代码到价格信息的字典
        """
        results = {}
        
        for code in stock_codes:
            price_data = self.get_realtime_price(code)
            if price_data:
                results[code] = price_data
            # 避免请求过于频繁
            time.sleep(0.5)
            
        return results
        
    def get_multiple_stocks_historical(self, stock_codes: List[str], 
                                     period: str = "daily") -> Dict[str, pd.DataFrame]:
        """
        批量获取多只股票的历史数据
        
        Args:
            stock_codes: 股票代码列表
            period: 时间周期
            
        Returns:
            股票代码到历史数据DataFrame的字典
        """
        results = {}
        
        for code in stock_codes:
            hist_data = self.get_historical_data(code, period)
            if hist_data is not None:
                results[code] = hist_data
            # 避免请求过于频繁
            time.sleep(1)
            
        return results
