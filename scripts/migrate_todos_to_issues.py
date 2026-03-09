#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将现有 TODO.md 和 agent-todos 导出为 GitHub Issues

使用方法:
    python3 scripts/migrate_todos_to_issues.py [--dry-run]

依赖:
    pip install PyGithub python-dotenv
"""

import os
import sys
import json
import re
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO", "aprilvkuo/stock_agent")
WORKSPACE = "/Users/egg/.openclaw/workspace"

if not GITHUB_TOKEN:
    print("❌ 错误：GITHUB_TOKEN 未设置")
    print("请在 .env 文件中设置 GITHUB_TOKEN")
    sys.exit(1)

# 导入 GitHub API
try:
    from github import Github, Auth
except ImportError:
    print("❌ 错误：缺少 PyGithub 库")
    print("请运行：pip install PyGithub")
    sys.exit(1)


class TodoMigrator:
    """TODO 迁移工具"""
    
    def __init__(self, dry_run: bool = False):
        """
        初始化迁移工具
        
        Args:
            dry_run: 仅显示，不实际创建 Issue
        """
        self.dry_run = dry_run
        self.auth = Auth.Token(GITHUB_TOKEN)
        self.gh = Github(auth=self.auth)
        self.repo = self.gh.get_repo(GITHUB_REPO)
        
        # Agent 名称映射
        self.agent_mapping = {
            '程序员 Agent': 'programmer-agent',
            '基本面 Agent': 'fundamental-agent',
            '技术面 Agent': 'technical-agent',
            '情绪 Agent': 'sentiment-agent',
            '协调 Agent': 'coordinator-agent',
            '质检 Agent': 'qa-agent',
            'CIO Agent': 'cio-agent',
            '数据获取 Agent': 'data-fetcher-agent',
        }
        
        # 统计
        self.stats = {
            'created': 0,
            'skipped': 0,
            'errors': 0
        }
    
    def parse_todo_md(self) -> List[Dict]:
        """
        解析 TODO.md 文件
        
        Returns:
            任务列表
        """
        todo_file = os.path.join(WORKSPACE, "TODO.md")
        
        if not os.path.exists(todo_file):
            print(f"⚠️  警告：{todo_file} 不存在")
            return []
        
        with open(todo_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tasks = []
        current_priority = 'P2'
        current_section = ''
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            # 检测优先级部分
            if '### 🔴 P0' in line:
                current_priority = 'P0'
                current_section = 'P0'
            elif '### 🔴 P1' in line:
                current_priority = 'P1'
                current_section = 'P1'
            elif '### 🟡 P2' in line:
                current_priority = 'P2'
                current_section = 'P2'
            elif '### 🟢 P3' in line:
                current_priority = 'P3'
                current_section = 'P3'
            
            # 解析任务项
            match = re.match(r'^-\s*\[([ x])\]\s*(.+)$', line.strip())
            if match:
                status_char = match.group(1)
                task_name = match.group(2).strip()
                
                # 跳过已完成的
                if status_char == 'x':
                    continue
                
                # 跳过需人工的任务
                if '[需人工]' in task_name:
                    print(f"  ⏭️  跳过（需人工）: {task_name[:50]}")
                    continue
                
                # 提取 Agent 和截止时间
                agent = 'unknown'
                deadline = None
                
                # 查看后续几行寻找 Agent 和截止时间
                for j in range(i + 1, min(i + 8, len(lines))):
                    next_line = lines[j]
                    if '负责' in next_line:
                        agent_match = re.search(r'负责 [:\s]*(\S+(?:\s+Agent)?)', next_line)
                        if agent_match:
                            agent = agent_match.group(1).strip('**')
                    if '截止' in next_line:
                        deadline_match = re.search(r'截止 [:\s]*(.+)$', next_line)
                        if deadline_match:
                            deadline = deadline_match.group(1).strip()
                
                tasks.append({
                    'source': 'TODO.md',
                    'name': task_name,
                    'priority': current_priority,
                    'agent': agent,
                    'deadline': deadline,
                    'section': current_section
                })
        
        print(f"📋 从 TODO.md 解析到 {len(tasks)} 个未完成任务")
        return tasks
    
    def parse_agent_todos(self) -> List[Dict]:
        """
        解析各 Agent 的 TODO 列表
        
        Returns:
            任务列表
        """
        agent_dir = os.path.join(WORKSPACE, "shared/stock-system/agent-todos")
        
        if not os.path.exists(agent_dir):
            print(f"⚠️  警告：{agent_dir} 不存在")
            return []
        
        tasks = []
        
        for filename in os.listdir(agent_dir):
            if filename.endswith('.json') and not filename.startswith('.'):
                filepath = os.path.join(agent_dir, filename)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        agent_data = json.load(f)
                    
                    agent_name = agent_data.get('agent', 'Unknown Agent')
                    
                    for task in agent_data.get('tasks', []):
                        if task.get('status') == 'pending':
                            tasks.append({
                                'source': f'agent-todos/{filename}',
                                'name': task.get('task', ''),
                                'priority': task.get('priority', 'P2'),
                                'agent': agent_name,
                                'deadline': None,
                                'notes': task.get('notes', '')
                            })
                
                except Exception as e:
                    print(f"  ❌ 读取 {filename} 失败：{e}")
                    self.stats['errors'] += 1
        
        print(f"📋 从 agent-todos 解析到 {len(tasks)} 个未完成任务")
        return tasks
    
    def generate_issue_body(self, task: Dict) -> str:
        """
        生成 Issue 描述
        
        Args:
            task: 任务信息
            
        Returns:
            Issue 描述文本
        """
        body = f"""## 📋 任务描述

