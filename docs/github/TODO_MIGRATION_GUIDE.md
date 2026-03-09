# 🔄 TODO 迁移到 GitHub Issues - 快速指南

**版本**: v1.0  
**创建日期**: 2026-03-09  
**执行日期**: 2026-03-10

---

## 🎯 迁移目标

将本地 TODO list 系统**完全迁移**到 GitHub Issues，实现任务管理的集中化、自动化和可追溯。

---

## 📋 迁移前准备

### 1. 检查环境变量

确保 `.env` 文件中已设置：

```bash
GITHUB_TOKEN=ghp_xxxxxxxxxxxx
GITHUB_REPO=aprilvkuo/stock_agent
```

### 2. 安装依赖

```bash
cd /Users/egg/.openclaw/workspace
pip install PyGithub python-dotenv
```

### 3. 验证 Token 权限

```bash
python3 scripts/verify_bot_token.py
```

确保 Token 有以下权限：
- ✅ `repo` (完整仓库权限)
- ✅ `workflow` (管理 GitHub Actions)
- ✅ `write:discussion` (创建评论)

---

## 🚀 迁移步骤

### 步骤 1: 创建 Issue 模板（已完成 ✅）

Issue 模板已创建：
- `.github/ISSUE_TEMPLATE/improvement-ticket.yml` - 改进工单
- `.github/ISSUE_TEMPLATE/task-ticket.yml` - 任务工单

### 步骤 2: 配置 Labels

运行以下命令创建 Labels：

```bash
python3 scripts/create_labels.py
```

或者手动在 GitHub 创建：

| Label | 颜色 | 描述 |
|-------|------|------|
| `improvement-ticket` | #FBCA04 | 改进工单 |
| `task` | #0075CA | 常规任务 |
| `migrated` | #C5DEF5 | 从旧系统迁移 |
| `auto-generated` | #C5DEF5 | 自动生成 |
| `urgent` | #B60205 | 紧急任务 |

### 步骤 3: Dry Run（推荐）

先运行 Dry Run 查看将要创建哪些 Issue：

```bash
cd /Users/egg/.openclaw/workspace
python3 scripts/migrate_todos_to_issues.py --dry-run
```

**输出示例**：
```
============================================================
🚀 TODO 系统迁移到 GitHub Issues
============================================================
⚠️  Dry Run 模式 - 仅显示，不实际创建 Issue

📋 步骤 1: 解析现有任务...
📋 从 TODO.md 解析到 15 个未完成任务
📋 从 agent-todos 解析到 8 个未完成任务

📊 共发现 23 个未完成任务

📝 步骤 2: 创建 GitHub Issues...
------------------------------------------------------------
[1/23]   📝 [Dry Run] 创建 Issue: [MIGRATED] 优化情绪 Agent 分析逻辑
     标签：migrated, auto-generated, improvement-ticket
     负责：@sentiment-agent
[2/23]   📝 [Dry Run] 创建 Issue: [MIGRATED] 添加新的数据源
     标签：migrated, auto-generated, task
     负责：@data-fetcher-agent
...

============================================================
📊 迁移统计
============================================================
✅ 成功创建：0 个 Issue
⏭️  跳过：23 个任务
❌ 失败：0 个错误
============================================================

⚠️  Dry Run 结束 - 未实际创建任何 Issue
   移除 --dry-run 参数执行实际迁移
```

### 步骤 4: 执行迁移

确认 Dry Run 结果无误后，执行实际迁移：

```bash
python3 scripts/migrate_todos_to_issues.py
```

**输出示例**：
```
============================================================
🚀 TODO 系统迁移到 GitHub Issues
============================================================

📋 步骤 1: 解析现有任务...
📋 从 TODO.md 解析到 15 个未完成任务
📋 从 agent-todos 解析到 8 个未完成任务

📊 共发现 23 个未完成任务

📝 步骤 2: 创建 GitHub Issues...
------------------------------------------------------------
[1/23]   ✅ 创建 Issue #123: [MIGRATED] 优化情绪 Agent 分析逻辑
[2/23]   ✅ 创建 Issue #124: [MIGRATED] 添加新的数据源
...

============================================================
📊 迁移统计
============================================================
✅ 成功创建：23 个 Issue
⏭️  跳过：0 个任务
❌ 失败：0 个错误
============================================================

✅ 迁移完成！

🔗 查看 Issues:
   https://github.com/aprilvkuo/stock_agent/issues?q=label:migrated
```

### 步骤 5: 验证迁移结果

访问 GitHub 查看创建的 Issues：

```bash
# 使用 GitHub CLI
gh issue list --label migrated --state open

# 或者访问网页
https://github.com/aprilvkuo/stock_agent/issues?q=label:migrated
```

