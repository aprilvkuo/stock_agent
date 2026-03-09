# ✅ TODO 迁移到 GitHub Issues - 准备完成报告

**日期**: 2026-03-09 21:55  
**状态**: ✅ 准备工作已完成，待执行迁移  
**Issue**: #002

---

## 🎯 迁移目标

将本地 TODO list 系统**完全迁移**到 GitHub Issues 体系：
- ✅ 集中管理 - 所有任务通过 GitHub Issues 跟踪
- ✅ 自动化流程 - Issue 创建 → 分配 → 执行 → 验证 → 关闭
- ✅ 可追溯性 - 完整的任务历史和审计日志
- ✅ 协作友好 - 支持多人/多 Agent 协作

---

## ✅ 已完成准备工作

### 1. Issue 模板（2 个）

| 模板 | 文件 | 用途 |
|------|------|------|
| 🚀 改进工单 | `.github/ISSUE_TEMPLATE/improvement-ticket.yml` | Agent 自我改进、系统优化 |
| 📋 任务工单 | `.github/ISSUE_TEMPLATE/task-ticket.yml` | 日常任务、定期工作 |

**特点**：
- ✅ 结构化表单
- ✅ 必填字段验证
- ✅ 自动分配负责 Agent
- ✅ 支持优先级和截止时间

### 2. 迁移脚本

| 脚本 | 功能 | 状态 |
|------|------|------|
| `scripts/migrate_todos_to_issues.py` | 迁移 TODO.md 和 agent-todos | ✅ 完成 |
| `scripts/create_labels.py` | 创建 GitHub Labels | ✅ 完成 |

