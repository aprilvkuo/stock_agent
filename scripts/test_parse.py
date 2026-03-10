#!/usr/bin/env python3
"""测试 stock-analyzer 输出解析"""

import subprocess
import sys
import os

sys.path.insert(0, '/Users/egg/.openclaw/workspace/memory/stock-system/scripts')
from auto_agent import parse_stock_output

# 运行 stock-analyzer
result = subprocess.run(
    ['python3', '/Users/egg/.openclaw/workspace/skills/stock-analyzer/scripts/analyze_stock.py', '600519'],
    capture_output=True,
    text=True
)

output = result.stdout
print("=" * 60)
print("stock-analyzer 原始输出:")
print("=" * 60)
print(output[:1000])
print("...")

# 解析
data = parse_stock_output(output, '600519')

print("\n" + "=" * 60)
print("解析结果:")
print("=" * 60)
for key, value in data.items():
    if value is not None:
        print(f"✅ {key}: {value}")
    else:
        print(f"❌ {key}: None")
