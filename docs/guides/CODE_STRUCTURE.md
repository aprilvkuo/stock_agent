# 🏗️ 代码结构规范 (Code Structure)

**版本**: v1.0  
**实施日期**: 2026-03-09  
**状态**: ✅ 已实施

---

## 🎯 设计原则

1. **清晰分离** - 草稿区与正式区严格分离
2. **职责单一** - 每个目录有明确的职责
3. **易于导航** - 目录结构直观，易于理解
4. **版本控制** - 所有变更通过 Git 管理
5. **文档完整** - 每个目录都有 README 说明

---

## 📁 目录结构

```
/Users/egg/.openclaw/workspace/
│
├── 📄 KEY_ROLES.md              # 关键人设定义 ⭐
├── 📄 CODE_STRUCTURE.md         # 代码结构规范 ⭐
├── 📄 HEARTBEAT.md              # 心跳任务配置
├── 📄 WORKSPACE_CLEANUP_REPORT.md  # 工作区整理报告
│
├── 📁 .github/                  # GitHub 配置
│   ├── workflows/               # GitHub Actions 工作流
│   │   ├── issue-notify.yml     # Issue 自动通知
│   │   └── pr-auto.yml          # PR 自动处理
│   ├── ISSUE_TEMPLATE/          # Issue 模板
│   │   ├── improvement-ticket.yml
│   │   └── feature-request.yml
│   └── pull_request_template.md # PR 模板
│
├── 📁 agents/                   # Agent 定义（正式）
│   ├── stock-coordinator/       # 协调 Agent
│   ├── stock-fundamental/       # 基本面 Agent
│   ├── stock-technical/         # 技术面 Agent
│   ├── stock-sentiment/         # 情绪 Agent
│   └── stock-review/            # 复盘 Agent
│
├── 📁 memory/stock-system/      # 核心业务数据 ⭐
│   ├── scripts/                 # 核心脚本
│   │   ├── auto_agent.py        # 主协调脚本
│   │   ├── git_version_control.py # Git 版本控制
│   │   └── github_issue_manager.py # GitHub Issue 管理
│   ├── analysis-log/            # 分析日志
│   ├── reports/                 # 分析报告
│   ├── agent-ratings/           # Agent 评分
│   ├── improvement-tickets/     # 改进工单
│   └── validation-queue.md      # 验证队列
│
├── 📁 shared/stock-system/      # 共享数据 ⭐
│   ├── agent-todos/             # Agent 任务
│   │   ├── meetings/            # 会议纪要
│   │   └── tasks/               # 任务列表
│   ├── monitor/                 # 监控数据
│   │   ├── five_step_log.json   # 五步法日志
│   │   └── quality_report.json  # 质量报告
│   └── web/                     # Web 界面
│
├── 📁 skills/                   # 技能模块（正式）
│   ├── stock-analyzer/          # 股票分析工具 ⭐
│   ├── stock-analyzer-readonly/ # 只读版
│   └── stock-monitor-skill/     # 股票监控 ⭐
│
├── 📁 dev/                      # 草稿区（开发中）⭐
│   ├── experiments/             # 实验性代码
│   ├── drafts/                  # 草稿文件
│   └── testing/                 # 测试代码
│
└── 📁 .backup/                  # 备份目录
    └── YYYYMMDD_HHMMSS_*/       # 按时间戳命名
```

---

## 🔑 关键目录说明

### 1️⃣ 主目录 (`/workspace/`)

**职责**: 项目根目录，包含核心配置和文档

**必须文件**:
- ✅ `KEY_ROLES.md` - 关键人设定义
- ✅ `CODE_STRUCTURE.md` - 代码结构规范
- ✅ `HEARTBEAT.md` - 心跳任务配置
- ✅ `.gitignore` - Git 忽略规则

**禁止**:
- ❌ 临时文件
- ❌ 实验性代码
- ❌ 大型数据文件

---

### 2️⃣ memory/stock-system/（核心业务数据）

**职责**: 股票多 Agent 系统的核心业务逻辑和数据

**结构**:
```
memory/stock-system/
├── scripts/              # 核心脚本（生产就绪）
├── analysis-log/         # 分析日志（按日期组织）
├── reports/              # 分析报告（周度/月度）
├── agent-ratings/        # Agent 评分记录
├── improvement-tickets/  # 改进工单
├── feedback-reports/     # 反馈报告
├── config.json           # 系统配置
└── validation-queue.md   # 验证队列
```

**规范**:
- ✅ 所有脚本必须有文档字符串
- ✅ 重要变更必须有 Git 提交
- ✅ 分析日志按 `YYYY-MM-DD_stock_code.md` 命名

---

### 3️⃣ shared/stock-system/（共享数据）

**职责**: Agent 之间共享的数据和状态

**结构**:
```
shared/stock-system/
├── agent-todos/          # Agent 任务管理
│   ├── meetings/         # 会议纪要
│   └── tasks/            # 任务列表
├── monitor/              # 系统监控
│   ├── five_step_log.json
│   └── quality_report.json
└── web/                  # Web 界面
    ├── app.py
    └── templates/
```

