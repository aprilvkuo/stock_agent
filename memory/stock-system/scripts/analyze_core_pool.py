#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心股票池分析脚本 - 独立版本

特点:
- 独立配置文件 stock-pool.json
- 系统升级不受影响
- 一键分析所有核心股票

使用:
python3 analyze_core_pool.py
"""

import sys
import os
import json
from datetime import datetime

# 配置路径
WORKSPACE = '/Users/egg/.openclaw/workspace'
STOCK_SYSTEM = os.path.join(WORKSPACE, 'memory/stock-system')
POOL_CONFIG_PATH = os.path.join(STOCK_SYSTEM, 'stock-pool.json')

# 导入主分析脚本
sys.path.insert(0, STOCK_SYSTEM + '/scripts')
from auto_agent_v2 import analyze_stock_v2


def load_stock_pool():
    """加载股票池配置"""
    try:
        with open(POOL_CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ 加载股票池配置失败：{e}")
        print("使用默认配置")
        return {
            "core_pool": [
                {"code": "600519", "name": "贵州茅台"},
                {"code": "00700", "name": "腾讯控股"},
                {"code": "AAPL", "name": "苹果公司"},
                {"code": "BABA", "name": "阿里巴巴"},
            ]
        }


def analyze_pool():
    """分析核心股票池"""
    print("\n" + "="*70)
    print("📊 核心股票池分析 - v2.0")
    print("="*70)
    print(f"分析时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"配置文件：{POOL_CONFIG_PATH}")
    print("="*70)
    
    # 加载股票池
    pool = load_stock_pool()
    core_stocks = pool.get('core_pool', [])
    
    if not core_stocks:
        print("❌ 股票池为空，请配置 stock-pool.json")
        return
    
    print(f"核心股票数量：{len(core_stocks)}")
    print("="*70 + "\n")
    
    results = []
    
    # 分析每只股票
    for i, stock in enumerate(core_stocks, 1):
        code = stock.get('code', '')
        name = stock.get('name', 'Unknown')
        
        print(f"\n{'='*70}")
        print(f"[{i}/{len(core_stocks)}] {name} ({code})")
        print(f"{'='*70}\n")
        
        try:
            result = analyze_stock_v2(code)
            
            if result and result.get('decision'):
                decision = result['decision']
                results.append({
                    'code': code,
                    'name': name,
                    'action': decision.get('action', 'UNKNOWN'),
                    'action_cn': decision.get('action_cn', '未知'),
                    'position': decision.get('position', 0),
                    'target_price': decision.get('target_price', 0),
                    'stop_loss': decision.get('stop_loss', 0),
                    'confidence': decision.get('confidence', 0),
                })
        except Exception as e:
            print(f"❌ {name} 分析失败：{e}")
            results.append({
                'code': code,
                'name': name,
                'action': 'ERROR',
                'action_cn': '分析失败',
                'error': str(e),
            })
    
    # 输出汇总报告
    print("\n" + "="*70)
    print("📋 核心股票池分析汇总")
    print("="*70)
    
    print(f"\n| # | 股票 | 行动 | 仓位 | 目标价 | 止损价 | 置信度 |")
    print(f"|---|------|------|------|--------|--------|--------|")
    
    for i, r in enumerate(results, 1):
        if r.get('action') == 'ERROR':
            print(f"| {i} | {r['name']} | ❌ 失败 | - | - | - | - |")
        else:
            print(f"| {i} | {r['name']} | {r['action_cn']} | {r['position']*100:.0f}% | ¥{r['target_price']:.2f} | ¥{r['stop_loss']:.2f} | {r['confidence']*100:.0f}% |")
    
    # 统计
    total = len(results)
    buy_count = sum(1 for r in results if r.get('action') in ['BUY', 'STRONG_BUY'])
    hold_count = sum(1 for r in results if r.get('action') == 'HOLD')
    sell_count = sum(1 for r in results if r.get('action') == 'SELL')
    error_count = sum(1 for r in results if r.get('action') == 'ERROR')
    
    print(f"\n统计:")
    print(f"  总计：{total} 只")
    print(f"  买入：{buy_count} 只")
    print(f"  持有：{hold_count} 只")
    print(f"  卖出：{sell_count} 只")
    print(f"  失败：{error_count} 只")
    
    print("\n" + "="*70)
    print("✅ 分析完成")
    print("="*70)
    
    return results


if __name__ == '__main__':
    analyze_pool()
