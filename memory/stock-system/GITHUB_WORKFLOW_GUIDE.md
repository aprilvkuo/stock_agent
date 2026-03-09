# GitHub Issues + PR 工作流指南

**版本**: v2.0  
**实施日期**: 2026-03-09  
**状态**: ✅ 已实施

---

## 🎯 概述

股票多 Agent 系统现已集成 **GitHub Issues + PR 完整工作流**：

```
Agent 评分低
    ↓
自动创建 GitHub Issue
    ↓
自动 @对应 Agent
    ↓
Agent 创建 Branch 解决问题
    ↓
创建 PR 关联 Issue
    ↓
Code Review
    ↓
Merge 后自动关闭 Issue
```

---

## 📋 前置配置

### 1️⃣ 生成 GitHub Token

访问：https://github.com/settings/tokens

**选择 Fine-grained tokens**，权限配置：

| 权限 | 范围 | 访问级别 |
|------|------|---------|
| `issues` | All repositories | Read and write |
| `contents` | All repositories | Read and write |
| `pull_requests` | All repositories | Read and write |
| `metadata` | All repositories | Read only |

**Token 名称**: `stock-agent-workflow`

### 2️⃣ 配置环境变量

```bash
cd /Users/egg/.openclaw/workspace
cp .env.github .env.github.local
# 编辑 .env.github.local，填入你的 Token
```

**.env.github.local**:
```bash
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
GITHUB_REPO=aprilvkuo/stock_agent
```

### 3️⃣ 安装依赖

```bash
pip3 install python-dotenv requests
```

---

## 🚀 使用流程

### 场景 1: 低分自动创建 Issue

**触发条件**: Agent 评分 ≤ 3 分

```python
# 系统自动调用（无需手动操作）
from improvement_ticket import ticket_system

ticket = ticket_system.create_ticket(
    provider_id='data-fetcher',  # 乙方
    consumer_id='fundamental',   # 甲方
    service_type='financial_data',
    rating={'overall_score': 2, ...}
)
```

**结果**:
- ✅ 本地工单已创建
- ✅ GitHub Issue 已创建（自动 @data-fetcher）
- ✅ Label 已添加（🔴 high-priority, 📊 基本面分析）
- ✅ Git 提交已记录

### 场景 2: Agent 接收任务

**被 @后**:

1. **查看 Issue**
   ```bash
   # 访问 Issue 链接（邮件或通知中）
   https://github.com/aprilvkuo/stock_agent/issues/123
   ```

2. **确认接收**
   - 在 Issue 中评论：`收到，立即处理`
   - 或点击 `Assign yourself`

3. **创建 Branch**
   ```bash
   cd /Users/egg/.openclaw/workspace
   git checkout -b fix/improve-20260309131544
   ```

### 场景 3: 解决问题并创建 PR

1. **实施改进**
   ```bash
   # 修改代码
   vim skills/stock-analyzer/scripts/analyze_stock.py
   
   # 提交
   git add -A
   git commit -m "fix: 添加 ROE、毛利率指标"
   ```

2. **推送 Branch**
   ```bash
   git push origin fix/improve-20260309131544
   ```

3. **创建 PR**
   - 访问 GitHub PR 页面
   - 点击 "Compare & pull request"
   - 填写 PR 描述（使用模板）
   - **关键**: 添加 `Closes #123` 关联 Issue

4. **等待 Review**
   - @coordinator-agent 和 @qa-agent 会自动收到通知
   - Reviewer 批准后即可 Merge

### 场景 4: Merge 后自动关闭

- PR Merge 后，GitHub 自动关闭关联 Issue
- 系统自动记录改进完成
- Agent 评分系统更新

---

## 🏷️ Label 说明

| Label | 说明 | 自动添加条件 |
|-------|------|-------------|
| `🔴 high-priority` | 高优先级 | 评分 ≤ 2 |
| `🚨 critical` | 紧急 | 评分 ≤ 1 |
| `🟠 medium-priority` | 中等 | 评分 2-3 |
| `🟡 low-priority` | 低 | 评分 3-4 |
| `📊 基本面分析` | 基本面相关 | service_type 匹配 |
| `📈 技术面分析` | 技术面相关 | service_type 匹配 |
| `😊 情绪分析` | 情绪相关 | service_type 匹配 |
| `💻 代码实现` | 代码相关 | service_type 匹配 |
| `🤖 数据抓取` | 数据相关 | service_type 匹配 |
| `🔧 pending-review` | 待 Review | PR 创建后 |

