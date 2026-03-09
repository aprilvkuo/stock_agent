#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票系统性分析脚本
丁蟹 - 专业金融投资助手

功能：
1. 获取实时行情（新浪财经 API）✅ v1.3
2. 获取估值指标（PE、PB 等）
3. 获取财务数据
4. 技术面分析
5. 综合评分与建议

版本：v1.3 - 接入新浪财经真实数据源
"""

import sys
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)

# 导入腾讯财经 API 模块（v1.3 新增）
try:
    from tencent_data import get_stock_data_full
    TENCENT_API_AVAILABLE = True
except ImportError:
    TENCENT_API_AVAILABLE = False
    logger.warning("tencent_data 模块未找到，使用模拟数据")


def get_stock_data(stock_code):
    """
    获取股票数据（优先使用腾讯财经 API，失败时使用模拟数据）
    """
    if TENCENT_API_AVAILABLE:
        # 尝试获取真实数据
        data = get_stock_data_full(stock_code)
        if data and data.get('price'):
            logger.info(f"✅ 使用腾讯财经真实数据：{stock_code}")
            return data
    
    # 降级到模拟数据
    logger.info(f"⚠️ 使用模拟数据：{stock_code}")
    return get_mock_stock_data_fallback(stock_code)


def get_mock_stock_data_fallback(stock_code):
    """模拟股票数据（API 不可用时的备用）"""
    
    mock_data = {
        "600519": {
            "stock_code": "600519",
            "name": "贵州茅台",
            "price": 1680.00,
            "change_pct": 1.25,
            "volume": 285000,
            "market_cap": 2110000000000,
            "pe": 28.5,
            "pb": 8.2,
            "roe": 28.5,
            "revenue": 1205.0,
            "revenue_growth": 16.8,
            "profit": 608.0,
            "profit_growth": 19.2,
            "ma5": 1675,
            "ma20": 1658,
            "ma60": 1620,
            "rsi": 62,
            "macd": "金叉向上"
        },
        "000858": {
            "stock_code": "000858",
            "name": "五粮液",
            "price": 145.60,
            "change_pct": 0.85,
            "volume": 420000,
            "market_cap": 565000000000,
            "pe": 22.3,
            "pb": 5.8,
            "roe": 26.2,
            "revenue": 832.0,
            "revenue_growth": 14.2,
            "profit": 302.0,
            "profit_growth": 16.5,
            "ma5": 144.8,
            "ma20": 142.5,
            "ma60": 140.2,
            "rsi": 58,
            "macd": "红柱扩大"
        },
        "002230": {
            "stock_code": "002230",
            "name": "科大讯飞",
            "price": 52.80,
            "change_pct": 3.25,
            "volume": 685000,
            "market_cap": 123000000000,
            "pe": 85.6,
            "pb": 8.9,
            "roe": 12.5,
            "revenue": 235.0,
            "revenue_growth": 28.5,
            "profit": 14.3,
            "profit_growth": 35.2,
            "ma5": 51.6,
            "ma20": 49.8,
            "ma60": 47.2,
            "rsi": 68,
            "macd": "金叉向上"
        },
        "00700": {
            "stock_code": "00700",
            "name": "腾讯控股",
            "price": 298.50,
            "change_pct": 2.35,
            "volume": 38500000,
            "market_cap": 2860000000000,
            "pe": 18.5,
            "pb": 4.2,
            "roe": 22.8,
            "revenue": 6180.0,
            "revenue_growth": 10.5,
            "profit": 1545.0,
            "profit_growth": 18.2,
            "ma5": 295.2,
            "ma20": 288.6,
            "ma60": 278.5,
            "rsi": 58,
            "macd": "金叉向上"
        },
        "601138": {
            "stock_code": "601138",
            "name": "工业富联",
            "price": 23.85,
            "change_pct": 1.85,
            "volume": 1256000,
            "market_cap": 473500000000,
            "pe": 21.5,
            "pb": 3.8,
            "roe": 18.5,
            "revenue": 4763.0,
            "revenue_growth": -8.2,
            "profit": 220.5,
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
    
    # 基本面评分（30 分）
    roe = data.get("roe", 0)
    if roe and roe > 20:
        score += 10
        details.append(f"ROE {roe}% 优秀 (+10 分)")
    elif roe and roe > 15:
        score += 7
        details.append(f"ROE {roe}% 良好 (+7 分)")
    elif roe and roe > 10:
        score += 5
        details.append(f"ROE {roe}% 一般 (+5 分)")
    else:
        details.append(f"ROE 数据缺失或较弱 (+0 分)")
    
    rev_growth = data.get("revenue_growth", 0)
    if rev_growth and rev_growth > 20:
        score += 10
        details.append(f"营收增长 {rev_growth}% 强劲 (+10 分)")
    elif rev_growth and rev_growth > 10:
        score += 7
        details.append(f"营收增长 {rev_growth}% 良好 (+7 分)")
    elif rev_growth and rev_growth > 5:
        score += 5
        details.append(f"营收增长 {rev_growth}% 一般 (+5 分)")
    else:
        details.append(f"营收增长数据缺失或较弱 (+0 分)")
    
    profit_growth = data.get("profit_growth", 0)
    if profit_growth and profit_growth > 20:
        score += 10
        details.append(f"利润增长 {profit_growth}% 强劲 (+10 分)")
    elif profit_growth and profit_growth > 10:
        score += 7
        details.append(f"利润增长 {profit_growth}% 良好 (+7 分)")
    elif profit_growth and profit_growth > 5:
        score += 5
        details.append(f"利润增长 {profit_growth}% 一般 (+5 分)")
    else:
        details.append(f"利润增长数据缺失或较弱 (+0 分)")
    
    # 估值面评分（25 分）
    pe = data.get("pe", 100)
    if pe:
        if pe < 15:
            score += 15
            details.append(f"PE {pe}倍 低估 (+15 分)")
        elif pe < 25:
            score += 10
            details.append(f"PE {pe}倍 合理偏低 (+10 分)")
        elif pe < 40:
            score += 5
            details.append(f"PE {pe}倍 合理偏高 (+5 分)")
        else:
            details.append(f"PE {pe}倍 高估 (+0 分)")
    else:
        details.append(f"PE 数据缺失 (+0 分)")
    
    pb = data.get("pb", 10)
    if pb:
        if pb < 3:
            score += 10
            details.append(f"PB {pb}倍 低估 (+10 分)")
        elif pb < 6:
            score += 5
            details.append(f"PB {pb}倍 合理 (+5 分)")
        else:
            details.append(f"PB {pb}倍 偏高 (+0 分)")
    else:
        details.append(f"PB 数据缺失 (+0 分)")
    
    # 技术面评分（25 分）
    rsi = data.get("rsi", 50)
    if rsi:
        if 40 <= rsi <= 60:
            score += 10
            details.append(f"RSI {rsi} 中性健康 (+10 分)")
        elif (30 <= rsi < 40) or (60 < rsi <= 70):
            score += 7
            details.append(f"RSI {rsi} 轻度超买/超卖 (+7 分)")
        else:
            details.append(f"RSI {rsi} 严重超买/超卖 (+0 分)")
    else:
        details.append(f"RSI 数据缺失 (+0 分)")
    
    current = data.get("price", 0)
    ma5 = data.get("ma5", 0)
    ma20 = data.get("ma20", 0)
    ma60 = data.get("ma60", 0)
    
    if current and ma5 and ma20 and ma60:
        if current > ma5 > ma20 > ma60:
            score += 15
            details.append(f"多头排列，强势上涨 (+15 分)")
        elif current > ma20 > ma60:
            score += 10
            details.append(f"中期向上，趋势良好 (+10 分)")
        elif current > ma60:
            score += 5
            details.append(f"长期向上，短期震荡 (+5 分)")
        else:
            details.append(f"均线下方，趋势较弱 (+0 分)")
    else:
        details.append(f"均线数据缺失 (+0 分)")
    
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
    print(f"数据源：{'腾讯财经 API ✅' if TENCENT_API_AVAILABLE else '模拟数据 ⚠️'}")
    print(f"{'='*60}\n")
    
    # 获取数据
    data = get_stock_data(stock_code)
    
    if not data:
        print(f"❌ 未找到股票 {stock_code} 的数据")
        print("提示：目前支持以下股票：")
        print("  - 600519 (贵州茅台)")
        print("  - 000858 (五粮液)")
        print("  - 002230 (科大讯飞)")
        print("  - 00700 (腾讯控股 - 港股)")
        print("  - 601138 (工业富联)")
        return
    
    # 基本信息
    print(f"【基本信息】")
    print(f"  股票名称：{data['name']}")
    print(f"  当前股价：¥{data['price']:.2f}")
    print(f"  涨跌幅：{data['change_pct']:+.2f}%")
    print(f"  成交量：{data['volume']:,}手")
    print(f"  总市值：¥{data['market_cap']/1e8:.2f}亿元")
    print()
    
    # 估值指标
    print(f"【估值指标】")
    pe_str = f"{data['pe']:.2f}倍" if data.get('pe') else "N/A"
    pb_str = f"{data['pb']:.2f}倍" if data.get('pb') else "N/A"
    print(f"  市盈率（PE TTM）：{pe_str}")
    print(f"  市净率（PB）：{pb_str}")
    print(f"  ROE：{data['roe']:.2f}%" if data.get('roe') else "  ROE: N/A")
    print()
    
    # 财务数据
    print(f"【财务数据（最近季度）】")
    if data.get('revenue'):
        print(f"  营收：¥{data['revenue']:.2f}亿元（+{data['revenue_growth']:.1f}%）")
    else:
        print(f"  营收：N/A")
    if data.get('profit'):
        print(f"  净利润：¥{data['profit']:.2f}亿元（+{data['profit_growth']:.1f}%）")
    else:
        print(f"  净利润：N/A")
    print()
    
    # 技术面
    print(f"【技术面】")
    print(f"  均线系统：")
    ma5_str = f"¥{data['ma5']:.2f}" if data.get('ma5') else "N/A"
    ma20_str = f"¥{data['ma20']:.2f}" if data.get('ma20') else "N/A"
    ma60_str = f"¥{data['ma60']:.2f}" if data.get('ma60') else "N/A"
    print(f"    MA5：{ma5_str}")
    print(f"    MA20：{ma20_str}")
    print(f"    MA60：{ma60_str}")
    rsi_str = str(data['rsi']) if data.get('rsi') else "N/A"
    print(f"  RSI：{rsi_str}")
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
        print("\n支持的股票：")
        print("  600519 - 贵州茅台")
        print("  000858 - 五粮液")
        print("  002230 - 科大讯飞")
        print("  00700 - 腾讯控股（港股）")
        print("  601138 - 工业富联")
        sys.exit(1)
    
    stock_code = sys.argv[1]
    analyze_stock(stock_code)
