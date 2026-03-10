#!/usr/bin/env python3
"""
基本面 Agent - 独立运行

职责:
- 分析财报数据 (ROE、营收增速、利润增速)
- 评估估值水平 (PE、PB)
- 给出基本面评级和置信度

调用方式:
python3 fundamental_agent.py <股票代码>
"""

import sys
import json
import subprocess
from datetime import datetime

def get_stock_data(stock_code):
    """获取股票数据"""
    script = '/Users/egg/.openclaw/workspace/skills/stock-analyzer/scripts/analyze_stock.py'
    result = subprocess.run(['python3', script, stock_code], capture_output=True, text=True)
    return result.stdout

def parse_data(output):
    """解析股票数据"""
    import re
    
    data = {}
    patterns = {
        'price': r'当前股价.*?¥([\d.]+)',
        'change_pct': r'涨跌幅.*?([+-]?[\d.]+)%',
        'pe': r'市盈率.*?([\d.]+)\s*倍',
        'pb': r'市净率.*?([\d.]+)\s*倍',
        'roe': r'ROE.*?([\d.]+)%',
        'revenue_growth': r'营收.*?¥([\d.]+)\s*亿元.*?\+([\d.]+)%',
        'profit_growth': r'净利润.*?¥([\d.]+)\s*亿元.*?\+([\d.]+)%',
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, output)
        if match:
            if key in ['revenue_growth', 'profit_growth']:
                data[f'{key}'] = float(match.group(2))
            else:
                data[key] = float(match.group(1)) if '.' in match.group(1) else int(match.group(1))
    
    return data

def analyze(data):
    """
    基本面分析（增强版 v1.1）
    
    分析维度:
    1. ROE - 盈利能力
    2. 营收/利润增速 - 成长性
    3. PE/PB - 估值水平
    """
    rating = '持有'
    confidence = 60
    reasons = []
    risks = []
    score = 50
    
    # ROE 评估（权重 30%）
    if data.get('roe'):
        if data['roe'] >= 25:
            reasons.append(f"ROE {data['roe']}% 优秀")
            confidence += 15
            score += 20
        elif data['roe'] >= 15:
            reasons.append(f"ROE {data['roe']}% 良好")
            confidence += 10
            score += 10
        elif data['roe'] < 5:
            risks.append(f"ROE {data['roe']}% 偏低")
            confidence -= 15
            score -= 20
    
    # 增长评估（权重 25%）
    if data.get('revenue_growth'):
        if data['revenue_growth'] >= 30:
            reasons.append(f"营收增速 {data['revenue_growth']}% 优秀")
            confidence += 15
            score += 15
        elif data['revenue_growth'] >= 15:
            reasons.append(f"营收增速 {data['revenue_growth']}% 良好")
            confidence += 10
            score += 10
        elif data['revenue_growth'] < 0:
            risks.append(f"营收负增长 {data['revenue_growth']}%")
            confidence -= 20
            score -= 20
    
    if data.get('profit_growth'):
        if data['profit_growth'] >= 30:
            reasons.append(f"利润增速 {data['profit_growth']}% 优秀")
            confidence += 15
            score += 15
        elif data['profit_growth'] >= 15:
            reasons.append(f"利润增速 {data['profit_growth']}% 良好")
            confidence += 10
            score += 10
        elif data['profit_growth'] < 0:
            risks.append(f"利润负增长 {data['profit_growth']}%")
            confidence -= 20
            score -= 15
    
    # 估值评估（权重 25%）
    if data.get('pe'):
        pe = data['pe']
        if pe < 15:
            reasons.append(f"PE {pe:.1f}倍 低估")
            confidence += 15
            score += 15
            rating = '买入'
        elif pe < 25:
            reasons.append(f"PE {pe:.1f}倍 合理")
            confidence += 10
            score += 10
        elif pe > 50:
            risks.append(f"PE {pe:.1f}倍 高估")
            confidence -= 15
            score -= 15
    
    if data.get('pb'):
        pb = data['pb']
        if pb < 2:
            reasons.append(f"PB {pb:.1f}倍 低估")
            confidence += 10
            score += 10
        elif pb > 10:
            risks.append(f"PB {pb:.1f}倍 偏高")
            confidence -= 10
            score -= 10
    
    # 综合评级
    if score >= 80:
        rating = '买入'
        confidence = max(confidence, 80)
    elif score >= 60:
        rating = '持有'
    elif score < 40:
        rating = '卖出'
        confidence = max(confidence, 70)
    
    confidence = max(50, min(95, confidence))
    
    return {
        'agent': '基本面',
        'version': 'v1.1',
        'rating': rating,
        'confidence': confidence,
        'score': score,
        'reasons': reasons,
        'risks': risks,
        'timestamp': datetime.now().isoformat()
    }

def main():
    if len(sys.argv) < 2:
        print(json.dumps({'error': '请提供股票代码'}, ensure_ascii=False))
        return
    
    stock_code = sys.argv[1]
    
    # 获取数据
    output = get_stock_data(stock_code)
    data = parse_data(output)
    
    # 分析
    result = analyze(data)
    result['stock_code'] = stock_code
    result['data'] = data
    
    # 输出 JSON 结果
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
