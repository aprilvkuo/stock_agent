#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
持仓股管理模块 v1.0
支持 A 股、港股、美股的持仓管理
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Optional
import re

# 数据文件路径
HOLDINGS_FILE = '/Users/egg/.openclaw/workspace/shared/stock-system/data/holdings.json'

class HoldingsManager:
    """持仓股管理器"""
    
    def __init__(self):
        self.holdings_file = HOLDINGS_FILE
        self._ensure_data_dir()
        self._load_holdings()
    
    def _ensure_data_dir(self):
        """确保数据目录存在"""
        os.makedirs(os.path.dirname(self.holdings_file), exist_ok=True)
    
    def _load_holdings(self):
        """加载持仓数据"""
        if os.path.exists(self.holdings_file):
            with open(self.holdings_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        else:
            self.data = {
                'holdings': [],
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
            }
    
    def _save_holdings(self):
        """保存持仓数据"""
        self.data['updated_at'] = datetime.now().isoformat()
        with open(self.holdings_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def add_holding(self, stock_code: str, stock_name: str, shares: float, 
                    cost_price: float, market_type: str = 'A', 
                    notes: str = '') -> Dict:
        """
        添加持仓股
        
        参数:
            stock_code: 股票代码
            stock_name: 股票名称
            shares: 股数
            cost_price: 成本价
            market_type: 市场类型 (A=A 股，HK=港股，US=美股)
            notes: 备注
        
        返回:
            添加的持仓信息
        """
        holding = {
            'id': f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{stock_code}",
            'stock_code': stock_code,
            'stock_name': stock_name,
            'shares': shares,
            'cost_price': cost_price,
            'market_type': market_type,
            'notes': notes,
            'created_at': datetime.now().isoformat(),
            'status': 'active',  # active, sold
        }
        
        self.data['holdings'].append(holding)
        self._save_holdings()
        
        return holding
    
    def update_holding(self, holding_id: str, **kwargs) -> Optional[Dict]:
        """
        更新持仓信息
        
        参数:
            holding_id: 持仓 ID
            **kwargs: 要更新的字段
        
        返回:
            更新后的持仓信息，未找到返回 None
        """
        for holding in self.data['holdings']:
            if holding['id'] == holding_id:
                for key, value in kwargs.items():
                    if key in holding and key not in ['id', 'created_at']:
                        holding[key] = value
                
                holding['updated_at'] = datetime.now().isoformat()
                self._save_holdings()
                return holding
        
        return None
    
    def delete_holding(self, holding_id: str) -> bool:
        """
        删除持仓
        
        参数:
            holding_id: 持仓 ID
        
        返回:
            是否删除成功
        """
        for i, holding in enumerate(self.data['holdings']):
            if holding['id'] == holding_id:
                self.data['holdings'].pop(i)
                self._save_holdings()
                return True
        
        return False
    
    def get_holdings(self, status: str = 'active') -> List[Dict]:
        """
        获取持仓列表
        
        参数:
            status: 状态 (active, sold, all)
        
        返回:
            持仓列表
        """
        if status == 'all':
            return self.data['holdings']
        
        return [h for h in self.data['holdings'] if h.get('status') == status]
    
    def get_holding_by_id(self, holding_id: str) -> Optional[Dict]:
        """根据 ID 获取持仓"""
        for holding in self.data['holdings']:
            if holding['id'] == holding_id:
                return holding
        return None
    
    def get_holdings_by_market(self, market_type: str) -> List[Dict]:
        """根据市场类型获取持仓"""
        return [h for h in self.data['holdings'] 
                if h.get('market_type') == market_type and h.get('status') == 'active']
    
    def get_summary(self) -> Dict:
        """
        获取持仓汇总
        
        返回:
            汇总统计信息
        """
        active_holdings = [h for h in self.data['holdings'] if h.get('status') == 'active']
        
        summary = {
            'total_count': len(active_holdings),
            'by_market': {
                'A': len([h for h in active_holdings if h.get('market_type') == 'A']),
                'HK': len([h for h in active_holdings if h.get('market_type') == 'HK']),
                'US': len([h for h in active_holdings if h.get('market_type') == 'US']),
            },
            'total_cost': sum(h['shares'] * h['cost_price'] for h in active_holdings),
        }
        
        return summary
    
    def parse_image_to_holding(self, image_data: str) -> Optional[Dict]:
        """
        从图片解析持仓信息（OCR）
        
        参数:
            image_data: Base64 编码的图片数据
        
        返回:
            解析出的持仓信息（需要用户确认）
        """
        # TODO: 集成 OCR 服务（如百度 OCR、腾讯 OCR）
        # 当前返回示例结构
        return {
            'stock_code': '待识别',
            'stock_name': '待识别',
            'shares': 0,
            'cost_price': 0,
            'note': 'OCR 功能待集成',
        }


# 工具函数

def validate_stock_code(stock_code: str, market_type: str) -> bool:
    """
    验证股票代码格式
    
    A 股：6 位数字（60xxxx, 00xxxx, 30xxxx）
    港股：5 位数字（00xxx）
    美股：字母组合（AAPL, TSLA）
    """
    if market_type == 'A':
        return bool(re.match(r'^\d{6}$', stock_code))
    elif market_type == 'HK':
        return bool(re.match(r'^\d{5}$', stock_code))
    elif market_type == 'US':
        return bool(re.match(r'^[A-Z]{1,5}$', stock_code.upper()))
    return False


def parse_stock_code_format(stock_code: str) -> Optional[str]:
    """
    根据股票代码格式自动判断市场类型
    
    返回:
        市场类型 (A, HK, US) 或 None
    """
    if re.match(r'^\d{6}$', stock_code):
        return 'A'
    elif re.match(r'^\d{5}$', stock_code):
        return 'HK'
    elif re.match(r'^[A-Za-z]{1,5}$', stock_code):
        return 'US'
    return None


# 测试
if __name__ == "__main__":
    manager = HoldingsManager()
    
    # 测试添加持仓
    print("测试添加持仓...")
    holding = manager.add_holding(
        stock_code='600519',
        stock_name='贵州茅台',
        shares=100,
        cost_price=1500.0,
        market_type='A',
        notes='长期持有'
    )
    print(f"添加成功：{holding}")
    
    # 测试获取持仓列表
    print("\n持仓列表:")
    holdings = manager.get_holdings()
    for h in holdings:
        print(f"  - {h['stock_name']} ({h['stock_code']}): {h['shares']}股 @ ¥{h['cost_price']}")
    
    # 测试汇总
    print("\n持仓汇总:")
    summary = manager.get_summary()
    print(f"  总持仓数：{summary['total_count']}")
    print(f"  A 股：{summary['by_market']['A']}")
    print(f"  港股：{summary['by_market']['HK']}")
    print(f"  美股：{summary['by_market']['US']}")
