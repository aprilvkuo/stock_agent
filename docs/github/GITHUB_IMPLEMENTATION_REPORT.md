# GitHub Issues + PR 工作流实施报告

**实施日期**: 2026-03-09 17:00-17:02  
**系统版本**: v2.0 (GitHub 集成版)  
**实施者**: 系统 Agent

---

## ✅ 已完成内容

### 1️⃣ 核心模块

**文件**: `memory/stock-system/scripts/github_issue_manager.py`

**功能**:
- ✅ GitHub Issue 自动创建
- ✅ 改进工单 Issue 模板
- ✅ 自动 @对应 Agent
- ✅ Label 自动添加
- ✅ PR 创建和管理
- ✅ Issue 状态管理

**代码量**: 380 行

---

### 2️⃣ 工单系统集成

**文件**: `improvement_ticket.py`

**新增功能**:
- ✅ 低分自动创建 GitHub Issue
- ✅ 本地工单 + GitHub Issue 双轨运行
- ✅ Issue 链接回写到本地工单
- ✅ Git 提交包含 Issue 编号

**修改量**: +40 行

---

### 3️⃣ GitHub Actions 工作流

**文件** (已创建，待推送):

| 文件 | 功能 | 状态 |
|------|------|------|
| `issue-notify.yml` | Issue 自动通知 | ⏳ 待推送 |
| `pr-auto.yml` | PR 自动处理 | ⏳ 待推送 |

**自动化功能**:
- Issue 创建时自动评论通知
- 提取工单 ID、优先级、负责人
- PR 关联 Issue 验证
- 自动添加 Label
- 通知 Reviewer

---

### 4️⃣ Issue 和 PR 模板

**文件**:

| 文件 | 说明 | 状态 |
|------|------|------|
| `improvement-ticket.yml` | 改进工单模板 | ✅ 已推送 |
| `feature-request.yml` | 功能建议模板 | ✅ 已推送 |
| `pull_request_template.md` | PR 模板 | ✅ 已推送 |

---

### 5️⃣ 配置文件

**文件**: `.env.github`

**配置项**:
```bash
GITHUB_TOKEN=your_token_here
GITHUB_REPO=aprilvkuo/stock_agent
AGENT_GITHUB_fundamental=fundamental-agent
AGENT_GITHUB_technical=technical-agent
...
```

**状态**: ⏳ 需要用户配置 Token

---

### 6️⃣ 文档

**文件**:

| 文件 | 说明 | 状态 |
|------|------|------|
| `GITHUB_WORKFLOW_GUIDE.md` | 完整使用指南 | ✅ 已推送 |
| `GITHUB_TOKEN_SETUP.md` | Token 配置指南 | ✅ 已推送 |

---

## 📊 实施统计

| 项目 | 数量 | 状态 |
|------|------|------|
| 新增模块 | 1 个 | ✅ |
| 修改模块 | 1 个 | ✅ |
| 工作流文件 | 2 个 | ⏳ 待推送 |
| 模板文件 | 3 个 | ✅ |
| 配置文件 | 1 个 | ⏳ 待配置 |
| 文档 | 2 个 | ✅ |
| **总代码量** | **+600 行** | ✅ |

---

## 🎯 完整工作流

```
Agent 评分 ≤ 3
    ↓
improvement_ticket.py
    ↓
github_issue_manager.py
    ↓
GitHub API → 创建 Issue
    ↓
自动 @对应 Agent
    ↓
Agent 创建 Branch: fix/improve-xxx
    ↓
解决问题 → 创建 PR
    ↓
PR 模板 → 关联 Issue (Closes #xxx)
    ↓
GitHub Actions → 通知 Reviewer
    ↓
Code Review → Merge
    ↓
自动关闭 Issue
    ↓
本地工单状态更新
    ↓
Git 提交记录
```

---

## ⚠️ 待完成步骤

### 用户操作（必需）

1. **生成 GitHub Token**
   - 访问：https://github.com/settings/tokens
   - 选择 Fine-grained tokens
   - 权限：Actions, Contents, Issues, Pull requests, Workflows (全部 Read and write)

