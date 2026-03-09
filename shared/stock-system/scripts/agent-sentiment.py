#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
情绪 Agent - 独立执行脚本
"""

import os
import sys
import json
from datetime import datetime
import subprocess
import re

# 配置
WORKSPACE = '/Users/egg/.openclaw/workspace'
COORDINATOR_DIR = os.path.join(WORKSPACE, 'agents/stock-coordinator')
DATA_DIR = os.path.join(COORDINATOR_DIR, 'data')
QUEUE_DIR = os.path.join(DATA_DIR, 'queue')
REQUESTS_DIR = os.path.join(QUEUE_DIR, 'requests')
RESULTS_DIR = os.path.join(QUEUE_DIR, 'results')
STOCK_ANALYZER = os.path.join(WORKSPACE, 'skills/stock-analyzer-readonly/scripts/analyze_stock.py')

def get_stock_data(stock_code):
    """获取股票数据"""
    try:
        result = subprocess.run(
            ['python3', STOCK_ANALYZER, stock_code],
            capture_output=True,
            text=True,
            timeout=60
        )
        return parse_output(result.stdout, stock_code)
    except Exception as e:
        print(f"获取数据失败：{e}")
        return None

def parse_output(output, stock_code):
    """解析 stock-analyzer 输出"""
    data = {'stock_code': stock_code}
    
    patterns = {
        'stock_name': r'股票名称：(.+)',
        'price': r'当前股价：¥([\d.]+)',
        'change_pct': r'涨跌幅：([+-]?[\d.]+)%',
        'volume': r'成交量：([\d,]+) 手',
        'market_cap': r'总市值：¥([\d.]+) 亿元',
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, output)
        if match:
            if key in ['price', 'market_cap']:
                data[key] = float(match.group(1))
            elif key == 'change_pct':
                data[key] = float(match.group(1))
            elif key == 'volume':
                data[key] = int(match.group(1).replace(',', ''))
            else:
                data[key] = match.group(1).strip()
    
    return data

def analyze_sentiment(data):
    """情绪分析"""
    rating = '中性'
    confidence = 55
    reasons = []
    risks = []
    
    # 基于涨跌幅判断
    if data.get('change_pct'):
        change = data['change_pct']
        if change > 5:
            rating = '乐观'
            reasons.append(f"大涨 +{change}%")
            confidence = 75
        elif change > 3:
            rating = '乐观'
            reasons.append(f"上涨 +{change}%")
            confidence = 70
        elif change > 1:
            rating = '乐观'
            reasons.append(f"小幅上涨 +{change}%")
            confidence = 65
        elif change < -5:
            rating = '悲观'
            reasons.append(f"大跌 -{abs(change)}%")
            confidence = 75
        elif change < -3:
            rating = '悲观'
            reasons.append(f"下跌 -{abs(change)}%")
            confidence = 70
        elif change < -1:
            rating = '悲观'
            reasons.append(f"小幅下跌 -{abs(change)}%")
            confidence = 65
        else:
            reasons.append(f"震荡 {change:+.2f}%")
            confidence = 60
    
    # 成交量分析
    if data.get('volume'):
        volume = data['volume']
        if volume > 50000000:  # 5000 万手以上
            reasons.append("成交量巨大，关注度高")
            confidence += 5
        elif volume < 1000000:  # 100 万手以下
            risks.append("成交量低迷，关注度低")
            confidence -= 5
    
    # 市值分析
    if data.get('market_cap'):
        cap = data['market_cap']
        if cap > 10000:  # 万亿以上
            reasons.append("万亿市值龙头，稳定性高")
            confidence += 5
        elif cap < 100:  # 100 亿以下
            risks.append("小市值，波动风险大")
            confidence -= 5
    
    # 一般性风险
    risks.append("需关注市场整体情绪和板块表现")
    
    confidence = max(50, min(90, confidence))
    
    return {
        'rating': rating,
        'confidence': confidence,
        'reasons': reasons,
        'risks': risks,
    }

def process_requests():
    """处理请求队列"""
    os.makedirs(REQUESTS_DIR, exist_ok=True)
    os.makedirs(RESULTS_DIR, exist_ok=True)
    
    # 查找待处理的请求
    pending = []
    for f in os.listdir(REQUESTS_DIR):
        if f.endswith('.md'):
            filepath = os.path.join(REQUESTS_DIR, f)
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
                if '情绪面：⏳ 待处理' in content:
                    match = re.search(r'股票代码：(\d+)', content)
                    if match:
                        pending.append({
                            'file': f,
                            'filepath': filepath,
                            'stock_code': match.group(1),
                            'content': content
                        })
    
    if not pending:
        print("✅ 无待处理请求")
        return
    
    print(f"📋 发现 {len(pending)} 个待处理请求")
    
    for req in pending:
        print(f"\n处理请求：{req['file']}")
        stock_code = req['stock_code']
        
        # 获取数据
        print(f"  获取 {stock_code} 数据...")
        data = get_stock_data(stock_code)
        if not data:
            print(f"  ❌ 获取数据失败")
            continue
        
        print(f"  ✅ {data.get('stock_name', stock_code)} 当前价：¥{data.get('price', 'N/A')} ({data.get('change_pct', 0):+.2f}%)")
        
        # 执行分析
        print(f"  执行情绪分析...")
        result = analyze_sentiment(data)
        print(f"  评级：{result['rating']} ({result['confidence']}%)")
        
        # 写入结果
        result_file = f"result-{datetime.now().strftime('%Y%m%d%H%M%S')}-sentiment.md"
        result_path = os.path.join(RESULTS_DIR, result_file)
        
        result_content = f"""# 分析结果 - 情绪面

## 请求 ID
{req['file'].replace('.md', '')}

## Agent
情绪 Agent-v1.0

## 分析时间
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 股票信息
- 代码：{stock_code}
- 名称：{data.get('stock_name', 'N/A')}
- 当前价：¥{data.get('price', 'N/A')}
- 涨跌幅：{data.get('change_pct', 0):+.2f}%

## 分析结果
| 项目 | 内容 |
|------|------|
| 评级 | {result['rating']} |
| 置信度 | {result['confidence']}% |
| 关键依据 | {'; '.join(result['reasons'][:3])} |
| 风险信号 | {'; '.join(result['risks'][:2])} |

## 市场数据
- 成交量：{data.get('volume', 'N/A')} 手
- 总市值：¥{data.get('market_cap', 'N/A')} 亿元
"""
        
        with open(result_path, 'w', encoding='utf-8') as f:
            f.write(result_content)
        
        print(f"  ✅ 结果写入：{result_file}")
        
        # 更新请求状态（同时更新复选框和状态行）
        new_content = req['content']
        new_content = new_content.replace('- [ ] 情绪 Agent', '- [x] 情绪 Agent')
        new_content = new_content.replace('情绪面：⏳ 待处理', '情绪面：✅ 已完成')
        with open(req['filepath'], 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"  ✅ 请求状态已更新")

def main():
    print(f"\n{'='*50}")
    print(f"📊 情绪 Agent - 检查请求")
    print(f"{'='*50}\n")
    
    process_requests()
    
    print(f"\n{'='*50}")
    print(f"✅ 情绪 Agent 执行完成")
    print(f"{'='*50}\n")

if __name__ == '__main__':
    main()
