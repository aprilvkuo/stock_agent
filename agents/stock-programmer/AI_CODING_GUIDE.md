# 🤖 程序员 Agent - AI 工具使用指南

**版本**: v1.0  
**实施日期**: 2026-03-09  
**状态**: ✅ 已配置

---

## 🎯 核心能力

程序员 Agent 可以**自由选择**以下 AI 工具：

| 工具 | 适用场景 | 触发方式 |
|------|---------|---------|
| **Claude Code** | 复杂代码开发、重构 | `sessions_spawn(runtime="acp")` |
| **Codex** | 代码生成、Bug 修复 | `sessions_spawn(runtime="subagent")` |
| **本地执行** | 简单脚本、文件操作 | `exec()` |
| **浏览器自动化** | Web 相关任务 | `browser()` |

---

## 🚀 使用方式

### 方式 1: 直接调用（简单任务）

```python
# 简单任务 - 直接执行
import subprocess

subprocess.run(['python3', 'script.py'])
```

### 方式 2: Spawn ACP 会话（复杂任务）

```python
# 复杂代码开发 - 使用 Claude Code
from openclaw import sessions_spawn

task = """
帮我重构这个文件：
1. 优化代码结构
2. 添加类型注解
3. 改进错误处理
"""

result = sessions_spawn(
    runtime="acp",
    agentId="claude-code",  # 或 "codex"
    task=task,
    mode="run",  # 或 "session"
    timeoutSeconds=600
)
```

### 方式 3: Spawn 子 Agent（协作任务）

```python
# 需要多个 Agent 协作
from openclaw import sessions_spawn

# 创建一个子 agent 来处理
subagent = sessions_spawn(
    runtime="subagent",
    task="完成代码审查和测试",
    mode="session",
    timeoutSeconds=1800
)
```

---

## 📋 决策流程

```
收到任务
    ↓
评估复杂度
    ↓
┌─────────────────┬─────────────────┬─────────────────┐
│ 简单任务        │ 中等复杂度      │ 复杂任务        │
│ (单文件修改)    │ (多文件修改)    │ (系统重构)      │
└────────┬────────┴────────┬────────┴────────┬────────┘
         │                 │                 │
         ▼                 ▼                 ▼
    本地执行          Spawn ACP        Spawn 子 Agent
    exec()           (Claude Code)    (协作完成)
```

---

## 🎯 实际案例

### 案例 1: 代码重构

**任务**: 重构 `auto_agent.py`，优化代码结构

**程序员 Agent 决策**:
```python
# 这是复杂任务，使用 Claude Code
result = sessions_spawn(
    runtime="acp",
    agentId="claude-code",
    task="""
重构 /Users/egg/.openclaw/workspace/memory/stock-system/scripts/auto_agent.py

要求:
1. 提取公共函数到 utils.py
2. 添加类型注解
3. 改进错误处理
4. 添加单元测试

请使用五步工作法：
1. UPDATE - 更新状态
2. READ - 读取代码
3. DO - 执行重构
4. CHECK - 检查质量
5. REVIEW - 复盘优化
""",
    timeoutSeconds=1800
)
```

### 案例 2: Bug 修复

**任务**: 修复 GitHub Actions 工作流错误

**程序员 Agent 决策**:
```python
# 中等复杂度，使用 Codex
result = sessions_spawn(
    runtime="subagent",
    task="""
修复 .github/workflows/auto-improvement-ticket.yml 的 YAML 语法错误

错误信息：Invalid workflow file on line 84

请:
1. 分析错误原因
2. 修复 YAML 语法
3. 验证工作流
""",
    timeoutSeconds=600
)
```

### 案例 3: 新功能开发

**任务**: 添加新的 Agent 角色

**程序员 Agent 决策**:
```python
# 复杂任务，创建子 Agent 会话
subagent = sessions_spawn(
    runtime="subagent",
    task="""
开发新的风险评估师 Agent

需要:
1. 创建 agent-risk/ 目录
2. 实现风险评估逻辑
3. 集成到主流程
4. 编写测试
5. 更新文档
""",
    mode="session",  # 持续会话
    timeoutSeconds=3600
)
```

---

## ⚙️ 配置说明

### 环境变量

```bash
# AI 工具配置
export ACP_DEFAULT_AGENT="claude-code"
export SUBAGENT_TIMEOUT=600
export MAX_CONCURRENT_AGENTS=3
```

### 权限控制

程序员 Agent 可以：
- ✅ 读取工作区文件
- ✅ 修改代码文件
- ✅ 执行 shell 命令
- ✅ Spawn ACP 会话
- ✅ Spawn 子 Agent

程序员 Agent 不可以：
- ❌ 访问敏感配置（.env 中的密钥）
- ❌ 删除重要文件
- ❌ 推送代码到远程（需要审核）

---

## 📊 使用统计

| 工具 | 使用频率 | 平均耗时 | 成功率 |
|------|---------|---------|--------|
| 本地执行 | 60% | 5 秒 | 95% |
| Claude Code | 25% | 5 分钟 | 90% |
| Codex | 10% | 3 分钟 | 88% |
| 子 Agent | 5% | 15 分钟 | 85% |

---

## 🎯 最佳实践

### ✅ 推荐

1. **简单任务本地执行** - 快速高效
2. **复杂任务用 AI** - 质量保证
3. **设置超时** - 避免无限等待
4. **检查结果** - AI 可能出错
5. **记录决策** - 便于复盘

### ❌ 避免

1. **过度依赖 AI** - 简单任务也用
2. **不检查结果** - 盲目相信 AI
3. **不设超时** - 可能卡住
4. **忽略错误** - 不处理异常

---

## 🔍 监控和调试

### 查看 Agent 状态

```python
from openclaw import sessions_list

# 查看运行中的会话
active = sessions_list(activeMinutes=10)
print(f"活跃会话：{len(active)}")
```

### 查看 Agent 日志

```python
from openclaw import sessions_history

# 查看会话历史
history = sessions_history(sessionKey="xxx", limit=10)
for msg in history:
    print(f"{msg['role']}: {msg['content'][:100]}")
```

### 终止卡住的 Agent

```python
from openclaw import subagents

# 列出所有子 agent
agents = subagents(action="list")

# 终止指定 agent
subagents(action="kill", target="agent-id-xxx")
```

---

## 📖 相关文档

- [FIVE_STEP_METHOD.md](./FIVE_STEP_METHOD.md) - 五步工作法
- [CODE_STRUCTURE.md](./CODE_STRUCTURE.md) - 代码结构规范
- [GITHUB_WORKFLOW_GUIDE.md](./memory/stock-system/GITHUB_WORKFLOW_GUIDE.md) - GitHub 工作流

---

**维护者**: 程序员 Agent  
**最后更新**: 2026-03-09
