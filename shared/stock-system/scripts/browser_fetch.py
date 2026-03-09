#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 OpenClaw browser 工具从东方财富获取股票数据
通过 execute JavaScript 直接提取页面数据
"""

import subprocess
import json
import sys
import time
from datetime import datetime

def run_browser_command(args):
    """运行 browser 命令"""
    cmd = ['openclaw', 'browser'] + args
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode == 0:
        try:
            return json.loads(result.stdout)
        except:
            return {'raw': result.stdout}
    return {'error': result.stderr}

def fetch_stock_data(stock_code):
    """获取股票数据"""
    
    # 确定交易所
    if stock_code.startswith('60') or stock_code.startswith('68'):
        market = 'sh'
    else:
        market = 'sz'
    
    url = f"https://quote.eastmoney.com/{market}{stock_code}.html"
    print(f"📊 访问东方财富：{url}")
    
    # 1. 打开页面
    print("  [1/4] 打开页面...")
    result = run_browser_command(['open', url])
    if 'error' in result:
        print(f"❌ 打开失败：{result['error']}")
        return None
    
    target_id = result.get('targetId')
    if not target_id:
        print("❌ 无法获取 targetId")
        return None
    
    print(f"  ✅ 页面已打开 (TargetID: {target_id})")
    
    # 2. 等待页面加载
    print("  [2/4] 等待页面加载...")
    time.sleep(3)
    
    # 3. 执行 JavaScript 获取数据
    print("  [3/4] 提取数据...")
    
    js_code = """
    () => {
        const data = {};
        
        // 尝试从页面提取数据
        const priceEl = document.querySelector('[data-field="f43"], .price, .hq-h1');
        const nameEl = document.querySelector('.name, .stock-name, h1');
        
        // 从表格中提取
        const rows = document.querySelectorAll('table tr');
        rows.forEach(row => {
            const text = row.textContent;
            if (text.includes('总市值')) {
                data.marketCap = text.match(/总市值 [:：]?\s*([\d.]+[亿万]?)/)?.[1];
            }
            if (text.includes('市盈')) {
                data.pe = text.match(/市盈.*?[:：]?\s*([\d.]+)/)?.[1];
            }
            if (text.includes('市净')) {
                data.pb = text.match(/市净.*?[:：]?\s*([\d.]+)/)?.[1];
            }
        });
        
        // 提取名称
        if (nameEl) data.name = nameEl.textContent.trim();
        
        return data;
    }
    """
    
    js_result = run_browser_command(['act', 'evaluate', '--target-id', target_id, '--fn', js_code])
    
    # 4. 关闭页面
    print("  [4/4] 清理...")
    run_browser_command(['close', '--target-id', target_id])
    
    if 'error' in js_result:
        print(f"⚠️  JS 执行失败：{js_result['error']}")
        return None
    
    return js_result


def main():
    if len(sys.argv) < 2:
        print("用法：python3 browser_fetch.py <股票代码>")
        print("示例：python3 browser_fetch.py 002594")
        sys.exit(1)
    
    stock_code = sys.argv[1]
    result = fetch_stock_data(stock_code)
    
    if result:
        print("\n✅ 数据获取成功!")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("\n❌ 数据获取失败")
        sys.exit(1)


if __name__ == '__main__':
    main()
