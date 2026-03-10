#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
风险评估师 Agent - v2.0 新增

核心职责:
1. 综合评估股票风险水平
2. 计算建议仓位上限
3. 设定止损位
4. 识别风险因素

输出:
- risk_level: low/medium/high/critical
- risk_score: 0-100 (越低越安全)
- position_limit: 建议仓位上限 (0-1)
- stop_loss_price: 止损价
- risk_factors: 风险因素列表
"""

import os
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

# 配置路径
WORKSPACE = '/Users/egg/.openclaw/workspace'
STOCK_SYSTEM = os.path.join(WORKSPACE, 'memory/stock-system')
CONFIG_PATH = os.path.join(STOCK_SYSTEM, 'config.json')

def load_config() -> Dict:
    """加载配置文件"""
    import json
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ 加载配置失败：{e}，使用默认配置")
        return {
            "risk": {
                "levels": {
                    "low": {"max_position": 0.30, "stop_loss_pct": 0.10},
                    "medium": {"max_position": 0.20, "stop_loss_pct": 0.08},
                    "high": {"max_position": 0.10, "stop_loss_pct": 0.05},
                    "critical": {"max_position": 0.00, "stop_loss_pct": 0.00}
                }
            }
        }

def analyze_risk(data: Dict[str, Any], fundamental: Dict, technical: Dict, sentiment: Dict) -> Dict[str, Any]:
    """
    风险评估师核心分析函数
    
    输入:
    - data: 原始股票数据
    - fundamental: 基本面分析结果
    - technical: 技术面分析结果
    - sentiment: 情绪面分析结果
    
    输出:
    - risk_level: low/medium/high/critical
    - risk_score: 0-100
    - position_limit: 0-1
    - stop_loss_price: 止损价
    - stop_loss_pct: 止损百分比
    - risk_factors: 风险因素列表
    """
    config = load_config()
    risk_factors = []
    risk_score = 0  # 0=无风险，100=极高风险
    
    current_price = data.get('price', 0)
    
    # ========== 维度 1: 估值风险 (0-25 分) ==========
    valuation_risk = 0
    
    if data.get('pe'):
        pe = data['pe']
        if pe > 50:
            valuation_risk += 15
            risk_factors.append(f"PE {pe}倍 显著偏高")
        elif pe > 35:
            valuation_risk += 10
            risk_factors.append(f"PE {pe}倍 偏高")
        elif pe > 25:
            valuation_risk += 5
            risk_factors.append(f"PE {pe}倍 略高")
    
    if data.get('pb'):
        pb = data['pb']
        if pb > 10:
            valuation_risk += 10
            risk_factors.append(f"PB {pb}倍 偏高")
        elif pb > 6:
            valuation_risk += 5
            risk_factors.append(f"PB {pb}倍 略高")
    
    valuation_risk = min(25, valuation_risk)
    risk_score += valuation_risk
    
    # ========== 维度 2: 基本面风险 (0-25 分) ==========
    fundamental_risk = 0
    
    if data.get('roe'):
        roe = data['roe']
        if roe < 8:
            fundamental_risk += 10
            risk_factors.append(f"ROE {roe}% 偏低")
        elif roe < 12:
            fundamental_risk += 5
            risk_factors.append(f"ROE {roe}% 一般")
    
    if data.get('revenue_growth'):
        growth = data['revenue_growth']
        if growth < 0:
            fundamental_risk += 15
            risk_factors.append(f"营收负增长 {growth}%")
        elif growth < 5:
            fundamental_risk += 8
            risk_factors.append(f"营收增速放缓 {growth}%")
    
    if data.get('profit_growth'):
        growth = data['profit_growth']
        if growth < 0:
            fundamental_risk += 10
            risk_factors.append(f"利润负增长 {growth}%")
    
    fundamental_risk = min(25, fundamental_risk)
    risk_score += fundamental_risk
    
    # ========== 维度 3: 技术面风险 (0-25 分) ==========
    technical_risk = 0
    
    # 均线排列风险
    if data.get('price') and data.get('ma5') and data.get('ma20') and data.get('ma60'):
        price = data['price']
        ma5 = data['ma5']
        ma20 = data['ma20']
        ma60 = data['ma60']
        
        if price < ma5 < ma20 < ma60:
            technical_risk += 15
            risk_factors.append("均线空头排列")
        elif price < ma20:
            technical_risk += 8
            risk_factors.append(f"股价低于 MA20 (¥{ma20:.1f})")
    
    # RSI 超买风险
    if data.get('rsi'):
        rsi = data['rsi']
        if rsi > 80:
            technical_risk += 10
            risk_factors.append(f"RSI {rsi} 严重超买")
        elif rsi > 70:
            technical_risk += 5
            risk_factors.append(f"RSI {rsi} 超买")
    
    # 涨跌幅风险（短期暴涨）
    if data.get('change_pct'):
        change = data['change_pct']
        if change > 10:
            technical_risk += 10
            risk_factors.append(f"单日暴涨 {change}%，警惕回调")
        elif change > 7:
            technical_risk += 5
            risk_factors.append(f"单日大涨 {change}%")
    
    technical_risk = min(25, technical_risk)
    risk_score += technical_risk
    
    # ========== 维度 4: 情绪面风险 (0-25 分) ==========
    sentiment_risk = 0
    
    # 情绪过于乐观
    if sentiment.get('rating') == '乐观' and sentiment.get('confidence', 0) > 80:
        sentiment_risk += 10
        risk_factors.append("市场情绪过热")
    
    # 情绪与基本面背离
    if fundamental.get('rating') in ['卖出', '悲观'] and sentiment.get('rating') == '乐观':
        sentiment_risk += 15
        risk_factors.append("情绪与基本面背离")
    
    sentiment_risk = min(25, sentiment_risk)
    risk_score += sentiment_risk
    
    # ========== 确定风险等级 ==========
    if risk_score >= 75:
        risk_level = 'critical'
    elif risk_score >= 50:
        risk_level = 'high'
    elif risk_score >= 25:
        risk_level = 'medium'
    else:
        risk_level = 'low'
    
    # ========== 计算仓位上限和止损位 ==========
    risk_config = config.get('risk', {}).get('levels', {}).get(risk_level, {})
    position_limit = risk_config.get('max_position', 0.10)
    stop_loss_pct = risk_config.get('stop_loss_pct', 0.08)
    
    # 计算止损价
    if current_price > 0:
        stop_loss_price = current_price * (1 - stop_loss_pct)
    else:
        stop_loss_price = 0
    
    # ========== 如果没有风险因素，添加默认说明 ==========
    if not risk_factors:
        risk_factors.append("无明显风险因素")
    
    # ========== 返回结果 ==========
    return {
        'risk_level': risk_level,
        'risk_score': risk_score,
        'position_limit': position_limit,
        'stop_loss_price': round(stop_loss_price, 2),
        'stop_loss_pct': stop_loss_pct * 100,
        'risk_factors': risk_factors,
        'breakdown': {
            'valuation': valuation_risk,
            'fundamental': fundamental_risk,
            'technical': technical_risk,
            'sentiment': sentiment_risk,
        },
        'timestamp': datetime.now().isoformat(),
    }

def format_risk_report(risk_result: Dict, stock_name: str, stock_code: str) -> str:
    """格式化风险报告"""
    level_emoji = {
        'low': '🟢',
        'medium': '🟡',
        'high': '🟠',
        'critical': '🔴'
    }
    
    level_names = {
        'low': '低风险',
        'medium': '中风险',
        'high': '高风险',
        'critical': '极高风险'
    }
    
    report = f"""
