#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务拆分和工单分配系统
将 TODO.md 中的任务拆分并分配给对应 Agent，创建工单实时跟踪（v1.7 新增 Git 自动提交）
"""

import os
import sys
import json
from datetime import datetime, timedelta

# 添加 stock-system 路径
WORKSPACE = '/Users/egg/.openclaw/workspace'
STOCK_SYSTEM = os.path.join(WORKSPACE, 'memory/stock-system')
sys.path.insert(0, STOCK_SYSTEM)

# 导入 Git 版本控制
from git_version_control import GitVersionControl

from improvement_ticket import ticket_system

# Git 控制器实例
_git = GitVersionControl()

# Agent 职责映射
AGENT_RESPONSIBILITIES = {
    'programmer': {
        'name': '程序员 Agent',
        'skills': ['代码开发', 'Bug 修复', '功能实现', '测试'],
        'tasks': []
    },
    'qa': {
        'name': '质检 Agent',
        'skills': ['质量检查', '测试验证', '代码审查'],
        'tasks': []
    },
    'coordinator': {
        'name': '主 Agent',
        'skills': ['任务协调', '汇总决策', '资源分配'],
        'tasks': []
    },
    'fundamental': {
        'name': '基本面 Agent',
        'skills': ['财报分析', '估值判断'],
        'tasks': []
    },
    'technical': {
        'name': '技术面 Agent',
        'skills': ['K 线分析', '技术指标'],
        'tasks': []
    },
    'sentiment': {
        'name': '情绪 Agent',
        'skills': ['情绪分析', '市场热度'],
        'tasks': []
    }
}

# 任务列表（从 TODO.md 提取）
TASKS = [
    {
        'id': 'TASK-001',
        'title': '集成 Agent 状态更新到 auto_agent.py',
        'description': '修改 auto_agent.py 添加状态更新调用，实现分析流程的状态展示',
        'priority': 'high',
        'assignee': 'programmer',
        'estimated_hours': 2,
        'deadline_days': 1
    },
    {
        'id': 'TASK-002',
        'title': '集成 Agent 状态更新到 analyze_core_pool.py',
        'description': '修改 analyze_core_pool.py 添加状态更新调用',
        'priority': 'high',
        'assignee': 'programmer',
        'estimated_hours': 1,
        'deadline_days': 1
    },
    {
        'id': 'TASK-003',
        'title': '创建守护进程脚本',
        'description': '实现自动化调度守护进程，每 30 秒检查请求',
        'priority': 'high',
        'assignee': 'programmer',
        'estimated_hours': 4,
        'deadline_days': 2
    },
    {
        'id': 'TASK-004',
        'title': '实现守护进程单实例锁',
        'description': '使用 PID 文件实现单实例锁，防止多实例运行',
        'priority': 'high',
        'assignee': 'programmer',
        'estimated_hours': 1,
        'deadline_days': 2
    },
    {
        'id': 'TASK-005',
        'title': '实现请求级文件锁',
        'description': '防止并发处理同一请求',
        'priority': 'medium',
        'assignee': 'programmer',
        'estimated_hours': 2,
        'deadline_days': 3
    },
    {
        'id': 'TASK-006',
        'title': '创建质检 Agent 脚本',
        'description': '实现质量监控 Agent，检查核心指标',
        'priority': 'high',
        'assignee': 'programmer',
        'estimated_hours': 4,
        'deadline_days': 2
    },
    {
        'id': 'TASK-007',
        'title': '实现质检核心指标检查',
        'description': '定义并实现核心质量指标检查逻辑',
        'priority': 'medium',
        'assignee': 'qa',
        'estimated_hours': 2,
        'deadline_days': 3
    },
    {
        'id': 'TASK-008',
        'title': '实现异常检测',
        'description': '实现系统异常检测和告警',
        'priority': 'medium',
        'assignee': 'qa',
        'estimated_hours': 2,
        'deadline_days': 3
    },
    {
        'id': 'TASK-009',
        'title': '测试完整评分流程',
        'description': '测试 Agent 互相指导系统的完整评分流程',
        'priority': 'medium',
        'assignee': 'qa',
        'estimated_hours': 2,
        'deadline_days': 2
    },
    {
        'id': 'TASK-010',
        'title': '验证低分触发工单',
        'description': '验证低分（<3 分）自动触发改进工单的功能',
        'priority': 'medium',
        'assignee': 'qa',
        'estimated_hours': 1,
        'deadline_days': 2
    },
    {
        'id': 'TASK-011',
        'title': '验证周度报告生成',
        'description': '验证反馈报告生成器的周度报告功能',
        'priority': 'low',
        'assignee': 'qa',
        'estimated_hours': 1,
        'deadline_days': 3
    },
    {
        'id': 'TASK-012',
        'title': '收集 Agent 反馈',
        'description': '收集各 Agent 对评分系统的反馈意见',
        'priority': 'low',
        'assignee': 'coordinator',
        'estimated_hours': 2,
        'deadline_days': 3
    },
    {
        'id': 'TASK-013',
        'title': '优化评分维度',
        'description': '根据反馈优化评分维度和权重',
        'priority': 'low',
        'assignee': 'coordinator',
        'estimated_hours': 2,
        'deadline_days': 5
    },
    {
        'id': 'TASK-014',
        'title': '添加自动重试机制',
        'description': '守护进程添加失败自动重试机制（最多 3 次）',
        'priority': 'medium',
        'assignee': 'programmer',
        'estimated_hours': 2,
        'deadline_days': 3
    },
    {
        'id': 'TASK-015',
        'title': '添加死信队列',
        'description': '实现失败请求的死信队列隔离机制',
        'priority': 'medium',
        'assignee': 'programmer',
        'estimated_hours': 2,
        'deadline_days': 3
    }
]

def create_task_tickets():
    """为所有任务创建工单"""
    print("📋 开始任务拆分和工单创建...")
    print("=" * 60)
    
    created_tickets = []
    
    for task in TASKS:
        # 创建工单
        rating = {
            'overall_score': 0,  # 新任务，无评分
            'scores': {},
            'feedback': f"任务来源：TODO.md - {task['id']}",
            'suggestions': [task['description']]
        }
        
        ticket = ticket_system.create_ticket(
            provider_id=task['assignee'],
            consumer_id='coordinator',
            service_type='task_implementation',
            rating=rating,
            auto_generate_actions=False
        )
        
        # 更新工单信息
        ticket['type'] = 'task'
        ticket['task_id'] = task['id']
        ticket['task_title'] = task['title']
        ticket['task_description'] = task['description']
        ticket['priority'] = task['priority']
        ticket['estimated_hours'] = task['estimated_hours']
        
        # 设置截止日期
        deadline = datetime.now() + timedelta(days=task['deadline_days'])
        ticket['improvement_plan']['deadline'] = deadline.strftime('%Y-%m-%d')
        ticket['improvement_plan']['estimated_effort'] = f"{task['estimated_hours']}小时"
        
        # 添加改进行动（任务步骤）
        ticket['improvement_plan']['actions'] = [
            {
                'task': f"开始任务：{task['title']}",
                'status': 'pending',
                'assignee': task['assignee'],
                'due_date': deadline.strftime('%Y-%m-%d'),
                'priority': task['priority']
            },
            {
                'task': '实现功能',
                'status': 'pending',
                'assignee': task['assignee'],
                'due_date': deadline.strftime('%Y-%m-%d'),
                'priority': task['priority']
            },
            {
                'task': '自测功能',
                'status': 'pending',
                'assignee': task['assignee'],
                'due_date': deadline.strftime('%Y-%m-%d'),
                'priority': 'medium'
            },
            {
                'task': '提交验收',
                'status': 'pending',
                'assignee': task['assignee'],
                'due_date': deadline.strftime('%Y-%m-%d'),
                'priority': 'medium'
            }
        ]
        
        # 更新进度记录
        ticket['progress'].append({
            'date': datetime.now().isoformat(),
            'action': 'task_assigned',
            'note': f"任务分配给 {AGENT_RESPONSIBILITIES[task['assignee']]['name']}"
        })
        
        # 保存工单
        ticket_system._save_ticket(ticket)
        created_tickets.append(ticket)
        
        # 记录到 Agent 任务列表
        AGENT_RESPONSIBILITIES[task['assignee']]['tasks'].append(task)
        
        print(f"✅ 工单创建：{ticket['id']}")
        print(f"   任务：{task['title']}")
        print(f"   分配给：{AGENT_RESPONSIBILITIES[task['assignee']]['name']}")
        print(f"   优先级：{task['priority']}")
        print(f"   截止：{deadline.strftime('%Y-%m-%d')}")
        print(f"   预计：{task['estimated_hours']}小时")
        print()
    
    print("=" * 60)
    print(f"✅ 共创建 {len(created_tickets)} 个工单")
    
    # 输出 Agent 任务分配统计
    print("\n📊 Agent 任务分配统计:")
    print("-" * 60)
    for agent_id, agent_info in AGENT_RESPONSIBILITIES.items():
        task_count = len(agent_info['tasks'])
        if task_count > 0:
            total_hours = sum(t['estimated_hours'] for t in agent_info['tasks'])
            print(f"{agent_info['name']}: {task_count} 个任务，预计{total_hours}小时")
            for task in agent_info['tasks']:
                print(f"  - {task['id']}: {task['title']} ({task['priority']})")
    
    # 保存任务分配结果
    save_task_assignment(AGENT_RESPONSIBILITIES, created_tickets)
    
    return created_tickets

def save_task_assignment(agents, tickets):
    """保存任务分配结果（v1.7 新增 Git 自动提交）"""
    assignment_file = os.path.join(STOCK_SYSTEM, 'task-assignment.json')
    
    assignment = {
        'created_at': datetime.now().isoformat(),
        'total_tasks': len(tickets),
        'agents': agents,
        'tickets': [
            {
                'id': t['id'],
                'task_id': t.get('task_id'),
                'task_title': t.get('task_title'),
                'provider': t['provider'],
                'priority': t['priority'],
                'deadline': t['improvement_plan']['deadline'],
                'status': t['status']
            }
            for t in tickets
        ]
    }
    
    with open(assignment_file, 'w', encoding='utf-8') as f:
        json.dump(assignment, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 任务分配已保存到：{assignment_file}")
    
    # Git 自动提交（v1.7 新增）
    total_tasks = len(tickets)
    commit_msg = f"任务分配：创建 {total_tasks} 个工单"
    git_record = _git.commit("协调 Agent", commit_msg, files=[assignment_file], auto_push=True)
    if git_record:
        print(f"✅ Git 提交：{git_record['hash'][:8]}")

if __name__ == '__main__':
    print("🚀 任务拆分和工单分配系统")
    print("=" * 60)
    
    # 创建任务工单
    tickets = create_task_tickets()
    
    print("\n✅ 任务拆分和工单分配完成！")
    print("\n🌐 访问 http://localhost:5001/agent-transparency 查看所有工单")