**功能**：
- ✅ 解析 TODO.md 中的任务
- ✅ 解析 agent-todos/*.json 中的任务
- ✅ 自动跳过已完成和需人工的任务
- ✅ 批量创建 GitHub Issues
- ✅ 添加迁移评论和标签
- ✅ Dry Run 模式支持

### 3. GitHub Actions 工作流（2 个）

| 工作流 | 文件 | 触发条件 |
|--------|------|---------|
| Issue 自动化 | `.github/workflows/issue-automation.yml` | Issue 创建/分配时 |
| 每日检查 | `.github/workflows/daily-issue-check.yml` | 每天 09:00 (UTC+8) |

**功能**：
- ✅ 自动处理新 Issue
- ✅ 自动分配负责 Agent
- ✅ 检查逾期任务
- ✅ 生成日报

### 4. 文档（3 份）

| 文档 | 位置 | 用途 |
|------|------|------|
| 完整方案 | `docs/github/TODO_MIGRATION_PLAN.md` | 详细迁移方案 |
| 快速指南 | `docs/github/TODO_MIGRATION_GUIDE.md` | 快速执行指南 |
| 准备报告 | `docs/github/MIGRATION_PREPARATION_REPORT.md` | 本文档 |

---

## 📊 当前 TODO 系统分析

### 待迁移任务统计

**TODO.md**:
- 总任务数：待统计
- 未完成：待统计
- 需人工：将跳过

**agent-todos/**:
- 基本面_Agent.json
- 技术面_Agent.json
- 情绪_Agent.json
- 程序员_Agent.json
- 质检_Agent.json

### 预计创建的 Issues

根据初步分析，预计将创建 **20-30 个** GitHub Issues：
- 改进工单：~15 个
- 任务工单：~10 个
- 紧急任务：~5 个

---

## 🚀 执行步骤

### 步骤 1: 配置 Labels

```bash
cd /Users/egg/.openclaw/workspace
python3 scripts/create_labels.py
```

**预期输出**：
```
============================================================
🏷️  创建 GitHub Issue Labels
============================================================

📦 仓库：aprilvkuo/stock_agent

📊 现有 Labels: 5 个

  ✅ 创建：improvement-ticket
  ✅ 创建：task
  ✅ 创建：feature
  ...
  ✅ 创建：coordinator-agent

============================================================
📊 统计
============================================================
✅ 新建：20 个
✏️  更新：0 个
⏭️  跳过：5 个
📦 总计：20 个
============================================================

✅ Labels 配置完成！
```

### 步骤 2: Dry Run

```bash
python3 scripts/migrate_todos_to_issues.py --dry-run
```

**查看将要创建的 Issues**，确认无误后继续。

### 步骤 3: 执行迁移

```bash
python3 scripts/migrate_todos_to_issues.py
```

**预期输出**：
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

### 步骤 4: 验证结果

```bash
# 使用 GitHub CLI
gh issue list --label migrated --state open

# 或访问网页
https://github.com/aprilvkuo/stock_agent/issues?q=label:migrated
```

### 步骤 5: 提交改动

```bash
# 创建分支
git checkout -b chore/todo-migration

# 添加文件
git add -A

# 提交
git commit -m "chore: 迁移 TODO 系统到 GitHub Issues

- 创建 Issue 模板 (improvement-ticket, task-ticket)
- 创建迁移脚本和 Labels 配置脚本
- 创建 GitHub Actions 工作流
- 迁移现有任务到 Issues

Closes #002"

# 推送
git push origin chore/todo-migration
```

### 步骤 6: 创建 PR

访问 GitHub 创建 Pull Request：
- **URL**: https://github.com/aprilvkuo/stock_agent/compare/chore/todo-migration
- **标题**: `[Chore] 迁移 TODO 系统到 GitHub Issues | #002`
- **描述**: 使用自动生成的描述

---

## 📖 新工作流程

### 创建任务

**方法 1: 手动创建**
1. 访问 https://github.com/aprilvkuo/stock_agent/issues/new/choose
2. 选择对应模板
3. 填写表单

**方法 2: 自动创建**
```bash
python3 scripts/create_issue.py \
    --title "任务标题" \
    --assignee programmer-agent \
    --labels task,urgent
```

### 处理任务

**Agent 工作流**：
```
1. 拉取 Issues → 2. 更新状态 → 3. 创建 PR → 4. 关闭 Issue
```

**示例**：
```python
# 获取分配给我的 Issues
issues = repo.get_issues(state='open', assignee='programmer-agent')

for issue in issues:
    # 添加进度评论
    issue.create_comment("🔧 开始处理...")
    
    # 执行任务...
    
    # 完成后创建 PR
    # PR 描述中包含 "Closes #xxx"
```

---

## 🎯 成功标准

- [x] Issue 模板已创建
- [ ] Labels 已配置（待执行）
- [ ] 所有任务已迁移（待执行）
- [ ] GitHub Actions 正常运行（待测试）
- [ ] 旧系统已归档（待执行）
- [ ] 团队熟悉新流程（待培训）

---

## 📅 时间表

| 阶段 | 内容 | 预计时间 | 状态 |
|------|------|---------|------|
| 准备 | 创建模板、脚本、文档 | 1 小时 | ✅ 完成 |
| 配置 | 创建 Labels | 5 分钟 | ⏳ 待执行 |
| 迁移 | 执行迁移脚本 | 10 分钟 | ⏳ 待执行 |
| 测试 | 验证工作流 | 15 分钟 | ⏳ 待执行 |
| 归档 | 备份旧系统 | 5 分钟 | ⏳ 待执行 |

**总计**: 约 1.5 小时

---

## 🔗 相关资源

- [迁移方案](./docs/github/TODO_MIGRATION_PLAN.md)
- [迁移指南](./docs/github/TODO_MIGRATION_GUIDE.md)
- [Issue 模板](./.github/ISSUE_TEMPLATE/)
- [迁移脚本](./scripts/migrate_todos_to_issues.py)

---

## ❓ 下一步

### 立即执行

```bash
# 1. 配置 Labels
python3 scripts/create_labels.py

# 2. Dry Run
python3 scripts/migrate_todos_to_issues.py --dry-run

# 3. 执行迁移
python3 scripts/migrate_todos_to_issues.py

# 4. 提交并创建 PR
git checkout -b chore/todo-migration
git add -A
git commit -m "chore: 迁移 TODO 系统到 GitHub Issues"
git push origin chore/todo-migration
```

### 后续工作

1. 在 GitHub 上 Review 并合并 PR
2. 启用 GitHub Actions 工作流
3. 测试自动化流程
4. 归档旧 TODO 系统
5. 团队培训

---

**准备者**: 协调 Agent 🤖  
**审核者**: 待审核  
**执行日期**: 2026-03-10
