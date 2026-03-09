#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接迁移所有 Agent TODO 到 GitHub Issues

使用方法:
    python3 scripts/migrate_all_agent_todos_to_github.py

依赖:
    pip install PyGithub python-dotenv
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
AGENT_TODOS_DIR = os.path.join(WORKSPACE, "shared/stock-system/agent-todos")

# 检查 Token
if not GITHUB_TOKEN:
    print("=" * 60)
    print("❌ 错误：GITHUB_TOKEN 未设置")
    print("=" * 60)
    print()
    print("请按以下步骤设置：")
    print()
    print("1. 访问 https://github.com/settings/tokens/new")
    print("2. 创建 Token，选择权限：repo, workflow")
    print("3. 复制 Token（格式：ghp_xxxxxxxxxxxx）")
    print()
    print("4. 添加到 .env 文件：")
    print(f"   vim {WORKSPACE}/.env")
    print()
    print("5. 添加以下内容：")
    print("   GITHUB_TOKEN=ghp_你的 token")
    print("   GITHUB_REPO=aprilvkuo/stock_agent")
    print()
    print("6. 重新运行此脚本")
    print("=" * 60)
    sys.exit(1)

# 导入 GitHub API
try:
    from github import Github, Auth
except ImportError:
    print("❌ 错误：缺少 PyGithub 库")
    print("请运行：pip install PyGithub")
    sys.exit(1)

# Agent 名称映射
AGENT_MAPPING = {
    '基本面 Agent': 'fundamental-agent',
    '技术面 Agent': 'technical-agent',
    '情绪 Agent': 'sentiment-agent',
    '程序员 Agent': 'programmer-agent',
    '质检 Agent': 'qa-agent',
    '协调 Agent': 'coordinator-agent',
    'CIO Agent': 'cio-agent',
    '数据获取 Agent': 'data-fetcher-agent',
}

# 优先级映射
PRIORITY_MAPPING = {
    'high': '🔴 P1 - 重要',
    'medium': '🟡 P2 - 普通',
    'low': '🟢 P3 - 低优先级',
}


class IssueMigrator:
    """Issue 迁移器"""
    
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
    
    def load_agent_todos(self) -> List[Dict]:
        """加载所有 Agent 的 TODO"""
        todos = []
        
        if not os.path.exists(AGENT_TODOS_DIR):
            print(f"❌ 目录不存在：{AGENT_TODOS_DIR}")
            return todos
        
        print(f"📂 加载 Agent TODO: {AGENT_TODOS_DIR}")
        print("-" * 60)
        
        for filename in os.listdir(AGENT_TODOS_DIR):
            if filename.endswith('.json'):
                filepath = os.path.join(AGENT_TODOS_DIR, filename)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        agent_data = json.load(f)
                    
                    agent_name = agent_data.get('agent', 'Unknown Agent')
                    
                    for task in agent_data.get('tasks', []):
                        if task.get('status') == 'pending':
                            todos.append({
                                'agent_name': agent_name,
                                'agent_github': AGENT_MAPPING.get(agent_name, 'coordinator-agent'),
                                'task': task.get('task', ''),
                                'priority': task.get('priority', 'medium'),
                                'notes': task.get('notes', ''),
                                'created_at': task.get('created_at', ''),
                                'source_file': filename
                            })
                    
                    print(f"  ✅ {agent_name}: {len(agent_data.get('tasks', []))} 个任务")
                
                except Exception as e:
                    print(f"  ❌ 读取 {filename} 失败：{e}")
        
        print("-" * 60)
        print(f"📊 共找到 {len(todos)} 个待迁移任务\n")
        return todos
    
    def generate_issue_body(self, task: Dict) -> str:
        """生成 Issue 描述"""
        body = f"""## 📋 任务描述

{task['task']}

---

## 🤖 负责方

@{task['agent_github']}

---

## 📊 任务信息

- **优先级**: {PRIORITY_MAPPING.get(task['priority'], '普通')}
- **来源 Agent**: {task['agent_name']}
- **创建时间**: {task['created_at']}
- **来源文件**: `{task['source_file']}`

---

## 📝 备注

{task['notes'] if task['notes'] else '无'}

---

## ✅ 完成标准

- [ ] 任务已完成
- [ ] 已创建相关 PR（如适用）
- [ ] 已通过测试/验证
- [ ] 已在 Issue 中更新状态

---

*此 Issue 由自动化迁移工具创建*
*迁移日期：{datetime.now().strftime('%Y-%m-%d %H:%M')}*
*从本地 agent-todos 系统迁移*
"""
        return body
    
    def create_issue(self, task: Dict) -> bool:
        """创建单个 Issue"""
        title = f"[MIGRATED] [{task['agent_name']}] {task['task'][:60]}"
        body = self.generate_issue_body(task)
        
        # 标签
        labels = [
            'migrated',
            'auto-generated',
            'improvement-ticket',
            task['agent_github']
        ]
        
        try:
            # 创建 Issue
            issue = self.repo.create_issue(
                title=title,
                body=body,
                labels=labels
            )
            
            # 分配给 Agent
            if task['agent_github']:
                try:
                    issue.add_to_assignees(task['agent_github'])
                except Exception as e:
                    print(f"     ⚠️  分配失败：{e}")
            
            # 添加迁移评论
            issue.create_comment(
                f"""🤖 **自动迁移通知**

此 Issue 是从本地 agent-todos 系统自动迁移而来。

**原始位置**: `{task['source_file']}`
**迁移时间**: {datetime.now().isoformat()}
**优先级**: {task['priority']}

请 @{task['agent_github']} 尽快处理此任务。"""
            )
            
            print(f"  ✅ 创建 Issue #{issue.number}: {title[:60]}")
            print(f"     链接：{issue.html_url}")
            print(f"     分配：@{task['agent_github']}")
            print(f"     标签：{', '.join(labels)}")
            
            self.stats['created'] += 1
            return True
        
        except Exception as e:
            print(f"  ❌ 创建失败：{e}")
            self.stats['errors'] += 1
            return False
    
    def migrate(self):
        """执行迁移"""
        print("=" * 60)
        print("🚀 迁移 Agent TODO 到 GitHub Issues")
        print("=" * 60)
        print()
        print(f"📦 仓库：{GITHUB_REPO}")
        print()
        
        # 加载 TODO
        todos = self.load_agent_todos()
        
        if not todos:
            print("\n✅ 没有需要迁移的任务！")
            return
        
        # 创建 Issues
        print("📝 创建 GitHub Issues...")
        print("-" * 60)
        
        for i, task in enumerate(todos, 1):
            print(f"[{i}/{len(todos)}] ", end="")
            self.create_issue(task)
        
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
            print(f"   https://github.com/{GITHUB_REPO}/issues?q=label:migrated")
            print()
            
            # 显示所有创建的 Issue
            print("📋 已创建的 Issues:")
            issues = self.repo.get_issues(state='open', labels=['migrated'])
            for issue in issues[:10]:  # 最多显示 10 个
                print(f"   #{issue.number}: {issue.title[:60]}")


def main():
    """主函数"""
    migrator = IssueMigrator()
    migrator.migrate()


if __name__ == "__main__":
    main()
