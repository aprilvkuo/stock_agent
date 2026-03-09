#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
紧急任务拆解和工单创建
用户任务：工作量统计优化 + 网页导航改造 + 工单系统增强
"""

import os
import sys
from datetime import datetime, timedelta

WORKSPACE = '/Users/egg/.openclaw/workspace'
STOCK_SYSTEM = os.path.join(WORKSPACE, 'memory/stock-system')
sys.path.insert(0, STOCK_SYSTEM)

from improvement_ticket import ticket_system

# 任务列表
TASKS = [
    # === 任务 1: 工作量统计优化 ===
    {
        'id': 'OPTIMIZE-001',
        'title': '分析当前工作量统计逻辑',
        'description': '分析现有统计逻辑，识别无效工作指标',
        'priority': 'high',
        'assignee': 'qa',
        'estimated_hours': 2,
        'deadline_days': 1
    },
    {
        'id': 'OPTIMIZE-002',
        'title': '定义有效工作指标',
        'description': '制定真实有效的工作量评估标准，过滤无效工作',
        'priority': 'high',
        'assignee': 'coordinator',
        'estimated_hours': 2,
        'deadline_days': 1
    },
    {
        'id': 'OPTIMIZE-003',
        'title': '实现工作量自动过滤',
        'description': '代码实现无效工作自动识别和过滤',
        'priority': 'high',
        'assignee': 'programmer',
        'estimated_hours': 3,
        'deadline_days': 2
    },
    {
        'id': 'OPTIMIZE-004',
        'title': '添加工作量验证机制',
        'description': '实现工作量真实性验证，防止糊弄',
        'priority': 'high',
        'assignee': 'qa',
        'estimated_hours': 2,
        'deadline_days': 2
    },
    
    # === 任务 2: 网页导航改造 ===
    {
        'id': 'UI-001',
        'title': '设计导航栏布局',
        'description': '设计顶部导航栏，包含：首页、工单系统、评分看板、反馈报告、TODO 清单',
        'priority': 'critical',
        'assignee': 'programmer',
        'estimated_hours': 2,
        'deadline_days': 1
    },
    {
        'id': 'UI-002',
        'title': '实现导航栏组件',
        'description': '实现响应式导航栏，支持移动端',
        'priority': 'critical',
        'assignee': 'programmer',
        'estimated_hours': 3,
        'deadline_days': 1
    },
    {
        'id': 'UI-003',
        'title': '拆分多看板页面',
        'description': '将当前页面拆分为独立看板：工单系统、评分看板、反馈报告',
        'priority': 'critical',
        'assignee': 'programmer',
        'estimated_hours': 4,
        'deadline_days': 2
    },
    
    # === 任务 3: 工单系统增强（最高优先级）===
    {
        'id': 'TICKET-001',
        'title': '创建独立工单系统页面',
        'description': '创建 tickets.html 独立页面，专门展示工单',
        'priority': 'critical',
        'assignee': 'programmer',
        'estimated_hours': 3,
        'deadline_days': 1
    },
    {
        'id': 'TICKET-002',
        'title': '实现工单筛选功能',
        'description': '支持按 Agent、优先级、状态、截止日期筛选',
        'priority': 'critical',
        'assignee': 'programmer',
        'estimated_hours': 3,
        'deadline_days': 1
    },
    {
        'id': 'TICKET-003',
        'title': '实现工单搜索功能',
        'description': '支持关键词搜索工单',
        'priority': 'high',
        'assignee': 'programmer',
        'estimated_hours': 2,
        'deadline_days': 1
    },
    {
        'id': 'TICKET-004',
        'title': '添加工单状态更新功能',
        'description': '支持在页面更新工单状态（open/in_progress/done）',
        'priority': 'critical',
        'assignee': 'programmer',
        'estimated_hours': 3,
        'deadline_days': 1
    },
    {
        'id': 'TICKET-005',
        'title': '添加工单行动项更新',
        'description': '支持更新行动项状态（pending→done）',
        'priority': 'high',
        'assignee': 'programmer',
        'estimated_hours': 2,
        'deadline_days': 2
    },
    {
        'id': 'TICKET-006',
        'title': '实现工单进度可视化',
        'description': '添加进度条、甘特图等可视化展示',
        'priority': 'medium',
        'assignee': 'programmer',
        'estimated_hours': 3,
        'deadline_days': 2
    },
    {
        'id': 'TICKET-007',
        'title': '测试工单系统功能',
        'description': '全面测试工单系统的筛选、搜索、更新功能',
        'priority': 'high',
        'assignee': 'qa',
        'estimated_hours': 2,
        'deadline_days': 2
    },
]

def create_urgent_tickets():
    """创建紧急任务工单"""
    print("🚀 紧急任务拆解和工单创建")
    print("=" * 70)
    
    created_tickets = []
    
    for task in TASKS:
        rating = {
            'overall_score': 0,
            'scores': {},
            'feedback': f"用户任务：工作量统计优化 + 网页导航改造",
            'suggestions': [task['description']]
        }
        
        ticket = ticket_system.create_ticket(
            provider_id=task['assignee'],
            consumer_id='coordinator',
            service_type='urgent_task',
            rating=rating,
            auto_generate_actions=False
        )
        
        # 更新工单信息
        ticket['type'] = 'urgent_task'
        ticket['task_id'] = task['id']
        ticket['task_title'] = task['title']
        ticket['task_description'] = task['description']
        ticket['priority'] = task['priority']
        ticket['estimated_hours'] = task['estimated_hours']
        
        # 设置截止日期
        deadline = datetime.now() + timedelta(days=task['deadline_days'])
        ticket['improvement_plan']['deadline'] = deadline.strftime('%Y-%m-%d')
        ticket['improvement_plan']['estimated_effort'] = f"{task['estimated_hours']}小时"
        
        # 添加改进行动
        ticket['improvement_plan']['actions'] = [
            {'task': '开始任务', 'status': 'pending', 'assignee': task['assignee'], 'due_date': deadline.strftime('%Y-%m-%d'), 'priority': task['priority']},
            {'task': '实施方案', 'status': 'pending', 'assignee': task['assignee'], 'due_date': deadline.strftime('%Y-%m-%d'), 'priority': task['priority']},
            {'task': '自测', 'status': 'pending', 'assignee': task['assignee'], 'due_date': deadline.strftime('%Y-%m-%d'), 'priority': 'medium'},
            {'task': '提交验收', 'status': 'pending', 'assignee': task['assignee'], 'due_date': deadline.strftime('%Y-%m-%d'), 'priority': 'medium'}
        ]
        
        ticket['progress'].append({
            'date': datetime.now().isoformat(),
            'action': 'urgent_task_assigned',
            'note': f"🔴 紧急任务分配给 {task['assignee']}"
        })
        
        ticket_system._save_ticket(ticket)
        created_tickets.append(ticket)
        
        print(f"✅ {ticket['id']}")
        print(f"   任务：{task['title']}")
        print(f"   分配：{task['assignee']} | 优先级：{task['priority']}")
        print(f"   截止：{deadline.strftime('%Y-%m-%d')} | 预计：{task['estimated_hours']}h")
        print()
    
    print("=" * 70)
    print(f"✅ 共创建 {len(created_tickets)} 个紧急工单")
    
    # 统计
    from collections import Counter
    by_assignee = Counter(t['assignee'] for t in TASKS)
    by_priority = Counter(t['priority'] for t in TASKS)
    
    print("\n📊 任务分配统计:")
    for agent, count in by_assignee.items():
        print(f"   {agent}: {count}个任务")
    
    print("\n🔴 优先级分布:")
    for priority, count in by_priority.items():
        print(f"   {priority}: {count}个任务")
    
    return created_tickets

if __name__ == '__main__':
    tickets = create_urgent_tickets()
    print(f"\n🌐 访问 http://localhost:5001/agent-transparency 查看工单")
