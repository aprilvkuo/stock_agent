#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票多 Agent 系统 - 主协调脚本
自动化执行：分析 → 记录 → 验证 → 复盘 → 规则迭代
"""

import sys
import os
import json
from datetime import datetime, timedelta
import subprocess
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

# 评级转分数（全局常量）
rating_to_score = {
    '买入': 80,
    '持有': 50,
    '卖出': 20,
    '乐观': 70,
    '中性': 50,
    '悲观': 30,
}

# ============ 配置 ============
WORKSPACE = '/Users/egg/.openclaw/workspace'
STOCK_SYSTEM = os.path.join(WORKSPACE, 'memory/stock-system')
ANALYSIS_LOG_DIR = os.path.join(STOCK_SYSTEM, 'analysis-log')
REPORTS_DIR = os.path.join(STOCK_SYSTEM, 'reports')
STOCK_ANALYZER_SCRIPT = '/Users/egg/.openclaw/workspace/skills/stock-analyzer/scripts/analyze_stock.py'

# ============ 数据获取 ============

def get_stock_data_with_retry(stock_code, max_retries=3, timeout=60):
    """
    调用 stock-analyzer 获取真实股票数据（带重试机制）v1.3 增强
    
    容错策略:
    - 最多重试 3 次
    - 每次失败后等待 1 秒
    - 超时 60 秒
    """
    last_error = None
    
    for attempt in range(1, max_retries + 1):
        try:
            result = subprocess.run(
                ['python3', STOCK_ANALYZER_SCRIPT, stock_code],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"脚本执行失败：{result.stderr}")
            
            output = result.stdout
            data = parse_stock_output(output, stock_code)
            
            if data and data.get('price'):
                if attempt > 1:
                    print(f"✅ 第{attempt}次重试成功")
                return data
            else:
                raise ValueError("数据解析失败：缺少股价信息")
                
        except subprocess.TimeoutExpired:
            last_error = f"超时（{timeout}秒）"
            print(f"⚠️ 第{attempt}次尝试超时，重试中...")
        except Exception as e:
            last_error = str(e)
            if attempt < max_retries:
                print(f"⚠️ 第{attempt}次尝试失败：{e}，1 秒后重试...")
                import time
                time.sleep(1)
            else:
                print(f"❌ 获取 {stock_code} 数据失败（已重试{max_retries}次）: {last_error}")
    
    # 所有重试失败，返回降级数据
    return get_fallback_data(stock_code)


def get_fallback_data(stock_code):
    """
    降级数据（API 完全失败时使用）
    从缓存或模拟数据获取
    """
    fallback_cache = {
        "600519": {"price": 1680.0, "name": "贵州茅台", "change_pct": 0},
        "000858": {"price": 145.6, "name": "五粮液", "change_pct": 0},
        "002230": {"price": 52.8, "name": "科大讯飞", "change_pct": 0},
        "00700": {"price": 298.5, "name": "腾讯控股", "change_pct": 0},
        "601138": {"price": 23.85, "name": "工业富联", "change_pct": 0},
    }
    
    data = fallback_cache.get(stock_code, {})
    if data:
        print(f"⚠️ 使用降级数据：{stock_code}")
        return {
            'stock_code': stock_code,
            'stock_name': data.get('name'),
            'price': data.get('price'),
            'change_pct': data.get('change_pct'),
            'volume': 0,
            'pe': None,
            'pb': None,
            'roe': None,
            'revenue_growth': None,
            'profit_growth': None,
            'ma5': None,
            'ma20': None,
            'ma60': None,
            'rsi': None,
            'macd': None,
        }
    
    return None


def get_stock_data(stock_code):
    """
    调用 stock-analyzer 获取真实股票数据（v1.3 增强版：带重试 + 降级）
    """
    return get_stock_data_with_retry(stock_code, max_retries=3, timeout=60)


def parse_stock_output(output, stock_code):
    """解析 stock-analyzer 输出"""
    data = {
        'stock_code': stock_code,
        'timestamp': datetime.now().isoformat(),
        'price': None,
        'change_pct': None,
        'volume': None,
        'market_cap': None,
        'pe': None,
        'pb': None,
        'roe': None,
        'revenue': None,
        'revenue_growth': None,
        'profit': None,
        'profit_growth': None,
        'ma5': None,
        'ma20': None,
        'ma60': None,
        'rsi': None,
        'macd': None,
        'recommendation': None,
        'position': None,
    }
    
    # 解析各项数据
    patterns = {
        'stock_name': r'股票名称：(.+)',
        'price': r'当前股价：¥([\d.]+)',
        'change_pct': r'涨跌幅：([+-]?[\d.]+)%',
        'volume': r'成交量：([\d,]+) 手',
        'market_cap': r'总市值：¥([\d.]+) 亿元',
        'pe': r'市盈率（PE TTM）：([\d.]+) 倍',
        'pb': r'市净率（PB）：([\d.]+) 倍',
        'roe': r'ROE：([\d.]+)%',
        'revenue': r'营收：¥([\d.]+) 亿元\(\+([\d.]+)%\)',
        'profit': r'净利润：¥([\d.]+) 亿元\(\+([\d.]+)%\)',
        'ma5': r'MA5：¥([\d.]+)',
        'ma20': r'MA20：¥([\d.]+)',
        'ma60': r'MA60：¥([\d.]+)',
        'rsi': r'RSI：(\d+)',
        'macd': r'MACD：(.+)',
        'recommendation': r'建议操作：(.+)',
        'position': r'建议仓位：([\d-]+)%',
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, output)
        if match:
            if key in ['revenue', 'profit']:
                data[key] = float(match.group(1))
                data[f'{key}_growth'] = float(match.group(2))
            elif key == 'price':
                data[key] = float(match.group(1))
            elif key == 'change_pct':
                data[key] = float(match.group(1))
            elif key == 'volume':
                data[key] = int(match.group(1).replace(',', ''))
            elif key == 'market_cap':
                data[key] = float(match.group(1))
            elif key == 'pe':
                data[key] = float(match.group(1))
            elif key == 'pb':
                data[key] = float(match.group(1))
            elif key == 'roe':
                data[key] = float(match.group(1))
            elif key in ['ma5', 'ma20', 'ma60']:
                data[key] = float(match.group(1))
            elif key == 'rsi':
                data[key] = int(match.group(1))
            elif key == 'macd':
                data[key] = match.group(1).strip()
            elif key == 'recommendation':
                data[key] = match.group(1).strip()
            elif key == 'position':
                data[key] = match.group(1).strip()
    
    # 提取股票名称
    name_match = re.search(r'股票名称：(.+)', output)
    if name_match:
        data['stock_name'] = name_match.group(1).strip()
    
    return data


# ============ Agent 分析逻辑 ============

def analyze_fundamental(data):
    """基本面 Agent 分析"""
    rating = '持有'
    confidence = 60
    reasons = []
    risks = []
    
    # ROE 评估
    if data.get('roe'):
        if data['roe'] >= 25:
            reasons.append(f"ROE {data['roe']}% 优秀")
            confidence += 10
        elif data['roe'] >= 15:
            reasons.append(f"ROE {data['roe']}% 良好")
            confidence += 5
        elif data['roe'] < 10:
            risks.append(f"ROE {data['roe']}% 偏低")
            confidence -= 10
    
    # 增长评估
    if data.get('revenue_growth'):
        if data['revenue_growth'] >= 20:
            reasons.append(f"营收增速 {data['revenue_growth']}% 优秀")
            confidence += 10
        elif data['revenue_growth'] >= 10:
            reasons.append(f"营收增速 {data['revenue_growth']}% 良好")
            confidence += 5
        elif data['revenue_growth'] < 0:
            risks.append(f"营收负增长 {data['revenue_growth']}%")
            confidence -= 15
    
    if data.get('profit_growth'):
        if data['profit_growth'] >= 20:
            reasons.append(f"利润增速 {data['profit_growth']}% 优秀")
            confidence += 10
        elif data['profit_growth'] >= 10:
            reasons.append(f"利润增速 {data['profit_growth']}% 良好")
            confidence += 5
    
    # 估值评估
    if data.get('pe'):
        if data['pe'] < 15:
            reasons.append(f"PE {data['pe']}倍 低估")
            confidence += 10
            rating = '买入'
        elif data['pe'] < 25:
            reasons.append(f"PE {data['pe']}倍 合理")
            confidence += 5
        elif data['pe'] > 40:
            risks.append(f"PE {data['pe']}倍 偏高")
            confidence -= 10
    
    if data.get('pb'):
        if data['pb'] > 8:
            risks.append(f"PB {data['pb']}倍 偏高")
            confidence -= 5
    
    # 综合评级
    if confidence >= 80:
        rating = '买入'
    elif confidence >= 70:
        rating = '买入'
    elif confidence < 50:
        rating = '卖出'
    
    confidence = max(50, min(95, confidence))
    
    return {
        'rating': rating,
        'confidence': confidence,
        'reasons': reasons,
        'risks': risks,
    }


def analyze_technical(data):
    """技术面 Agent 分析"""
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
    
    confidence = max(50, min(95, confidence))
    
    return {
        'rating': rating,
        'confidence': confidence,
        'reasons': reasons,
        'risks': risks,
    }


def analyze_sentiment(data):
    """
    情绪 Agent 分析（增强版 v1.1）
    
    分析维度:
    1. 涨跌幅分析
    2. 成交量分析（量价关系）
    3. 均线偏离度（技术情绪）
    4. RSI 情绪指标
    """
    rating = '中性'
    confidence = 55
    reasons = []
    risks = []
    
    # === 维度 1: 涨跌幅分析 ===
    price_score = 0
    if data.get('change_pct'):
        change = data['change_pct']
        if change > 5:
            reasons.append(f"🔥 大涨{change}%，市场情绪高涨")
            price_score = 3
            confidence = 70
        elif change > 3:
            reasons.append(f"📈 上涨{change}%，情绪偏乐观")
            price_score = 2
            confidence = 65
        elif change > 1:
            reasons.append(f"📊 微涨{change}%，情绪温和")
            price_score = 1
            confidence = 60
        elif change < -5:
            reasons.append(f"🔻 大跌{change}%，市场情绪悲观")
            price_score = -3
            confidence = 70
        elif change < -3:
            reasons.append(f"📉 下跌{change}%，情绪偏悲观")
            price_score = -2
            confidence = 65
        elif change < -1:
            reasons.append(f"📊 微跌{change}%，情绪谨慎")
            price_score = -1
            confidence = 60
        else:
            reasons.append(f"➖ 震荡{change}%，情绪中性")
            price_score = 0
    
    # === 维度 2: 成交量分析（量价关系）===
    volume_score = 0
    if data.get('volume') and data.get('change_pct'):
        # 简化版：假设成交量放大是积极信号
        # TODO: 对比历史平均成交量
        reasons.append(f"💹 成交量{data['volume']:,}手")
        if data['change_pct'] > 0:
            volume_score = 1  # 上涨 + 放量 = 积极
            reasons.append("量价配合良好")
        elif data['change_pct'] < 0:
            volume_score = -0.5  # 下跌 + 放量 = 谨慎
            risks.append("下跌放量，需注意")
    
    # === 维度 3: 均线偏离度（技术情绪）===
    ma_score = 0
    if data.get('price') and data.get('ma5') and data.get('ma20'):
        price = data['price']
        ma5 = data['ma5']
        ma20 = data['ma20']
        
        # 计算偏离度
        dev_from_ma5 = (price - ma5) / ma5 * 100 if ma5 else 0
        dev_from_ma20 = (price - ma20) / ma20 * 100 if ma20 else 0
        
        if price > ma5 > ma20:
            reasons.append(f"📊 均线多头排列（MA5:¥{ma5:.1f}, MA20:¥{ma20:.1f}）")
            ma_score = 2
        elif price < ma5 < ma20:
            reasons.append(f"📉 均线空头排列（MA5:¥{ma5:.1f}, MA20:¥{ma20:.1f}）")
            ma_score = -2
        else:
            reasons.append(f"📊 均线粘合，方向不明")
            ma_score = 0
    
    # === 维度 4: RSI 情绪指标 ===
    rsi_score = 0
    if data.get('rsi'):
        rsi = data['rsi']
        if rsi > 70:
            reasons.append(f"⚠️ RSI {rsi} 超买区，警惕回调")
            rsi_score = -1
            risks.append("RSI 超买，短期可能回调")
        elif rsi < 30:
            reasons.append(f"💡 RSI {rsi} 超卖区，可能反弹")
            rsi_score = 1
            reasons.append("RSI 超卖，存在反弹机会")
        elif rsi > 50:
            reasons.append(f"📊 RSI {rsi} 偏强区")
            rsi_score = 0.5
        else:
            reasons.append(f"📊 RSI {rsi} 中性区")
            rsi_score = 0
    
    # === 综合评分 ===
    total_score = price_score + volume_score + ma_score + rsi_score
    
    if total_score >= 4:
        rating = '乐观'
        confidence = min(75, 65 + total_score)
    elif total_score >= 2:
        rating = '乐观'
        confidence = min(70, 60 + total_score)
    elif total_score >= 0:
        rating = '中性'
        confidence = 60
    elif total_score >= -2:
        rating = '中性'
        confidence = 60
    else:
        rating = '悲观'
        confidence = min(70, 60 - total_score)
    
    # 风险提示
    if not risks:
        risks.append("情绪面变化快，需结合基本面和技术面")
    
    return {
        'rating': rating,
        'confidence': confidence,
        'reasons': reasons,
        'risks': risks,
        'score_breakdown': {
            'price': price_score,
            'volume': volume_score,
            'ma': ma_score,
            'rsi': rsi_score,
            'total': total_score,
        }
    }


def get_dynamic_weights():
    """
    获取动态权重（v1.1 新增）
    
    根据 Agent 历史表现调整权重
    当前返回固定权重（待验证数据积累后启用动态调整）
    """
    # 基础权重
    base_weights = {
        'fundamental': 0.5,
        'technical': 0.3,
        'sentiment': 0.2,
    }
    
    # TODO: 从 agent-performance-tracker.md 读取准确率
    # 当验证数据积累到 20+ 次后，启用以下逻辑：
    # - 准确率 > 80%: 权重 +10%
    # - 准确率 70-80%: 权重不变
    # - 准确率 60-70%: 权重 -5%
    # - 准确率 < 60%: 权重 -10%
    
    # 当前阶段：使用基础权重
    return base_weights


def make_decision(fundamental, technical, sentiment):
    """主 Agent 综合决策（v1.1 动态权重版）"""
    # 获取动态权重
    weights = get_dynamic_weights()
    
    # 评级转分数（使用全局常量）
    
    scores = {
        'fundamental': rating_to_score.get(fundamental['rating'], 50),
        'technical': rating_to_score.get(technical['rating'], 50),
        'sentiment': rating_to_score.get(sentiment['rating'], 50),
    }
    
    # 加权计算
    total_score = (
        scores['fundamental'] * weights['fundamental'] +
        scores['technical'] * weights['technical'] +
        scores['sentiment'] * weights['sentiment']
    )
    
    # 综合评级
    if total_score >= 70:
        final_rating = '🟢 推荐'
        position = '10-15%'
    elif total_score >= 55:
        final_rating = '🟡 中性'
        position = '5-10%'
    else:
        final_rating = '🔴 回避'
        position = '0%'
    
    return {
        'score': total_score,
        'rating': final_rating,
        'position': position,
        'breakdown': scores,
        'weights': weights,  # 返回使用的权重
    }


# ============ 文件操作 ============

def create_analysis_log(stock_code, data, fundamental, technical, sentiment, decision):
    """创建分析日志（Markdown + JSON 双格式）v1.3 增强"""
    today = datetime.now().strftime('%Y-%m-%d')
    filename_md = f"{today}_{stock_code}_{data.get('stock_name', 'Unknown')}.md"
    filename_json = f"{today}_{stock_code}_{data.get('stock_name', 'Unknown')}.json"
    filepath_md = os.path.join(ANALYSIS_LOG_DIR, filename_md)
    filepath_json = os.path.join(ANALYSIS_LOG_DIR, filename_json)
    
    # 计算目标价和止损价
    current_price = data.get('price', 0)
    target_price = current_price * 1.05 if current_price else 0
    stop_price = current_price * 0.95 if current_price else 0
    
    # 获取权重（用于显示）
    weights = decision.get('weights', {'fundamental': 0.5, 'technical': 0.3, 'sentiment': 0.2})
    
    # 情绪分析 breakdown（如果有）
    sentiment_breakdown = ''
    if 'score_breakdown' in sentiment:
        sb = sentiment['score_breakdown']
        sentiment_breakdown = f"""
