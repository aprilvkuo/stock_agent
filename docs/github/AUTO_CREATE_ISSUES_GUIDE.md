# 🚀 自动化创建 GitHub Issues 指南

**目标**: 将所有 Agent TODO 自动创建到 GitHub Issues

---

## ⚠️ 需要设置 GITHUB_TOKEN

由于缺少 GITHUB_TOKEN，无法自动创建 Issues。请按以下步骤设置：

### 步骤 1: 创建 GitHub Token

1. 访问 https://github.com/settings/tokens/new
2. 填写描述：`OpenClaw Issue Automation`
3. 选择过期时间：建议 90 天
4. 选择权限（Scopes）：
   - ✅ `repo` (完整仓库权限)
   - ✅ `workflow` (管理 GitHub Actions)
5. 点击 "Generate token"
6. **复制 Token**（只显示一次，格式：`ghp_xxxxxxxxxxxx`）

### 步骤 2: 添加到 .env 文件

```bash
cd /Users/egg/.openclaw/workspace

# 编辑 .env 文件
vim .env
# 或
nano .env
```

**添加以下内容**：
```bash
# GitHub Token（用于 Issue 自动化）
GITHUB_TOKEN=ghp_你的 token 在这里
GITHUB_REPO=aprilvkuo/stock_agent
```

**保存后验证**：
```bash
cat .env | grep GITHUB
```

### 步骤 3: 安装 PyGithub

```bash
pip install PyGithub python-dotenv
```

### 步骤 4: 运行自动化脚本

```bash
cd /Users/egg/.openclaw/workspace
python3 scripts/migrate_all_agent_todos_to_github.py
```

---

## 📋 或者：手动创建 Issues（无需 Token）

如果不想设置 Token，可以手动创建：

### Issue #1: 质检 Agent - 检查系统健康

**访问**: https://github.com/aprilvkuo/stock_agent/issues/new/choose

**选择**: "📋 任务工单"

**标题**:
```
[MIGRATED] [质检 Agent] 检查系统健康
```

**内容**:
```markdown
## 📋 任务描述

检查系统健康

---

## 🤖 负责方

@qa-agent

---

## 📊 任务信息

- **优先级**: 🔴 P1 - 重要
- **来源 Agent**: 质检 Agent
- **创建时间**: 2026-03-08T16:16:59.123789
- **来源文件**: `质检_Agent.json`

---

## ✅ 完成标准

- [ ] 任务已完成
- [ ] 已创建相关 PR
- [ ] 已通过测试/验证

---

*从本地 agent-todos 系统自动迁移*
```

**标签**: `migrated`, `auto-generated`, `improvement-ticket`, `qa-agent`

**Assignee**: `qa-agent`

---

### Issue #2: 技术面 Agent - 分析腾讯 K 线

**标题**:
```
[MIGRATED] [技术面 Agent] 分析 00700 腾讯控股 K 线
```

**内容**:
```markdown
## 📋 任务描述

分析 00700 腾讯控股 K 线

---

## 🤖 负责方

@technical-agent

---

## 📊 任务信息

- **优先级**: 🟡 P2 - 普通
- **来源 Agent**: 技术面 Agent
- **创建时间**: 2026-03-08T16:16:59.123524
- **来源文件**: `技术面_Agent.json`

---

## ✅ 完成标准

- [ ] 完成 K 线分析
- [ ] 更新分析日志
- [ ] 生成技术面报告

---

*从本地 agent-todos 系统自动迁移*
```

**标签**: `migrated`, `auto-generated`, `improvement-ticket`, `technical-agent`

**Assignee**: `technical-agent`

---

### Issue #3: 程序员 Agent - 修复 Bug

**标题**:
```
[MIGRATED] [程序员 Agent] 修复 Bug
```

**内容**:
```markdown
## 📋 任务描述

修复 Bug

---

## 🤖 负责方

@programmer-agent

---

## 📊 任务信息

- **优先级**: 🟡 P2 - 普通
- **来源 Agent**: 程序员 Agent
- **创建时间**: 2026-03-08T16:16:59.123901
- **来源文件**: `程序员_Agent.json`

---

## ✅ 完成标准

- [ ] 定位 Bug
- [ ] 修复 Bug
- [ ] 添加测试
- [ ] 创建 PR

---

*从本地 agent-todos 系统自动迁移*
```

**标签**: `migrated`, `auto-generated`, `improvement-ticket`, `programmer-agent`

**Assignee**: `programmer-agent`

---

### Issue #4: 基本面 Agent - 分析茅台财报

**标题**:
```
[MIGRATED] [基本面 Agent] 分析 600519 贵州茅台财报
```

**内容**:
```markdown
## 📋 任务描述

分析 600519 贵州茅台财报

---

## 🤖 负责方

@fundamental-agent

---

## 📊 任务信息

- **优先级**: 🔴 P1 - 重要
- **来源 Agent**: 基本面 Agent
- **创建时间**: 2026-03-08T16:16:59.123228
- **来源文件**: `基本面_Agent.json`

---

## ✅ 完成标准

- [ ] 获取最新财报数据
- [ ] 分析营收、利润、现金流
- [ ] 生成基本面分析报告
- [ ] 更新估值模型

---

*从本地 agent-todos 系统自动迁移*
```

**标签**: `migrated`, `auto-generated`, `improvement-ticket`, `fundamental-agent`

**Assignee**: `fundamental-agent`

---

### Issue #5: 情绪 Agent - 监控市场舆情

**标题**:
```
[MIGRATED] [情绪 Agent] 监控市场舆情
```

**内容**:
```markdown
## 📋 任务描述

监控市场舆情

---

## 🤖 负责方

@sentiment-agent

---

## 📊 任务信息

- **优先级**: 🟢 P3 - 低优先级
- **来源 Agent**: 情绪 Agent
- **创建时间**: 2026-03-08T16:16:59.123664
- **来源文件**: `情绪_Agent.json`

---

## ✅ 完成标准

- [ ] 收集市场舆情数据
- [ ] 分析情绪指标
- [ ] 更新情绪报告

---

*从本地 agent-todos 系统自动迁移*
```

**标签**: `migrated`, `auto-generated`, `improvement-ticket`, `sentiment-agent`

**Assignee**: `sentiment-agent`

---

## ✅ 完成检查

创建完所有 Issues 后：

- [ ] Issue #1: 质检 Agent - 检查系统健康 ✅
- [ ] Issue #2: 技术面 Agent - 分析腾讯 K 线 ✅
- [ ] Issue #3: 程序员 Agent - 修复 Bug ✅
- [ ] Issue #4: 基本面 Agent - 分析茅台财报 ✅
- [ ] Issue #5: 情绪 Agent - 监控市场舆情 ✅

---

## 🎯 推荐：设置 Token 实现自动化

为了以后能够自动化创建 Issues，建议设置 GITHUB_TOKEN：

```bash
# 1. 编辑 .env
vim /Users/egg/.openclaw/workspace/.env

# 2. 添加
GITHUB_TOKEN=ghp_xxxxxxxxxxxx
GITHUB_REPO=aprilvkuo/stock_agent

# 3. 验证
cat .env | grep GITHUB

# 4. 运行自动化脚本
python3 scripts/migrate_all_agent_todos_to_github.py
```

---

**创建日期**: 2026-03-09 21:55  
**迁移任务数**: 5 个 Agent TODO