{task['name']}

---

## 🤖 负责方

@{self.agent_mapping.get(task['agent'], 'coordinator-agent')}

---

## 📊 来源

- **来源文件**: {task['source']}
- **优先级**: {task['priority']}
"""
        
        if task.get('deadline'):
            body += f"- **截止时间**: {task['deadline']}\n"
        
        if task.get('notes'):
            body += f"\n---\n\n## 📝 备注\n\n{task['notes']}\n"
        
        body += f"""
---

## ✅ 完成标准

- [ ] 任务已完成
- [ ] 已创建相关 PR（如适用）
- [ ] 已通过测试/验证

---

*此 Issue 由自动化迁移工具创建*
*迁移日期：{datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
        
        return body
    
    def determine_labels(self, task: Dict) -> List[str]:
        """
        确定 Issue 标签
        
        Args:
            task: 任务信息
            
        Returns:
            标签列表
        """
        labels = ['migrated', 'auto-generated']
        
        # 根据来源添加标签
        if 'agent-todos' in task['source']:
            labels.append('improvement-ticket')
        else:
            labels.append('task')
        
        # 根据优先级添加标签
        if task['priority'] in ['P0', 'P1']:
            labels.append('urgent')
        
        return labels
    
    def create_issue(self, task: Dict) -> Optional[int]:
        """
        创建 GitHub Issue
        
        Args:
            task: 任务信息
            
        Returns:
            Issue 编号或 None
        """
        title = f"[MIGRATED] {task['name'][:80]}"  # 限制标题长度
        body = self.generate_issue_body(task)
        labels = self.determine_labels(task)
        
        if self.dry_run:
            print(f"  📝 [Dry Run] 创建 Issue: {title[:60]}")
            print(f"     标签：{', '.join(labels)}")
            print(f"     负责：@{self.agent_mapping.get(task['agent'], 'unknown')}")
            return None
        
        try:
            issue = self.repo.create_issue(
                title=title,
                body=body,
                labels=labels
            )
            
            # 添加评论说明迁移
            issue.create_comment(
                f"""🤖 **自动迁移通知**
                
此 Issue 是从本地 TODO 系统自动迁移而来。

**原始位置**: {task['source']}
**迁移时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

请负责方尽快处理此任务。"""
            )
            
            print(f"  ✅ 创建 Issue #{issue.number}: {title[:60]}")
            return issue.number
        
        except Exception as e:
            print(f"  ❌ 创建失败：{e}")
            self.stats['errors'] += 1
            return None
    
    def migrate(self):
        """执行迁移"""
        print("=" * 60)
        print("🚀 TODO 系统迁移到 GitHub Issues")
        print("=" * 60)
        
        if self.dry_run:
            print("⚠️  Dry Run 模式 - 仅显示，不实际创建 Issue\n")
        else:
            print()
        
        # 解析所有任务
        print("📋 步骤 1: 解析现有任务...")
        todo_tasks = self.parse_todo_md()
        agent_tasks = self.parse_agent_todos()
        all_tasks = todo_tasks + agent_tasks
        
        if not all_tasks:
            print("\n✅ 没有需要迁移的任务！")
            return
        
        print(f"\n📊 共发现 {len(all_tasks)} 个未完成任务\n")
        
        # 创建 Issues
        print("📝 步骤 2: 创建 GitHub Issues...")
        print("-" * 60)
        
        for i, task in enumerate(all_tasks, 1):
            print(f"[{i}/{len(all_tasks)}] ", end="")
            issue_number = self.create_issue(task)
            
            if issue_number:
                self.stats['created'] += 1
            else:
                self.stats['skipped'] += 1
        
        # 显示统计
        print("\n" + "=" * 60)
        print("📊 迁移统计")
        print("=" * 60)
        print(f"✅ 成功创建：{self.stats['created']} 个 Issue")
        print(f"⏭️  跳过：{self.stats['skipped']} 个任务")
        print(f"❌ 失败：{self.stats['errors']} 个错误")
        print("=" * 60)
        
        if self.dry_run:
            print("\n⚠️  Dry Run 结束 - 未实际创建任何 Issue")
            print("   移除 --dry-run 参数执行实际迁移")
        else:
            print("\n✅ 迁移完成！")
            print(f"\n🔗 查看 Issues:")
            print(f"   https://github.com/{GITHUB_REPO}/issues?q=label:migrated")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="将 TODO.md 和 agent-todos 迁移到 GitHub Issues"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅显示，不实际创建 Issue"
    )
    
    args = parser.parse_args()
    
    migrator = TodoMigrator(dry_run=args.dry_run)
    migrator.migrate()


if __name__ == "__main__":
    main()
