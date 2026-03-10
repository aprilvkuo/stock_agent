#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
首席投资官 (CIO) - v2.0 核心决策模块

核心职责:
1. 汇总 4 个 Agent 的分析结果
2. 根据风险等级调整仓位
3. 生成最终 BUY/HOLD/SELL 建议
4. 输出完整可执行的投资建议

决策逻辑:
1. 加权计算综合评分
2. 根据风险调整仓位上限
3. 生成目标价和止损价
4. 输出完整投资建议
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List

# 配置路径
WORKSPACE = '/Users/egg/.openclaw/workspace'
STOCK_SYSTEM = os.path.join(WORKSPACE, 'memory/stock-system')
CONFIG_PATH = os.path.join(STOCK_SYSTEM, 'config.json')

def load_config() -> Dict:
    """加载配置文件"""
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ 加载配置失败：{e}")
        return {
            "agents": {
                "fundamental": {"weight": 0.30},
                "technical": {"weight": 0.25},
                "sentiment": {"weight": 0.20},
                "risk": {"weight": 0.15}
            },
            "rating": {
                "thresholds": {
                    "strong_buy": 85,
                    "buy": 70,
                    "hold": 50,
                    "sell": 30
                },
                "score_map": {
                    "bullish": 80,
                    "neutral": 50,
                    "bearish": 20
                }
            }
        }

def rating_to_score(rating: str, config: Dict) -> int:
    """将评级转换为分数"""
    score_map = config.get('rating', {}).get('score_map', {
        'bullish': 80,
        'neutral': 50,
        'bearish': 20,
        '买入': 80,
        '持有': 50,
        '卖出': 20,
        '乐观': 70,
        '中性': 50,
        '悲观': 30,
    })
    return score_map.get(rating, 50)