## 🛡️ 风险评估报告

**股票**: {stock_name} ({stock_code})
**评估时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

### 风险等级
{level_emoji.get(risk_result['risk_level'], '🟡')} **{level_names.get(risk_result['risk_level'], '未知')}**
风险评分：{risk_result['risk_score']}/100

### 仓位建议
| 项目 | 建议 |
|------|------|
| 仓位上限 | {risk_result['position_limit']*100:.0f}% |
| 止损位 | ¥{risk_result['stop_loss_price']:.2f} |
| 止损幅度 | -{risk_result['stop_loss_pct']:.1f}% |

### 风险因素
"""
    
    for factor in risk_result['risk_factors']:
        report += f"- {factor}\n"
    
    report += f"""
### 风险分解
| 维度 | 风险分 | 说明 |
|------|--------|------|
| 估值风险 | {risk_result['breakdown']['valuation']}/25 | PE/PB 评估 |
| 基本面风险 | {risk_result['breakdown']['fundamental']}/25 | ROE/增长评估 |
| 技术面风险 | {risk_result['breakdown']['technical']}/25 | 均线/RSI 评估 |
| 情绪面风险 | {risk_result['breakdown']['sentiment']}/25 | 情绪过热评估 |
| **总分** | **{risk_result['risk_score']}/100** | |
"""
    
    return report

if __name__ == '__main__':
    # 测试代码
    test_data = {
        'price': 1700,
        'pe': 30,
        'pb': 7,
        'roe': 15,
        'revenue_growth': 10,
        'profit_growth': 8,
        'ma5': 1680,
        'ma20': 1650,
        'ma60': 1600,
        'rsi': 55,
        'change_pct': 2.5,
    }
    
    test_fundamental = {'rating': '买入', 'confidence': 70}
    test_technical = {'rating': 'bullish', 'confidence': 65}
    test_sentiment = {'rating': '中性', 'confidence': 60}
    
    result = analyze_risk(test_data, test_fundamental, test_technical, test_sentiment)
    
    print("=== 风险评估师测试 ===")
    print(f"风险等级：{result['risk_level']}")
    print(f"风险评分：{result['risk_score']}")
    print(f"仓位上限：{result['position_limit']*100:.0f}%")
    print(f"止损价：¥{result['stop_loss_price']:.2f}")
    print(f"风险因素：{result['risk_factors']}")
