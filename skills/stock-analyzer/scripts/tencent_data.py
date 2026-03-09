#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
腾讯财经 API 数据获取模块
v1.3 新增 - 真实股票数据源

支持：
- A 股（上海/深圳）
- 港股
- 实时行情、估值指标、财务数据

API 文档：https://stockapp.finance.qq.com/mstats/
"""

import urllib.request
import urllib.parse
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# ============ 腾讯财经 API ============

def fetch_tencent_stock_data(stock_code: str) -> Optional[Dict[str, Any]]:
    """
    从腾讯财经获取股票实时数据
    
    A 股代码前缀:
    - sh + 6 位代码 (上海)
    - sz + 6 位代码 (深圳)
    
    港股代码前缀:
    - hk + 5 位代码
    
    返回 JSON 格式数据
    """
    
    # 转换股票代码为腾讯格式
    tencent_code = convert_to_tencent_code(stock_code)
    if not tencent_code:
        logger.error(f"无法转换股票代码：{stock_code}")
        return None
    
    # 腾讯财经 API（返回 JSONP，需要去除回调函数名）
    url = f"http://qt.gtimg.cn/q={tencent_code}"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://stockapp.finance.qq.com/',
        }
        
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read().decode('gbk')  # 腾讯返回 GBK 编码
            
        # 解析数据（格式：v_sh600519="51~贵州茅台~600519~1680.00~..."）
        return parse_tencent_response(content, stock_code)
        
    except urllib.error.URLError as e:
        logger.error(f"网络请求失败：{e}")
        return None
    except Exception as e:
        logger.error(f"获取数据异常：{e}")
        return None


def convert_to_tencent_code(stock_code: str) -> Optional[str]:
    """
    将股票代码转换为腾讯格式
    
    规则:
    - A 股 6 开头 → sh + 代码
    - A 股 0/3 开头 → sz + 代码
    - 港股 → hk + 代码
    """
    code = stock_code.strip()
    
    # 港股处理
    if code.startswith('0') and len(code) == 5:
        return f'hk{code}'
    elif code.startswith('hk') or code.startswith('HK'):
        return f'hk{code[2:]}'
    
    # A 股处理
    if len(code) == 6:
        if code.startswith('6'):
            return f'sh{code}'
        elif code.startswith('0') or code.startswith('3'):
            return f'sz{code}'
    
    logger.warning(f"未知的股票代码格式：{code}")
    return None


def parse_tencent_response(content: str, stock_code: str) -> Optional[Dict[str, Any]]:
    """
    解析腾讯财经返回的数据
    
    格式：v_sh600519="51~贵州茅台~600519~1680.00~1675.00~..."
    
    字段说明（~分隔）:
    0: 未知
    1: 股票名称
    2: 股票代码
    3: 当前价
    4: 昨收价
    5: 开盘价
    6: 最高价
    7: 最低价
    8: 买一价
    9: 买一量
    10: 买二价/量
    ...
    20: 涨跌幅（%）
    21: 涨跌额
    22: 换手率（%）
    23: 成交量（手）
    24: 成交额（万元）
    25: 总市值（亿元）
    26: 流通市值（亿元）
    27: 市盈率（PE TTM）
    28: 市净率（PB）
    29: 动态市盈率
    30: 未知
    31: 最高价（历史）
    32: 最低价（历史）
    33: 振幅
    34: 涨速（%）
    35: 未知
    36: 今开
    37: 昨收
    38: 未知
    39: 未知
    40: 未知
    41: 内盘
    42: 外盘
    43: 未知
    44: 量比
    45: 未知
    46: 股息率
    47: 未知
    48: 未知
    49: 未知
    50: 未知
    51: 未知
    52: ROE（%）
    53: 未知
    54: 总股本（亿股）
    55: 流通股本（亿股）
    """
    try:
        # 提取引号内的数据
        if '=' not in content or '""' in content:
            logger.warning(f"数据为空或格式错误：{content[:100]}")
            return None
        
        data_str = content.split('=')[1].strip().strip('"').strip('"')
        
        if not data_str:
            return None
        
        # 分割字段
        fields = data_str.split('~')
        
        if len(fields) < 30:
            logger.warning(f"数据字段不足：{len(fields)}")
            return None
        
        # 解析数据
        data = {
            'stock_code': stock_code,
            'name': fields[1] if len(fields) > 1 else '',
            'current_price': float(fields[3]) if len(fields) > 3 and fields[3] else 0,
            'close_yesterday': float(fields[4]) if len(fields) > 4 and fields[4] else 0,
            'open': float(fields[5]) if len(fields) > 5 and fields[5] else 0,
            'high': float(fields[6]) if len(fields) > 6 and fields[6] else 0,
            'low': float(fields[7]) if len(fields) > 7 and fields[7] else 0,
            'change_pct': float(fields[20]) if len(fields) > 20 and fields[20] else 0,
            'change': float(fields[21]) if len(fields) > 21 and fields[21] else 0,
            'turnover_rate': float(fields[22]) if len(fields) > 22 and fields[22] else 0,
            'volume': int(float(fields[23])) * 100 if len(fields) > 23 and fields[23] else 0,  # 手→股
            'turnover': float(fields[24]) * 1e4 if len(fields) > 24 and fields[24] else 0,  # 万元→元
            'market_cap': float(fields[25]) * 1e8 if len(fields) > 25 and fields[25] else 0,  # 亿元→元
            'float_market_cap': float(fields[26]) * 1e8 if len(fields) > 26 and fields[26] else 0,
            'pe_ttm': float(fields[27]) if len(fields) > 27 and fields[27] else None,
            'pb': float(fields[28]) if len(fields) > 28 and fields[28] else None,
            'amplitude': float(fields[33]) if len(fields) > 33 and fields[33] else 0,
            'roe': float(fields[52]) if len(fields) > 52 and fields[52] else None,
        }
        
        logger.info(f"成功获取 {stock_code} {data['name']} 数据，当前价：{data['current_price']}")
        return data
        
    except Exception as e:
        logger.error(f"解析数据异常：{e}")
        logger.debug(f"原始数据：{content[:200]}")
        return None


# ============ 补充数据（财务指标等） ============

def get_financial_data(stock_code: str) -> Dict[str, Any]:
    """
    获取财务数据（ROE、营收、利润等）
    
    当前实现：
    - 优先从缓存读取
    - 缓存缺失时使用模拟数据（待接入东方财富 API）
    """
    
    # 缓存数据（示例）
    financial_cache = {
        "600519": {
            "roe": 28.5,
            "revenue": 1205.0,
            "revenue_growth": 16.8,
            "net_profit": 608.0,
            "profit_growth": 19.2,
            "gross_margin": 92.5,
            "debt_ratio": 15.2,
        },
        "000858": {
            "roe": 26.2,
            "revenue": 832.0,
            "revenue_growth": 14.2,
            "net_profit": 302.0,
            "profit_growth": 16.5,
            "gross_margin": 75.8,
            "debt_ratio": 18.5,
        },
        "002230": {
            "roe": 12.5,
            "revenue": 235.0,
            "revenue_growth": 28.5,
            "net_profit": 14.3,
            "profit_growth": 35.2,
            "gross_margin": 42.3,
            "debt_ratio": 25.8,
        },
        "00700": {
            "roe": 22.8,
            "revenue": 6180.0,
            "revenue_growth": 10.5,
            "net_profit": 1545.0,
            "profit_growth": 18.2,
            "gross_margin": 48.5,
            "debt_ratio": 22.3,
        },
        "601138": {
            "roe": 18.5,
            "revenue": 4763.0,
            "revenue_growth": -8.2,
            "net_profit": 220.5,
            "profit_growth": 15.8,
            "gross_margin": 8.5,
            "debt_ratio": 45.2,
        },
    }
    
    return financial_cache.get(stock_code, {
        "roe": None,
        "revenue": None,
        "revenue_growth": None,
        "net_profit": None,
        "profit_growth": None,
        "gross_margin": None,
        "debt_ratio": None,
    })


def get_technical_indicators(stock_code: str) -> Dict[str, Any]:
    """
    获取技术指标（MA、RSI、MACD 等）
    
    当前实现：
    - 简单计算 MA（基于历史数据，当前使用缓存）
    - RSI、MACD 待实现
    """
    
    # 缓存数据（示例）
    technical_cache = {
        "600519": {"ma5": 1675, "ma20": 1658, "ma60": 1620, "rsi": 62, "macd": "金叉向上"},
        "000858": {"ma5": 144.8, "ma20": 142.5, "ma60": 140.2, "rsi": 58, "macd": "红柱扩大"},
        "002230": {"ma5": 51.6, "ma20": 49.8, "ma60": 47.2, "rsi": 68, "macd": "金叉向上"},
        "00700": {"ma5": 295.2, "ma20": 288.6, "ma60": 278.5, "rsi": 58, "macd": "金叉向上"},
        "601138": {"ma5": 23.45, "ma20": 22.85, "ma60": 21.50, "rsi": 64, "macd": "红柱扩大"},
    }
    
    return technical_cache.get(stock_code, {
        "ma5": None,
        "ma20": None,
        "ma60": None,
        "rsi": None,
        "macd": "未知",
    })


# ============ 统一接口 ============

def get_stock_data_full(stock_code: str) -> Optional[Dict[str, Any]]:
    """
    获取完整的股票数据（实时 + 财务 + 技术）
    
    返回统一格式的数据字典
    """
    
    # Step 1: 获取实时行情（腾讯财经 API）
    realtime_data = fetch_tencent_stock_data(stock_code)
    if not realtime_data:
        logger.error(f"获取实时数据失败：{stock_code}")
        return None
    
    # Step 2: 获取财务数据
    financial_data = get_financial_data(stock_code)
    
    # Step 3: 获取技术指标
    technical_data = get_technical_indicators(stock_code)
    
    # Step 4: 合并数据
    full_data = {
        'stock_code': stock_code,
        'timestamp': datetime.now().isoformat(),
        
        # 实时行情
        'name': realtime_data.get('name'),
        'price': realtime_data.get('current_price'),
        'change_pct': realtime_data.get('change_pct'),
        'change': realtime_data.get('change'),
        'open': realtime_data.get('open'),
        'high': realtime_data.get('high'),
        'low': realtime_data.get('low'),
        'close_yesterday': realtime_data.get('close_yesterday'),
        'volume': realtime_data.get('volume'),
        'turnover': realtime_data.get('turnover'),
        'market_cap': realtime_data.get('market_cap'),
        
        # 估值指标
        'pe': realtime_data.get('pe_ttm'),
        'pb': realtime_data.get('pb'),
        'turnover_rate': realtime_data.get('turnover_rate'),
        'amplitude': realtime_data.get('amplitude'),
        'roe': realtime_data.get('roe') or financial_data.get('roe'),
        
        # 财务数据
        'revenue': financial_data.get('revenue'),
        'revenue_growth': financial_data.get('revenue_growth'),
        'profit': financial_data.get('net_profit'),
        'profit_growth': financial_data.get('profit_growth'),
        'gross_margin': financial_data.get('gross_margin'),
        'debt_ratio': financial_data.get('debt_ratio'),
        
        # 技术指标
        'ma5': technical_data.get('ma5'),
        'ma20': technical_data.get('ma20'),
        'ma60': technical_data.get('ma60'),
        'rsi': technical_data.get('rsi'),
        'macd': technical_data.get('macd'),
    }
    
    logger.info(f"完整数据获取成功：{stock_code} {full_data['name']}")
    return full_data


# ============ 测试 ============

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法：python tencent_data.py <股票代码>")
        print("示例：python tencent_data.py 600519")
        sys.exit(1)
    
    stock_code = sys.argv[1]
    
    print(f"\n{'='*60}")
    print(f"测试腾讯财经 API - {stock_code}")
    print(f"{'='*60}\n")
    
    data = get_stock_data_full(stock_code)
    
    if not data:
        print("❌ 获取数据失败")
        sys.exit(1)
    
    print(f"【基本信息】")
    print(f"  股票名称：{data['name']}")
    print(f"  股票代码：{data['stock_code']}")
    print(f"  当前股价：¥{data['price']:.2f}")
    print(f"  涨跌幅：{data['change_pct']:+.2f}%")
    print(f"  成交量：{data['volume']:,}股")
    print()
    
    print(f"【估值指标】")
    pe_str = f"{data['pe']}" if data['pe'] else "N/A"
    pb_str = f"{data['pb']}" if data['pb'] else "N/A"
    print(f"  PE(TTM): {pe_str}")
    print(f"  PB: {pb_str}")
    print(f"  ROE: {data['roe']}%" if data['roe'] else "  ROE: N/A")
    print()
    
    print(f"【财务数据】")
    if data['revenue']:
        print(f"  营收：¥{data['revenue']}亿元（+{data['revenue_growth']}%）")
    else:
        print(f"  营收：N/A")
    if data['profit']:
        print(f"  净利润：¥{data['profit']}亿元（+{data['profit_growth']}%）")
    else:
        print(f"  净利润：N/A")
    print()
    
    print(f"【技术指标】")
    if data['ma5']:
        print(f"  MA5: ¥{data['ma5']}")
        print(f"  MA20: ¥{data['ma20']}")
        print(f"  MA60: ¥{data['ma60']}")
    else:
        print(f"  MA: N/A")
    print(f"  RSI: {data['rsi']}" if data['rsi'] else "  RSI: N/A")
    print(f"  MACD: {data['macd']}")
    print()
    
    print(f"{'='*60}")
    print(f"✅ 数据获取成功！")
    print(f"{'='*60}\n")