def make_decision(
    fundamental: Dict[str, Any],
    technical: Dict[str, Any],
    sentiment: Dict[str, Any],
    risk: Dict[str, Any],
    data: Dict[str, Any],
    config: Dict = None
) -> Dict[str, Any]:
    """
    CIO 综合决策
    
    输入:
    - fundamental: 基本面分析结果
    - technical: 技术面分析结果
    - sentiment: 情绪面分析结果
    - risk: 风险评估结果
    - data: 原始股票数据
    - config: 配置（可选）
    
    输出:
    - action: BUY/HOLD/SELL
    - confidence: 置信度 0-1
    - position: 建议仓位 (0-1)
    - target_price: 目标价
    - stop_loss: 止损价
    - reasoning: 决策理由
    - time_horizon: 持有周期
    """
    if config is None:
        config = load_config()
    
    # ========== Step 1: 计算各 Agent 评分 ==========
    scores = {
        'fundamental': rating_to_score(fundamental.get('rating', '中性'), config),
        'technical': rating_to_score(technical.get('rating', '中性'), config),
        'sentiment': rating_to_score(sentiment.get('rating', '中性'), config),
    }
    
    # ========== Step 2: 获取权重 ==========
    agent_weights = config.get('agents', {})
    weights = {
        'fundamental': agent_weights.get('fundamental', {}).get('weight', 0.30),
        'technical': agent_weights.get('technical', {}).get('weight', 0.25),
        'sentiment': agent_weights.get('sentiment', {}).get('weight', 0.20),
    }
    
    # ========== Step 3: 计算加权综合评分 ==========
    # 权重总和（不包括 CIO 自己的权重）
    total_weight = weights['fundamental'] + weights['technical'] + weights['sentiment']
    
    base_score = (
        scores['fundamental'] * weights['fundamental'] +
        scores['technical'] * weights['technical'] +
        scores['sentiment'] * weights['sentiment']
    ) / total_weight
    
    # ========== Step 4: 根据风险调整评分 ==========
    risk_score = risk.get('risk_score', 50)
    risk_level = risk.get('risk_level', 'medium')
    
    # 风险调整因子：高风险降低评分
    risk_adjustment = 0
    if risk_level == 'critical':
        risk_adjustment = -20
    elif risk_level == 'high':
        risk_adjustment = -10
    elif risk_level == 'low':
        risk_adjustment = +5
    
    adjusted_score = base_score + risk_adjustment
    adjusted_score = max(0, min(100, adjusted_score))  # 限制在 0-100
    
    # ========== Step 5: 确定行动 (BUY/HOLD/SELL) ==========
    thresholds = config.get('rating', {}).get('thresholds', {
        'strong_buy': 85,
        'buy': 70,
        'hold': 50,
        'sell': 30
    })
    
    if adjusted_score >= thresholds['strong_buy']:
        action = 'STRONG_BUY'
        action_cn = '强烈买入'
        base_position = 0.25
    elif adjusted_score >= thresholds['buy']:
        action = 'BUY'
        action_cn = '买入'
        base_position = 0.20
    elif adjusted_score >= thresholds['hold']:
        action = 'HOLD'
        action_cn = '持有'
        base_position = 0.10
    elif adjusted_score >= thresholds['sell']:
        action = 'HOLD'
        action_cn = '谨慎持有'
        base_position = 0.05
    else:
        action = 'SELL'
        action_cn = '卖出'
        base_position = 0.00
    
    # ========== Step 6: 根据风险限制仓位 ==========
    position_limit = risk.get('position_limit', 0.20)
    final_position = min(base_position, position_limit)
    
    # ========== Step 7: 计算目标价和止损价 ==========
    current_price = data.get('price', 0)
    
    # 目标价：基于预期涨幅
    if action in ['STRONG_BUY', 'BUY']:
        target_pct = 0.10 if action == 'STRONG_BUY' else 0.08
    elif action == 'HOLD':
        target_pct = 0.05
    else:
        target_pct = 0.00
    
    target_price = current_price * (1 + target_pct) if current_price > 0 else 0
    
    # 止损价：使用风险评估的结果
    stop_loss = risk.get('stop_loss_price', current_price * 0.92 if current_price > 0 else 0)
    
    # ========== Step 8: 计算置信度 ==========
    avg_confidence = (
        fundamental.get('confidence', 60) * 0.3 +
        technical.get('confidence', 60) * 0.25 +
        sentiment.get('confidence', 60) * 0.2 +
        (100 - risk_score) * 0.25  # 风险越低，置信度越高
    )
    confidence = avg_confidence / 100  # 归一化到 0-1
    
    # ========== Step 9: 生成决策理由 ==========
    reasoning_parts = []
    
    # 基本面理由
    if fundamental.get('reasons'):
        reasoning_parts.append(f"基本面：{fundamental['reasons'][0]}")
    
    # 技术面理由
    if technical.get('reasons'):
        reasoning_parts.append(f"技术面：{technical['reasons'][0]}")
    
    # 风险因素
    if risk_level in ['high', 'critical']:
        reasoning_parts.append(f"⚠️ 风险：{risk.get('risk_factors', ['未知'])[0]}")
    
    reasoning = "；".join(reasoning_parts) if reasoning_parts else "综合评估"
    
    # ========== Step 10: 确定持有周期 ==========
    if action in ['STRONG_BUY', 'BUY']:
        time_horizon = "3-6 个月"
    elif action == 'HOLD':
        time_horizon = "1-3 个月"
    else:
        time_horizon = "立即执行"
    
    # ========== 返回完整决策 ==========
    return {
        'action': action,
        'action_cn': action_cn,
        'confidence': round(confidence, 2),
        'position': round(final_position, 2),
        'target_price': round(target_price, 2),
        'stop_loss': round(stop_loss, 2),
        'reasoning': reasoning,
        'time_horizon': time_horizon,
        'score': {
            'base': round(base_score, 1),
            'adjusted': round(adjusted_score, 1),
            'risk_adjustment': risk_adjustment,
        },
        'agent_scores': scores,
        'weights': weights,
        'risk_level': risk_level,
        'timestamp': datetime.now().isoformat(),
    }

