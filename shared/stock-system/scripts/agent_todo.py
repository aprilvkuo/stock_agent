#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent TODO List 管理模块
功能：管理每个 Agent 的任务清单，支持例会纪要生成
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List

# 配置
WORKSPACE = '/Users/egg/.openclaw/workspace'
AGENT_TODO_DIR = os.path.join(WORKSPACE, 'shared/stock-system/agent-todos')
MEETING_DIR = os.path.join(AGENT_TODO_DIR, 'meetings')

class AgentTodoManager:
    """Agent TODO List 管理器"""
    
    def __init__(self):
        self.todo_dir = AGENT_TODO_DIR
        self.meeting_dir = MEETING_DIR
        self._ensure_dirs()
    
    def _ensure_dirs(self):
        """确保目录存在"""
        os.makedirs(self.todo_dir, exist_ok=True)
        os.makedirs(self.meeting_dir, exist_ok=True)
    
    def add_task(self, agent_name: str, task: str, priority: str = 'medium', 
                 status: str = 'pending', notes: str = ''):
        """
        添加任务
        
        参数:
            agent_name: Agent 名称
            task: 任务描述
            priority: 优先级 (high/medium/low)
            status: 状态 (pending/doing/done)
            notes: 备注
        """
        todo_file = os.path.join(self.todo_dir, f'{agent_name.replace(" ", "_")}.json')
        
        # 读取现有 TODO
        if os.path.exists(todo_file):
            with open(todo_file, 'r', encoding='utf-8') as f:
                todo_data = json.load(f)
        else:
            todo_data = {
                'agent': agent_name,
                'created_at': datetime.now().isoformat(),
                'tasks': [],
                'completed': 0,
                'pending': 0
            }
        
        # 添加新任务
        new_task = {
            'id': f'task-{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'task': task,
            'priority': priority,
            'status': status,
            'notes': notes,
            'created_at': datetime.now().isoformat(),
            'completed_at': None
        }
        
        todo_data['tasks'].append(new_task)
        todo_data['pending'] += 1
        
        # 保存
        with open(todo_file, 'w', encoding='utf-8') as f:
            json.dump(todo_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ {agent_name} 添加任务：{task}")
        return new_task['id']
    
    def complete_task(self, agent_name: str, task_id: str):
        """完成任务"""
        todo_file = os.path.join(self.todo_dir, f'{agent_name.replace(" ", "_")}.json')
        
        if not os.path.exists(todo_file):
            print(f"❌ {agent_name} 的 TODO 文件不存在")
            return False
        
        with open(todo_file, 'r', encoding='utf-8') as f:
            todo_data = json.load(f)
        
        # 查找并更新任务
        for task in todo_data['tasks']:
            if task['id'] == task_id:
                task['status'] = 'done'
                task['completed_at'] = datetime.now().isoformat()
                todo_data['completed'] += 1
                todo_data['pending'] -= 1
                print(f"✅ {agent_name} 完成任务：{task['task']}")
                break
        
        # 保存
        with open(todo_file, 'w', encoding='utf-8') as f:
            json.dump(todo_data, f, ensure_ascii=False, indent=2)
        
        return True
    
    def get_agent_todo(self, agent_name: str) -> Dict:
        """获取 Agent 的 TODO list"""
        todo_file = os.path.join(self.todo_dir, f'{agent_name.replace(" ", "_")}.json')
        
        if not os.path.exists(todo_file):
            return {
                'agent': agent_name,
                'tasks': [],
                'completed': 0,
                'pending': 0
            }
        
        with open(todo_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_all_agents_todo(self) -> Dict[str, Dict]:
        """获取所有 Agent 的 TODO list"""
        agents = ['基本面 Agent', '技术面 Agent', '情绪 Agent', '资金面 Agent', 
                  '主 Agent', '质检 Agent', '程序员 Agent']
        
        all_todos = {}
        for agent in agents:
            all_todos[agent] = self.get_agent_todo(agent)
        
        return all_todos
    
    def hold_meeting(self, meeting_type: str = 'hourly') -> Dict:
        """
        召开 Agent 例会
        
        参数:
            meeting_type: 会议类型 (hourly/daily/weekly)
        
        返回:
            会议纪要
        """
        print(f"\n{'='*60}")
        print(f"📋 召开 Agent {meeting_type} 例会")
        print(f"{'='*60}\n")
        
        # 收集所有 Agent 的状态
        all_todos = self.get_all_agents_todo()
        
        # 生成会议纪要
        meeting_minutes = {
            'meeting_id': f'meeting-{datetime.now().strftime("%Y%m%d%H%M")}',
            'meeting_type': meeting_type,
            'timestamp': datetime.now().isoformat(),
            'attendees': list(all_todos.keys()),
            'agent_status': {},
            'summary': '',
            'action_items': [],
            'next_meeting': ''
        }
        
        # 收集每个 Agent 的状态
        for agent_name, todo_data in all_todos.items():
            tasks = todo_data.get('tasks', [])
            pending_tasks = [t for t in tasks if t['status'] == 'pending']
            doing_tasks = [t for t in tasks if t['status'] == 'doing']
            completed_tasks = [t for t in tasks if t['status'] == 'done'][-3:]  # 最近 3 个完成的任务
            
            meeting_minutes['agent_status'][agent_name] = {
                'pending': len(pending_tasks),
                'doing': len(doing_tasks),
                'completed': len(completed_tasks),
                'recent_completed': completed_tasks,
                'current_tasks': pending_tasks[:3] + doing_tasks  # 显示最多 3 个待办 + 进行中
            }
        
        # 生成总结
        total_pending = sum(s['pending'] for s in meeting_minutes['agent_status'].values())
        total_doing = sum(s['doing'] for s in meeting_minutes['agent_status'].values())
        total_completed = sum(s['completed'] for s in meeting_minutes['agent_status'].values())
        
        meeting_minutes['summary'] = (
            f"本次会议共 {len(all_todos)} 个 Agent 参加。\n"
            f"待办任务：{total_pending} 个\n"
            f"进行中：{total_doing} 个\n"
            f"已完成：{total_completed} 个"
        )
        
        # 生成行动项
        if total_pending > 5:
            meeting_minutes['action_items'].append({
                'priority': 'high',
                'item': '待办任务较多，建议优先处理高优先级任务'
            })
        
        # 计算下次会议时间
        if meeting_type == 'hourly':
            next_meeting = datetime.now() + timedelta(hours=1)
        elif meeting_type == 'daily':
            next_meeting = datetime.now() + timedelta(days=1)
        else:
            next_meeting = datetime.now() + timedelta(weeks=1)
        
        meeting_minutes['next_meeting'] = next_meeting.strftime('%Y-%m-%d %H:%M:%S')
        
        # 保存会议纪要
        meeting_file = os.path.join(
            self.meeting_dir, 
            f"{meeting_minutes['meeting_id']}.json"
        )
        with open(meeting_file, 'w', encoding='utf-8') as f:
            json.dump(meeting_minutes, f, ensure_ascii=False, indent=2)
        
        # 同时保存 Markdown 格式
        md_file = os.path.join(
            self.meeting_dir,
            f"{meeting_minutes['meeting_id']}.md"
        )
        self._save_meeting_markdown(meeting_minutes, md_file)
        
        print(f"✅ 会议纪要已生成：{meeting_file}")
        print(f"📝 Markdown 版本：{md_file}")
        print(f"\n📊 会议总结:")
        print(f"   参会 Agent: {len(all_todos)} 个")
        print(f"   待办任务：{total_pending} 个")
        print(f"   进行中：{total_doing} 个")
        print(f"   已完成：{total_completed} 个")
        print(f"   下次会议：{meeting_minutes['next_meeting']}")
        
        return meeting_minutes
    
    def _save_meeting_markdown(self, meeting: Dict, filepath: str):
        """保存会议纪要为 Markdown 格式"""
        md = f"""# Agent {meeting['meeting_type']} 例会纪要

**会议 ID**: {meeting['meeting_id']}  
**时间**: {meeting['timestamp']}  
**参会 Agent**: {', '.join(meeting['attendees'])}

---

## 📊 会议总结

{meeting['summary']}

---

## 🤖 各 Agent 状态

"""
        for agent_name, status in meeting['agent_status'].items():
            md += f"### {agent_name}\n\n"
            md += f"- 待办：{status['pending']} 个\n"
            md += f"- 进行中：{status['doing']} 个\n"
            md += f"- 已完成：{status['completed']} 个\n\n"
            
            if status['current_tasks']:
                md += "**当前任务**:\n"
                for task in status['current_tasks']:
                    priority_icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(task['priority'], '⚪')
                    md += f"- {priority_icon} {task['task']}\n"
                md += "\n"
            
            if status['recent_completed']:
                md += "**最近完成**:\n"
                for task in status['recent_completed']:
                    md += f"- ✅ {task['task']}\n"
                md += "\n"
        
        if meeting['action_items']:
            md += "## 🎯 行动项\n\n"
            for item in meeting['action_items']:
                priority_icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(item.get('priority', 'medium'), '⚪')
                md += f"- {priority_icon} {item['item']}\n"
        
        md += f"\n---\n\n**下次会议**: {meeting['next_meeting']}\n"
        md += f"\n*会议纪要由系统自动生成*\n"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md)
    
    def get_latest_meeting(self) -> Dict:
        """获取最新的会议纪要"""
        if not os.path.exists(self.meeting_dir):
            return {}
        
        meeting_files = sorted([
            f for f in os.listdir(self.meeting_dir) 
            if f.endswith('.json')
        ], reverse=True)
        
        if not meeting_files:
            return {}
        
        latest_file = os.path.join(self.meeting_dir, meeting_files[0])
        with open(latest_file, 'r', encoding='utf-8') as f:
            return json.load(f)


# 全局实例
todo_manager = AgentTodoManager()


# 便捷函数
def add_agent_task(agent_name: str, task: str, priority: str = 'medium'):
    """添加 Agent 任务"""
    return todo_manager.add_task(agent_name, task, priority)

def complete_agent_task(agent_name: str, task_id: str):
    """完成 Agent 任务"""
    return todo_manager.complete_task(agent_name, task_id)

def get_agent_todo(agent_name: str) -> Dict:
    """获取 Agent TODO list"""
    return todo_manager.get_agent_todo(agent_name)

def get_all_todos() -> Dict:
    """获取所有 Agent TODO"""
    return todo_manager.get_all_agents_todo()

def hold_agent_meeting(meeting_type: str = 'hourly') -> Dict:
    """召开 Agent 例会"""
    return todo_manager.hold_meeting(meeting_type)

def get_latest_meeting() -> Dict:
    """获取最新会议纪要"""
    return todo_manager.get_latest_meeting()


# 测试
if __name__ == "__main__":
    print("测试 Agent TODO List 系统...")
    
    # 添加测试任务
    add_agent_task('基本面 Agent', '分析 600519 贵州茅台财报', 'high')
    add_agent_task('技术面 Agent', '分析 00700 腾讯控股 K 线', 'medium')
    add_agent_task('情绪 Agent', '监控市场舆情', 'low')
    add_agent_task('质检 Agent', '检查系统健康', 'high')
    add_agent_task('程序员 Agent', '修复 Bug', 'medium')
    
    # 获取所有 TODO
    all_todos = get_all_todos()
    print(f"\n📋 所有 Agent TODO:")
    for agent, data in all_todos.items():
        print(f"\n{agent}:")
        print(f"  待办：{data['pending']} 个")
        print(f"  已完成：{data['completed']} 个")
    
    # 召开例会
    print("\n" + "="*60)
    meeting = hold_agent_meeting('hourly')
    
    print(f"\n✅ 测试完成！")
