#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
东方财富股票数据抓取脚本 - 浏览器自动化版本
使用 OpenClaw browser 工具访问东方财富网站获取真实数据
"""

import json
import sys
import subprocess
import re
from datetime import datetime

def fetch_stock_data_from_eastmoney(stock_code):
    """
    通过浏览器访问东方财富获取股票数据
    
    Args:
        stock_code: 股票代码 (如 002594)
    
    Returns:
        dict: 股票数据
    """
    # 确定交易所前缀
    if stock_code.startswith('60') or stock_code.startswith('68'):
        market = 'sh'
    elif stock_code.startswith('00') or stock_code.startswith('30'):
        market = 'sz'
    else:
        market = 'sz'
    
    url = f"https://quote.eastmoney.com/{market}{stock_code}.html"
    
    print(f" 访问东方财富：{url}")
    
    # 使用 browser 工具访问页面
    try:
        # 1. 打开页面
        result = subprocess.run(
            ['openclaw', 'browser', 'open', url],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print(f"❌ 打开页面失败：{result.stderr}")
            return None
        
        # 解析 targetId
        try:
            browser_result = json.loads(result.stdout)
            target_id = browser_result.get('targetId')
        except:
            print("❌ 无法解析浏览器响应")
            return None
        
        # 2. 等待页面加载
        subprocess.run(
            ['openclaw', 'browser', 'act', 'wait', '--target-id', target_id, '--timeout', '5000'],
            capture_output=True,
            timeout=10
        )
        
        # 3. 截图并分析 (简化版本 - 直接返回 URL 供后续处理)
        print(f"✅ 页面已加载，TargetID: {target_id}")
        
        return {
            'success': True,
            'url': url,
            'target_id': target_id,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ 错误：{e}")
        return None


def parse_stock_data_from_snapshot(snapshot_text, stock_code):
    """
    从浏览器快照文本中解析股票数据
    
    Args:
        snapshot_text: 浏览器快照文本
        stock_code: 股票代码
    
    Returns:
        dict: 解析后的股票数据
    """
    data = {
        'stock_code': stock_code,
        'source': '东方财富'
    }
    
    # 解析各种数据模式
    patterns = {
        'stock_name': r'比亚迪|贵州茅台|五粮液|宁德时代',  # 需要根据实际股票调整
        'price': r'最新：([¥\d.]+)',
        'change_pct': r'涨幅：([+-]?[\d.]+)%',
        'volume': r'成交量：([\d.]+)[万手 手]',
        'turnover': r'成交额：([\d.]+)[亿 万]',
        'market_cap': r'总市值：([\d.]+)[亿 万]',
        'pe': r'市盈.*?：([\d.]+)',
        'pb': r'市净.*?：([\d.]+)',
        'high_52w': r'最高：([\d.]+)',
        'low_52w': r'最低：([\d.]+)',
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, snapshot_text)
        if match:
            value = match.group(1)
            # 尝试转换为数字
            try:
                data[key] = float(value.replace('¥', ''))
            except:
                data[key] = value
    
    return data


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法：python3 eastmoney_browser.py <股票代码>")
        print("示例：python3 eastmoney_browser.py 002594")
        sys.exit(1)
    
    stock_code = sys.argv[1]
    
    print(f"📊 开始获取股票数据：{stock_code}")
    print("=" * 50)
    
    # 获取数据
    result = fetch_stock_data_from_eastmoney(stock_code)
    
    if result and result.get('success'):
        print("\n✅ 数据获取成功!")
        print(f"📄 页面 URL: {result['url']}")
        print(f"⏰ 时间：{result['timestamp']}")
        print("\n💡 提示：请使用 browser snapshot 工具获取页面内容并解析")
    else:
        print("\n❌ 数据获取失败")
        sys.exit(1)


if __name__ == '__main__':
    main()
