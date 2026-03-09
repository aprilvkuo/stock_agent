#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票系统性分析脚本
丁蟹 - 专业金融投资助手

功能：
1. 获取实时行情
2. 获取估值指标（PE、PB等）
3. 获取财务数据
4. 技术面分析
5. 综合评分与建议
"""

import urllib.request
import urllib.parse
import json
import sys
import logging
from datetime import datetime
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)

# 模拟数据（实际应用需要接入真实API）
def get_mock_stock_data(stock_code):
    """模拟股票数据（实际应用需接入东方财富/同花顺API）"""
    
    # 一些示例股票数据
    mock_data = {
        "600519": {  # 贵州茅台
            "name": "贵州茅台",
            "current_price": 1680.00,
            "change": 1.25,
            "volume": 285000,
            "market_cap": 2110000000000,
            "pe_ttm": 28.5,
            "pb": 8.2,
            "roe": 28.5,
            "revenue": 120500000000,
            "net_profit": 60800000000,
            "revenue_growth": 16.8,
            "profit_growth": 19.2,
            "ma5": 1675,
            "ma20": 1658,
            "ma60": 1620,
            "rsi": 62,
            "macd": "金叉向上"
        },
        "000858": {  # 五粮液
            "name": "五粮液",
            "current_price": 145.60,
            "change": 0.85,
            "volume": 420000,
            "market_cap": 565000000000,
            "pe_ttm": 22.3,
            "pb": 5.8,
            "roe": 26.2,
            "revenue": 83200000000,
            "net_profit": 30200000000,
            "revenue_growth": 14.2,
            "profit_growth": 16.5,
            "ma5": 144.8,
            "ma20": 142.5,
            "ma60": 140.2,
            "rsi": 58,
            "macd": "红柱扩大"
        },
        "002230": {  # 科大讯飞
            "name": "科大讯飞",
            "current_price": 52.80,
            "change": 3.25,
            "volume": 685000,
            "market_cap": 123000000000,
            "pe_ttm": 85.6,
            "pb": 8.9,
            "roe": 12.5,
            "revenue": 23500000000,
            "net_profit": 1430000000,
            "revenue_growth": 28.5,
            "profit_growth": 35.2,
            "ma5": 51.6,
            "ma20": 49.8,
            "ma60": 47.2,
            "rsi": 68,
            "macd": "金叉向上"
        },
        "00700": {  # 腾讯控股（港股）
            "name": "腾讯控股",
            "current_price": 298.50,
            "change": 2.35,
            "volume": 38500000,
            "market_cap": 2860000000000,
            "pe_ttm": 18.5,
            "pb": 4.2,
            "roe": 22.8,
            "revenue": 618000000000,
            "net_profit": 154500000000,
            "revenue_growth": 10.5,
            "profit_growth": 18.2,
            "ma5": 295.2,
            "ma20": 288.6,
            "ma60": 278.5,
            "rsi": 58,
            "macd": "金叉向上"
        },
        "HK00700": {  # 腾讯控股（港股，带HK前缀）
            "name": "腾讯控股",
            "current_price": 298.50,
            "change": 2.35,
            "volume": 38500000,
            "market_cap": 2860000000000,
            "pe_ttm": 18.5,
            "pb": 4.2,
            "roe": 22.8,
            "revenue": 618000000000,
            "net_profit": 154500000000,
            "revenue_growth": 10.5,
            "profit_growth": 18.2,
            "ma5": 295.2,
            "ma20": 288.6,
            "ma60": 278.5,
            "rsi": 58,
            "macd": "金叉向上"
        },
        "601138": {  # 工业富联
            "name": "工业富联",
            "current_price": 23.85,
            "change": 1.85,
            "volume": 1256000,
            "market_cap": 473500000000,
            "pe_ttm": 21.5,
            "pb": 3.8,
            "roe": 18.5,
            "revenue": 476300000000,
            "net_profit": 22050000000,
            "revenue_growth": -8.2,
            "profit_growth": 15.8,
            "ma5": 23.45,
            "ma20": 22.85,
            "ma60": 21.50,
            "rsi": 64,
            "macd": "红柱扩大"
        }
    }
    
    return mock_data.get(stock_code, None)

def calculate_score(data):
    """计算综合评分"""
    score = 0
    details = []
    
    # 基本面评分（30分）
    # ROE
    roe = data.get("roe", 0)
    if roe > 20:
        score += 10
        details.append(f"ROE {roe}% 优秀 (+10分)")
    elif roe > 15:
        score += 7
        details.append(f"ROE {roe}% 良好 (+7分)")
    elif roe > 10:
        score += 5
        details.append(f"ROE {roe}% 一般 (+5分)")
    else:
        details.append(f"ROE {roe}% 较弱 (+0分)")
    
    # 营收增长
    rev_growth = data.get("revenue_growth", 0)
    if rev_growth > 20:
        score += 10
        details.append(f"营收增长 {rev_growth}% 强劲 (+10分)")
    elif rev_growth > 10:
        score += 7
        details.append(f"营收增长 {rev_growth}% 良好 (+7分)")
    elif rev_growth > 5:
        score += 5
        details.append(f"营收增长 {rev_growth}% 一般 (+5分)")
    else:
        details.append(f"营收增长 {rev_growth}% 较弱 (+0分)")
    
    # 利润增长
    profit_growth = data.get("profit_growth", 0)
    if profit_growth > 20:
        score += 10
        details.append(f"利润增长 {profit_growth}% 强劲 (+10分)")
    elif profit_growth > 10:
        score += 7
        details.append(f"利润增长 {profit_growth}% 良好 (+7分)")
    elif profit_growth > 5:
        score += 5
        details.append(f"利润增长 {profit_growth}% 一般 (+5分)")
    else:
        details.append(f"利润增长 {profit_growth}% 较弱 (+0分)")
    
    # 估值面评分（25分）
    pe = data.get("pe_ttm", 100)
    if pe < 15:
        score += 15
        details.append(f"PE {pe}倍 低估 (+15分)")
    elif pe < 25:
        score += 10
        details.append(f"PE {pe}倍 合理偏低 (+10分)")
    elif pe < 40:
        score += 5
        details.append(f"PE {pe}倍 合理偏高 (+5分)")
    else:
        details.append(f"PE {pe}倍 高估 (+0分)")
    
    pb = data.get("pb", 10)
    if pb < 3:
        score += 10
        details.append(f"PB {pb}倍 低估 (+10分)")
    elif pb < 6:
        score += 5
        details.append(f"PB {pb}倍 合理 (+5分)")
    else:
        details.append(f"PB {pb}倍 偏高 (+0分)")
    
    # 技术面评分（25分）
    rsi = data.get("rsi", 50)
    if 40 <= rsi <= 60:
        score += 10
        details.append(f"RSI {rsi} 中性健康 (+10分)")
    elif 30 <= rsi < 40 or 60 < rsi <= 70:
        score += 7
        details.append(f"RSI {rsi} 轻度超买/超卖 (+7分)")
    else:
        details.append(f"RSI {rsi} 严重超买/超卖 (+0分)")
    
    # 趋势判断
    current = data.get("current_price", 0)
    ma5 = data.get("ma5", 0)
    ma20 = data.get("ma20", 0)
    ma60 = data.get("ma60", 0)
    
    if current > ma5 > ma20 > ma60:
        score += 15
        details.append(f"多头排列，强势上涨 (+15分)")
    elif current > ma20 > ma60:
        score += 10
        details.append(f"中期向上，趋势良好 (+10分)")
    elif current > ma60:
        score += 5
        details.append(f"长期向上，短期震荡 (+5分)")
    else:
        details.append(f"均线下方，趋势较弱 (+0分)")
    
    return score, details

def get_recommendation(score):
    """根据评分给出投资建议"""
    if score >= 80:
        return "🟢 强烈推荐", "建议重仓，逢低买入", "15-20%"
    elif score >= 60:
        return "🟡 推荐", "建议适中仓位，分批建仓", "10-15%"
    elif score >= 40:
        return "🟠 中性", "建议轻仓，观望为主", "5-10%"
    else:
        return "🔴 回避", "建议回避，不宜持有", "0-5%"

def analyze_stock(stock_code):
    """主分析函数"""
    print(f"\n{'='*60}")
    print(f"📊 股票系统性分析报告")
    print(f"{'='*60}")
    print(f"分析时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"股票代码：{stock_code}")
    print(f"{'='*60}\n")
    
    # 获取数据
    data = get_mock_stock_data(stock_code)
    
    if not data:
        print(f"❌ 未找到股票 {stock_code} 的数据")
        print("提示：目前支持以下示例股票：")
        print("  - 600519 (贵州茅台)")
        print("  - 000858 (五粮液)")
        print("  - 002230 (科大讯飞)")
        print("  - 00700 (腾讯控股-港股)")
        print("  - 601138 (工业富联)")
        return
    
    # 基本信息
    print(f"【基本信息】")
    print(f"  股票名称：{data['name']}")
    print(f"  当前股价：¥{data['current_price']:.2f}")
    print(f"  涨跌幅：{data['change']:+.2f}%")
    print(f"  成交量：{data['volume']:,}手")
    print(f"  总市值：¥{data['market_cap']/1e8:.2f}亿元")
    print()
    
    # 估值指标
    print(f"【估值指标】")
    print(f"  市盈率（PE TTM）：{data['pe_ttm']:.2f}倍")
    print(f"  市净率（PB）：{data['pb']:.2f}倍")
    print(f"  ROE：{data['roe']:.2f}%")
    print()
    
    # 财务数据
    print(f"【财务数据（最近季度）】")
    print(f"  营收：¥{data['revenue']/1e8:.2f}亿元（+{data['revenue_growth']:.1f}%）")
    print(f"  净利润：¥{data['net_profit']/1e8:.2f}亿元（+{data['profit_growth']:.1f}%）")
    print()
    
    # 技术面
    print(f"【技术面】")
    print(f"  均线系统：")
    print(f"    MA5：¥{data['ma5']:.2f}")
    print(f"    MA20：¥{data['ma20']:.2f}")
    print(f"    MA60：¥{data['ma60']:.2f}")
    print(f"  RSI：{data['rsi']}")
    print(f"  MACD：{data['macd']}")
    print()
    
    # 计算评分
    score, details = calculate_score(data)
    recommendation, advice, position = get_recommendation(score)
    
    # 评分详情
    print(f"【评分详情】")
    for detail in details:
        print(f"  {detail}")
    print()
    
    # 综合评分
    print(f"【综合评分】")
    print(f"  总分：{score}/100")
    print(f"  评级：{recommendation}")
    print()
    
    # 投资建议
    print(f"【投资建议】")
    print(f"  建议操作：{advice}")
    print(f"  建议仓位：{position}")
    print()
    
    # 风险提示
    print(f"【风险提示】")
    print(f"  1. 以上分析基于历史数据和当前市场情况")
    print(f"  2. 股市有风险，投资需谨慎")
    print(f"  3. 本分析仅供参考，不构成投资建议")
    print()
    
    print(f"{'='*60}")
    print(f"📊 丁蟹 - 专业、靠谱、通俗易懂")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python analyze_stock.py <股票代码>")
        print("示例：python analyze_stock.py 600519")
        print("\n支持的示例股票：")
        print("  600519 - 贵州茅台")
        print("  000858 - 五粮液")
        print("  002230 - 科大讯飞")
        print("  00700 - 腾讯控股（港股）")
        print("  601138 - 工业富联")
        sys.exit(1)
    
    stock_code = sys.argv[1]
    analyze_stock(stock_code)