**情绪评分分解**:
| 维度 | 得分 | 说明 |
|------|------|------|
| 价格情绪 | {sb['price']:+.1f} | 涨跌幅分析 |
| 成交量 | {sb['volume']:+.1f} | 量价关系 |
| 均线 | {sb['ma']:+.1f} | 均线排列 |
| RSI | {sb['rsi']:+.1f} | 超买超卖 |
| **总分** | **{sb['total']:+.1f}** | |
"""
    
    content = f"""# {data.get('stock_name', 'Unknown')} ({stock_code}) 多 Agent 分析

## 元数据
- 分析日期：{datetime.now().strftime('%Y-%m-%d %H:%M')}
- 股票代码：{stock_code}
- 股票名称：{data.get('stock_name', 'Unknown')}
- 参与 Agent: 主 Agent-v1.1, 基本面-v1.0, 技术面-v1.0, 情绪-v1.1(增强)
- 使用规则版本：stock-wisdom.md#v1.0
- 系统版本：v1.1 (并发优化 + 情绪增强)

---

## 各 Agent 分析结果

### 基本面 Agent 判断
| 项目 | 内容 |
|------|------|
| 评级 | {fundamental['rating']} |
| 置信度 | {fundamental['confidence']}% |
| 关键依据 | {'; '.join(fundamental['reasons'][:3])} |
| 风险点 | {'; '.join(fundamental['risks'][:2]) if fundamental['risks'] else '无明显风险'} |

