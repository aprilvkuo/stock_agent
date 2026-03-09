#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地迁移所有 Agent TODO 到 GitHub Issues 格式
生成 Issue 数据文件，稍后可批量创建到 GitHub

使用方法:
    python3 scripts/migrate_all_agent_todos.py
"""

import os
import sys
import json
from datetime import datetime
from typing import List, Dict

WORKSPACE = "/Users/egg/.openclaw/workspace"
AGENT_TODOS_DIR = os.path.join(WORKSPACE, "shared/stock-system/agent-todos")
OUTPUT_DIR = os.path.join(WORKSPACE, ".github/ISSUE_TEMPLATE/migrated-issues")

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
    'high': 'P1',
    'medium': 'P2',
    'low': 'P3',
}


def load_agent_todos() -> List[Dict]:
    """加载所有 Agent 的 TODO 列表"""
    todos = []
    
    if not os.path.exists(AGENT_TODOS_DIR):
        print(f"❌ 目录不存在：{AGENT_TODOS_DIR}")
        return todos
    
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
                
                print(f"  ✅ 加载 {agent_name}: {len(agent_data.get('tasks', []))} 个任务")
            
            except Exception as e:
                print(f"  ❌ 读取 {filename} 失败：{e}")
    
    return todos


def generate_issue_body(task: Dict) -> str:
    """生成 Issue 描述"""
    priority_cn = {
        'high': '🔴 P1 - 重要',
        'medium': '🟡 P2 - 普通',
        'low': '🟢 P3 - 低优先级'
    }
    
    body = f"""## 📋 任务描述

{task['task']}

---

## 🤖 负责方

@{task['agent_github']}

---

## 📊 任务信息

- **优先级**: {priority_cn.get(task['priority'], '普通')}
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


def generate_issue_json(task: Dict, issue_number: int = None) -> Dict:
    """生成 Issue JSON 数据"""
    return {
        "title": f"[MIGRATED] [{task['agent_name']}] {task['task'][:60]}",
        "body": generate_issue_body(task),
        "labels": [
            "migrated",
            "auto-generated",
            "improvement-ticket",
            task['agent_github']
        ],
        "assignee": task['agent_github'],
        "priority": task['priority'],
        "source": {
            "file": task['source_file'],
            "agent": task['agent_name'],
            "migrated_at": datetime.now().isoformat()
        }
    }


def save_issue_json(issue_data: Dict, output_path: str):
    """保存 Issue JSON 文件"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(issue_data, f, ensure_ascii=False, indent=2)


def generate_markdown_summary(issues: List[Dict], output_path: str):
    """生成迁移摘要 Markdown"""
    content = f"""# 📊 Agent TODO 迁移摘要

