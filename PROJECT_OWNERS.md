# 📋 项目归属人 (Project Owners)

**版本**: v1.0  
**创建日期**: 2026-03-09  
**生效日期**: 2026-03-09  
**状态**: ✅ 正式版

---

## 🎯 核心原则

1. **用户本人** - 拥有核心系统最终决策权
2. **程序员 Agent** - 负责技术实现类项目
3. **协调 Agent** - 负责流程管理类项目
4. **各 Agent** - 各自模块的自主维护

---

## 📊 项目归属人清单

| 项目 | 路径 | 归属人 | 职责 |
|------|------|--------|------|
| **股票多 Agent 系统** (核心) | `memory/stock-system/` | **用户本人** | 最终决策、方向规划、审批重大改动 |
| **Web 网站项目** | `dev/` | **程序员 Agent** | 开发、优化、维护 |
| **Git 项目管理** | `scripts/` + `.github/` | **协调 Agent** | 流程管理、Issue 分配、进度追踪 |
| **协调 Agent** | `agents/stock-coordinator/` | **协调 Agent** | 自身模块优化、任务分发逻辑 |
| **基本面 Agent** | `agents/stock-fundamental/` | **基本面 Agent** | 自身模块优化、分析逻辑 |
| **技术面 Agent** | `agents/stock-technical/` | **技术面 Agent** | 自身模块优化、分析逻辑 |
| **情绪 Agent** | `agents/stock-sentiment/` | **情绪 Agent** | 自身模块优化、分析逻辑 |
| **审核 Agent** | `agents/stock-review/` | **审核 Agent** | 自身模块优化、审核逻辑 |
| **程序员 Agent** | `agents/stock-programmer/` | **程序员 Agent** | 自身模块优化、编码能力 |
| **文档系统** | `docs/` | **协调 Agent** | 文档整理、更新、归档 |
| **技能系统** | `skills/` | **程序员 Agent** | 技能开发、更新、测试 |
| **每日记忆** | `memory/YYYY-MM-DD.md` | **协调 Agent** | 日志记录、信息整理 |
| **长期记忆** | `MEMORY.md` | **用户本人** | 重要决策、关键上下文 |

---

## 🤖 Agent 职责详解

### 协调 Agent (stock-coordinator)

**负责项目**:
- ✅ Git 项目管理 (`scripts/` + `.github/`)
- ✅ 文档系统 (`docs/`)
- ✅ 每日记忆 (`memory/YYYY-MM-DD.md`)

**核心职责**:
- 任务分发和协调
- Issue 管理和分配
- 进度追踪和报告
- 文档整理和归档
- 日志记录和总结

---

### 程序员 Agent (stock-programmer)

**负责项目**:
- ✅ Web 网站项目 (`dev/`)
- ✅ 技能系统 (`skills/`)

**核心职责**:
- Web 功能开发
- 技能开发和优化
- 代码 Review
- 技术验证和实验
- Bug 修复

---

### 基本面 Agent (stock-fundamental)

**负责项目**:
- ✅ 自身模块 (`agents/stock-fundamental/`)

**核心职责**:
- 财报分析逻辑优化
- 估值模型改进
- 财务健康度评估
- 基本面规则迭代

---

### 技术面 Agent (stock-technical)

**负责项目**:
- ✅ 自身模块 (`agents/stock-technical/`)

**核心职责**:
- K 线分析逻辑优化
- 技术指标改进
- 均线系统优化
- 技术面规则迭代

---

### 情绪 Agent (stock-sentiment)

**负责项目**:
- ✅ 自身模块 (`agents/stock-sentiment/`)

**核心职责**:
- 舆情分析逻辑优化
- 市场热度评估
- 情绪指标改进
- 情绪面规则迭代

---

### 审核 Agent (stock-review)

**负责项目**:
- ✅ 自身模块 (`agents/stock-review/`)

**核心职责**:
- 审核逻辑优化
- 风险评估
- 质量把关
- 审核规则迭代

---

## 👤 用户本人职责

**负责项目**:
- ✅ 股票多 Agent 系统核心方向 (`memory/stock-system/`)
- ✅ 长期记忆 (`MEMORY.md`)

**核心职责**:
- 系统方向规划
- 重大改动审批
- 关键决策
- 最终审核

---

## 🔄 协作流程

### 跨项目协作

```
1. 发现问题/需求
   ↓
2. 创建 GitHub Issue
   ↓
3. 协调 Agent 分配给对应归属人
   ↓
4. 归属人处理
   ↓
5. 提交 PR
   ↓
6. 相关方 Review
   ↓
7. Merge
```

### 重大改动审批

```
1. 归属人提出改动方案
   ↓
2. 创建 Issue + 方案文档
   ↓
3. 用户本人审批
   ↓
4. 审批通过后执行
   ↓
5. 提交 PR
   ↓
6. 用户本人最终 Review
   ↓
7. Merge
```

---

## 📞 联系方式

| 角色 | 联系方式 |
|------|---------|
| 用户本人 | 直接对话 |
| 协调 Agent | GitHub Issue @coordinator |
| 程序员 Agent | GitHub Issue @programmer |
| 其他 Agent | GitHub Issue @对应 Agent |

---

## 📝 变更记录

| 版本 | 日期 | 变更内容 | 审批人 |
|------|------|---------|--------|
| v1.0 | 2026-03-09 | 初始版本，明确所有项目归属人 | 用户本人 |

---

## 🔗 相关文档

- [CONTRIBUTING.md](./CONTRIBUTING.md) - 贡献指南
- [HEARTBEAT.md](./HEARTBEAT.md) - 心跳任务
- [IDENTITY.md](./IDENTITY.md) - 身份定义
- [GitHub Issues](https://github.com/aprilvkuo/stock_agent/issues) - 任务管理

---

**维护者**: 协调 Agent  
**最后更新**: 2026-03-09  
**下次审查**: 2026-04-09 (每月审查一次)