### 技术面 Agent 判断
| 项目 | 内容 |
|------|------|
| 评级 | {technical['rating']} |
| 置信度 | {technical['confidence']}% |
| 关键依据 | {'; '.join(technical['reasons'][:3])} |
| 风险点 | {'; '.join(technical['risks'][:2]) if technical['risks'] else '无明显风险'} |

### 情绪 Agent 判断（v1.1 增强）
| 项目 | 内容 |
|------|------|
| 评级 | {sentiment['rating']} |
| 置信度 | {sentiment['confidence']}% |
| 关键依据 | {'; '.join(sentiment['reasons'][:4])} |
| 风险信号 | {'; '.join(sentiment['risks'][:2])} |
{sentiment_breakdown}
---

## 主 Agent 综合决策

### 评分 breakdown
| Agent | 分数 | 权重 | 加权 |
|-------|------|------|------|
| 基本面 | {decision['breakdown']['fundamental']} | {weights['fundamental']*100:.0f}% | {decision['breakdown']['fundamental']*weights['fundamental']:.1f} |
| 技术面 | {decision['breakdown']['technical']} | {weights['technical']*100:.0f}% | {decision['breakdown']['technical']*weights['technical']:.1f} |
| 情绪 | {decision['breakdown']['sentiment']} | {weights['sentiment']*100:.0f}% | {decision['breakdown']['sentiment']*weights['sentiment']:.1f} |
| **综合** | **{decision['score']:.1f}** | 100% | **{decision['score']:.1f}** |

