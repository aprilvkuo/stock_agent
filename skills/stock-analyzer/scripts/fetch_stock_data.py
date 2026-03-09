#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票实时数据抓取脚本
支持：东方财富、同花顺、新浪财经等数据源
丁蟹 - 专业金融投资助手
"""

import urllib.request
import urllib.parse
import json
import re
import sys
from datetime import datetime

class StockDataFetcher:
    """股票数据抓取器"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
    
    def _get_full_code(self, stock_code):
        """获取完整的股票代码（带交易所前缀）"""
        # 上海主板：60开头
        if stock_code.startswith('60') or stock_code.startswith('68'):
            return f"sh{stock_code}"
        # 深圳主板/创业板：00/30开头
        elif stock_code.startswith('00') or stock_code.startswith('30') or stock_code.startswith('39'):
            return f"sz{stock_code}"
        # 港股
        elif len(stock_code) == 5 or (len(stock_code) == 4 and stock_code.isdigit()):
            return f"hk{stock_code}"
        else:
            return stock_code
    
    def fetch_from_eastmoney(self, stock_code):
        """
        从东方财富获取股票数据
        数据来源：东方财富网实时行情API
        """
        full_code = self._get_full_code(stock_code)
        
        try:
            # 东方财富实时行情API
            url = f"https://push2.eastmoney.com/api/qt/stock/get?ut=fa5fd1943c7b386f172d6893dbfba10b&fltt=2&invt=2&volt=2&fields=f43,f44,f45,f46,f47,f48,f50,f51,f52,f57,f58,f60,f61,f62,f116,f117,f162,f163,f164,f165,f167,f168,f169,f170,f171,f173,f177,f183,f184,f185,f186,f187,f188,f189,f190&secid={full_code}"
            
            req = urllib.request.Request(url, headers=self.headers)
            
            with urllib.request.urlopen(req, timeout=10) as f:
                response = f.read().decode('utf-8')
                data = json.loads(response)
            
            if data.get('data'):
                d = data['data']
                return {
                    'source': '东方财富',
                    'stock_name': d.get('f58', ''),
                    'stock_code': stock_code,
                    'current_price': d.get('f43', 0) / 100 if d.get('f43') else 0,
                    'change_percent': d.get('f170', 0) / 100 if d.get('f170') else 0,
                    'volume': d.get('f47', 0) / 100 if d.get('f47') else 0,
                    'turnover': d.get('f48', 0) / 10000 if d.get('f48') else 0,
                    'market_cap': d.get('f116', 0) / 100000000 if d.get('f116') else 0,
                    'pe_ttm': d.get('f162', 0) / 100 if d.get('f162') else 0,
                    'pb': d.get('f167', 0) / 100 if d.get('f167') else 0,
                    'high_52w': d.get('f174', 0) / 100 if d.get('f174') else 0,
                    'low_52w': d.get('f175', 0) / 100 if d.get('f175') else 0,
                }
            else:
                return None
                
        except Exception as e:
            print(f"东方财富数据获取失败: {e}")
            return None
    
    def fetch_from_sina(self, stock_code):
        """
        从新浪财经获取股票数据
        数据来源：新浪财经实时行情API
        """
        full_code = self._get_full_code(stock_code)
        
        try:
            # 新浪财经实时行情API
            url = f"https://hq.sinajs.cn/list={full_code}"
            
            # 新浪财经需要特定的Referer
            headers = self.headers.copy()
            headers['Referer'] = 'https://finance.sina.com.cn'
            
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=10) as f:
                response = f.read().decode('gb2312', errors='ignore')
            
            # 解析数据
            match = re.search(r'"([^"]+)"', response)
            if match:
                data_str = match.group(1)
                parts = data_str.split(',')
                
                if len(parts) >= 33:
                    # 根据新浪财经数据格式解析
                    return {
                        'source': '新浪财经',
                        'stock_name': parts[0],
                        'stock_code': stock_code,
                        'current_price': float(parts[3]),
                        'change_percent': float(parts[32]) if len(parts) > 32 else 0,
                        'volume': int(parts[8]) / 100 if len(parts) > 8 else 0,
                        'turnover': float(parts[9]) / 10000 if len(parts) > 9 else 0,
                        'market_cap': 0,  # 新浪财经接口不直接提供
                        'high_52w': float(parts[5]) if len(parts) > 5 else 0,
                        'low_52w': float(parts[6]) if len(parts) > 6 else 0,
                    }
            
            return None
            
        except Exception as e:
            print(f"新浪财经数据获取失败: {e}")
            return None
    
    def analyze(self, stock_code):
        """
        综合分析股票
        尝试多个数据源，取最完整的数据
        """
        print(f"\n{'='*60}")
        print(f"📊 开始分析股票：{stock_code}")
        print(f"{'='*60}\n")
        
        # 尝试从东方财富获取数据
        data = self.fetch_from_eastmoney(stock_code)
        
        # 如果失败，尝试新浪财经
        if not data:
            print("尝试从新浪财经获取数据...")
            data = self.fetch_from_sina(stock_code)
        
        if not data:
            print(f"\n❌ 未能获取到 {stock_code} 的数据")
            print("可能原因：")
            print("  1. 股票代码不存在")
            print("  2. 该股票已退市")
            print("  3. 数据源暂时不可用")
            print("\n请检查股票代码是否正确（如：600519、000858）")
            return None
        
        # 输出分析结果
        self._print_analysis(data)
        
        return data
    
    def _print_analysis(self, data):
        """打印分析结果"""
        print(f"\n{'='*60}")
        print(f"📊 {data['stock_name']}（{data['stock_code']}）分析结果")
        print(f"数据来源：{data['source']}")
        print(f"{'='*60}\n")
        
        # 实时行情
        print(f"【实时行情】")
        print(f"  当前股价：¥{data.get('current_price', 0):.2f}")
        print(f"  涨跌幅：{data.get('change_percent', 0):+.2f}%")
        print(f"  成交量：{data.get('volume', 0):,.0f}手")
        print(f"  成交额：{data.get('turnover', 0):.2f}亿元")
        if data.get('market_cap'):
            print(f"  总市值：{data.get('market_cap', 0):.2f}亿元")
        print()
        
        # 估值指标
        if data.get('pe_ttm') or data.get('pb'):
            print(f"【估值指标】")
            if data.get('pe_ttm'):
                print(f"  市盈率（PE TTM）：{data.get('pe_ttm', 0):.2f}倍")
            if data.get('pb'):
                print(f"  市净率（PB）：{data.get('pb', 0):.2f}倍")
            print()
        
        # 技术面（如果有数据）
        if data.get('high_52w') or data.get('low_52w'):
            print(f"【价格区间】")
            if data.get('high_52w'):
                print(f"  52周最高价：¥{data.get('high_52w', 0):.2f}")
            if data.get('low_52w'):
                print(f"  52周最低价：¥{data.get('low_52w', 0):.2f}")
            print()
        
        # 综合建议（基于获取到的数据给出简单建议）
        print(f"【简要建议】")
        
        # 基于涨跌幅给出简单建议
        change = data.get('change_percent', 0)
        if change > 5:
            print(f"  ⚠️ 今日涨幅较大（+{change:.2f}%），建议谨慎追高")
        elif change > 2:
            print(f"  📈 今日表现强势（+{change:.2f}%），可关注回调机会")
        elif change > -2:
            print(f"  ➡️ 今日横盘震荡（{change:+.2f}%），建议观望")
        elif change > -5:
            print(f"  📉 今日回调（{change:+.2f}%），可关注支撑位")
        else:
            print(f"  🔴 今日大跌（{change:+.2f}%），建议谨慎操作")
        
        print(f"\n{'='*60}")
        print(f"📊 丁蟹 - 专业、靠谱、通俗易懂")
        print(f"{'='*60}\n")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法：python analyze_stock.py <股票代码>")
        print("示例：")
        print("  python analyze_stock.py 600519  （贵州茅台）")
        print("  python analyze_stock.py 000858  （五粮液）")
        print("  python analyze_stock.py 00700  （腾讯控股-港股）")
        sys.exit(1)
    
    stock_code = sys.argv[1]
    
    # 创建分析器并运行
    analyzer = StockDataFetcher()
    analyzer.analyze(stock_code)


if __name__ == "__main__":
    main()