### 步骤 6: 提交迁移改动

```bash
# 创建迁移分支
git checkout -b chore/todo-migration

# 添加所有新文件
git add -A

# 提交
git commit -m "chore: 迁移 TODO 系统到 GitHub Issues

- 创建 Issue 模板 (improvement-ticket, task-ticket)
- 创建迁移脚本 (migrate_todos_to_issues.py)
- 创建 GitHub Actions 工作流
- 迁移 23 个现有任务到 Issues

Closes #002"

# 推送
git push origin chore/todo-migration
```

### 步骤 7: 创建 PR

访问 GitHub 创建 Pull Request：
- Base: `main`
- Compare: `chore/todo-migration`
- 标题：`[Chore] 迁移 TODO 系统到 GitHub Issues | #002`

---

## 🔧 迁移后配置

### 1. 启用 GitHub Actions

确保 GitHub Actions 已启用：
1. 访问 https://github.com/aprilvkuo/stock_agent/actions
2. 如果是首次使用，点击 "Enable Actions"

### 2. 测试自动化工作流

手动触发一次工作流测试：
1. 访问 https://github.com/aprilvkuo/stock_agent/actions/workflows/issue-automation.yml
2. 点击 "Run workflow"
3. 选择分支 `main`
4. 点击 "Run workflow"

### 3. 归档旧系统

```bash
# 备份旧 TODO 系统
cd /Users/egg/.openclaw/workspace
tar -czf .backup/old-todo-system/backup_$(date +%Y%m%d).tar.gz \
    TODO.md \
    shared/stock-system/agent-todos/ \
    shared/stock-system/task_history.json

# 重命名旧脚本
mv shared/stock-system/scripts/auto_task_queue.py \
   shared/stock-system/scripts/auto_task_queue.py.deprecated
```

---

## 📊 新工作流程

### 创建新任务

**方法 1: 手动创建**
1. 访问 https://github.com/aprilvkuo/stock_agent/issues/new/choose
2. 选择 "🚀 改进工单" 或 "📋 任务工单"
3. 填写表单
4. 点击 "Submit new issue"

**方法 2: 自动创建**
```bash
# 通过脚本创建
python3 scripts/create_issue.py \
    --title "添加新功能" \
    --body "任务描述..." \
    --assignee programmer-agent \
    --labels feature,urgent
```

### 处理任务

**Agent 工作流程**：
1. **拉取任务** - 从 GitHub 获取分配给自己的 Issues
2. **更新状态** - 在 Issue 中添加评论更新进度
3. **提交代码** - 创建 Branch → 开发 → 提交 PR
4. **关闭 Issue** - PR 合并后自动关闭

**示例**：
```python
# Agent 代码示例
from github import Github

gh = Github(GITHUB_TOKEN)
repo = gh.get_repo("aprilvkuo/stock_agent")

# 获取分配给我的 Issues
issues = repo.get_issues(state='open', assignee='programmer-agent')

for issue in issues:
    print(f"处理 Issue #{issue.number}: {issue.title}")
    
    # 添加进度评论
    issue.create_comment("🔧 开始处理...")
    
    # 执行任务...
    
    # 完成后
    issue.create_comment("✅ 任务完成，已创建 PR #xxx")
```

---

## 🎯 成功标准

- [x] Issue 模板已创建
- [ ] Labels 已配置
- [ ] 所有未完成任务已迁移
- [ ] GitHub Actions 工作流正常运行
- [ ] 旧系统已归档
- [ ] 团队熟悉新流程

---

## 📖 相关文档

- [TODO_MIGRATION_PLAN.md](./docs/github/TODO_MIGRATION_PLAN.md) - 完整迁移方案
- [ISSUE_AUTOMATION_GUIDE.md](./docs/github/ISSUE_AUTOMATION_GUIDE.md) - Issue 自动化指南
- [CONTRIBUTING.md](./CONTRIBUTING.md) - 贡献指南

---

## ❓ 常见问题

### Q: 迁移后旧任务还能查看吗？

A: 可以！所有旧任务都已备份到 `.backup/old-todo-system/`，可以随时查看。

### Q: 如何查看迁移的 Issues？

A: 使用标签过滤：
```
https://github.com/aprilvkuo/stock_agent/issues?q=label:migrated
```

### Q: 如何禁用自动化工作流？

A: 在 GitHub Actions 页面禁用：
1. 访问 https://github.com/aprilvkuo/stock_agent/actions
2. 选择工作流
3. 点击右上角 "..." → "Disable workflow"

---

**维护者**: 协调 Agent  
**最后更新**: 2026-03-09