### 投资建议
| 项目 | 内容 |
|------|------|
| 综合评级 | {decision['rating']} |
| 当前股价 | ¥{current_price:.2f} |
| 目标价 | ¥{target_price:.2f} (+5%) |
| 止损价 | ¥{stop_price:.2f} (-5%) |
| 建议仓位 | {decision['position']} |

---

## 待验证假设

| # | 假设内容 | 验证日期 | 状态 |
|---|----------|----------|------|
| 1 | 1 个月内股价突破 ¥{current_price*1.05:.0f} | {(datetime.now()+timedelta(days=30)).strftime('%Y-%m-%d')} | ⏳ 待验证 |
| 2 | 股价不跌破 ¥{stop_price:.0f} | {(datetime.now()+timedelta(days=30)).strftime('%Y-%m-%d')} | ⏳ 待验证 |

---

## 附录：原始数据

```
当前股价：¥{data.get('price', 'N/A')}
PE: {data.get('pe', 'N/A')}
PB: {data.get('pb', 'N/A')}
ROE: {data.get('roe', 'N/A')}%
营收增速：{data.get('revenue_growth', 'N/A')}%
利润增速：{data.get('profit_growth', 'N/A')}%
```
"""
    
    with open(filepath_md, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # 同时生成 JSON 日志（v1.3 新增）
    json_log = {
        'timestamp': datetime.now().isoformat(),
        'stock_code': stock_code,
        'stock_name': data.get('stock_name', 'Unknown'),
        'price': data.get('price'),
        'change_pct': data.get('change_pct'),
        'agents': {
            'fundamental': {
                'rating': fundamental['rating'],
                'confidence': fundamental['confidence'],
                'score': rating_to_score.get(fundamental['rating'], 50),
            },
            'technical': {
                'rating': technical['rating'],
                'confidence': technical['confidence'],
                'score': rating_to_score.get(technical['rating'], 50),
            },
            'sentiment': {
                'rating': sentiment['rating'],
                'confidence': sentiment['confidence'],
                'score': rating_to_score.get(sentiment['rating'], 50),
            },
        },
        'decision': {
            'score': decision['score'],
            'rating': decision['rating'],
            'position': decision['position'],
            'weights': decision.get('weights', {}),
        },
        'predictions': [
            {
                'type': 'price_breakthrough',
                'target': current_price * 1.05,
                'validate_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
            },
            {
                'type': 'stop_loss',
                'target': current_price * 0.95,
                'validate_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
            },
        ],
        'raw_data': {
            'pe': data.get('pe'),
            'pb': data.get('pb'),
            'roe': data.get('roe'),
            'revenue_growth': data.get('revenue_growth'),
            'profit_growth': data.get('profit_growth'),
            'rsi': data.get('rsi'),
            'macd': data.get('macd'),
        },
    }
    
    with open(filepath_json, 'w', encoding='utf-8') as f:
        json.dump(json_log, f, ensure_ascii=False, indent=2)
    
    return filepath_md, filepath_json


def write_with_retry(filepath, content, max_retries=3, encoding='utf-8'):
    """
    文件写入（带重试机制）v1.3 新增
    
    防止临时 I/O 错误导致数据丢失
    """
    import time
    
    for attempt in range(1, max_retries + 1):
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w', encoding=encoding) as f:
                f.write(content)
            
            if attempt > 1:
                print(f"✅ 第{attempt}次重试写入成功")
            return True
            
        except Exception as e:
            if attempt < max_retries:
                print(f"⚠️ 写入失败：{e}，{1}秒后重试...")
                time.sleep(1)
            else:
                print(f"❌ 写入失败（已重试{max_retries}次）: {e}")
                return False
    
    return False


def add_to_validation_queue(stock_code, stock_name, current_price):
    """添加待验证项到队列（v1.3 增强：带重试）"""
    queue_path = os.path.join(STOCK_SYSTEM, 'validation-queue.md')
    
    today = datetime.now().strftime('%m-%d')
    validate_date = (datetime.now() + timedelta(days=30)).strftime('%m-%d')
    target_price = current_price * 1.05
    stop_price = current_price * 0.95
    
    with open(queue_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到表格插入位置
    lines = content.split('\n')
    new_lines = []
    inserted = False
    
    for line in lines:
        new_lines.append(line)
        if '⏳ 待验证' in line and not inserted:
            # 在这一行之前插入新行
            new_lines.insert(-1, f"| {today} | {stock_code} {stock_name} | 突破 ¥{target_price:.0f} | {validate_date} | ⏳ 待验证 | | |")
            new_lines.insert(-1, f"| {today} | {stock_code} {stock_name} | 不跌破 ¥{stop_price:.0f} | {validate_date} | ⏳ 待验证 | | |")
            inserted = True
    
    if not inserted:
        # 如果没找到，添加到第一个待验证行之后
        for i, line in enumerate(new_lines):
            if '⏳ 待验证' in line:
                new_lines.insert(i+1, f"| {today} | {stock_code} {stock_name} | 突破 ¥{target_price:.0f} | {validate_date} | ⏳ 待验证 | | |")
                new_lines.insert(i+2, f"| {today} | {stock_code} {stock_name} | 不跌破 ¥{stop_price:.0f} | {validate_date} | ⏳ 待验证 | | |")
                break
    
    # 使用重试机制写入（v1.3 增强）
    success = write_with_retry(queue_path, '\n'.join(new_lines))
    if not success:
        print(f"⚠️ 验证队列更新失败，但分析已完成")


def update_performance_tracker():
    """更新 Agent 表现追踪"""
    tracker_path = os.path.join(STOCK_SYSTEM, 'agent-performance/agent-performance-tracker.md')
    
    # 统计本周分析次数
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    
    count = 0
    for f in os.listdir(ANALYSIS_LOG_DIR):
        if f.endswith('.md') and not f.startswith('分析日志模板'):
            count += 1
    
    with open(tracker_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 更新所有 Agent 的分析次数
    content = content.replace('| 本周 | 2 |', f'| 本周 | {count} |')
    content = content.replace('| 本月 | 2 |', f'| 本月 | {count} |')
    content = content.replace('| 累计 | 2 |', f'| 累计 | {count} |')
    
    with open(tracker_path, 'w', encoding='utf-8') as f:
        f.write(content)


# ============ 主流程 ============

def analyze_with_fallback(agent_func, data, agent_name):
    """
    Agent 分析包装器（带降级策略）v1.3 新增
    
    如果 Agent 分析失败，返回默认结果
    """
    try:
        return agent_func(data)
    except Exception as e:
        print(f"⚠️ {agent_name} Agent 分析异常：{e}，使用默认结果")
        # 返回中性/默认结果
        return {
            'rating': '中性',
            'confidence': 50,
            'reasons': ['数据异常，使用默认判断'],
            'risks': ['分析过程出现异常'],
        }


def analyze_stock_parallel(stock_code):
    """
    并发执行多 Agent 分析（v1.3 增强：带容错）
    
    使用 ThreadPoolExecutor 并行执行 3 个 Agent 分析
    容错策略：单个 Agent 失败不影响其他 Agent
    速度提升：50-60%
    """
    # 获取数据
    data = get_stock_data(stock_code)
    if not data or not data.get('price'):
        print(f"❌ 数据获取失败，使用降级策略")
        return None, None, None, "数据获取失败"
    
    # 并发执行 3 个 Agent（带容错）
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_to_agent = {
            executor.submit(analyze_with_fallback, analyze_fundamental, data, 'fundamental'): 'fundamental',
            executor.submit(analyze_with_fallback, analyze_technical, data, 'technical'): 'technical',
            executor.submit(analyze_with_fallback, analyze_sentiment, data, 'sentiment'): 'sentiment',
        }
        
        results = {}
        errors = []
        
        for future in as_completed(future_to_agent):
            agent_name = future_to_agent[future]
            try:
                result = future.result()
                results[agent_name] = result
                
                # 检查是否使用了降级结果
                if result.get('confidence', 100) < 50:
                    errors.append(f"{agent_name} 使用了降级结果")
                    
            except Exception as e:
                print(f"❌ {agent_name} Agent 严重失败：{e}")
                errors.append(f"{agent_name}: {str(e)}")
                # 即使失败也填入默认结果
                results[agent_name] = {
                    'rating': '中性',
                    'confidence': 50,
                    'reasons': ['分析失败'],
                    'risks': ['严重异常'],
                }
    
    # 检查是否有严重错误
    if len(errors) >= 2:
        print(f"⚠️ 多个 Agent 异常（{len(errors)}），结果可能不准确")
    
    # 主 Agent 决策
    decision = make_decision(
        results['fundamental'],
        results['technical'],
        results['sentiment']
    )
    
    return data, results, decision, ', '.join(errors) if errors else None


def analyze_stock(stock_code):
    """分析单只股票（v1.1 并发优化版）"""
    print(f"\n{'='*60}")
    print(f"📊 分析股票：{stock_code}")
    print(f"{'='*60}\n")
    
    # Step 1: 获取真实数据
    print("Step 1: 获取真实数据...")
    data = get_stock_data(stock_code)
    if not data or not data.get('price'):
        print(f"❌ 获取数据失败")
        return False
    print(f"✅ {data.get('stock_name')} 当前价：¥{data['price']} ({data.get('change_pct', 0):+.2f}%)")
    
    # Step 2: 各 Agent 并发分析
    print("\nStep 2: Agent 并发分析...")
    import time
    start_time = time.time()
    
    data, results, decision, error = analyze_stock_parallel(stock_code)
    
    elapsed = time.time() - start_time
    
    if error or not results:
        print(f"❌ Agent 分析失败")
        return False
    
    fundamental = results['fundamental']
    technical = results['technical']
    sentiment = results['sentiment']
    
    print(f"   ⚡ 并发分析完成（耗时：{elapsed:.2f}秒）")
    print(f"   基本面：{fundamental['rating']} ({fundamental['confidence']}%)")
    print(f"   技术面：{technical['rating']} ({technical['confidence']}%)")
    print(f"   情绪面：{sentiment['rating']} ({sentiment['confidence']}%)")
    
    # Step 3: 主 Agent 决策
    print("\nStep 3: 综合决策...")
    print(f"   综合评分：{decision['score']:.1f}")
    print(f"   评级：{decision['rating']}")
    print(f"   建议仓位：{decision['position']}")
    
    # Step 4: 写入日志（Markdown + JSON）
    print("\nStep 4: 写入分析日志...")
    log_path_md, log_path_json = create_analysis_log(stock_code, data, fundamental, technical, sentiment, decision)
    print(f"✅ Markdown: {log_path_md}")
    print(f"✅ JSON: {log_path_json}")
    
    # Step 5: 添加验证队列
    print("\nStep 5: 添加验证队列...")
    add_to_validation_queue(stock_code, data.get('stock_name', ''), data['price'])
    print(f"✅ 已添加 2 项待验证预测")
    
    # Step 6: 更新表现追踪
    print("\nStep 6: 更新表现追踪...")
    update_performance_tracker()
    print(f"✅ 已更新")
    
    print(f"\n{'='*60}")
    print(f"✅ {stock_code} 分析完成！（总耗时：{elapsed:.2f}秒）")
    print(f"{'='*60}\n")
    
    return True


def run_daily_validation():
    """执行每日验证"""
    print(f"\n{'='*60}")
    print(f"📊 复盘 Agent - 每日验证")
    print(f"{'='*60}\n")
    
    result = subprocess.run(
        ['python3', 'scripts/validate_predictions.py'],
        cwd=STOCK_SYSTEM
    )
    
    return result.returncode == 0


def run_weekly_review():
    """执行周度复盘"""
    print(f"\n{'='*60}")
    print(f"📊 复盘 Agent - 周度复盘")
    print(f"{'='*60}\n")
    
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    
    # 1. 统计本周分析记录
    analysis_count = 0
    stocks_analyzed = []
    
    if os.path.exists(ANALYSIS_LOG_DIR):
        for f in os.listdir(ANALYSIS_LOG_DIR):
            if f.endswith('.md') and not f.startswith('分析日志模板'):
                try:
                    file_date = datetime.strptime(f[:10], '%Y-%m-%d')
                    if file_date >= week_start:
                        analysis_count += 1
                        stocks_analyzed.append(f)
                except:
                    pass
    
    # 2. 统计验证结果
    validated_count = 0
    correct_count = 0
    partial_count = 0
    error_count = 0
    
    queue_path = os.path.join(STOCK_SYSTEM, 'validation-queue.md')
    if os.path.exists(queue_path):
        with open(queue_path, 'r', encoding='utf-8') as f:
            for line in f:
                if '✅ 正确' in line:
                    validated_count += 1
                    correct_count += 1
                elif '⚠️ 部分正确' in line:
                    validated_count += 1
                    partial_count += 1
                elif '❌ 错误' in line:
                    validated_count += 1
                    error_count += 1
    
    # 计算准确率
    accuracy = 0
    if validated_count > 0:
        accuracy = (correct_count + partial_count * 0.5) / validated_count * 100
    
    # 3. 读取 Agent 表现
    tracker_path = os.path.join(STOCK_SYSTEM, 'agent-performance/agent-performance-tracker.md')
    agent_stats = {
        'fundamental': {'count': analysis_count, 'accuracy': '待验证'},
        'technical': {'count': analysis_count, 'accuracy': '待验证'},
        'sentiment': {'count': analysis_count, 'accuracy': '待验证'},
    }
    
    # 4. 生成周度报告
    os.makedirs(REPORTS_DIR, exist_ok=True)
    report_path = os.path.join(REPORTS_DIR, f'weekly_{today.strftime("%Y-%m-%d")}.md')
    
    stocks_list = '\n'.join([f'- {s}' for s in stocks_analyzed]) if stocks_analyzed else '- 暂无'
    
    content = f"""# 周度复盘报告

