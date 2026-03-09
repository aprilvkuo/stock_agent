#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工单系统 - 管理复盘 Agent 和程序员 Agent 之间的协作
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional

# 配置
WORKSPACE = '/Users/egg/.openclaw/workspace'
TICKETS_DIR = os.path.join(WORKSPACE, 'shared/stock-system/tickets')

class TicketSystem:
    """工单系统"""
    
    def __init__(self):
        self.tickets_dir = TICKETS_DIR
        self._ensure_tickets_dir()
    
    def _ensure_tickets_dir(self):
        """确保工单目录存在"""
        os.makedirs(self.tickets_dir, exist_ok=True)
    
    def create_ticket(self, title: str, description: str, severity: str, 
                     files: List[str] = None, suggested_fix: str = None) -> Dict:
        """
        创建工单
        
        参数:
            title: 工单标题
            description: 问题描述
            severity: 严重性 (critical/high/medium/low)
            files: 涉及文件列表
            suggested_fix: 建议修复方案
        
        返回:
            工单详情
        """
        ticket_id = f"TICKET-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        ticket = {
            'id': ticket_id,
            'title': title,
            'description': description,
            'severity': severity,
            'status': 'open',
            'assign_to': '程序员 Agent',
            'created_at': datetime.now().isoformat(),
            'files': files or [],
            'suggested_fix': suggested_fix or '',
            'priority': self._calculate_priority(severity)
        }
        
        # 保存工单
        ticket_file = os.path.join(self.tickets_dir, f"{ticket_id}.json")
        with open(ticket_file, 'w', encoding='utf-8') as f:
            json.dump(ticket, f, ensure_ascii=False, indent=2)
        
        print(f"📋 创建工单 #{ticket_id}: {title}")
        print(f"   严重性：{severity}")
        print(f"   优先级：{ticket['priority']}")
        
        return ticket
    
    def _calculate_priority(self, severity: str) -> int:
        """计算优先级数字"""
        priority_map = {
            'critical': 1,
            'high': 2,
            'medium': 3,
            'low': 4
        }
        return priority_map.get(severity, 3)
    
    def get_pending_tickets(self) -> List[Dict]:
        """获取待处理工单"""
        tickets = []
        
        if not os.path.exists(self.tickets_dir):
            return tickets
        
        for filename in os.listdir(self.tickets_dir):
            if filename.endswith('.json') and 'TICKET-' in filename:
                filepath = os.path.join(self.tickets_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        ticket = json.load(f)
                        if ticket.get('status') == 'open':
                            tickets.append(ticket)
                except Exception as e:
                    print(f"读取工单失败 {filename}: {e}")
        
        # 按优先级排序
        tickets.sort(key=lambda x: x.get('priority', 3))
        
        return tickets
    
    def update_ticket_status(self, ticket_id: str, status: str, 
                            result: Dict = None):
        """更新工单状态"""
        ticket_file = os.path.join(self.tickets_dir, f"{ticket_id}.json")
        
        if not os.path.exists(ticket_file):
            print(f"❌ 工单不存在：{ticket_id}")
            return False
        
        with open(ticket_file, 'r', encoding='utf-8') as f:
            ticket = json.load(f)
        
        ticket['status'] = status
        ticket['updated_at'] = datetime.now().isoformat()
        
        if result:
            ticket['result'] = result
        
        with open(ticket_file, 'w', encoding='utf-8') as f:
            json.dump(ticket, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 更新工单 #{ticket_id} 状态：{status}")
        return True
    
    def get_ticket_stats(self) -> Dict:
        """获取工单统计"""
        stats = {
            'total': 0,
            'open': 0,
            'in_progress': 0,
            'completed': 0,
            'failed': 0
        }
        
        if not os.path.exists(self.tickets_dir):
            return stats
        
        for filename in os.listdir(self.tickets_dir):
            if filename.endswith('.json') and 'TICKET-' in filename:
                stats['total'] += 1
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        ticket = json.load(f)
                        status = ticket.get('status', 'unknown')
                        if status in stats:
                            stats[status] += 1
                except:
                    pass
        
        return stats


# 测试
if __name__ == "__main__":
    print("测试工单系统...")
    
    system = TicketSystem()
    
    # 创建测试工单
    ticket = system.create_ticket(
        title="修复网站状态显示不准确",
        description="主 Agent 实际运行中，但网站显示 offline",
        severity="medium",
        files=["agents.html"],
        suggested_fix="修改状态检测逻辑"
    )
    
    # 获取待处理工单
    pending = system.get_pending_tickets()
    print(f"\n待处理工单：{len(pending)} 个")
    
    # 获取统计
    stats = system.get_ticket_stats()
    print(f"\n工单统计:")
    print(f"  总计：{stats['total']}")
    print(f"  待处理：{stats['open']}")
    print(f"  进行中：{stats['in_progress']}")
    print(f"  已完成：{stats['completed']}")