---

## 🤖 GitHub Actions 自动化

### Issue 通知工作流

**文件**: `.github/workflows/issue-notify.yml`

**触发**: Issue 创建/标记/分配时

**自动执行**:
1. 解析 Issue 内容（提取工单 ID、优先级、负责人）
2. 添加评论通知（包含处理流程说明）
3. @对应 Agent

### PR 自动处理工作流

**文件**: `.github/workflows/pr-auto.yml`

**触发**: PR 创建/更新时

**自动执行**:
1. 验证 PR 是否关联 Issue（必须包含 `Closes #xxx`）
2. 检查 Branch 命名规范
3. 复制 Issue Label 到 PR
4. 通知 Reviewer（@coordinator-agent, @qa-agent）

---

## 📊 状态追踪

### 查看进行中的改进工单

```bash
# GitHub 网页
https://github.com/aprilvkuo/stock_agent/issues?q=is%3Aopen+label%3Aimprovement-ticket

# 或使用 GitHub CLI
gh issue list --label improvement-ticket --state open
```

### 查看已完成的改进

```bash
# GitHub 网页
https://github.com/aprilvkuo/stock_agent/issues?q=is%3Aclosed+label%3Aimprovement-ticket

# 本地文件
cat memory/stock-system/improvement-tickets.json | jq '.[] | select(.status=="done")'
```

---

## 🎯 最佳实践

### Issue 创建

- ✅ 系统自动创建（推荐）
- ⚠️ 手动创建时使用模板
- ✅ 清晰描述问题和影响
- ✅ 提供具体改进建议

### Branch 命名

```bash
# ✅ 推荐
fix/improve-20260309131544
fix/add-roe-indicator
feature/sentiment-analysis-v2

# ❌ 避免
patch-1
test-branch
my-fix
```

### PR 描述

- ✅ 使用 PR 模板
- ✅ 关联 Issue（`Closes #xxx`）
- ✅ 提供测试步骤
- ✅ 标注影响范围

### Code Review

- ✅ 24 小时内响应
- ✅ 具体指出问题
- ✅ 提供改进建议
- ✅ 批准后及时 Merge

---

## ⚠️ 故障排查

### Issue 未自动创建

**检查**:
1. `.env.github` 中 Token 是否正确
2. `python-dotenv` 和 `requests` 是否安装
3. 查看错误日志

**解决**:
```bash
cd /Users/egg/.openclaw/workspace/memory/stock-system
python3 scripts/github_issue_manager.py
```

### PR 未自动关联 Issue

**原因**: PR 描述中缺少 `Closes #xxx`

**解决**: 编辑 PR 描述，添加：
```markdown
Closes #123
```

### Actions 未触发

**检查**:
1. GitHub Actions 是否启用
2. 工作流文件语法是否正确
3. 查看 Actions 日志

**解决**:
```bash
# 验证工作流文件
yamllint .github/workflows/*.yml
```

---

## 📖 相关文件

| 文件 | 说明 |
|------|------|
| `.env.github` | GitHub API 配置 |
| `scripts/github_issue_manager.py` | Issue 管理模块 |
| `.github/workflows/issue-notify.yml` | Issue 通知工作流 |
| `.github/workflows/pr-auto.yml` | PR 自动处理工作流 |
| `.github/ISSUE_TEMPLATE/` | Issue 模板 |
| `.github/pull_request_template.md` | PR 模板 |

---

## 🎉 总结

**完整工作流**:

```
低分 → Issue → @Agent → Branch → PR → Review → Merge → Close
```

**关键特性**:
- ✅ 自动创建 Issue
- ✅ 自动 @对应 Agent
- ✅ 自动通知 Reviewer
- ✅ 自动关联 Issue 和 PR
- ✅ 自动关闭已完成工单
- ✅ 完整 Git 版本控制

**系统版本**: v2.0 (GitHub 集成版)  
**文档更新**: 2026-03-09

---

**开始使用**: 配置 `.env.github` 后，系统会自动处理所有流程！🚀
