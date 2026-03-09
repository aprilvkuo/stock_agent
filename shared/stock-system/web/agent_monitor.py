#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent 状态监控模块
"""

import os
import time
from datetime import datetime, timedelta

DATA_DIR = '/Users/egg/.openclaw/workspace/agents/stock-coordinator/data'
STATE_FILE = os.path.join(DATA_DIR, 'agent-state.json')

class AgentMonitor:
    """Agent 状态监控器"""
    
    def __init__(self):
        self.agents = {
            'fundamental': {
                'name': '基本面 Agent',
                'status': 'unknown',
                'last_active': None,
                'tasks_completed': 0,
                'last_error': None
            },
            'technical': {
                'name': '技术面 Agent',
                'status': 'unknown',
                'last_active': None,
                'tasks_completed': 0,
                'last_error': None
            },
            'sentiment': {
                'name': '情绪 Agent',
                'status': 'unknown',
                'last_active': None,
                'tasks_completed': 0,
                'last_error': None
            },
            'coordinator': {
                'name': '主 Agent',
                'status': 'unknown',
                'last_active': None,
                'tasks_completed': 0,
                'last_error': None
            },
            'review': {
                'name': '复盘 Agent',
                'status': 'unknown',
                'last_active': None,
                'tasks_completed': 0,
                'last_error': None
            }
        }
        self.load_state()
    
    def load_state(self):
        """从文件加载状态"""
        if os.path.exists(STATE_FILE):
            try:
                import json
                with open(STATE_FILE, 'r', encoding='utf-8') as f:
                    saved_state = json.load(f)
                    for agent_id, state in saved_state.items():
                        if agent_id in self.agents:
                            self.agents[agent_id].update(state)
            except Exception as e:
                print(f"加载状态失败：{e}")
    
    def save_state(self):
        """保存状态到文件"""
        import json
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.agents, f, ensure_ascii=False, indent=2)
    
    def check_agent_activity(self, agent_id):
        """检查 Agent 活动状态"""
        agent = self.agents.get(agent_id)
        if not agent:
            return 'unknown'
        
        last_active = agent.get('last_active')
        if not last_active:
            return 'idle'
        
        try:
            # 解析时间
            if isinstance(last_active, str):
                last_active = datetime.fromisoformat(last_active)
            
            # 计算时间差
            now = datetime.now()
            diff = now - last_active
            
            # 判断状态
            if diff < timedelta(minutes=2):
                return 'active'  # 2 分钟内有活动
            elif diff < timedelta(hours=1):
                return 'idle'  # 1 小时内无活动
            else:
                return 'offline'  # 超过 1 小时无活动
        except Exception:
            return 'unknown'
    
    def get_status_emoji(self, status):
        """获取状态表情"""
        emoji_map = {
            'active': '🟢',
            'idle': '🟡',
            'offline': '🔴',
            'error': '❌',
            'unknown': '⚪'
        }
        return emoji_map.get(status, '⚪')
    
    def get_all_agents_status(self):
        """获取所有 Agent 状态"""
        result = {}
        for agent_id, agent in self.agents.items():
            status = self.check_agent_activity(agent_id)
            result[agent_id] = {
                'name': agent['name'],
                'status': status,
                'emoji': self.get_status_emoji(status),
                'last_active': agent.get('last_active'),
                'tasks_completed': agent.get('tasks_completed', 0),
                'last_error': agent.get('last_error')
            }
        return result
    
    def update_agent_activity(self, agent_id, task_completed=False):
        """更新 Agent 活动状态"""
        if agent_id in self.agents:
            self.agents[agent_id]['last_active'] = datetime.now().isoformat()
            if task_completed:
                self.agents[agent_id]['tasks_completed'] = \
                    self.agents[agent_id].get('tasks_completed', 0) + 1
            self.save_state()
    
    def set_agent_error(self, agent_id, error_msg):
        """设置 Agent 错误状态"""
        if agent_id in self.agents:
            self.agents[agent_id]['status'] = 'error'
            self.agents[agent_id]['last_error'] = error_msg
            self.agents[agent_id]['last_active'] = datetime.now().isoformat()
            self.save_state()

# 全局监控器实例
monitor = AgentMonitor()

def update_agent_state_from_logs():
    """从日志文件更新 Agent 状态"""
    import re
    
    logs_dir = os.path.join(DATA_DIR, 'logs')
    if not os.path.exists(logs_dir):
        return
    
    # 扫描最近的日志文件
    now = datetime.now()
    for filename in os.listdir(logs_dir):
        if filename.endswith('.md'):
            filepath = os.path.join(logs_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # 提取 Agent 活动
                    agent_patterns = {
                        'fundamental': r'基本面 Agent',
                        'technical': r'技术面 Agent',
                        'sentiment': r'情绪 Agent',
                        'coordinator': r'主 Agent|Coordinator',
                        'review': r'复盘 Agent'
                    }
                    
                    for agent_id, pattern in agent_patterns.items():
                        if re.search(pattern, content):
                            # 提取时间戳
                            time_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', content)
                            if time_match:
                                try:
                                    timestamp = datetime.strptime(time_match.group(1), '%Y-%m-%d %H:%M:%S')
                                    # 只更新最近 24 小时的活动
                                    if now - timestamp < timedelta(hours=24):
                                        monitor.update_agent_activity(agent_id)
                                except Exception:
                                    pass
            except Exception:
                pass
    
    monitor.save_state()

if __name__ == '__main__':
    # 测试
    update_agent_state_from_logs()
    status = monitor.get_all_agents_status()
    
    print("Agent 状态监控")
    print("=" * 50)
    for agent_id, info in status.items():
        print(f"{info['emoji']} {info['name']}: {info['status']}")
        if info.get('last_active'):
            print(f"   最后活动：{info['last_active']}")
        if info.get('tasks_completed'):
            print(f"   完成任务：{info['tasks_completed']}")
