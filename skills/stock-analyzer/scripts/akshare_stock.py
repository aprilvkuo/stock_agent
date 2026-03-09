#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用akshare获取真实股票数据 - 简化版
丁蟹 - 专业金融投资助手
"""

import sys
sys.path.insert(0, '/Users/egg/.openclaw/workspace-economist/stock-analyzer/venv/lib/python3.13/site-packages')

import akshare as ak
import pandas as pd
from datetime import datetime

def get_stock_realtime(stock_code):
    """获取股票实时行情"""
    try:
        print(f"正在获取 {stock_code} 的实时数据...")
        
        # 使用akshare获取沪深A股实时行情
        df = ak.stock_zh_a_spot_em()
        
        # 查找指定股票
        stock_row = df[df['代码'] == stock_code]
        
        if stock_row.empty:
            print(f"❌ 未找到股票 {stock_code} 的数据")
            return None
        
        # 提取数据
        row = stock_row.iloc[0]
        
        data = {
            'name': row['名称'],
            'code': stock_code,
            'current_price': float(row['最新价']) if pd.notna(row['最新价']) else 0,
            'change_percent': float(row['涨跌幅']) if pd.notna(row['涨跌幅']) else 0,
            'change_amount': float(row['涨跌额']) if pd.notna(row['涨跌额']) else 0,
            'volume': float(row['成交量']) / 100 if pd.notna(row['成交量']) else 0,  # 转换为手
            'turnover': float(row['成交额']) / 10000 if pd.notna(row['成交额']) else 0,  # 转换为万元
            'market_cap': float(row['总市值']) / 100000000 if pd.notna(row['总市值']) else 0,  # 转换为亿元
            'pe_ttm': float(row['市盈率-动态']) if pd.notna(row['市盈率-动态']) else 0,
            'pb': float(row['市净率']) if pd.notna(row['市净率']) else 0,
            'high_52w': float(row['最高']) if pd.notna(row['最高']) else 0,
            'low_52w': float(row['最低']) if pd.notna(row['最低']) else 0,
            'open': float(row['今开']) if pd.notna(row['今开']) else 0,
            'high': float(row['最高']) if pd.notna(row['最高']) else 0,
            'low': float(row['最低']) if pd.notna(row['最低']) else 0,
            'prev_close': float(row['昨收']) if pd.notna(row['昨收']) else 0,
        }
        
        return data
        
    except Exception as e:
        print(f"❌ 获取数据失败: {e}")
        return None

def display_stock_info(data):
    """显示股票信息"""
    if not data:
        return
    
    print("\n" + "="*60)
    print(f"📊 {data['name']} ({data['code']}) 实时行情")
    print("="*60)
    print(f"当前价格: ¥{data['current_price']:.2f}")
    print(f"涨跌幅: {data['change_percent']:+.2f}%")
    print(f"涨跌额: ¥{data['change_amount']:.2f}")
    print(f"成交量: {data['volume']:,.0f} 手")
    print(f"成交额: ¥{data['turnover']:,.2f} 万元")
    print(f"总市值: ¥{data['market_cap']:.2f} 亿元")
    print("-"*60)
    print(f"市盈率(TTM): {data['pe_ttm']:.2f}")
    print(f"市净率: {data['pb']:.2f}")
    print("="*60 + "\n")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python akshare_stock.py <股票代码>")
        print("示例:")
        print("  python akshare_stock.py 601138  (工业富联)")
        print("  python akshare_stock.py 600519  (贵州茅台)")
        sys.exit(1)
    
    stock_code = sys.argv[1]
    
    # 获取股票数据
    data = get_stock_realtime(stock_code)
    
    # 显示结果
    if data:
        display_stock_info(data)
        print(f"✅ 成功获取 {stock_code} 的数据")
    else:
        print(f"❌ 获取 {stock_code} 的数据失败")

if __name__ == "__main__":
    main()