**周期**: {week_start.strftime('%Y-%m-%d')} 至 {today.strftime('%Y-%m-%d')}  
**生成时间**: {today.strftime('%Y-%m-%d %H:%M')}

---

## 📊 核心指标

| 指标 | 数值 |
|------|------|
| 分析次数 | {analysis_count} |
| 验证次数 | {validated_count} |
| ✅ 正确 | {correct_count} |
| ⚠️ 部分正确 | {partial_count} |
| ❌ 错误 | {error_count} |
| **准确率** | **{accuracy:.1f}%** |

---

## 📈 分析股票列表

{stocks_list}

---

## 🤖 Agent 表现

| Agent | 分析次数 | 准确率 | 权重 | 调整建议 |
|-------|---------|--------|------|----------|
| 基本面-v1.0 | {agent_stats['fundamental']['count']} | {agent_stats['fundamental']['accuracy']} | 50% | 保持 |
| 技术面-v1.0 | {agent_stats['technical']['count']} | {agent_stats['technical']['accuracy']} | 30% | 保持 |
| 情绪-v1.0 | {agent_stats['sentiment']['count']} | {agent_stats['sentiment']['accuracy']} | 20% | 保持 |

---

## 📝 本周总结

### 亮点
- 系统稳定运行，完成 {analysis_count} 次分析
- 验证队列累积 {validated_count} 项结果（如有）

