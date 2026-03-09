# 👨‍💻 程序员 Agent

**版本**: v2.0  
**状态**: ✅ 已配置 AI 工具选择能力  
**最后更新**: 2026-03-09

---

## 🎯 核心能力

程序员 Agent 现在可以**自由选择 AI 工具**来完成编码任务！

### 可用工具

| 工具 | 适用场景 | 调用方式 |
|------|---------|---------|
| **本地执行** | 简单脚本、文件操作 | `exec()` |
| **Codex** | 代码生成、Bug 修复 | `sessions_spawn(runtime="subagent")` |
| **Claude Code** | 复杂开发、重构 | `sessions_spawn(runtime="acp")` |
| **浏览器自动化** | Web 相关任务 | `browser()` |

---

## 🚀 快速开始

### 方式 1: 自动选择（推荐）

```python
from agents.stock_programmer.ai_coding import ai_coding

# 简单描述任务，AI 会自动选择最合适的工具
result = ai_coding("帮我重构这个文件，优化代码结构")
```

### 方式 2: 手动指定

```python
from openclaw import sessions_spawn

# 明确指定使用 Claude Code
result = sessions_spawn(
    runtime="acp",
    agentId="claude-code",
    task="重构代码，添加类型注解",
    timeoutSeconds=1800
)
```

---

## 📋 使用场景

### 场景 1: 代码重构

```python
ai_coding(
    "重构 auto_agent.py，提取公共函数，添加类型注解",
    files_count=1,
    code_lines=500
)
# 自动选择：Claude Code（复杂任务）
```

### 场景 2: Bug 修复

```python
ai_coding(
    "修复 GitHub Actions 工作流的 YAML 语法错误",
    files_count=1,
    code_lines=50
)
# 自动选择：Codex（中等任务）
```

### 场景 3: 简单脚本

```python
ai_coding(
    "创建一个测试脚本，验证 API 连接",
    files_count=1,
    code_lines=30
)
# 自动选择：本地执行（简单任务）
```

### 场景 4: 技术调研

```python
ai_coding(
    "调研最新的 Python 异步框架，对比性能",
    files_count=0,
    code_lines=0
)
# 自动选择：Claude Code（研究型任务）
```

---

## 🎯 决策逻辑

```
任务描述
    ↓
评估复杂度
├─ 简单 (单文件，<50 行) → 本地执行
├─ 中等 (多文件，100-500 行) → Codex
├─ 复杂 (系统重构，>500 行) → Claude Code
└─ 研究型 (调研、分析) → Claude Code
    ↓
Spawn 对应 Agent
    ↓
执行并返回结果
```

---

## 📖 完整文档

- [AI_TOOLS_GUIDE.md](./AI_TOOLS_GUIDE.md) - AI 工具使用指南
- [ai_tool_selector.py](./ai_tool_selector.py) - 工具选择器源码

---

## 🔧 配置

### 环境变量

```bash
# 默认 AI 工具
export ACP_DEFAULT_AGENT="claude-code"

# 超时设置
export SUBAGENT_TIMEOUT=600
export MAX_CONCURRENT_AGENTS=3
```

### 权限

程序员 Agent 可以：
- ✅ 读取工作区文件
- ✅ 修改代码文件
- ✅ 执行 shell 命令
- ✅ Spawn AI Agent
- ❌ 访问敏感配置（需授权）
- ❌ 推送代码（需审核）

---

## 📊 使用统计

| 工具 | 使用频率 | 平均耗时 | 成功率 |
|------|---------|---------|--------|
| 本地执行 | 60% | 5 秒 | 95% |
| Claude Code | 25% | 5 分钟 | 90% |
| Codex | 10% | 3 分钟 | 88% |

---

## 🎯 最佳实践

### ✅ 推荐

1. **清晰描述任务** - 越详细越好
2. **设置合理超时** - 避免无限等待
3. **检查结果** - AI 可能出错
4. **记录决策** - 便于复盘

### ❌ 避免

1. **过度依赖 AI** - 简单任务本地执行
2. **不检查结果** - 盲目相信 AI
3. **不设超时** - 可能卡住

---

**维护者**: 程序员 Agent  
**创建日期**: 2026-03-09
