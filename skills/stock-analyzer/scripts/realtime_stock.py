#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用akshare获取真实股票数据
丁蟹 - 专业金融投资助手
"""

import sys
sys.path.insert(0, '/Users/egg/.openclaw/workspace-economist/stock-analyzer/venv/lib/python3.13/site-packages')

import akshare as ak
from datetime import datetime, timedelta
import pandas as pd

class RealtimeStockData:
    """实时股票数据获取器"""
    
    def __init__(self):
        self.stock_name = ""
        self.stock_code = ""
    
    def get_a_stock_data(self, stock_code):
        """
        获取A股实时数据
        stock_code: 6位数字，如 601138 (工业富联)
        """
        try:
            # 获取实时行情
            print(f"正在获取 {stock_code} 的数据...")
            
            # 使用akshare获取实时行情
            df = ak.stock_zh_a_spot_em()
            
            # 查找指定股票
            stock_row = df[df['代码'] == stock_code]
            
            if stock_row.empty:
                print(f"❌ 未找到股票 {stock_code} 的数据")
                return None
            
            # 提取数据
            row = stock_row.iloc[0]
            self.stock_name = row['名称']
            self.stock_code = stock_code
            
            # 计算涨跌幅
            current_price = float(row['最新价']) if pd.notna(row['最新价']) else 0
            prev_close = float(row['昨收']) if pd.notna(row['昨收']) else 0
            change_percent = ((current_price - prev_close) / prev_close * 100) if prev_close > 0 else 0
            
            # 构建数据字典
            data = {
                'name': self.stock_name,
                'current_price': current_price,
                'change': change_percent,
                'volume': float(row['成交量']) / 100 if pd.notna(row['成交量']) else 0,  # 转换为手
                'turnover': float(row['成交额']) / 10000 if pd.notna(row['成交额']) else 0,  # 转换为万元
                'market_cap': float(row['总市值']) / 100000000 if pd.notna(row['总市值']) else 0,  # 转换为亿元
                'pe_ttm': float(row['市盈率-动态']) if pd.notna(row['市盈率-动态']) else 0,
                'pb': float(row['市净率']) if pd.notna(row['市净率']) else 0,
                'roe': 0,  # akshare实时数据中没有ROE，需要另外获取
                'high_52w': float(row['最高']) if pd.notna(row['最高']) else 0,
                'low_52w': float(row['最低']) if pd.notna(row['最低']) else 0,
            }
            
            return data
            
        except Exception as e:
            print(f"❌ 获取数据失败: {e}")
            return None
    
    def get_financial_data(self, stock_code):
        """获取财务数据"""
        try:
            # 获取主要财务指标
            print(f"正在获取 {stock_code} 的财务数据...")
            
            # 获取财务指标
            df = ak.stock_financial_analysis_indicator(symbol=stock_code)
            
            if df.empty:
                return None
            
            # 获取最新一期数据
            latest = df.iloc[0]
            
            # 计算营收和净利润（需要从其他接口获取，这里简化处理）
            financial_data = {
                'revenue': 0,  # 需要另外获取
                'net_profit': 0,  # 需要另外获取
                'revenue_growth': 0,  # 需要另外获取
                'profit_growth': 0,  # 需要另外获取
                'roe': float(latest['净资产收益率']) if '净资产收益率' in latest else 0,
            }
            
            return financial_data
            
        except Exception as e:
            print(f"⚠️ 获取财务数据失败: {e}")
            return None
    
    def get_kline_data(self, stock_code, period="daily"):
        """获取K线数据用于技术分析"""
        try:
            print(f"正在获取 {stock_code} 的K线数据...")
            
            # 获取日K线
            if period == "daily":
                df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", start_date="20250101", adjust="qfq")
            else:
                df = ak.stock_zh_a_hist(symbol=stock_code, period=period, start_date="20250101", adjust="qfq")
            
            if df.empty or len(df) < 60:
                return None
            
            # 计算均线
            df['MA5'] = df['收盘'].rolling(window=5).mean()
            df['MA20'] = df['收盘'].rolling(window=20).mean()
            df['MA60'] = df['收盘'].rolling(window=60).mean()
            
            # 计算RSI
            delta = df['收盘'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            # 获取最新数据
            latest = df.iloc[-1]
            
            kline_data = {
                'ma5': latest['MA5'],
                'ma20': latest['MA20'],
                'ma60': latest['MA60'],
                'rsi': latest['RSI'],
                'macd': "金叉向上" if latest['MA5'] > latest['MA20'] > latest['MA60'] else "其他"
            }
            
            return kline_data
            
        except Exception as e:
            print(f"⚠️ 获取K线数据失败: {e}")
            return None
    
    def analyze_stock(self, stock_code):
        """综合分析股票"""
        print(f"\n{'='*60}")
        print(f"📊 开始分析股票：{stock_code}")
        print(f"{'='*60}\n")
        
        # 获取实时数据
        data = self.get_a_stock_data(stock_code)
        if not data:
            return None
        
        # 获取财务数据
        financial_data = self.get_financial_data(stock_code)
        if financial_data:
            data.update(financial_data)
        
        # 获取K线数据
        kline_data = self.get_kline_data(stock_code)
        if kline_data:
            data.update(kline_data)
        
        return data


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法：python realtime_stock.py <股票代码>")
        print("示例：")
        print("  python realtime_stock.py 601138  （工业富联）")
        print("  python realtime_stock.py 600519  （贵州茅台）")
        sys.exit(1)
    
    stock_code = sys.argv[1]
    
    # 创建分析器并运行
    analyzer = RealtimeStockData()
    data = analyzer.analyze_stock(stock_code)
    
    if data:
        print(f"\n✅ 成功获取 {stock_code} 的数据")
        print(f"股票名称：{data.get('name', '未知')}")
        print(f"当前价格：¥{data.get('current_price', 0):.2f}")
        print(f"涨跌幅：{data.get('change', 0):+.2f}%")
    else:
        print(f"\n❌ 获取 {stock_code} 的数据失败")


if __name__ == "__main__":
    main()