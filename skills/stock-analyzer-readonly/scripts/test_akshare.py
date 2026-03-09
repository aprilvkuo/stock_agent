#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试akshare获取股票数据
"""

import sys
sys.path.insert(0, '/Users/egg/.openclaw/workspace-economist/stock-analyzer/venv/lib/python3.13/site-packages')

import akshare as ak
import pandas as pd

print("正在测试akshare...")

try:
    # 测试获取单只股票数据
    print("\n1. 测试获取个股行情...")
    df = ak.stock_zh_a_spot_em()
    print(f"✅ 成功获取 {len(df)} 只股票数据")
    print(f"列名: {df.columns.tolist()[:5]}...")
    
    # 查找工业富联
    fwl = df[df['代码'] == '601138']
    if not fwl.empty:
        print(f"\n✅ 找到工业富联:")
        print(fwl[['代码', '名称', '最新价', '涨跌幅']].to_string())
    else:
        print("\n❌ 未找到工业富联")
    
    print("\n✅ 所有测试通过！")
    
except Exception as e:
    print(f"\n❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()