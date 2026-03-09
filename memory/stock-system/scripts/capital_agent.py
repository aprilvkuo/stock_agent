#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
资金面 Agent - v1.5 新增

分析维度:
1. 北向资金流向
2. 主力资金流向
3. 成交量分析
4. 资金热度评估

数据源:
- 东方财富 API（北向资金）
- 腾讯财经 API（主力资金）
"""

import urllib.request
import urllib.parse
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# ============ 东方财富 API - 北向资金 ============

def fetch_northbound_flow(stock_code: str) -> Optional[Dict[str, Any]]:
    """
    获取北向资金流向数据
    
    返回:
    - 净流入金额（万元）
    - 占成交额比
    - 连续净流入天数
    """
    try:
        # 东方财富北向资金个股数据
        # 格式：sh600519 或 sz000858
        sina_code = convert_to_sina_code(stock_code)
        if not sina_code:
            return None
        
        url = f"http://push2.eastmoney.com/api/qt/stock/northflow/get?secid={sina_code}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Referer': 'https://data.eastmoney.com/hsgt/index.html',
        }
        
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read().decode('utf-8')
        
        data = json.loads(content)
        
        if data.get('data'):
            nf_data = data['data']
            return {
                'northbound_net_inflow': nf_data.get('netInflow', 0),  # 净流入（万元）
                'northbound_ratio': nf_data.get('inflowRatio', 0),  # 占成交额比（%）
                'northbound_buy': nf_data.get('buy', 0),  # 买入额（万元）
                'northbound_sell': nf_data.get('sell', 0),  # 卖出额（万元）
            }
        
        return None
        
    except Exception as e:
        logger.debug(f"获取北向资金失败：{e}")
        return None


def convert_to_sina_code(stock_code: str) -> Optional[str]:
    """转换为东方财富格式"""
    code = stock_code.strip()
    if len(code) == 6:
        if code.startswith('6'):
            return f'1.{code}'  # 上海
        elif code.startswith('0') or code.startswith('3'):
            return f'0.{code}'  # 深圳
    return None


# ============ 主力资金分析 ============

def analyze_main_flow(stock_code: str, price_data: Dict) -> Optional[Dict[str, Any]]:
    """
    分析主力资金流向
    
    基于量价关系推算主力资金
    """
    try:
        # 简化版：基于涨跌幅和成交量推算
        change_pct = price_data.get('change_pct', 0)
        volume = price_data.get('volume', 0)
        
        # 估算主力资金（简化模型）
        # 上涨 + 放量 = 主力流入
        # 下跌 + 放量 = 主力流出
        # 上涨 + 缩量 = 主力观望
        # 下跌 + 缩量 = 主力观望
        
        if change_pct > 3 and volume > 0:
            flow_direction = '流入'
            flow_strength = '强'
            flow_score = 80
        elif change_pct > 1:
            flow_direction = '流入'
            flow_strength = '中'
            flow_score = 60
        elif change_pct > -1:
            flow_direction = '观望'
            flow_strength = '弱'
            flow_score = 50
        elif change_pct > -3:
            flow_direction = '流出'
            flow_strength = '中'
            flow_score = 40
        else:
            flow_direction = '流出'
            flow_strength = '强'
            flow_score = 20
        
        return {
            'main_flow_direction': flow_direction,
            'main_flow_strength': flow_strength,
            'main_flow_score': flow_score,
            'volume': volume,
        }
        
    except Exception as e:
        logger.error(f"分析主力资金失败：{e}")
        return None


# ============ 资金热度分析 ============

def analyze_capital_heat(stock_code: str, price_data: Dict, northbound_data: Optional[Dict]) -> Dict[str, Any]:
    """
    分析资金热度
    
    综合北向资金、主力资金、成交量
    """
    score = 50  # 基础分
    reasons = []
    risks = []
    
    # 北向资金评分（最高 30 分）
    if northbound_data and northbound_data.get('northbound_net_inflow'):
        net_inflow = northbound_data['northbound_net_inflow']
        if net_inflow > 5000:  # 净流入>5000 万
            score += 30
            reasons.append(f"北向资金大幅净流入{net_inflow/10000:.1f}亿元 (+30 分)")
        elif net_inflow > 1000:
            score += 20
            reasons.append(f"北向资金净流入{net_inflow/10000:.1f}亿元 (+20 分)")
        elif net_inflow > 0:
            score += 10
            reasons.append(f"北向资金小幅净流入{net_inflow/10000:.1f}亿元 (+10 分)")
        elif net_inflow < -5000:
            score -= 30
            risks.append(f"北向资金大幅净流出{abs(net_inflow)/10000:.1f}亿元 (-30 分)")
        elif net_inflow < -1000:
            score -= 20
            risks.append(f"北向资金净流出{abs(net_inflow)/10000:.1f}亿元 (-20 分)")
        else:
            score -= 10
            risks.append(f"北向资金小幅净流出{abs(net_inflow)/10000:.1f}亿元 (-10 分)")
    else:
        reasons.append("北向资金数据缺失 (0 分)")
    
    # 主力资金评分（最高 30 分）
    main_flow = analyze_main_flow(stock_code, price_data)
    if main_flow and main_flow.get('main_flow_score'):
        flow_score = main_flow.get('main_flow_score', 50)
        flow_dir = main_flow.get('flow_direction', '未知')
        flow_str = main_flow.get('flow_strength', '未知')
        
        if flow_score >= 70:
            score += 30
            reasons.append(f"主力资金{flow_dir}({flow_str}) (+30 分)")
        elif flow_score >= 50:
            score += 15
            reasons.append(f"主力资金{flow_dir}({flow_str}) (+15 分)")
        else:
            score -= 15
            risks.append(f"主力资金{flow_dir}({flow_str}) (-15 分)")
    
    # 成交量评分（最高 20 分）
    if price_data.get('volume'):
        volume = price_data['volume']
        if volume > 10000000:  # 成交量>1000 万手
            score += 20
            reasons.append(f"成交量{volume/10000:.1f}万手，交投活跃 (+20 分)")
        elif volume > 1000000:
            score += 10
            reasons.append(f"成交量{volume/10000:.1f}万手，交投正常 (+10 分)")
        else:
            reasons.append(f"成交量{volume/10000:.1f}万手，交投清淡 (0 分)")
    
    # 综合评级
    if score >= 90:
        rating = '🔥 极热'
        confidence = 85
    elif score >= 70:
        rating = '📈 偏热'
        confidence = 75
    elif score >= 50:
        rating = '➖ 中性'
        confidence = 60
    elif score >= 30:
        rating = '📉 偏冷'
        confidence = 70
    else:
        rating = '❄️ 极冷'
        confidence = 80
    
    return {
        'rating': rating,
        'confidence': confidence,
        'score': score,
        'reasons': reasons,
        'risks': risks,
        'northbound': northbound_data,
        'main_flow': main_flow,
    }


# ============ 资金面 Agent 主函数 ============

def analyze_capital_face(stock_code: str, price_data: Dict) -> Dict[str, Any]:
    """
    资金面 Agent 分析 v1.5
    
    参数:
        stock_code: 股票代码
        price_data: 价格数据（包含涨跌幅、成交量等）
    
    返回:
        资金面分析结果
    """
    logger.info(f"开始资金面分析：{stock_code}")
    
    # Step 1: 获取北向资金数据
    northbound_data = fetch_northbound_flow(stock_code)
    
    # Step 2: 分析资金热度
    heat_result = analyze_capital_heat(stock_code, price_data, northbound_data)
    
    # Step 3: 生成分析结论
    rating = heat_result['rating']
    confidence = heat_result['confidence']
    reasons = heat_result['reasons']
    risks = heat_result['risks']
    
    # 投资建议
    if heat_result['score'] >= 70:
        suggestion = '资金面积极，可关注'
    elif heat_result['score'] >= 50:
        suggestion = '资金面中性，观望为主'
    else:
        suggestion = '资金面消极，注意风险'
    
    return {
        'rating': rating,
        'confidence': confidence,
        'score': heat_result['score'],
        'reasons': reasons,
        'risks': risks,
        'suggestion': suggestion,
        'northbound_data': northbound_data,
        'main_flow': heat_result.get('main_flow'),
    }


# ============ 测试 ============

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法：python capital_agent.py <股票代码>")
        print("示例：python capital_agent.py 600519")
        sys.exit(1)
    
    stock_code = sys.argv[1]
    
    print(f"\n{'='*60}")
    print(f"资金面 Agent 分析 - {stock_code}")
    print(f"{'='*60}\n")
    
    # 模拟价格数据
    price_data = {
        'change_pct': 3.0,
        'volume': 1256000,
    }
    
    result = analyze_capital_face(stock_code, price_data)
    
    print(f"【资金面评级】")
    print(f"  评级：{result['rating']}")
    print(f"  置信度：{result['confidence']}%")
    print(f"  综合得分：{result['score']}")
    print()
    
    print(f"【分析依据】")
    for reason in result['reasons']:
        print(f"  ✅ {reason}")
    print()
    
    if result['risks']:
        print(f"【风险提示】")
        for risk in result['risks']:
            print(f"  ⚠️ {risk}")
        print()
    
    print(f"【投资建议】")
    print(f"  {result['suggestion']}")
    print()
    
    if result['northbound_data']:
        print(f"【北向资金】")
        nb = result['northbound_data']
        print(f"  净流入：{nb.get('northbound_net_inflow', 0)/10000:.2f}亿元")
        print(f"  占成交额比：{nb.get('northbound_ratio', 0):.2f}%")
        print()
    
    print(f"{'='*60}")