2. **配置 Token**
   ```bash
   cd /Users/egg/.openclaw/workspace
   vim .env.github
   # 填入 GITHUB_TOKEN=ghp_xxxxx
   ```

3. **推送工作流文件**
   ```bash
   git add .github/workflows/*.yml
   git commit -m "feat: GitHub Actions 工作流"
   git push origin main
   ```

### 验证测试

```bash
cd /Users/egg/.openclaw/workspace/memory/stock-system
python3 scripts/github_issue_manager.py
```

---

## 🚀 功能特性

### 自动创建 Issue

- ✅ 低分自动触发（≤3 分）
- ✅ 模板化 Issue 内容
- ✅ 自动 @对应 Agent
- ✅ 优先级 Label
- ✅ 服务类型 Label
- ✅ 截止日期设置

### PR 流程

- ✅ PR 模板
- ✅ 关联 Issue 验证
- ✅ Branch 命名规范
- ✅ 自动通知 Reviewer
- ✅ Merge 后自动关闭 Issue

### GitHub Actions

- ✅ Issue 通知工作流
- ✅ PR 自动处理工作流
- ✅ 自动评论
- ✅ Label 管理

### 双轨运行

- ✅ 本地工单保留
- ✅ GitHub Issue 同步
- ✅ Git 提交记录
- ✅ 状态一致性

---

## 📝 Issue 示例

**标题**: `[HIGH] @data-fetcher 需要改进：financial_data`

**内容**:
```markdown
# 🎫 改进工单：IMPROVE-20260309131544

**优先级**: HIGH  
**乙方**: @data-fetcher  
**甲方**: @fundamental  
**服务类型**: `financial_data`  
**创建时间**: 2026-03-09 13:15  
**截止日期**: 2026-03-12

---

## ⭐ 总体评分

**得分**: 2.2/5.0 ⭐⭐

### 📊 评分详情
| 维度 | 得分 |
|------|------|
| 准确性 | ⭐⭐☆☆☆ (2/5) |
| 完整性 | ⭐☆☆☆☆ (1/5) |
| 有用性 | ⭐⭐☆☆☆ (2/5) |

## 📝 问题描述

数据缺少关键指标，需要手动补充

## 💡 改进建议

- 添加 ROE 指标
- 添加毛利率指标
- 添加净利率指标

## 📋 处理流程

1. 接收任务 - @乙方 确认接收
2. 创建 Branch - `fix/improve-20260309131544`
3. 解决问题 - 实施改进
4. 创建 PR - 关联此 Issue
5. Code Review - 等待审核
6. Merge - 合并后自动关闭
```

---

## 🔧 配置检查清单

- [ ] GitHub Token 已生成（带 workflow 权限）
- [ ] `.env.github` 已配置
- [ ] 依赖已安装（`pip3 install python-dotenv requests`）
- [ ] 工作流文件已推送
- [ ] GitHub Actions 已启用
- [ ] Agent GitHub 账号已映射

---

## 📖 相关文档

- [GITHUB_WORKFLOW_GUIDE.md](./memory/stock-system/GITHUB_WORKFLOW_GUIDE.md) - 完整使用指南
- [GITHUB_TOKEN_SETUP.md](./GITHUB_TOKEN_SETUP.md) - Token 配置指南

---

## 🎉 总结

**核心成果**:
- ✅ GitHub Issue 自动创建模块完成
- ✅ 工单系统集成完成
- ✅ Issue 和 PR 模板完成
- ✅ GitHub Actions 工作流完成（待推送）
- ✅ 完整文档完成

**待用户操作**:
- ⏳ 配置 GitHub Token（带 workflow 权限）
- ⏳ 推送工作流文件
- ⏳ 测试完整流程

**系统版本**: v2.0 (GitHub 集成版)  
**下一步**: 配置 Token → 推送工作流 → 测试流程

---

**报告生成时间**: 2026-03-09 17:02  
**生成者**: 系统 Agent
