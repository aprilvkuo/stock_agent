#!/usr/bin/env python3
"""
情绪 Agent - 独立运行

职责:
- 分析价格情绪 (涨跌幅)
- 分析市场热度 (成交量)
- 分析技术情绪 (均线偏离)
- 分析超买超卖 (RSI)
- 分析市场地位 (市值)
- 给出情绪评级和置信度

调用方式:
python3 sentiment_agent.py <股票代码>
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
        'market_cap': r'总市值.*?¥([\d.]+)\s*亿元',
        'ma20': r'MA20.*?¥([\d.]+)',
        'rsi': r'RSI.*?(\d+)',
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
    情绪面分析（增强版 v1.1）
    
    分析维度:
    1. 涨跌幅 - 价格情绪
    2. 成交量 - 市场热度
    3. 均线偏离 - 技术情绪
    4. RSI - 超买超卖情绪
    5. 市值 - 市场地位
    """
    rating = '中性'
    confidence = 55
    reasons = []
    risks = []
    score = 50
    
    # 涨跌幅分析（权重 30%）
    if data.get('change_pct') is not None:
        change = float(data['change_pct'])
        if change > 5:
            reasons.append(f"大涨{change}%，情绪高涨")
            confidence += 15
            score += 20
        elif change > 2:
            reasons.append(f"上涨{change}%，情绪偏多")
            confidence += 10
            score += 10
        elif change > 0:
            reasons.append(f"微涨{change}%，情绪温和")
            score += 5
        elif change > -2:
            reasons.append(f"微跌{change}%，情绪稳定")
        elif change > -5:
            risks.append(f"下跌{change}%，情绪偏空")
            confidence -= 10
            score -= 10
        else:
            risks.append(f"大跌{change}%，情绪低迷")
            confidence -= 15
            score -= 20
    
    # 成交量分析（权重 20%）
    if data.get('volume'):
        volume = int(data.get('volume', 0))
        if volume > 200000:
            reasons.append("成交量巨大，市场关注度高")
            confidence += 10
            score += 10
        elif volume > 100000:
            reasons.append("成交量活跃")
            confidence += 5
            score += 5
        elif volume < 30000:
            risks.append("成交量低迷，关注度低")
            confidence -= 10
            score -= 10
    
    # 均线偏离度（权重 20%）
    if data.get('price') and data.get('ma20'):
        price = float(data['price'])
        ma20 = float(data['ma20'])
        if ma20 > 0:
            deviation = (price - ma20) / ma20 * 100
            if deviation > 20:
                risks.append(f"股价偏离 20 日均线{deviation:.1f}%，可能回调")
                confidence -= 10
                score -= 10
            elif deviation > 10:
                reasons.append(f"股价强势，偏离 20 日均线{deviation:.1f}%")
                score += 5
            elif deviation < -10:
                reasons.append(f"股价弱势，偏离 20 日均线{deviation:.1f}%")
    
    # RSI 情绪（权重 15%）
    if data.get('rsi'):
        rsi = int(data['rsi'])
        if rsi > 75:
            reasons.append(f"RSI {rsi} 市场热情高")
            score += 5
        elif rsi > 50:
            reasons.append(f"RSI {rsi} 情绪偏多")
            score += 5
        elif rsi < 25:
            reasons.append(f"RSI {rsi} 情绪偏空")
            score -= 5
    
    # 市值分析（权重 15%）
    if data.get('market_cap'):
        cap = float(data['market_cap'])
        if cap > 10000:
            reasons.append("万亿市值，行业龙头")
            confidence += 10
            score += 10
        elif cap > 1000:
            reasons.append("千亿市值，大型企业")
            confidence += 5
            score += 5
        elif cap < 100:
            risks.append("市值较小，波动可能较大")
            confidence -= 5
    
    # 综合评级
    if score >= 80:
        rating = '乐观'
        confidence = max(confidence, 80)
    elif score >= 60:
        rating = '乐观'
        confidence = max(confidence, 65)
    elif score < 40:
        rating = '悲观'
        confidence = max(confidence, 65)
    
    confidence = max(50, min(95, confidence))
    
    return {
        'agent': '情绪',
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