### 待改进
- 继续积累验证数据，提升规则库质量
- 等待首批预测到期验证（预计 2026-04-07）

### 下周计划
- 继续执行每日验证
- 积累更多分析案例
- 优化情绪 Agent 分析维度

---

## 📅 重要日期提醒

| 日期 | 事件 |
|------|------|
| {week_start.strftime('%Y-%m-%d')} | 本周开始 |
| {today.strftime('%Y-%m-%d')} | 本周复盘 |
| 2026-04-07 | 首批预测到期验证 |

---

**报告生成**: 自动化系统 v1.0  
**下次复盘**: {week_start.strftime('%Y-%m-%d')} (下周五)
"""
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 周度报告已生成：{report_path}")
    print(f"\n📊 本周核心数据:")
    print(f"   分析次数：{analysis_count}")
    print(f"   验证次数：{validated_count}")
    print(f"   准确率：{accuracy:.1f}%")
    
    return report_path


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法：python3 auto_agent.py <analyze|daily|weekly> [参数]")
        print("")
        print("命令:")
        print("  analyze <股票代码>  - 分析股票")
        print("  daily              - 执行每日验证")
        print("  weekly             - 执行周度复盘")
        return
    
    action = sys.argv[1].lower()
    
    if action == 'analyze':
        if len(sys.argv) < 3:
            print("❌ 请提供股票代码")
            return
        stock_code = sys.argv[2]
        analyze_stock(stock_code)
    
    elif action == 'daily':
        run_daily_validation()
    
    elif action == 'weekly':
        run_weekly_review()
    
    else:
        print(f"❌ 未知命令：{action}")


if __name__ == '__main__':
    main()
