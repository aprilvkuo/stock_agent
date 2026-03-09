#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
迁移 Web 工单系统到 GitHub Issues

使用方法:
    python3 scripts/migrate_web_tickets_to_github.py
"""

import os
import sys
import json
from datetime import datetime
from typing import List, Dict
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO", "aprilvkuo/stock_agent")
WORKSPACE = "/Users/egg/.openclaw/workspace"

# 检查 Token
if not GITHUB_TOKEN:
    print("❌ 错误：GITHUB_TOKEN 未设置")
    sys.exit(1)

# 导入 GitHub API
try:
    from github import Github, Auth
except ImportError:
    print("❌ 错误：缺少 PyGithub 库")
    print("请运行：pip3 install --break-system-packages PyGithub")
    sys.exit(1)

# Agent 映射
AGENT_MAPPING = {
    'programmer': 'programmer-agent',
    'fundamental': 'fundamental-agent',
    'technical': 'technical-agent',
    'sentiment': 'sentiment-agent',
    'coordinator': 'coordinator-agent',
    'qa': 'qa-agent',
    'cio': 'cio-agent',
    'data-fetcher': 'data-fetcher-agent',
}

# 工单类型映射
TICKET_TYPE_MAPPING = {
    'task': 'task',
    'urgent_task': 'urgent',
    'improvement': 'improvement-ticket',
}

# 优先级映射
PRIORITY_MAPPING = {
    'critical': '🔴 P0 - 紧急',
    'high': '🔴 P1 - 重要',
    'medium': '🟡 P2 - 普通',
    'low': '🟢 P3 - 低优先级',
}


class WebTicketMigrator:
    """Web 工单迁移器"""
    
    def __init__(self):
        """初始化"""
        self.auth = Auth.Token(GITHUB_TOKEN)
        self.gh = Github(auth=self.auth)
        self.repo = self.gh.get_repo(GITHUB_REPO)
        
        # 统计
        self.stats = {
            'created': 0,
            'errors': 0,
            'skipped': 0
        }
    
    def load_improvement_tickets(self) -> List[Dict]:
        """加载改进工单"""
        tickets_file = os.path.join(WORKSPACE, "memory/stock-system/improvement-tickets.json")
        
        if not os.path.exists(tickets_file):
            print(f"⚠️  文件不存在：{tickets_file}")
            return []
        
        with open(tickets_file, 'r', encoding='utf-8') as f:
            tickets = json.load(f)
        
        print(f"✅ 加载改进工单：{len(tickets)} 个")
        return tickets
    
    def load_ticket_files(self) -> List[Dict]:
        """加载 tickets 目录下的所有工单"""
        tickets_dir = os.path.join(WORKSPACE, "shared/stock-system/tickets")
        tickets = []
        
        if not os.path.exists(tickets_dir):
            print(f"⚠️  目录不存在：{tickets_dir}")
            return tickets
        
        for filename in os.listdir(tickets_dir):
            if filename.endswith('.json') and not filename.startswith('.'):
                filepath = os.path.join(tickets_dir, filename)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        ticket_data = json.load(f)
                    
                    # 合并 .review.json 和 .status.json
                    if 'review' in filename or 'status' in filename:
                        continue
                    
                    tickets.append(ticket_data)
                    print(f"  ✅ 加载 {filename}")
                
                except Exception as e:
                    print(f"  ❌ 读取 {filename} 失败：{e}")
        
        return tickets
    
    def generate_issue_body(self, ticket: Dict) -> str:
        """生成 Issue 描述"""
        ticket_id = ticket.get('id', 'UNKNOWN')
        ticket_type = ticket.get('type', 'task')
        priority = ticket.get('priority', 'medium')
        status = ticket.get('status', 'open')
        provider = ticket.get('provider', 'unknown')
        
        # 任务信息
        task_title = ticket.get('task_title', ticket.get('task_id', '无标题'))
        task_description = ticket.get('task_description', ticket.get('issue', {}).get('description', '无描述'))
        
        # 改进计划
        improvement_plan = ticket.get('improvement_plan', {})
        actions = improvement_plan.get('actions', [])
        estimated_effort = improvement_plan.get('estimated_effort', '未知')
        deadline = improvement_plan.get('deadline', None)
        
        # 触发原因
        trigger = ticket.get('trigger_rating', {})
        feedback = trigger.get('feedback', '')
        suggestions = trigger.get('suggestions', [])
        
        body = f"""## 📋 工单描述

{task_description}

---

## 🎫 工单信息

- **工单 ID**: `{ticket_id}`
- **类型**: {ticket_type}
- **优先级**: {PRIORITY_MAPPING.get(priority, priority)}
- **状态**: {status}
- **提供方**: @{AGENT_MAPPING.get(provider, provider)}

---

## 🤖 负责方

@{AGENT_MAPPING.get(provider, 'coordinator-agent')}

---

## 📝 触发原因

{feedback}

---

## 🎯 改进建议

