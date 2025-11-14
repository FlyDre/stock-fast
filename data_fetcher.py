"""
股票数据获取核心模块
使用腾讯API获取实时数据（已验证可访问）
使用AkShare获取历史数据
"""

import akshare as ak
import pandas as pd
import requests
import logging
from datetime import datetime
from typing import List, Dict, Optional
import os

from config import *

class StockDataFetcher:
    """股票数据获取器 - 支持多数据源"""
    
    def __init__(self, proxy_host: str = None, proxy_port: int = None):
        """初始化数据获取器"""
        self.setup_logging()
        self.ensure_directories()
        
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.session = requests.Session()
        
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
            
    def _get_tencent_data(self, stock_code: str) -> Optional[Dict]:
        """从腾讯API获取实时数据"""
        try:
            # 腾讯API格式: sh=上海, sz=深圳
            prefix = "sh" if stock_code.startswith("6") else "sz"
            symbol = f"{prefix}{stock_code}"
            
            url = f"https://qt.gtimg.cn/q={symbol}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200 and f"v_{symbol}" in response.text:
                # 解析腾讯API响应格式
                text = response.text
                start = text.find('"') + 1
                end = text.rfind('"')
                data_str = text[start:end]
                
                parts = data_str.split('~')
                if len(parts) > 5:
                    return {
                        'code': stock_code,
                        'name': parts[1],
                        'price': float(parts[3]) if parts[3] else 0,
                        'change': float(parts[32]) if len(parts) > 32 and parts[32] else 0,
                    }
        except Exception as e:
            self.logger.warning(f"腾讯API获取失败: {str(e)[:80]}")
        
        return None
        
    def get_stock_info(self, stock_code: str) -> Optional[Dict]:
        """获取股票基本信息"""
        # 先尝试腾讯API
        tencent_data = self._get_tencent_data(stock_code)
        if tencent_data:
            self.logger.info(f"成功获取股票 {stock_code} 基本信息")
            return tencent_data
        
        # 再尝试AkShare
        try:
            stock_info = ak.stock_individual_info_em(symbol=stock_code)
            if stock_info is not None and not stock_info.empty:
                result = {}
                for _, row in stock_info.iterrows():
                    result[row['item']] = row['value']
                self.logger.info(f"成功获取股票 {stock_code} 基本信息")
                return result
        except Exception as e:
            self.logger.warning(f"AkShare获取失败: {str(e)[:80]}")
        
        self.logger.error(f"获取股票 {stock_code} 信息失败")
        return None
        
    def get_realtime_price(self, stock_code: str) -> Optional[Dict]:
        """获取股票实时价格"""
        # 先尝试腾讯API
        tencent_data = self._get_tencent_data(stock_code)
        if tencent_data:
            tencent_data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.logger.info(f"成功获取股票 {stock_code} 实时价格")
            return tencent_data
        
        # 再尝试AkShare
        try:
            df = ak.stock_zh_a_spot_em()
            stock_data = df[df['代码'] == stock_code]
            
            if not stock_data.empty:
                row = stock_data.iloc[0]
                result = {
                    'code': stock_code,
                    'name': row['名称'],
                    'price': float(row['最新价']),
                    'change': float(row['涨跌幅']),
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                self.logger.info(f"成功获取股票 {stock_code} 实时价格")
                return result
        except Exception as e:
            self.logger.warning(f"AkShare实时价格获取失败: {str(e)[:80]}")
        
        self.logger.error(f"获取股票 {stock_code} 实时价格失败")
        return None
        
    def get_historical_data(self, stock_code: str, period: str = "daily", 
                          start_date: str = None, end_date: str = None) -> Optional[pd.DataFrame]:
        """获取股票历史数据 - 使用腾讯API"""
        try:
            # 腾讯API格式: sh=上海, sz=深圳
            prefix = "sh" if stock_code.startswith("6") else "sz"
            symbol = f"{prefix}{stock_code}"
            
            # 腾讯API: 获取最近的K线数据
            # 参数: code=股票代码, begin=开始日期, end=结束日期, fqt=复权类型(0不复权)
            url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get"
            params = {
                'param': f'{symbol},day,,,320,qfq'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                import json
                data = response.json()
                
                if data.get('code') == 0 and data.get('data'):
                    stock_data = data['data'].get(symbol, {})
                    # 腾讯API返回qfqday (复权数据)
                    day_data = stock_data.get('qfqday', []) or stock_data.get('day', [])
                    
                    if day_data:
                        # 解析腾讯API数据格式: [日期, 开, 收, 高, 低, 成交量, 成交额]
                        records = []
                        for item in day_data[-320:]:  # 最多320条
                            try:
                                records.append({
                                    '日期': item[0],
                                    '开盘': float(item[1]),
                                    '收盘': float(item[2]),
                                    '最高': float(item[3]),
                                    '最低': float(item[4]),
                                    '成交量': int(float(item[5])),
                                    '成交额': 0,
                                })
                            except (ValueError, IndexError, TypeError):
                                continue
                        
                        if records:
                            df = pd.DataFrame(records)
                            df['股票代码'] = stock_code
                            # 计算涨跌幅
                            df['涨跌幅'] = ((df['收盘'] - df['开盘']) / df['开盘'] * 100).round(2)
                            self.logger.info(f"成功获取股票 {stock_code} 历史数据，共 {len(df)} 条")
                            return df
        except Exception as e:
            self.logger.warning(f"腾讯API历史数据获取失败: {str(e)[:80]}")
        
        # 备用方案：尝试AkShare
        try:
            if not end_date:
                end_date = datetime.now().strftime('%Y%m%d')
            if not start_date:
                start_date = (datetime.now().replace(year=datetime.now().year-1)).strftime('%Y%m%d')
            
            df = ak.stock_zh_a_hist(
                symbol=stock_code,
                period=period,
                start_date=start_date,
                end_date=end_date,
                adjust=""
            )
            
            if df is not None and not df.empty:
                column_names = ['日期', '开盘', '收盘', '最高', '最低', '成交量', '成交额', '振幅', '涨跌幅', '涨跌额', '换手率']
                if len(df.columns) <= len(column_names):
                    df.columns = column_names[:len(df.columns)]
                df['股票代码'] = stock_code
                self.logger.info(f"成功获取股票 {stock_code} 历史数据(AkShare)，共 {len(df)} 条")
                return df
        except Exception as e:
            self.logger.warning(f"AkShare历史数据获取失败: {str(e)[:80]}")
        
        self.logger.error(f"获取股票 {stock_code} 历史数据失败")
        return None
        
    def save_to_csv(self, data: pd.DataFrame, filename: str):
        """保存数据到CSV文件"""
        try:
            filepath = os.path.join(DATA_DIR, filename)
            data.to_csv(filepath, index=False, encoding='utf-8')
            self.logger.info(f"数据已保存到 {filepath}")
        except Exception as e:
            self.logger.error(f"保存数据失败: {e}")
            
    def get_multiple_stocks_realtime(self, stock_codes: List[str]) -> Dict[str, Dict]:
        """批量获取实时价格"""
        results = {}
        for code in stock_codes:
            price_data = self.get_realtime_price(code)
            if price_data:
                results[code] = price_data
        return results
        
    def get_multiple_stocks_historical(self, stock_codes: List[str]) -> Dict[str, pd.DataFrame]:
        """批量获取历史数据"""
        results = {}
        for code in stock_codes:
            hist_data = self.get_historical_data(code)
            if hist_data is not None:
                results[code] = hist_data
        return results
