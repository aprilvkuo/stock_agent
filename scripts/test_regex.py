#!/usr/bin/env python3
"""测试正则表达式匹配"""

import re

output = """
【基本信息】
  股票名称：贵州茅台
  当前股价：¥1407.20
  涨跌幅：+1.00%
  成交量：140,700 手
  总市值：¥1407.30 亿元

【估值指标】
  市盈率（PE TTM）：1407.34 倍
  市净率（PB）：1.00 倍
  ROE：20.45%

【财务数据（最近季度）】
  营收：¥1205.00 亿元（+16.8%）
  净利润：¥608.00 亿元（+19.2%）
"""

patterns = {
    'volume': r'成交量：([\d,]+) 手',
    'market_cap': r'总市值：¥([\d.]+) 亿元',
    'pe': r'市盈率（PE TTM）：([\d.]+) 倍',
    'pb': r'市净率（PB）：([\d.]+) 倍',
    'revenue': r'营收：¥([\d.]+) 亿元（\+([\d.]+)%）',
    'profit': r'净利润：¥([\d.]+) 亿元（\+([\d.]+)%）',
}

print("测试正则匹配:")
print("=" * 60)

for key, pattern in patterns.items():
    match = re.search(pattern, output)
    if match:
        print(f"✅ {key}: {match.group(1)}")
        if len(match.groups()) > 1:
            print(f"   增长率：{match.group(2)}")
    else:
        print(f"❌ {key}: 不匹配")
        print(f"   模式：{pattern}")