**迁移日期**: {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**来源**: `shared/stock-system/agent-todos/`  
**目标**: GitHub Issues

---

## 📋 迁移统计

| 指标 | 数量 |
|------|------|
| 总任务数 | {len(issues)} |
| 涉及 Agent | {len(set(i['assignee'] for i in issues))} |
| 高优先级 | {len([i for i in issues if i['priority'] == 'high'])} |
| 中优先级 | {len([i for i in issues if i['priority'] == 'medium'])} |
| 低优先级 | {len([i for i in issues if i['priority'] == 'low'])} |

---

## 🤖 各 Agent 任务分布

"""
    
    # 按 Agent 分组
    agent_groups = {}
    for issue in issues:
        agent = issue['assignee']
        if agent not in agent_groups:
            agent_groups[agent] = []
        agent_groups[agent].append(issue)
    
    for agent, agent_issues in agent_groups.items():
        content += f"### @{agent}\n\n"
        for i, issue in enumerate(agent_issues, 1):
            priority_icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(issue['priority'], '⚪')
            content += f"{i}. {priority_icon} {issue['title'].replace('[MIGRATED] ', '')}\n"
        content += "\n"
    
    content += """
---

## 📁 生成的 Issue 文件

所有 Issue 数据文件已保存到：`.github/ISSUE_TEMPLATE/migrated-issues/`

文件格式：`issue-XXX.json`

---

## 🚀 下一步

### 方法 1: 使用 GitHub CLI 批量创建

```bash
cd /Users/egg/.openclaw/workspace/.github/ISSUE_TEMPLATE/migrated-issues

for file in issue-*.json; do
    title=$(jq -r '.title' "$file")
    body=$(jq -r '.body' "$file")
    labels=$(jq -r '.labels | join(",")' "$file")
    assignee=$(jq -r '.assignee' "$file")
    
    gh issue create \
        --title "$title" \
        --body "$body" \
        --label "$labels" \
        --assignee "$assignee"
done
```

### 方法 2: 手动创建

访问 https://github.com/aprilvkuo/stock_agent/issues/new/choose

选择对应模板，复制粘贴 Issue 内容。

---

## ✅ 迁移完成标准

- [ ] 所有 Issue 已创建到 GitHub
- [ ] 所有 Issue 已分配给对应 Agent
- [ ] 所有 Issue 已添加正确标签
- [ ] 本地 agent-todos 已归档

---

*生成日期：{datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)


def main():
    """主函数"""
    print("=" * 60)
    print("🚀 Agent TODO 迁移到 GitHub Issues")
    print("=" * 60)
    print()
    
    # 创建输出目录
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 加载所有 Agent TODO
    print("📋 步骤 1: 加载 Agent TODO...")
    todos = load_agent_todos()
    
    if not todos:
        print("\n❌ 没有找到待迁移的任务")
        return
    
    print(f"\n📊 共找到 {len(todos)} 个待迁移任务\n")
    
    # 生成 Issue JSON
    print("📝 步骤 2: 生成 Issue 数据...")
    print("-" * 60)
    
    issues = []
    for i, task in enumerate(todos, 1):
        issue_data = generate_issue_json(task, i)
        
        # 保存 Issue JSON
        filename = f"issue-{i:03d}.json"
        filepath = os.path.join(OUTPUT_DIR, filename)
        save_issue_json(issue_data, filepath)
        
        print(f"  ✅ [{i}/{len(todos)}] {task['agent_name']}: {task['task'][:40]}")
        issues.append(issue_data)
    
    # 生成迁移摘要
    print("\n📝 步骤 3: 生成迁移摘要...")
    summary_path = os.path.join(OUTPUT_DIR, "MIGRATION_SUMMARY.md")
    generate_markdown_summary(issues, summary_path)
    print(f"  ✅ 摘要已保存到：{summary_path}")
    
    # 显示统计
    print("\n" + "=" * 60)
    print("📊 迁移统计")
    print("=" * 60)
    print(f"✅ 生成 Issue 文件：{len(issues)} 个")
    print(f"📁 输出目录：{OUTPUT_DIR}")
    print(f"📄 迁移摘要：{summary_path}")
    print("=" * 60)
    
    # 显示各 Agent 分布
    print("\n🤖 各 Agent 任务分布:")
    agent_counts = {}
    for issue in issues:
        agent = issue['assignee']
        agent_counts[agent] = agent_counts.get(agent, 0) + 1
    
    for agent, count in sorted(agent_counts.items()):
        print(f"   @{agent}: {count} 个任务")
    
    print("\n" + "=" * 60)
    print("✅ 迁移准备完成！")
    print("=" * 60)
    print("\n📖 下一步:")
    print("   1. 查看迁移摘要：cat .github/ISSUE_TEMPLATE/migrated-issues/MIGRATION_SUMMARY.md")
    print("   2. 设置 GITHUB_TOKEN 环境变量")
    print("   3. 使用 GitHub CLI 批量创建 Issues")
    print("   4. 或手动创建 Issues")
    print()


if __name__ == "__main__":
    main()
