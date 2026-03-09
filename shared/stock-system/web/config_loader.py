#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置加载器 v1.0
集中管理配置文件
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path

# 配置文件路径
CONFIG_FILE = '/Users/egg/.openclaw/workspace/shared/stock-system/config.json'

class ConfigLoader:
    """配置加载器"""
    
    _instance = None
    _config = None
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config is None:
            self.load_config()
    
    def load_config(self, config_file: str = None) -> Dict[str, Any]:
        """
        加载配置文件
        
        参数:
            config_file: 配置文件路径（默认使用 CONFIG_FILE）
        
        返回:
            配置字典
        """
        if config_file is None:
            config_file = CONFIG_FILE
        
        if not os.path.exists(config_file):
            print(f"警告：配置文件不存在 {config_file}，使用默认配置")
            self._config = self._get_default_config()
            return self._config
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
            print(f"配置加载成功：{config_file}")
        except Exception as e:
            print(f"加载配置失败：{e}，使用默认配置")
            self._config = self._get_default_config()
        
        return self._config
    
    def get(self, key_path: str, default=None) -> Any:
        """
        获取配置值（支持嵌套键）
        
        参数:
            key_path: 键路径，如 "data_sources.tencent.timeout"
            default: 默认值
        
        返回:
            配置值
        """
        keys = key_path.split('.')
        value = self._config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """获取配置节"""
        return self._config.get(section, {})
    
    def reload(self):
        """重新加载配置"""
        return self.load_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            'system': {
                'name': '股票多 Agent 系统',
                'version': 'v1.6',
                'timezone': 'Asia/Shanghai',
                'log_level': 'INFO',
            },
            'data_sources': {
                'tencent': {
                    'enabled': True,
                    'timeout': 5,
                    'retry_times': 3,
                    'cache_ttl': 60,
                }
            },
            'agents': {
                'fundamental': {'enabled': True, 'weight': 0.35},
                'technical': {'enabled': True, 'weight': 0.30},
                'sentiment': {'enabled': True, 'weight': 0.20},
                'capital': {'enabled': True, 'weight': 0.15},
            },
            'cache': {
                'enabled': True,
                'ttl': {
                    'realtime': 60,
                    'daily': 3600,
                    'financial': 86400,
                    'default': 300,
                }
            },
        }


# 全局配置实例
config = ConfigLoader()


# 工具函数

def get_config(key_path: str, default=None) -> Any:
    """获取配置值的便捷函数"""
    return config.get(key_path, default)

def get_agent_weights() -> Dict[str, float]:
    """获取 Agent 权重配置"""
    agents = config.get_section('agents')
    weights = {}
    
    for agent_name, agent_config in agents.items():
        if isinstance(agent_config, dict) and agent_config.get('enabled', True):
            weights[agent_name] = agent_config.get('weight', 0.25)
    
    # 归一化权重
    total = sum(weights.values())
    if total > 0:
        weights = {k: v/total for k, v in weights.items()}
    
    return weights

def get_rating_thresholds() -> Dict[str, int]:
    """获取评级阈值"""
    return config.get('rating.thresholds', {
        'strong_buy': 85,
        'buy': 70,
        'hold': 50,
        'sell': 30,
        'strong_sell': 0,
    })

def get_data_source_config(source_name: str) -> Dict[str, Any]:
    """获取数据源配置"""
    return config.get(f'data_sources.{source_name}', {})


# 测试
if __name__ == "__main__":
    print("测试配置加载器...")
    
    # 测试加载配置
    cfg = ConfigLoader()
    
    print("\n1. 系统配置:")
    print(f"   名称：{cfg.get('system.name')}")
    print(f"   版本：{cfg.get('system.version')}")
    print(f"   时区：{cfg.get('system.timezone')}")
    
    print("\n2. Agent 权重:")
    weights = get_agent_weights()
    for agent, weight in weights.items():
        print(f"   {agent}: {weight:.2%}")
    
    print("\n3. 评级阈值:")
    thresholds = get_rating_thresholds()
    for rating, threshold in thresholds.items():
        print(f"   {rating}: >= {threshold}")
    
    print("\n4. 数据源配置（腾讯）:")
    tencent_cfg = get_data_source_config('tencent')
    for key, value in tencent_cfg.items():
        print(f"   {key}: {value}")