**规范**:
- ✅ JSON 文件必须格式化（indent=2）
- ✅ 会议纪要必须有时间和参与者
- ✅ 监控数据实时更新

---

### 4️⃣ dev/（草稿区）⭐

**职责**: 开发中、实验性、未完成的代码

**结构**:
```
dev/
├── experiments/          # 实验性代码
│   └── experiment-xxx/
├── drafts/               # 草稿文件
│   └── draft-xxx.md
└── testing/              # 测试代码
    └── test-xxx.py
```

**规范**:
- ✅ 所有草稿必须在 dev/ 目录下
- ✅ 实验性代码必须有 README 说明
- ✅ 完成并验证后迁移到正式目录
- ❌ 禁止直接在生产目录测试

---

### 5️⃣ skills/（技能模块）

**职责**: 可复用的技能模块

**结构**:
```
skills/
├── stock-analyzer/       # 股票分析（正式）
│   ├── SKILL.md
│   ├── scripts/
│   └── _meta.json
├── stock-monitor-skill/  # 股票监控（正式）
└── stock-analyzer-readonly/
```

**规范**:
- ✅ 每个技能必须有 SKILL.md
- ✅ 必须有 _meta.json 元数据
- ✅ 经过测试验证才能放入

---

## 📝 Git 工作流规范

### Branch 命名

```bash
# 改进工单
fix/improve-code-structure
fix/improve-20260309185000

# 新功能
feature/sentiment-analysis-v2

# Bug 修复
bugfix/price-calculation

# 紧急修复
hotfix/critical-issue
```

### 提交消息格式

```
[Agent 名称] YYYY-MM-DD HH:mm - 提交消息

示例:
[协调 Agent] 2026-03-09 18:50 - 分析 贵州茅台 (600519) - 评级：🟢 推荐
[程序员 Agent] 2026-03-09 18:50 - 添加代码规范文档
[系统 Agent] 2026-03-09 18:50 - 创建改进工单 IMPROVE-xxx
```

### PR 流程

1. **创建 Branch** - 从 main 分支
2. **实施改进** - 在 dev/ 中测试
3. **验证通过** - 迁移到正式目录
4. **创建 PR** - 关联 Issue (`Closes #xxx`)
5. **Code Review** - QA Agent 审核
6. **Merge** - 合并到 main
7. **删除 Branch** - 清理

---

## 🔒 安全规范

### 敏感信息

**禁止提交**:
- ❌ API Keys
- ❌ 密码
- ❌ Token
- ❌ 个人身份信息

**正确做法**:
- ✅ 使用系统环境变量
- ✅ 使用 `.env` 文件（加入 .gitignore）
- ✅ 使用 macOS 钥匙串

### .gitignore 规则

```gitignore
# 敏感信息
.env
.env.*
*.key
*.pem

# 临时文件
*.tmp
*.bak
.DS_Store

# Python
__pycache__/
*.py[cod]
*.pyo

# 草稿区（可选）
dev/drafts/
dev/experiments/
```

---

## 📖 文档规范

### README.md 模板

每个目录应有 README.md：

```markdown
# 目录名称

**职责**: 简短描述

**文件结构**:
- file1.py - 说明
- file2.md - 说明

**使用说明**:
简要说明如何使用

**维护者**: @agent-name
```

### 文档更新

- ✅ 代码变更时同步更新文档
- ✅ 新增功能必须有文档
- ✅ 废弃功能必须标注

---

## ✅ 检查清单

### 新目录创建时

- [ ] 创建 README.md
- [ ] 添加到 .gitignore（如需要）
- [ ] 更新 CODE_STRUCTURE.md
- [ ] Git 提交

### 代码提交前

- [ ] 代码通过测试
- [ ] 文档已更新
- [ ] 符合命名规范
- [ ] Git 提交消息规范

### PR 创建前

- [ ] 在 dev/ 中测试通过
- [ ] 迁移到正式目录
- [ ] 关联 Issue
- [ ] Code Review 通过

---

## 📊 目录成熟度

| 目录 | 成熟度 | 说明 |
|------|--------|------|
| memory/stock-system/ | ✅ 生产就绪 | 核心业务，严格规范 |
| shared/stock-system/ | ✅ 生产就绪 | 共享数据，实时更新 |
| skills/stock-*/ | ✅ 生产就绪 | 正式技能，已验证 |
| agents/stock-*/ | ✅ 生产就绪 | Agent 配置 |
| dev/ | 🟡 开发中 | 草稿区，灵活 |
| .backup/ | 🟡 备份 | 历史文件 |

---

## 🎯 持续改进

本规范会随着系统发展而更新。改进建议：

1. 创建 GitHub Issue
2. 讨论改进方案
3. 创建 PR
4. Review 通过后更新

---

**维护者**: 程序员 Agent  
**最后更新**: 2026-03-09  
**版本**: v1.0
