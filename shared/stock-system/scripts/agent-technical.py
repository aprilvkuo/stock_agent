#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技术面 Agent - 独立执行脚本

遵循五步工作法:
1️⃣ UPDATE → 2️⃣ READ → 3️⃣ DO → 4️⃣ CHECK → 5️⃣ REVIEW
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
        'ma5': r'MA5：¥([\d.]+)',
        'ma20': r'MA20：¥([\d.]+)',
        'ma60': r'MA60：¥([\d.]+)',
        'rsi': r'RSI：(\d+)',
        'macd': r'MACD：(.+)',
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, output)
        if match:
            if key in ['price']:
                data[key] = float(match.group(1))
            elif key in ['change_pct']:
                data[key] = float(match.group(1))
            elif key in ['ma5', 'ma20', 'ma60']:
                data[key] = float(match.group(1))
            elif key == 'rsi':
                data[key] = int(match.group(1))
            elif key == 'macd':
                data[key] = match.group(1).strip()
            else:
                data[key] = match.group(1).strip()
    
    return data

def analyze_technical(data):
    """技术面分析"""
    rating = '持有'
    confidence = 60
    reasons = []
    risks = []
    
    # 均线分析
    if data.get('price') and data.get('ma5') and data.get('ma20') and data.get('ma60'):
        if data['price'] > data['ma5'] > data['ma20'] > data['ma60']:
            reasons.append("均线多头排列")
            confidence += 15
            rating = '买入'
        elif data['price'] < data['ma5'] < data['ma20'] < data['ma60']:
            reasons.append("均线空头排列")
            confidence -= 15
            rating = '卖出'
        else:
            reasons.append("均线粘合，方向不明")
    
    # RSI 分析
    if data.get('rsi'):
        if data['rsi'] > 70:
            risks.append(f"RSI {data['rsi']} 超买")
            confidence -= 10
        elif data['rsi'] < 30:
            reasons.append(f"RSI {data['rsi']} 超卖")
            confidence += 10
        else:
            reasons.append(f"RSI {data['rsi']} 中性")
    
    # MACD 分析
    if data.get('macd'):
        if '金叉' in data['macd']:
            reasons.append("MACD 金叉")
            confidence += 10
        elif '死叉' in data['macd']:
            risks.append("MACD 死叉")
            confidence -= 10
    
    # 涨跌幅
    if data.get('change_pct'):
        if data['change_pct'] > 3:
            reasons.append(f"强势上涨 +{data['change_pct']}%")
            confidence += 5
        elif data['change_pct'] < -3:
            risks.append(f"大跌 -{abs(data['change_pct'])}%")
            confidence -= 5
    
    confidence = max(50, min(95, confidence))
    
    # 计算支撑/阻力位
    support = data.get('ma60', data.get('price', 0) * 0.95)
    resistance = data.get('price', 0) * 1.05
    
    return {
        'rating': rating,
        'confidence': confidence,
        'reasons': reasons,
        'risks': risks,
        'support': round(support, 2),
        'resistance': round(resistance, 2),
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
                if '技术面：⏳ 待处理' in content:
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
        
        print(f"  ✅ {data.get('stock_name', stock_code)} 当前价：¥{data.get('price', 'N/A')}")
        
        # 执行分析
        print(f"  执行技术面分析...")
        result = analyze_technical(data)
        print(f"  评级：{result['rating']} ({result['confidence']}%)")
        
        # 写入结果
        result_file = f"result-{datetime.now().strftime('%Y%m%d%H%M%S')}-technical.md"
        result_path = os.path.join(RESULTS_DIR, result_file)
        
        result_content = f"""# 分析结果 - 技术面

## 请求 ID
{req['file'].replace('.md', '')}

## Agent
技术面 Agent-v1.0

## 分析时间
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 股票信息
- 代码：{stock_code}
- 名称：{data.get('stock_name', 'N/A')}
- 当前价：¥{data.get('price', 'N/A')}

## 分析结果
| 项目 | 内容 |
|------|------|
| 评级 | {result['rating']} |
| 置信度 | {result['confidence']}% |
| 关键依据 | {'; '.join(result['reasons'][:3])} |
| 风险点 | {'; '.join(result['risks'][:2]) if result['risks'] else '无明显风险'} |
| 支撑位 | ¥{result['support']} |
| 阻力位 | ¥{result['resistance']} |

## 技术指标
- MA5: ¥{data.get('ma5', 'N/A')}
- MA20: ¥{data.get('ma20', 'N/A')}
- MA60: ¥{data.get('ma60', 'N/A')}
- RSI: {data.get('rsi', 'N/A')}
- MACD: {data.get('macd', 'N/A')}
"""
        
        with open(result_path, 'w', encoding='utf-8') as f:
            f.write(result_content)
        
        print(f"  ✅ 结果写入：{result_file}")
        
        # 更新请求状态（同时更新复选框和状态行）
        new_content = req['content']
        new_content = new_content.replace('- [ ] 技术面 Agent', '- [x] 技术面 Agent')
        new_content = new_content.replace('技术面：⏳ 待处理', '技术面：✅ 已完成')
        with open(req['filepath'], 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"  ✅ 请求状态已更新")

def main():
    print(f"\n{'='*50}")
    print(f"📊 技术面 Agent - 检查请求")
    print(f"{'='*50}\n")
    
    process_requests()
    
    print(f"\n{'='*50}")
    print(f"✅ 技术面 Agent 执行完成")
    print(f"{'='*50}\n")

if __name__ == '__main__':
    main()
