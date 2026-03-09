#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用baostock获取股票数据
"""

import sys
sys.path.insert(0, '/Users/egg/.openclaw/workspace-economist/stock-analyzer/venv/lib/python3.13/site-packages')

import baostock as bs
import pandas as pd
from datetime import datetime, timedelta

def get_stock_data(stock_code):
    """获取股票数据"""
    try:
        print(f"正在获取 {stock_code} 的数据...")
        
        # 登录baostock
        lg = bs.login()
        if lg.error_code != '0':
            print(f"登录失败: {lg.error_msg}")
            return None
        
        # 获取股票代码格式（baostock格式：sh.601138 或 sz.000001）
        if stock_code.startswith('6'):
            bs_code = f"sh.{stock_code}"
        else:
            bs_code = f"sz.{stock_code}"
        
        # 获取当前日期
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        
        # 获取日K线数据
        rs = bs.query_history_k_data_plus(bs_code,
            "date,code,open,high,low,close,preclose,volume,amount,turn,pctChg",
            start_date=start_date, end_date=end_date,
            frequency="d", adjustflag="3")
        
        if rs.error_code != '0':
            print(f"获取数据失败: {rs.error_msg}")
            bs.logout()
            return None
        
        # 读取数据
        data_list = []
        while (rs.error_code == '0') & rs.next():
            data_list.append(rs.get_row_data())
        
        if not data_list:
            print("未获取到数据")
            bs.logout()
            return None
        
        # 创建DataFrame
        df = pd.DataFrame(data_list, columns=rs.fields)
        
        # 转换数据类型
        numeric_cols = ['open', 'high', 'low', 'close', 'preclose', 'volume', 'amount', 'turn', 'pctChg']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 获取最新数据
        latest = df.iloc[-1]
        
        # 计算均线
        df['MA5'] = df['close'].rolling(window=5).mean()
        df['MA20'] = df['close'].rolling(window=20).mean()
        df['MA60'] = df['close'].rolling(window=60).mean()
        
        # 计算RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # 获取最新技术指标
        latest_ma = df.iloc[-1]
        
        # 构建数据字典
        data = {
            'name': stock_code,  # baostock不提供股票名称
            'code': stock_code,
            'current_price': float(latest['close']),
            'change_percent': float(latest['pctChg']),
            'change_amount': float(latest['close']) - float(latest['preclose']),
            'volume': float(latest['volume']) / 100,  # 转换为手
            'turnover': float(latest['amount']) / 10000,  # 转换为万元
            'open': float(latest['open']),
            'high': float(latest['high']),
            'low': float(latest['low']),
            'prev_close': float(latest['preclose']),
            'ma5': float(latest_ma['MA5']),
            'ma20': float(latest_ma['MA20']),
            'ma60': float(latest_ma['MA60']),
            'rsi': float(latest_ma['RSI']),
        }
        
        bs.logout()
        return data
        
    except Exception as e:
        print(f"❌ 获取数据失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def display_stock_info(data):
    """显示股票信息"""
    if not data:
        return
    
    print("\n" + "="*60)
    print(f"📊 {data['name']} ({data['code']}) 行情")
    print("="*60)
    print(f"当前价格: ¥{data['current_price']:.2f}")
    print(f"涨跌幅: {data['change_percent']:+.2f}%")
    print(f"涨跌额: ¥{data['change_amount']:.2f}")
    print(f"今日开盘: ¥{data['open']:.2f}")
    print(f"今日最高: ¥{data['high']:.2f}")
    print(f"今日最低: ¥{data['low']:.2f}")
    print(f"昨日收盘: ¥{data['prev_close']:.2f}")
    print(f"成交量: {data['volume']:,.0f} 手")
    print(f"成交额: ¥{data['turnover']:,.2f} 万元")
    print("-"*60)
    print(f"MA5: ¥{data['ma5']:.2f}")
    print(f"MA20: ¥{data['ma20']:.2f}")
    print(f"MA60: ¥{data['ma60']:.2f}")
    print(f"RSI(14): {data['rsi']:.2f}")
    print("="*60 + "\n")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python simple_stock.py <股票代码>")
        print("示例:")
        print("  python simple_stock.py 601138  (工业富联)")
        print("  python simple_stock.py 600519  (贵州茅台)")
        sys.exit(1)
    
    stock_code = sys.argv[1]
    
    # 获取股票数据
    data = get_stock_data(stock_code)
    
    # 显示结果
    if data:
        display_stock_info(data)
        print(f"✅ 成功获取 {stock_code} 的数据")
    else:
        print(f"❌ 获取 {stock_code} 的数据失败")


if __name__ == "__main__":
    main()