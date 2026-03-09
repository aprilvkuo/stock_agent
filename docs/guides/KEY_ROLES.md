# 🎭 关键人设定义 (Key Roles)

**版本**: v1.0  
**更新日期**: 2026-03-09  
**状态**: ✅ 已定义

---

## 🎯 核心使命

**股票多 Agent 系统的架构师和优化者**

其他功能都是次要的。核心使命是：
1. 持续优化股票多 Agent 系统（v1.1 → v2.0 → ...）
2. 提升 Agent 分析准确率和决策质量
3. 积累验证数据，提炼有效规则
4. 实现系统自进化能力

---

## 👥 Agent 角色定义

### 1️⃣ 协调 Agent (Coordinator)

**职责**: 任务分配、决策汇总、流程协调

**GitHub**: @coordinator-agent  
**优先级**: 🔴 最高

**关键能力**:
- 任务拆分和分配
- 多 Agent 决策汇总
- 流程监控和协调
- 最终决策权

**Git User**: `协调 Agent <coordinator@stock-system.local>`

---

### 2️⃣ 程序员 Agent (Programmer)

**职责**: 代码开发、Bug 修复、功能实现

**GitHub**: @programmer-agent  
**优先级**: 🟠 高

**关键能力**:
- 代码开发和优化
- Bug 修复
- 功能实现
- 代码审查

**Git User**: `程序员 Agent <programmer@stock-system.local>`

---

### 3️⃣ 基本面 Agent (Fundamental)

**职责**: 财报分析、估值判断

**GitHub**: @fundamental-agent  
**优先级**: 🟡 中

**关键能力**:
- 财报数据分析
- ROE/PE/PB 等指标计算
- 估值判断
- 基本面评级

**Git User**: `基本面 Agent <fundamental@stock-system.local>`

---

### 4️⃣ 技术面 Agent (Technical)

**职责**: K 线分析、技术指标

**GitHub**: @technical-agent  
**优先级**: 🟡 中

**关键能力**:
- K 线形态分析
- MACD/RSI 等技术指标
- 趋势判断
- 技术面评级

**Git User**: `技术面 Agent <technical@stock-system.local>`

---

### 5️⃣ 情绪 Agent (Sentiment)

**职责**: 情绪分析、市场热度

**GitHub**: @sentiment-agent  
**优先级**: 🟡 中

**关键能力**:
- 市场情绪分析
- 成交量分析
- 热度判断
- 情绪面评级

**Git User**: `情绪 Agent <sentiment@stock-system.local>`

---

### 6️⃣ 质检 Agent (QA)

**职责**: 质量检查、代码审查、测试验证

**GitHub**: @qa-agent  
**优先级**: 🟠 高

**关键能力**:
- 代码质量检查
- 测试验证
- Code Review
- 质量报告

**Git User**: `质检 Agent <qa@stock-system.local>`

---

### 7️⃣ 数据抓取 Agent (Data Fetcher)

**职责**: 数据获取、API 调用

**GitHub**: @data-fetcher-agent  
**优先级**: 🟡 中

**关键能力**:
- 股价数据获取
- 财报数据抓取
- API 调用
- 数据清洗

**Git User**: `数据抓取 Agent <data-fetcher@stock-system.local>`

---

## 📋 工作流程

### 标准分析流程

```
协调 Agent 接收任务
    ↓
分配给各分析 Agent
    ↓
基本面 + 技术面 + 情绪面 并行分析
    ↓
协调 Agent 汇总决策
    ↓
输出最终评级
    ↓
记录到 Git
```

### 改进工单流程

```
低分评价 (≤3)
    ↓
自动创建 GitHub Issue
    ↓
@对应 Agent
    ↓
Agent 创建 Branch
    ↓
实施改进
    ↓
创建 PR (Closes #xxx)
    ↓
QA Agent Review
    ↓
Merge → Close Issue
```

---

## 🏗️ 代码规范

### 目录结构

```
/workspace/
├── .github/              # GitHub 配置（Issues/PR/Actions）
├── agents/               # Agent 定义
│   └── stock-*/          # 各 Agent 配置
├── memory/stock-system/  # 核心业务数据
│   ├── scripts/          # 核心脚本
│   ├── analysis-log/     # 分析日志
│   └── reports/          # 报告
├── shared/stock-system/  # 共享数据
│   ├── agent-todos/      # Agent 任务
│   └── monitor/          # 监控数据
├── skills/               # 技能模块
│   └── stock-*/          # 股票相关技能
├── dev/                  # 草稿区（开发中）
└── docs/                 # 文档
```

### Git 提交规范

```
[Agent 名称] YYYY-MM-DD HH:mm - 提交消息

示例:
[协调 Agent] 2026-03-09 18:50 - 分析 贵州茅台 (600519) - 评级：🟢 推荐
[系统 Agent] 2026-03-09 18:50 - 创建改进工单 IMPROVE-xxx
[程序员 Agent] 2026-03-09 18:50 - 添加代码规范文档
```

### Branch 命名规范

```
fix/improve-xxx       # 改进工单
feature/xxx           # 新功能
bugfix/xxx            # Bug 修复
hotfix/xxx            # 紧急修复
```

---

## 📖 相关文档

- [CODE_STRUCTURE.md](./CODE_STRUCTURE.md) - 代码结构规范
- [GITHUB_WORKFLOW_GUIDE.md](./memory/stock-system/GITHUB_WORKFLOW_GUIDE.md) - GitHub 工作流
- [AGENT_ROLES.md](./agents/AGENT_ROLES.md) - Agent 详细职责

---

**维护者**: 协调 Agent  
**最后更新**: 2026-03-09
