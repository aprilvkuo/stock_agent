#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 GitHub Issues 同步 Agent 状态

使用方法:
    python3 scripts/sync_agent_status_from_github.py
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO", "aprilvkuo/stock_agent")
WORKSPACE = "/Users/egg/.openclaw/workspace"
STATUS_DIR = os.path.join(WORKSPACE, "shared/stock-system/agent-status")

if not GITHUB_TOKEN:
    print("❌ 错误：GITHUB_TOKEN 未设置")
    sys.exit(1)

try:
    from github import Github, Auth
except ImportError:
    print("❌ 错误：缺少 PyGithub 库")
    sys.exit(1)

# Agent 配置
AGENTS = {
    'fundamental': {'name': '基本面 Agent', 'emoji': '📊'},
    'technical': {'name': '技术面 Agent', 'emoji': '📈'},
    'sentiment': {'name': '情绪 Agent', 'emoji': '😊'},
    'coordinator': {'name': '协调 Agent', 'emoji': '🎯'},
    'qa': {'name': '质检 Agent', 'emoji': '🔍'},
    'programmer': {'name': '程序员 Agent', 'emoji': '💻'},
    'cio': {'name': 'CIO Agent', 'emoji': '👔'},
    'data-fetcher': {'name': '数据获取 Agent', 'emoji': '📡'},
}


class AgentStatusSyncer:
    """Agent 状态同步器"""
    
    def __init__(self):
        """初始化"""
        self.auth = Auth.Token(GITHUB_TOKEN)
        self.gh = Github(auth=self.auth)
        self.repo = self.gh.get_repo(GITHUB_REPO)
        
        # 确保目录存在
        os.makedirs(STATUS_DIR, exist_ok=True)
    
    def get_agent_issues(self, agent_id: str) -> List[Dict]:
        """获取 Agent 的 Issues（使用 labels 过滤）"""
        # 使用 label 过滤而不是 assignee（因为 GitHub 用户可能不存在）
        agent_label = f"{agent_id}-agent"
        issues = self.repo.get_issues(state='open', labels=[agent_label])
        
        result = []
        for issue in issues:
            # 跳过 PR
            if issue.pull_request:
                continue
            
            result.append({
                'issue_number': issue.number,
                'title': issue.title,
                'url': issue.html_url,
                'labels': [label.name for label in issue.labels],
                'created_at': issue.created_at.isoformat(),
                'updated_at': issue.updated_at.isoformat(),
            })
        
        return result
    
    def determine_status(self, issues: List[Dict]) -> str:
        """根据 Issues 确定 Agent 状态"""
        if not issues:
            return 'idle'
        
        # 如果有紧急任务，状态为 active
        for issue in issues:
            if 'urgent' in issue['labels']:
                return 'active'
        
        # 如果有任务，状态为 busy
        return 'busy'
    
    def save_agent_status(self, agent_id: str, status_data: Dict):
        """保存 Agent 状态"""
        filepath = os.path.join(STATUS_DIR, f"{agent_id}.json")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, ensure_ascii=False, indent=2)
        
        print(f"  ✅ 保存 {agent_id}: {status_data['status']}")
    
    def sync_all_agents(self):
        """同步所有 Agent 状态"""
        print("=" * 60)
        print("🔄 同步 Agent 状态从 GitHub Issues")
        print("=" * 60)
        print()
        
        for agent_id, agent_info in AGENTS.items():
            print(f"🤖 {agent_info['emoji']} {agent_info['name']}")
            
            # 获取 Issues
            issues = self.get_agent_issues(agent_id)
            
            # 确定状态
            status = self.determine_status(issues)
            
            # 分离 TODO 和 DOING
            todo_issues = []
            doing_issues = []
            
            for issue in issues:
                # 如果有 in-progress 标签，表示正在做
                if 'in-progress' in issue['labels']:
                    doing_issues.append(issue)
                else:
                    todo_issues.append(issue)
            
            # 保存状态
            status_data = {
                'agent_id': agent_id,
                'agent_name': agent_info['name'],
                'agent_emoji': agent_info['emoji'],
                'status': status,
                'status_text': {
                    'active': '🔴 工作中',
                    'busy': '🟡 忙碌中',
                    'idle': '🟢 空闲'
                }.get(status, '⚪ 未知'),
                'todo_count': len(todo_issues),
                'doing_count': len(doing_issues),
                'done_count': 0,  # 已关闭的 Issues 不计入
                'todo_list': [
                    {
                        'id': f"issue-{issue['issue_number']}",
                        'task': issue['title'],
                        'priority': 'high' if 'urgent' in issue['labels'] else 'medium',
                        'status': 'pending',
                        'url': issue['url'],
                        'created_at': issue['created_at']
                    }
                    for issue in todo_issues[:10]  # 最多 10 个
                ],
                'doing_list': [
                    {
                        'id': f"issue-{issue['issue_number']}",
                        'task': issue['title'],
                        'priority': 'high' if 'urgent' in issue['labels'] else 'medium',
                        'status': 'in_progress',
                        'url': issue['url'],
                        'created_at': issue['created_at']
                    }
                    for issue in doing_issues[:10]  # 最多 10 个
                ],
                'last_sync': datetime.now().isoformat(),
                'github_label': f"{agent_id}-agent"
            }
            
            self.save_agent_status(agent_id, status_data)
            print(f"     TODO: {len(todo_issues)} 个，DOING: {len(doing_issues)} 个")
            print()
        
        # 保存汇总数据
        self.save_summary()
        
        print("=" * 60)
        print("✅ 同步完成！")
        print("=" * 60)
        print()
        print(f"📁 状态目录：{STATUS_DIR}")
        print(f"🔗 GitHub: https://github.com/{GITHUB_REPO}/issues")
    
    def save_summary(self):
        """保存汇总数据"""
        summary = {
            'total_agents': len(AGENTS),
            'active_count': 0,
            'busy_count': 0,
            'idle_count': 0,
            'total_todo': 0,
            'total_doing': 0,
            'last_sync': datetime.now().isoformat()
        }
        
        # 读取所有 Agent 状态
        for agent_id in AGENTS.keys():
            filepath = os.path.join(STATUS_DIR, f"{agent_id}.json")
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                status = data.get('status', 'idle')
                if status == 'active':
                    summary['active_count'] += 1
                elif status == 'busy':
                    summary['busy_count'] += 1
                else:
                    summary['idle_count'] += 1
                
                summary['total_todo'] += data.get('todo_count', 0)
                summary['total_doing'] += data.get('doing_count', 0)
        
        # 保存汇总
        summary_path = os.path.join(STATUS_DIR, "summary.json")
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print(f"📊 汇总：{summary['active_count']} 工作中，{summary['busy_count']} 忙碌，{summary['idle_count']} 空闲")
        print(f"📋 总任务：TODO {summary['total_todo']} 个，DOING {summary['total_doing']} 个")


def main():
    """主函数"""
    syncer = AgentStatusSyncer()
    syncer.sync_all_agents()


if __name__ == "__main__":
    main()
