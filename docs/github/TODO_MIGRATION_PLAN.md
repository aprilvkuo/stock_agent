# 🔄 TODO List 系统迁移到 GitHub Issues 方案

**版本**: v1.0  
**创建日期**: 2026-03-09  
**状态**: 待执行

---

## 🎯 迁移目标

将现有的本地 TODO list 系统（基于文件和脚本）**完全迁移**到 GitHub Issues 体系，实现：

1. **集中管理** - 所有任务通过 GitHub Issues 跟踪
2. **自动化流程** - Issue 创建 → 分配 → 执行 → 验证 → 关闭
3. **可追溯性** - 完整的任务历史和审计日志
4. **协作友好** - 支持多人/多 Agent 协作

---

## 📊 当前系统分析

### 现有组件

| 组件 | 位置 | 功能 | 迁移方案 |
|------|------|------|---------|
| Agent TODOs | `shared/stock-system/agent-todos/` | 各 Agent 任务列表 | → GitHub Issues (labels) |
| 任务队列 | `shared/stock-system/scripts/auto_task_queue.py` | 自动执行任务 | → GitHub Actions |
| 任务历史 | `shared/stock-system/task_history.json` | 完成任务记录 | → GitHub Issue 历史 |
| Issue 跟踪 | `scripts/issue_tracker.py` | Issue 分配和跟踪 | → 保留并增强 |
| TODO.md | 根目录 | 总任务列表 | → GitHub Issues (归档) |

### 现有问题

1. **数据分散** - 任务信息分散在多个 JSON 文件和 Markdown 中
2. **状态不同步** - 本地状态与 GitHub Issues 不一致
3. **缺乏审计** - 任务执行历史不完整
4. **协作困难** - 不支持多人查看和评论

---

## 🏗️ 新架构设计

### GitHub Issues 工作流

```
┌─────────────┐
│  需求/问题   │
└─────┬───────┘
      │
      ▼
┌─────────────────┐
│ 创建 GitHub Issue │ ← 自动化脚本 / 手动创建
└─────┬───────────┘
      │
      ▼
┌─────────────────┐
│  分配负责 Agent   │ ← 根据 labels / @mention
└─────┬───────────┘
      │
      ▼
┌─────────────────┐
│  Agent 执行任务   │ ← 拉取 Issue → 执行 → 提交 PR
└─────┬───────────┘
      │
      ▼
┌─────────────────┐
│  Code Review    │ ← 其他 Agent / 人工
└─────┬───────────┘
      │
      ▼
┌─────────────────┐
│  Merge & Close  │ ← 自动关闭 Issue
└─────────────────┘
```

### Issue 分类（Labels）

| Label | 颜色 | 用途 | 示例 |
|-------|------|------|------|
| `improvement-ticket` | 🟡 | 改进工单 | Agent 自我改进 |
| `feature` | 🟢 | 新功能 | 添加情绪分析 Agent |
| `bug` | 🔴 | Bug 修复 | 股价获取超时 |
| `task` | 🔵 | 常规任务 | 数据更新、文档整理 |
| `urgent` | 🔴 | 紧急任务 | 需要立即处理 |
| `auto-generated` | ⚪ | 自动生成 | 系统自动创建的任务 |

### Issue 模板

#### 1. 改进工单（Improvement Ticket）

```markdown
---
name: 🚀 改进工单
description: Agent 自我改进或系统优化
title: "[IMPROVE] 简短描述"
labels: [improvement-ticket]
---

## 🎯 改进目标
[描述需要改进的内容]

## 📊 当前问题
[描述当前存在的问题或不足]

## ✅ 预期结果
[改进后应达到的效果]

## 🤖 负责方
@programmer-agent (或其他 Agent)

## 📝 实现建议
[可选：提供实现思路或建议]

## ⏰ 截止时间
[可选：YYYY-MM-DD]
```

#### 2. 任务工单（Task Ticket）

