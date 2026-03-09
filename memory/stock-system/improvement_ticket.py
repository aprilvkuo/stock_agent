#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent 互相指导系统 - 改进工单模块
低分自动触发改进工单，追踪改进进度（v2.0 新增 GitHub Issues + PR 流程）
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# 导入 Git 版本控制
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))
from git_version_control import GitVersionControl

# 导入 GitHub Issue 管理器
try:
    from github_issue_manager import issue_manager
    GITHUB_ENABLED = True
except Exception as e:
    print(f"⚠️  GitHub Issue 模块加载失败：{e}，将使用本地工单模式")
    GITHUB_ENABLED = False

# 配置
WORKSPACE = '/Users/egg/.openclaw/workspace'
STOCK_SYSTEM = os.path.join(WORKSPACE, 'memory/stock-system')
TICKETS_DIR = os.path.join(STOCK_SYSTEM, 'improvement-tickets')
TICKETS_FILE = os.path.join(STOCK_SYSTEM, 'improvement-tickets.json')

# 确保目录存在
os.makedirs(TICKETS_DIR, exist_ok=True)

# Git 控制器实例
_git = GitVersionControl()

class ImprovementTicket:
    """改进工单系统"""
    
    def __init__(self):
        self.ticket_template = {
            'id': '',
            'type': 'improvement',
            'priority': 'medium',  # low/medium/high/critical
            'status': 'open',  # open/in_progress/done/closed
            'created_at': '',
            'updated_at': '',
            'closed_at': None,
            
            # 问题描述
            'provider': '',  # 乙方 Agent
            'consumer': '',  # 甲方 Agent
            'service_type': '',
            'trigger_rating': None,  # 触发工单的评分
            
            # 问题详情
            'issue': {
                'description': '',
                'scores': {},
                'feedback': '',
                'impact': ''
            },
            
            # 改进计划
            'improvement_plan': {
                'actions': [],  # [{task, status, assignee, due_date}]
                'estimated_effort': '',
                'deadline': '',
                'actual_completion': None
            },
            
            # 进度追踪
            'progress': [],  # [{date, action, note}]
            
            # 验收
            'verification': {
                'verified': False,
                'verified_by': '',
                'verified_at': None,
                'new_rating': None
            }
        }
    
    def create_ticket(
        self,
        provider_id: str,
        consumer_id: str,
        service_type: str,
        rating: Dict,
        auto_generate_actions: bool = True
    ) -> Dict:
        """
        创建改进工单
        
        Args:
            provider_id: 服务提供者（乙方）
            consumer_id: 服务使用者（甲方）
            service_type: 服务类型
            rating: 评分记录
            auto_generate_actions: 是否自动生成改进行动
            
        Returns:
            工单字典
        """
        ticket = self.ticket_template.copy()
        
        # 生成工单 ID
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        ticket['id'] = f"IMPROVE-{timestamp}"
        
        # 基本信息
        ticket['provider'] = provider_id
        ticket['consumer'] = consumer_id
        ticket['service_type'] = service_type
        ticket['trigger_rating'] = rating
        ticket['created_at'] = datetime.now().isoformat()
        ticket['updated_at'] = ticket['created_at']
        
        # 计算优先级
        overall_score = rating.get('overall_score', 3)
        if overall_score < 2.0:
            ticket['priority'] = 'critical'
        elif overall_score < 2.5:
            ticket['priority'] = 'high'
        elif overall_score < 3.0:
            ticket['priority'] = 'medium'
        else:
            ticket['priority'] = 'low'
        
        # 问题描述
        ticket['issue'] = {
            'description': rating.get('feedback', ''),
            'scores': rating.get('scores', {}),
            'feedback': rating.get('feedback', ''),
            'impact': self._assess_impact(rating)
        }
        
        # 自动生成改进行动
        if auto_generate_actions:
            ticket['improvement_plan']['actions'] = self._generate_actions(rating)
        
        # 设置截止日期（根据优先级）
        deadline_days = {
            'critical': 1,
            'high': 3,
            'medium': 5,
            'low': 7
        }
        deadline = datetime.now() + timedelta(days=deadline_days.get(ticket['priority'], 5))
        ticket['improvement_plan']['deadline'] = deadline.strftime('%Y-%m-%d')
        
        # 估计工作量
        ticket['improvement_plan']['estimated_effort'] = self._estimate_effort(ticket)
        
        # 初始进度记录
        ticket['progress'].append({
            'date': datetime.now().isoformat(),
            'action': 'ticket_created',
            'note': f'工单创建，优先级 {ticket["priority"]}'
        })
        
        # 保存工单
        self._save_ticket(ticket)
        
        # 记录到日志
        self._log_ticket_creation(ticket)
        
        return ticket
    
    def _assess_impact(self, rating: Dict) -> str:
        """评估问题影响"""
        overall_score = rating.get('overall_score', 3)
        
        if overall_score < 2.0:
            return '严重影响服务质量，需要立即改进'
        elif overall_score < 2.5:
            return '明显影响服务质量，需要优先改进'
        elif overall_score < 3.0:
            return '影响服务质量，建议改进'
        else:
            return '轻微影响，可选改进'
    
    def _generate_actions(self, rating: Dict) -> List[Dict]:
        """根据评分自动生成改进行动"""
        actions = []
        scores = rating.get('scores', {})
        suggestions = rating.get('suggestions', [])
        
        # 根据低分维度生成行动
        dimension_names = {
            'accuracy': '准确性',
            'timeliness': '及时性',
            'completeness': '完整性',
            'usefulness': '有用性',
            'reliability': '可靠性'
        }
        
        for dim, score in scores.items():
            if score < 3:
                actions.append({
                    'task': f'提升{dimension_names.get(dim, dim)}（当前{score}/5）',
                    'status': 'pending',
                    'assignee': '',
                    'due_date': '',
                    'priority': 'high' if score < 2 else 'medium'
                })
        
        # 添加用户建议
        for suggestion in suggestions:
            actions.append({
                'task': suggestion,
                'status': 'pending',
                'assignee': '',
                'due_date': '',
                'priority': 'medium'
            })
        
        return actions
    
    def _estimate_effort(self, ticket: Dict) -> str:
        """估计工作量"""
        action_count = len(ticket['improvement_plan']['actions'])
        
        if action_count <= 2:
            return '1-2 小时'
        elif action_count <= 5:
            return '2-4 小时'
        elif action_count <= 8:
            return '4-8 小时'
        else:
            return '8+ 小时'
    
    def _save_ticket(self, ticket: Dict):
        """保存工单到文件"""
        # 保存到总文件
        all_tickets = self._load_all_tickets()
        
        # 更新或添加工单
        existing_idx = None
        for i, t in enumerate(all_tickets):
            if t['id'] == ticket['id']:
                existing_idx = i
                break
        
        if existing_idx is not None:
            all_tickets[existing_idx] = ticket
        else:
            all_tickets.append(ticket)
        
        # 保存
        with open(TICKETS_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_tickets, f, ensure_ascii=False, indent=2)
        
        # 同时保存单独文件
        ticket_file = os.path.join(TICKETS_DIR, f"{ticket['id']}.json")
        with open(ticket_file, 'w', encoding='utf-8') as f:
            json.dump(ticket, f, ensure_ascii=False, indent=2)
        
        # GitHub Issue 创建（v2.0 新增）
        github_issue_number = None
        if GITHUB_ENABLED:
            try:
                rating = ticket.get('trigger_rating', {})
                improvement_plan = [
                    action['task'] for action in ticket['improvement_plan']['actions']
                ]
                
                issue = issue_manager.create_improvement_issue(
                    provider_id=ticket['provider'],
                    consumer_id=ticket['consumer'],
                    service_type=ticket['service_type'],
                    rating=rating,
                    improvement_plan=improvement_plan
                )
                github_issue_number = issue.get('number')
                ticket['github_issue'] = {
                    'number': github_issue_number,
                    'url': issue.get('html_url'),
                    'created_at': datetime.now().isoformat()
                }
                
                # 更新本地文件
                with open(ticket_file, 'w', encoding='utf-8') as f:
                    json.dump(ticket, f, ensure_ascii=False, indent=2)
                
                print(f"✅ GitHub Issue 已创建：#{github_issue_number}")
                
            except Exception as e:
                print(f"⚠️  GitHub Issue 创建失败：{e}，将使用本地工单模式")
        
        # Git 自动提交（v1.7 新增）
        provider = ticket.get('provider', 'Unknown')
        priority = ticket.get('priority', 'medium')
        score = ticket.get('trigger_rating', {}).get('overall_score', 0)
        commit_msg = f"创建改进工单 {ticket['id']} - {provider} - 优先级：{priority} - 评分：{score}/5.0"
        files_to_commit = [ticket_file]
        if github_issue_number:
            commit_msg += f" (GitHub #{github_issue_number})"
        git_record = _git.commit("系统 Agent", commit_msg, files=files_to_commit, auto_push=True)
        if git_record:
            print(f"✅ Git 提交：{git_record['hash'][:8]}")
    
    def _load_all_tickets(self) -> List[Dict]:
        """加载所有工单"""
        if os.path.exists(TICKETS_FILE):
            try:
                with open(TICKETS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _log_ticket_creation(self, ticket: Dict):
        """记录工单创建日志"""
        log_file = os.path.join(STOCK_SYSTEM, 'improvement-triggers.md')
        
        log_entry = f"""
## {ticket['id']} - {datetime.now().strftime('%Y-%m-%d %H:%M')}

**优先级**: {ticket['priority'].upper()}  
**乙方**: {ticket['provider']}  
**甲方**: {ticket['consumer']}  
**服务类型**: {ticket['service_type']}  
**评分**: {ticket['trigger_rating'].get('overall_score', 0)}/5.0 ⭐

**问题描述**:
{ticket['issue'].get('description', '无')}

**影响评估**:
{ticket['issue'].get('impact', '无')}

**改进计划**:
{chr(10).join('- [ ] ' + action['task'] for action in ticket['improvement_plan']['actions'])}

**截止日期**: {ticket['improvement_plan']['deadline']}  
**预计工作量**: {ticket['improvement_plan']['estimated_effort']}

---
"""
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    
    def update_ticket_status(self, ticket_id: str, status: str, note: str = '') -> Optional[Dict]:
        """
        更新工单状态
        
        Args:
            ticket_id: 工单 ID
            status: 新状态 (open/in_progress/done/closed)
            note: 备注
            
        Returns:
            更新后的工单
        """
        all_tickets = self._load_all_tickets()
        
        for ticket in all_tickets:
            if ticket['id'] == ticket_id:
                old_status = ticket['status']
                ticket['status'] = status
                ticket['updated_at'] = datetime.now().isoformat()
                
                # 添加进度记录
                ticket['progress'].append({
                    'date': datetime.now().isoformat(),
                    'action': f'status_change_{old_status}_to_{status}',
                    'note': note
                })
                
                # 如果完成，记录完成时间
                if status == 'done':
                    ticket['improvement_plan']['actual_completion'] = datetime.now().strftime('%Y-%m-%d')
                elif status == 'closed':
                    ticket['closed_at'] = datetime.now().isoformat()
                
                # 保存
                self._save_ticket(ticket)
                
                return ticket
        
        return None
    
    def add_action(self, ticket_id: str, task: str, assignee: str = '', due_date: str = '') -> Optional[Dict]:
        """添加改进行动"""
        all_tickets = self._load_all_tickets()
        
        for ticket in all_tickets:
            if ticket['id'] == ticket_id:
                ticket['improvement_plan']['actions'].append({
                    'task': task,
                    'status': 'pending',
                    'assignee': assignee,
                    'due_date': due_date,
                    'priority': 'medium'
                })
                ticket['updated_at'] = datetime.now().isoformat()
                
                self._save_ticket(ticket)
                return ticket
        
        return None
    
    def update_action_status(self, ticket_id: str, action_index: int, status: str) -> Optional[Dict]:
        """更新行动状态"""
        all_tickets = self._load_all_tickets()
        
        for ticket in all_tickets:
            if ticket['id'] == ticket_id:
                if 0 <= action_index < len(ticket['improvement_plan']['actions']):
                    ticket['improvement_plan']['actions'][action_index]['status'] = status
                    ticket['updated_at'] = datetime.now().isoformat()
                    
                    # 添加进度记录
                    ticket['progress'].append({
                        'date': datetime.now().isoformat(),
                        'action': f'action_{action_index}_status_{status}',
                        'note': f'行动 "{ticket["improvement_plan"]["actions"][action_index]["task"]}" 状态更新为 {status}'
                    })
                    
                    self._save_ticket(ticket)
                    return ticket
        
        return None
    
    def get_ticket(self, ticket_id: str) -> Optional[Dict]:
        """获取工单"""
        all_tickets = self._load_all_tickets()
        
        for ticket in all_tickets:
            if ticket['id'] == ticket_id:
                return ticket
        
        return None
    
    def get_all_tickets(self, status_filter: str = None, provider_filter: str = None) -> List[Dict]:
        """获取所有工单（可筛选）"""
        all_tickets = self._load_all_tickets()
        
        result = []
        for ticket in all_tickets:
            if status_filter and ticket['status'] != status_filter:
                continue
            if provider_filter and ticket['provider'] != provider_filter:
                continue
            result.append(ticket)
        
        # 按创建时间倒序
        result.sort(key=lambda x: x['created_at'], reverse=True)
        
        return result
    
    def get_statistics(self) -> Dict:
        """获取工单统计"""
        all_tickets = self._load_all_tickets()
        
        stats = {
            'total': len(all_tickets),
            'by_status': {},
            'by_priority': {},
            'by_provider': {},
            'overdue': 0,
            'completion_rate': 0
        }
        
        today = datetime.now()
        
        for ticket in all_tickets:
            # 按状态统计
            status = ticket['status']
            stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
            
            # 按优先级统计
            priority = ticket['priority']
            stats['by_priority'][priority] = stats['by_priority'].get(priority, 0) + 1
            
            # 按提供者统计
            provider = ticket['provider']
            stats['by_provider'][provider] = stats['by_provider'].get(provider, 0) + 1
            
            # 逾期检查
            if ticket['status'] not in ['done', 'closed']:
                deadline = datetime.strptime(ticket['improvement_plan']['deadline'], '%Y-%m-%d')
                if deadline < today:
                    stats['overdue'] += 1
        
        # 计算完成率
        if stats['total'] > 0:
            completed = stats['by_status'].get('done', 0) + stats['by_status'].get('closed', 0)
            stats['completion_rate'] = round(completed / stats['total'] * 100, 2)
        
        return stats


# 全局实例
ticket_system = ImprovementTicket()


# 便捷函数
def create_improvement_ticket(provider_id, consumer_id, service_type, rating, **kwargs):
    """便捷函数：创建改进工单"""
    return ticket_system.create_ticket(provider_id, consumer_id, service_type, rating, **kwargs)

def get_ticket(ticket_id):
    """便捷函数：获取工单"""
    return ticket_system.get_ticket(ticket_id)

def get_all_tickets(**kwargs):
    """便捷函数：获取所有工单"""
    return ticket_system.get_all_tickets(**kwargs)

def get_statistics():
    """便捷函数：获取统计"""
    return ticket_system.get_statistics()

def update_ticket_status(ticket_id, status, note=''):
    """便捷函数：更新工单状态"""
    return ticket_system.update_ticket_status(ticket_id, status, note)


# 测试
if __name__ == '__main__':
    print("🧪 测试改进工单系统...")
    
    # 模拟一个低分评分
    test_rating = {
        'overall_score': 2.2,
        'scores': {
            'accuracy': 2,
            'timeliness': 3,
            'completeness': 1,
            'usefulness': 2,
            'reliability': 3
        },
        'feedback': '数据缺少关键指标，需要手动补充',
        'suggestions': ['添加 ROE 指标', '添加毛利率指标', '添加净利率指标']
    }
    
    # 创建工单
    ticket = create_improvement_ticket(
        provider_id='data-fetcher',
        consumer_id='fundamental',
        service_type='financial_data',
        rating=test_rating
    )
    
    print(f"✅ 工单创建成功：{ticket['id']}")
    print(f"   优先级：{ticket['priority']}")
    print(f"   乙方：{ticket['provider']}")
    print(f"   甲方：{ticket['consumer']}")
    print(f"   评分：{ticket['trigger_rating']['overall_score']}/5.0")
    print(f"   改进行动：{len(ticket['improvement_plan']['actions'])} 项")
    print(f"   截止日期：{ticket['improvement_plan']['deadline']}")
    
    # 获取统计
    stats = get_statistics()
    print(f"\n📊 工单统计:")
    print(f"   总工单数：{stats['total']}")
    print(f"   按状态：{stats['by_status']}")
    print(f"   按优先级：{stats['by_priority']}")
    print(f"   完成率：{stats['completion_rate']}%")
    
    print("\n✅ 测试完成！")
