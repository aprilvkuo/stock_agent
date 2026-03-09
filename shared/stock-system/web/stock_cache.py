#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股价数据缓存模块 v1.0
避免重复请求，提升系统性能
"""

import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, List

# 缓存配置文件
CACHE_DIR = '/Users/egg/.openclaw/workspace/shared/stock-system/data/cache'
CACHE_CONFIG = {
    'realtime': {'ttl': 60},      # 实时数据：60 秒
    'daily': {'ttl': 3600},       # 日线数据：1 小时
    'financial': {'ttl': 86400},  # 财务数据：24 小时
    'default': {'ttl': 300},      # 默认：5 分钟
}

class StockCache:
    """股价数据缓存管理器"""
    
    def __init__(self):
        self.cache_dir = CACHE_DIR
        self._ensure_cache_dir()
    
    def _ensure_cache_dir(self):
        """确保缓存目录存在"""
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def _get_cache_key(self, stock_code: str, data_type: str) -> str:
        """生成缓存键"""
        return f"{stock_code}_{data_type}"
    
    def _get_cache_file(self, cache_key: str) -> str:
        """获取缓存文件路径"""
        safe_key = cache_key.replace('/', '_').replace('\\', '_')
        return os.path.join(self.cache_dir, f"{safe_key}.json")
    
    def get(self, stock_code: str, data_type: str = 'default') -> Optional[Dict]:
        """
        获取缓存数据
        
        参数:
            stock_code: 股票代码
            data_type: 数据类型 (realtime/daily/financial/default)
        
        返回:
            缓存数据（如果未过期），否则返回 None
        """
        cache_key = self._get_cache_key(stock_code, data_type)
        cache_file = self._get_cache_file(cache_key)
        
        if not os.path.exists(cache_file):
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 检查是否过期
            ttl = CACHE_CONFIG.get(data_type, CACHE_CONFIG['default'])['ttl']
            if time.time() - data['timestamp'] > ttl:
                # 过期，删除缓存
                os.remove(cache_file)
                return None
            
            return data
        except Exception as e:
            print(f"读取缓存失败 {cache_key}: {e}")
            return None
    
    def set(self, stock_code: str, data: Dict, data_type: str = 'default'):
        """
        设置缓存数据
        
        参数:
            stock_code: 股票代码
            data: 要缓存的数据
            data_type: 数据类型
        """
        cache_key = self._get_cache_key(stock_code, data_type)
        cache_file = self._get_cache_file(cache_key)
        
        cache_data = {
            'timestamp': time.time(),
            'datetime': datetime.now().isoformat(),
            'data': data,
        }
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"写入缓存失败 {cache_key}: {e}")
    
    def delete(self, stock_code: str, data_type: str = 'default'):
        """删除缓存"""
        cache_key = self._get_cache_key(stock_code, data_type)
        cache_file = self._get_cache_file(cache_key)
        
        if os.path.exists(cache_file):
            os.remove(cache_file)
    
    def clear_all(self):
        """清空所有缓存"""
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.cache_dir, filename)
                try:
                    os.remove(filepath)
                except Exception as e:
                    print(f"删除缓存失败 {filepath}: {e}")
    
    def get_stats(self) -> Dict:
        """获取缓存统计信息"""
        stats = {
            'total_files': 0,
            'total_size': 0,
            'by_type': {},
            'oldest': None,
            'newest': None,
        }
        
        if not os.path.exists(self.cache_dir):
            return stats
        
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.cache_dir, filename)
                try:
                    stat = os.stat(filepath)
                    stats['total_files'] += 1
                    stats['total_size'] += stat.st_size
                    
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        timestamp = data.get('timestamp', 0)
                        
                        if stats['oldest'] is None or timestamp < stats['oldest']:
                            stats['oldest'] = timestamp
                        if stats['newest'] is None or timestamp > stats['newest']:
                            stats['newest'] = timestamp
                except Exception as e:
                    print(f"统计缓存失败 {filepath}: {e}")
        
        # 计算平均 TTL
        if stats['newest'] and stats['oldest']:
            stats['age_range_hours'] = (stats['newest'] - stats['oldest']) / 3600
        else:
            stats['age_range_hours'] = 0
        
        return stats
    
    def cleanup_expired(self) -> int:
        """清理过期缓存，返回清理数量"""
        cleaned = 0
        
        if not os.path.exists(self.cache_dir):
            return cleaned
        
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.cache_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # 检查是否过期
                    timestamp = data.get('timestamp', 0)
                    ttl = CACHE_CONFIG['default']['ttl']
                    
                    if time.time() - timestamp > ttl:
                        os.remove(filepath)
                        cleaned += 1
                except Exception as e:
                    print(f"清理缓存失败 {filepath}: {e}")
        
        return cleaned


class StockDataFetcher:
    """带缓存的股价数据获取器"""
    
    def __init__(self):
        self.cache = StockCache()
        self.api_calls = 0
        self.cache_hits = 0
    
    def get_realtime_data(self, stock_code: str, market_type: str = 'A') -> Optional[Dict]:
        """
        获取实时股价数据（带缓存）
        
        参数:
            stock_code: 股票代码
            market_type: 市场类型 (A/HK/US)
        
        返回:
            股价数据
        """
        # 尝试从缓存获取
        cached = self.cache.get(stock_code, 'realtime')
        if cached:
            self.cache_hits += 1
            return cached['data']
        
        # 缓存未命中，调用 API
        data = self._fetch_from_api(stock_code, market_type)
        if data:
            self.cache.set(stock_code, data, 'realtime')
            self.api_calls += 1
        
        return data
    
    def _fetch_from_api(self, stock_code: str, market_type: str) -> Optional[Dict]:
        """
        从 API 获取真实数据
        
        这里集成腾讯财经 API
        """
        try:
            import urllib.request
            
            if market_type == 'A':
                if stock_code.startswith('6'):
                    symbol = f'sh{stock_code}'
                else:
                    symbol = f'sz{stock_code}'
            elif market_type == 'HK':
                symbol = f'hk{stock_code}'
            else:
                # 美股暂不支持
                return None
            
            url = f'http://qt.gtimg.cn/q={symbol}'
            
            with urllib.request.urlopen(url, timeout=5) as response:
                content = response.read().decode('gbk')
            
            # 解析腾讯 API 响应
            # v=~60, name="贵州茅台", open=1670.00, last=1680.50, ...
            parts = content.split('~')
            
            if len(parts) < 50:
                return None
            
            data = {
                'code': stock_code,
                'name': parts[2].strip('"'),
                'current': float(parts[3]) if parts[3] else 0,
                'open': float(parts[5]) if parts[5] else 0,
                'high': float(parts[33]) if parts[33] else 0,
                'low': float(parts[34]) if parts[34] else 0,
                'close': float(parts[4]) if parts[4] else 0,
                'volume': float(parts[6]) if parts[6] else 0,
                'amount': float(parts[37]) if parts[37] else 0,
                'timestamp': datetime.now().isoformat(),
            }
            
            # 计算涨跌幅
            if data['close'] > 0:
                data['change'] = data['current'] - data['close']
                data['change_percent'] = (data['change'] / data['close']) * 100
            else:
                data['change'] = 0
                data['change_percent'] = 0
            
            return data
            
        except Exception as e:
            print(f"获取股价数据失败 {stock_code}: {e}")
            return None
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        cache_stats = self.cache.get_stats()
        total_requests = self.api_calls + self.cache_hits
        
        return {
            'api_calls': self.api_calls,
            'cache_hits': self.cache_hits,
            'hit_rate': (self.cache_hits / total_requests * 100) if total_requests > 0 else 0,
            'cache': cache_stats,
        }


# 测试
if __name__ == "__main__":
    print("测试股价数据缓存模块...")
    
    fetcher = StockDataFetcher()
    
    # 测试获取实时数据
    print("\n1. 首次获取（API 调用）...")
    data = fetcher.get_realtime_data('600519', 'A')
    if data:
        print(f"   贵州茅台：¥{data['current']} ({data['change_percent']:+.2f}%)")
    
    print("\n2. 再次获取（缓存命中）...")
    data = fetcher.get_realtime_data('600519', 'A')
    if data:
        print(f"   贵州茅台：¥{data['current']} ({data['change_percent']:+.2f}%)")
    
    # 统计
    stats = fetcher.get_stats()
    print(f"\n3. 统计信息:")
    print(f"   API 调用：{stats['api_calls']}")
    print(f"   缓存命中：{stats['cache_hits']}")
    print(f"   命中率：{stats['hit_rate']:.1f}%")
    print(f"   缓存文件：{stats['cache']['total_files']}")
    print(f"   缓存大小：{stats['cache']['total_size']} bytes")