def format_investment_report(decision: Dict, stock_name: str, stock_code: str, current_price: float) -> str:
    """格式化投资建议报告"""
    action_emoji = {
        'STRONG_BUY': '🔥',
        'BUY': '✅',
        'HOLD': '⏸️',
        'SELL': '❌'
    }
    
    # 计算预期收益和风险比
    if current_price > 0 and decision['stop_loss'] > 0:
        upside = (decision['target_price'] - current_price) / current_price * 100
        downside = (current_price - decision['stop_loss']) / current_price * 100
        reward_risk = upside / downside if downside > 0 else 0
    else:
        upside = 0
        downside = 0
        reward_risk = 0
    
    report = f"""
# 📈 投资建议报告

**股票**: {stock_name} ({stock_code})
**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**当前股价**: ¥{current_price:.2f}

---

## 🎯 核心建议

{action_emoji.get(decision['action'], '⏸️')} **{decision['action_cn']}** ({decision['action']})

| 项目 | 建议 |
|------|------|
| 建议仓位 | {decision['position']*100:.0f}% |
| 目标价 | ¥{decision['target_price']:.2f} (+{upside:.1f}%) |
| 止损价 | ¥{decision['stop_loss']:.2f} (-{downside:.1f}%) |
| 盈亏比 | {reward_risk:.1f}:1 |
| 置信度 | {decision['confidence']*100:.0f}% |
| 持有周期 | {decision['time_horizon']} |

---

## 📊 决策依据

**综合评分**: {decision['score']['adjusted']:.1f}/100 (基础分：{decision['score']['base']:.1f}, 风险调整：{decision['score']['risk_adjustment']:+.1f})

**Agent 评分**:
| Agent | 评分 | 权重 | 加权 |
|-------|------|------|------|
| 基本面 | {decision['agent_scores']['fundamental']} | {decision['weights']['fundamental']*100:.0f}% | {decision['agent_scores']['fundamental']*decision['weights']['fundamental']:.1f} |
| 技术面 | {decision['agent_scores']['technical']} | {decision['weights']['technical']*100:.0f}% | {decision['agent_scores']['technical']*decision['weights']['technical']:.1f} |
| 情绪面 | {decision['agent_scores']['sentiment']} | {decision['weights']['sentiment']*100:.0f}% | {decision['agent_scores']['sentiment']*decision['weights']['sentiment']:.1f} |

**风险等级**: {decision['risk_level']}

**决策理由**: {decision['reasoning']}

---

## 📝 执行计划

1. **买入**: 现价 ¥{current_price:.2f} 买入 {decision['position']*100:.0f}% 仓位
2. **止盈**: 达到 ¥{decision['target_price']:.2f} 分批止盈
3. **止损**: 跌破 ¥{decision['stop_loss']:.2f} 坚决止损
4. **复盘**: {decision['time_horizon']}后复盘

---

## ⚠️ 风险提示

- 本建议仅供参考，不构成投资推荐
- 股市有风险，投资需谨慎
- 请结合自身风险承受能力决策
"""
    
    return report

if __name__ == '__main__':
    # 测试代码
    config = load_config()
    
    test_fundamental = {'rating': '买入', 'confidence': 75, 'reasons': ['ROE 优秀']}
    test_technical = {'rating': 'bullish', 'confidence': 70, 'reasons': ['均线多头']}
    test_sentiment = {'rating': '中性', 'confidence': 60, 'reasons': ['震荡整理']}
    test_risk = {
        'risk_level': 'medium',
        'risk_score': 35,
        'position_limit': 0.20,
        'stop_loss_price': 1580,
    }
    test_data = {'price': 1700}
    
    decision = make_decision(test_fundamental, test_technical, test_sentiment, test_risk, test_data, config)
    
    print("=== CIO 决策测试 ===")
    print(f"行动：{decision['action']} ({decision['action_cn']})")
    print(f"仓位：{decision['position']*100:.0f}%")
    print(f"目标价：¥{decision['target_price']:.2f}")
    print(f"止损价：¥{decision['stop_loss']:.2f}")
    print(f"置信度：{decision['confidence']*100:.0f}%")