```markdown
---
name: 📋 任务工单
description: 日常任务或定期工作
title: "[TASK] 简短描述"
labels: [task]
---

## 📋 任务描述
[详细描述任务内容]

## 🎯 目标
[任务完成后应达到的目标]

## 🤖 负责方
@<agent-name>

## ✅ 完成标准
- [ ] 标准 1
- [ ] 标准 2
- [ ] 标准 3

## ⏰ 截止时间
[YYYY-MM-DD]

## 📎 相关资源
[相关链接、文档等]
```

---

## 🔄 迁移步骤

### 阶段 1: 准备工作（Day 1）

#### 1.1 创建 Issue 模板

```bash
# 创建 Issue 模板文件
mkdir -p .github/ISSUE_TEMPLATE

# 模板文件
.github/ISSUE_TEMPLATE/
├── improvement-ticket.md      # 改进工单
├── task-ticket.md             # 任务工单
├── bug-report.md              # Bug 报告
└── feature-request.md         # 功能请求
```

#### 1.2 配置 Labels

使用 GitHub API 或手动创建以下 Labels：

```json
[
  {"name": "improvement-ticket", "color": "FBCA04", "description": "改进工单"},
  {"name": "task", "color": "0075CA", "description": "常规任务"},
  {"name": "feature", "color": "0E8A16", "description": "新功能"},
  {"name": "bug", "color": "D73A4A", "description": "Bug 修复"},
  {"name": "urgent", "color": "B60205", "description": "紧急任务"},
  {"name": "auto-generated", "color": "C5DEF5", "description": "自动生成"}
]
```

#### 1.3 增强 Issue 跟踪脚本

更新 `scripts/issue_tracker.py`：
- 添加自动创建 Issue 功能
- 添加任务状态同步功能
- 添加本地缓存机制

---

### 阶段 2: 迁移现有任务（Day 2）

#### 2.1 导出当前 TODO

```python
# scripts/export_todos_to_issues.py
"""
将现有 TODO.md 和 agent-todos 导出为 GitHub Issues
"""

import json
import requests
from datetime import datetime

def export_todo_md():
    """导出 TODO.md 中的任务"""
    with open('TODO.md', 'r') as f:
        content = f.read()
    
    # 解析任务
    tasks = parse_todo_content(content)
    
    # 创建 Issue
    for task in tasks:
        if task['status'] == 'pending':
            create_github_issue(
                title=task['name'],
                body=generate_issue_body(task),
                labels=['task', 'migrated'],
                assignee=task['agent']
            )

def export_agent_todos():
    """导出各 Agent 的 TODO 列表"""
    agent_dir = 'shared/stock-system/agent-todos/'
    
    for filename in os.listdir(agent_dir):
        if filename.endswith('.json'):
            with open(os.path.join(agent_dir, filename), 'r') as f:
                agent_data = json.load(f)
            
            for task in agent_data['tasks']:
                if task['status'] == 'pending':
                    create_github_issue(
                        title=task['task'],
                        body=generate_agent_issue_body(agent_data['agent'], task),
                        labels=['improvement-ticket', 'migrated'],
                        assignee=agent_data['agent']
                    )

if __name__ == "__main__":
    export_todo_md()
    export_agent_todos()
    print("✅ 所有任务已迁移到 GitHub Issues")
```

#### 2.2 批量创建 Issues

```bash
# 执行迁移脚本
cd /Users/egg/.openclaw/workspace
python3 scripts/export_todos_to_issues.py
```

#### 2.3 验证迁移结果

```bash
# 检查创建的 Issues
gh issue list --state open --label migrated
```

---

### 阶段 3: 自动化集成（Day 3-4）

#### 3.1 GitHub Actions 工作流

创建 `.github/workflows/issue-automation.yml`：

```yaml
name: Issue 自动化处理

on:
  issues:
    types: [opened, labeled, assigned]

jobs:
  process-issue:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: 设置 Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: 安装依赖
        run: |
          pip install PyGithub python-dotenv
      
      - name: 处理新 Issue
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          python scripts/issue_tracker.py --auto-assign
      
      - name: 通知负责 Agent
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          python scripts/notify_agent.py --issue-number ${{ github.event.issue.number }}
```

