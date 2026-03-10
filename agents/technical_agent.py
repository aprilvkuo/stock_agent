#!/usr/bin/env python3
"""
技术面 Agent - 独立运行

职责:
- 分析均线系统
- 分析 RSI 指标
- 分析 MACD 指标
- 分析成交量
- 给出技术面评级和置信度

调用方式:
python3 technical_agent.py <股票代码>
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
        'volume': r'成交量.*?([\d,]+)\s*手',
        'ma5': r'MA5.*?¥([\d.]+)',
        'ma20': r'MA20.*?¥([\d.]+)',
        'ma60': r'MA60.*?¥([\d.]+)',
        'rsi': r'RSI.*?(\d+)',
        'macd': r'MACD.*?(.+?)(?:\n|$)',
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, output)
        if match:
            if key == 'volume':
                data[key] = int(match.group(1).replace(',', ''))
            elif key == 'rsi':
                data[key] = int(match.group(1))
            else:
                data[key] = float(match.group(1)) if '.' in match.group(1) else match.group(1).strip()
    
    return data

def analyze(data):
    """
    技术面分析（增强版 v1.1）
    
    分析维度:
    1. 均线系统 - 趋势方向
    2. RSI - 超买超卖
    3. MACD - 动能指标
    4. 成交量 - 量价关系
    """
    rating = '持有'
    confidence = 60
    reasons = []
    risks = []
    score = 50
    
    # 均线分析（权重 30%）
    if data.get('price') and data.get('ma5') and data.get('ma20') and data.get('ma60'):
        price = float(data['price'])
        ma5 = float(data['ma5'])
        ma20 = float(data['ma20'])
        ma60 = float(data['ma60'])
        
        if price > ma5 > ma20 > ma60:
            reasons.append("均线多头排列，趋势向上")
            confidence += 20
            score += 20
            rating = '买入'
        elif price < ma5 < ma20 < ma60:
            reasons.append("均线空头排列，趋势向下")
            confidence -= 20
            score -= 20
            rating = '卖出'
        elif price > ma20 and price > ma60:
            reasons.append("股价在中期均线上方")
            confidence += 10
            score += 10
        elif price < ma20 and price < ma60:
            reasons.append("股价在中期均线下方")
            confidence -= 10
            score -= 10
        else:
            reasons.append("均线粘合，方向不明")
    
    # RSI 分析（权重 20%）
    if data.get('rsi'):
        rsi = int(data['rsi'])
        if rsi > 80:
            risks.append(f"RSI {rsi} 严重超买")
            confidence -= 15
            score -= 15
        elif rsi > 70:
            risks.append(f"RSI {rsi} 超买区")
            confidence -= 10
            score -= 10
        elif rsi < 20:
            reasons.append(f"RSI {rsi} 严重超卖")
            confidence += 15
            score += 15
        elif rsi < 30:
            reasons.append(f"RSI {rsi} 超卖区")
            confidence += 10
            score += 10
        elif 45 <= rsi <= 55:
            reasons.append(f"RSI {rsi} 中性")
        else:
            reasons.append(f"RSI {rsi} 偏强")
            score += 5
    
    # MACD 分析（权重 25%）
    if data.get('macd'):
        macd = str(data['macd'])
        if '金叉' in macd and '向上' in macd:
            reasons.append("MACD 金叉向上，动能强劲")
            confidence += 20
            score += 20
        elif '金叉' in macd:
            reasons.append("MACD 金叉")
            confidence += 10
            score += 10
        elif '死叉' in macd and '向下' in macd:
            risks.append("MACD 死叉向下，动能减弱")
            confidence -= 20
            score -= 20
        elif '死叉' in macd:
            risks.append("MACD 死叉")
            confidence -= 10
            score -= 10
    
    # 成交量分析（权重 15%）
    if data.get('volume') and data.get('change_pct'):
        volume = int(data.get('volume', 0))
        change = float(data.get('change_pct', 0))
        
        if change > 3 and volume > 100000:
            reasons.append("放量上涨，量价配合良好")
            confidence += 15
            score += 15
        elif change > 3 and volume < 50000:
            risks.append("缩量上涨，需警惕")
            confidence -= 10
        elif change < -3 and volume > 100000:
            risks.append("放量下跌，抛压重")
            confidence -= 15
            score -= 15
        elif change < -3 and volume < 50000:
            reasons.append("缩量下跌，抛压有限")
            confidence += 5
    
    # 综合评级
    if score >= 80:
        rating = '买入'
        confidence = max(confidence, 80)
    elif score >= 60:
        rating = '持有'
        confidence = max(confidence, 65)
    elif score < 40:
        rating = '卖出'
        confidence = max(confidence, 70)
    
    confidence = max(50, min(95, confidence))
    
    return {
        'agent': '技术面',
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