"""
        
        for i, suggestion in enumerate(suggestions, 1):
            body += f"{i}. {suggestion}\n"
        
        if actions:
            body += "\n---\n\n## ✅ 行动计划\n\n"
            for i, action in enumerate(actions, 1):
                action_task = action.get('task', '未知任务')
                action_status = action.get('status', 'pending')
                action_assignee = action.get('assignee', '未分配')
                action_due = action.get('due_date', '无截止日期')
                
                status_icon = {'pending': '⏳', 'completed': '✅', 'in_progress': '🔧'}.get(action_status, '⏳')
                body += f"{i}. {status_icon} **{action_task}**\n"
                body += f"   - 负责人：{action_assignee}\n"
                body += f"   - 截止：{action_due}\n"
        
        body += f"""
---

## 📊 预估工作量

**预计**: {estimated_effort}

"""
        
        if deadline:
            body += f"**截止日期**: {deadline}\n"
        
        body += f"""
---

## ✅ 完成标准

- [ ] 任务已完成
- [ ] 已创建相关 PR（如适用）
- [ ] 已通过测试/验证
- [ ] 已在 Issue 中更新状态

---

*此 Issue 从 Web 工单系统自动迁移*
*迁移日期：{datetime.now().strftime('%Y-%m-%d %H:%M')}*
*原始工单：`{ticket_id}`*
"""
        
        return body
    
    def create_issue(self, ticket: Dict) -> bool:
        """创建单个 Issue"""
        ticket_id = ticket.get('id', 'UNKNOWN')
        task_title = ticket.get('task_title', ticket.get('task_id', 'Unknown'))
        ticket_type = ticket.get('type', 'task')
        priority = ticket.get('priority', 'medium')
        provider = ticket.get('provider', 'unknown')
        
        # 生成标题
        type_prefix = TICKET_TYPE_MAPPING.get(ticket_type, 'task')
        title = f"[WEB-MIGRATED] [{type_prefix.upper()}] {task_title[:60]}"
        
        # 生成描述
        body = self.generate_issue_body(ticket)
        
        # 标签
        labels = [
            'migrated',
            'web-ticket',
            'auto-generated',
            TICKET_TYPE_MAPPING.get(ticket_type, 'task'),
        ]
        
        # 添加优先级标签
        if priority in ['critical', 'high']:
            labels.append('urgent')
        
        # 添加 Agent 标签
        agent_github = AGENT_MAPPING.get(provider, None)
        if agent_github:
            labels.append(agent_github)
        
        try:
            # 创建 Issue
            issue = self.repo.create_issue(
                title=title,
                body=body,
                labels=labels
            )
            
            # 分配给 Agent
            if agent_github:
                try:
                    issue.add_to_assignees(agent_github)
                except Exception as e:
                    print(f"     ⚠️  分配失败：{e}")
            
            # 添加迁移评论
            issue.create_comment(
                f"""🤖 **自动迁移通知**

此 Issue 是从 Web 工单系统自动迁移而来。

**原始工单 ID**: `{ticket_id}`
**迁移时间**: {datetime.now().isoformat()}
**优先级**: {priority}
**类型**: {ticket_type}

请 @{agent_github or 'coordinator-agent'} 尽快处理此工单。

---

**原始工单进度**:
{chr(10).join([f"- {p.get('date', '')}: {p.get('action', '')} - {p.get('note', '')}" for p in ticket.get('progress', [])[:5]])}
"""
            )
            
            print(f"  ✅ 创建 Issue #{issue.number}: {title[:60]}")
            print(f"     链接：{issue.html_url}")
            print(f"     分配：@{agent_github or 'unassigned'}")
            
            self.stats['created'] += 1
            return True
        
        except Exception as e:
            print(f"  ❌ 创建失败：{e}")
            self.stats['errors'] += 1
            return False
    
    def migrate(self):
        """执行迁移"""
        print("=" * 60)
        print("🚀 迁移 Web 工单到 GitHub Issues")
        print("=" * 60)
        print()
        print(f"📦 仓库：{GITHUB_REPO}")
        print()
        
        # 加载所有工单
        print("📂 加载 Web 工单...")
        print("-" * 60)
        
        improvement_tickets = self.load_improvement_tickets()
        ticket_files = self.load_ticket_files()
        
        all_tickets = improvement_tickets + ticket_files
        
        if not all_tickets:
            print("\n✅ 没有需要迁移的工单！")
            return
        
        print(f"\n📊 共找到 {len(all_tickets)} 个待迁移工单\n")
        
        # 创建 Issues
        print("📝 创建 GitHub Issues...")
        print("-" * 60)
        
        for i, ticket in enumerate(all_tickets, 1):
            print(f"[{i}/{len(all_tickets)}] ", end="")
            self.create_issue(ticket)
        
        # 显示统计
        print()
        print("=" * 60)
        print("📊 迁移统计")
        print("=" * 60)
        print(f"✅ 成功创建：{self.stats['created']} 个 Issue")
        print(f"❌ 失败：{self.stats['errors']} 个")
        print("=" * 60)
        
        if self.stats['created'] > 0:
            print()
            print("🎉 迁移完成！")
            print()
            print("🔗 查看 Issues:")
            print(f"   https://github.com/{GITHUB_REPO}/issues?q=label:web-ticket")
            print()


def main():
    """主函数"""
    migrator = WebTicketMigrator()
    migrator.migrate()


if __name__ == "__main__":
    main()