#### 3.2 定时任务（Cron）

```yaml
# .github/workflows/daily-issue-check.yml
name: 每日 Issue 检查

on:
  schedule:
    - cron: '0 9 * * *'  # 每天 9:00 UTC

jobs:
  check-issues:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: 检查逾期任务
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          python scripts/check_overdue_issues.py
      
      - name: 发送日报
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          python scripts/daily_issue_report.py
```

#### 3.3 Agent 集成

更新各 Agent 的启动脚本，使其能够：

1. **拉取任务** - 从 GitHub Issues 获取分配给自己的任务
2. **更新状态** - 在执行过程中更新 Issue 状态
3. **提交结果** - 完成后创建 PR 并关闭 Issue

```python
# agents/base_agent.py
class BaseAgent:
    def fetch_my_issues(self):
        """获取分配给我的未解决 Issues"""
        issues = github_api.get_issues(
            state='open',
            assignee=self.github_username
        )
        return issues
    
    def update_issue_status(self, issue_number, status, comment=None):
        """更新 Issue 状态"""
        if comment:
            github_api.add_comment(issue_number, comment)
        
        if status == 'in_progress':
            github_api.add_label(issue_number, 'in-progress')
        elif status == 'completed':
            github_api.close_issue(issue_number)
```

---

### 阶段 4: 归档旧系统（Day 5）

#### 4.1 备份本地数据

```bash
# 备份现有 TODO 系统
cd /Users/egg/.openclaw/workspace
tar -czf backup_todo_$(date +%Y%m%d).tar.gz \
    TODO.md \
    shared/stock-system/agent-todos/ \
    shared/stock-system/task_history.json \
    shared/stock-system/logs/

# 移动到归档目录
mkdir -p .backup/old-todo-system
mv backup_todo_*.tar.gz .backup/old-todo-system/
```

#### 4.2 停用旧脚本

```bash
# 重命名旧脚本（添加 .deprecated 后缀）
mv shared/stock-system/scripts/auto_task_queue.py \
   shared/stock-system/scripts/auto_task_queue.py.deprecated

mv scripts/issue_tracker.py \
   scripts/issue_tracker.py.deprecated
```

#### 4.3 更新文档

更新 `HEARTBEAT.md` 和相关文档，说明新的任务管理流程。

---

## 📊 迁移对比

| 特性 | 旧系统（本地 TODO） | 新系统（GitHub Issues） |
|------|-------------------|----------------------|
| **可视性** | 仅本地可见 | 全局可见，支持协作 |
| **历史追溯** | 有限 | 完整的 Git 历史 |
| **自动化** | 本地脚本 | GitHub Actions |
| **通知机制** | 无 | GitHub 通知 + @mention |
| **搜索过滤** | 困难 | 强大的搜索和过滤 |
| **集成能力** | 弱 | 与 PR、CI/CD 深度集成 |
| **移动端支持** | 无 | GitHub App |

---

## 🎯 成功标准

- [ ] 所有未完成任务已迁移到 GitHub Issues
- [ ] Issue 模板和 Labels 配置完成
- [ ] 自动化工作流正常运行
- [ ] Agent 能够从 GitHub 拉取任务
- [ ] 本地 TODO 系统已归档
- [ ] 团队熟悉新流程

---

## 📅 时间表

| 阶段 | 内容 | 预计时间 |
|------|------|---------|
| 阶段 1 | 准备工作（模板、Labels、脚本） | Day 1 |
| 阶段 2 | 迁移现有任务 | Day 2 |
| 阶段 3 | 自动化集成 | Day 3-4 |
| 阶段 4 | 归档旧系统 | Day 5 |

---

## 🔗 相关资源

- [GitHub Issues 文档](https://docs.github.com/en/issues)
- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [Issue 模板语法](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-issue-forms)

---

**创建者**: 协调 Agent  
**审核者**: 待审核  
**执行日期**: 2026-03-10
