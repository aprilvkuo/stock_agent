# 股票多 Agent 系统 - 架构设计

## 系统架构

```
OpenClaw Gateway
       │
       ├─→ Session: stock-fundamental (基本面 Agent)
       ├─→ Session: stock-technical (技术面 Agent)
       ├─→ Session: stock-sentiment (情绪 Agent)
       ├─→ Session: stock-coordinator (主 Agent/协调者)
       └─→ Session: stock-review (复盘 Agent)
```

## 工作区结构

```
/Users/egg/.openclaw/workspace/
├── agents/
│   ├── stock-fundamental/       # 基本面 Agent 工作区
│   │   ├── MEMORY.md            # 基本面分析经验
│   │   ├── config.md            # Agent 配置
│   │   └── history/             # 分析历史
│   │
│   ├── stock-technical/         # 技术面 Agent 工作区
│   │   ├── MEMORY.md            # 技术分析经验
│   │   ├── config.md            # Agent 配置
│   │   └── history/             # 分析历史
│   │
│   ├── stock-sentiment/         # 情绪 Agent 工作区
│   │   ├── MEMORY.md            # 情绪分析经验
│   │   ├── config.md            # Agent 配置
│   │   └── history/             # 分析历史
│   │
│   ├── stock-coordinator/       # 主 Agent 工作区
│   │   ├── MEMORY.md            # 协调决策经验
│   │   ├── config.md            # Agent 配置
│   │   └── decisions/           # 决策记录
│   │
│   └── stock-review/            # 复盘 Agent 工作区
│       ├── MEMORY.md            # 复盘方法论
│       ├── config.md            # Agent 配置
│       └── validations/         # 验证历史
│
└── shared/                      # 共享数据区
    └── stock-system/
        ├── queue/               # 任务队列
        │   ├── requests/        # 待分析请求
        │   └── results/         # 分析结果
        ├── validation-queue.md  # 验证队列
        ├── stock-wisdom.md      # 共享规则库
        └── status.md            # 系统状态
```

## Agent 配置

### 基本面 Agent

| 配置项 | 值 |
|--------|-----|
| **Session Label** | `stock-fundamental` |
| **工作区** | `agents/stock-fundamental/` |
| **职责** | 财报分析、估值判断、财务健康度评估 |
| **Heartbeat** | 检查请求队列 |
| **输出** | `shared/stock-system/queue/results/` |

### 技术面 Agent

| 配置项 | 值 |
|--------|-----|
| **Session Label** | `stock-technical` |
| **工作区** | `agents/stock-technical/` |
| **职责** | K 线分析、技术指标、买卖点判断 |
| **Heartbeat** | 检查请求队列 |
| **输出** | `shared/stock-system/queue/results/` |

### 情绪 Agent

| 配置项 | 值 |
|--------|-----|
| **Session Label** | `stock-sentiment` |
| **工作区** | `agents/stock-sentiment/` |
| **职责** | 舆情分析、市场热度、资金流向 |
| **Heartbeat** | 检查请求队列 |
| **输出** | `shared/stock-system/queue/results/` |

### 主 Agent (协调者)

| 配置项 | 值 |
|--------|-----|
| **Session Label** | `stock-coordinator` |
| **工作区** | `agents/stock-coordinator/` |
| **职责** | 任务分发、结果汇总、最终决策 |
| **Heartbeat** | 检查新请求 + 汇总结果 |
| **输出** | `shared/stock-system/validation-queue.md` |

### 复盘 Agent

| 配置项 | 值 |
|--------|-----|
| **Session Label** | `stock-review` |
| **工作区** | `agents/stock-review/` |
| **职责** | 验证预测、评估 Agent 表现、更新规则 |
| **Heartbeat** | 每日验证 + 周度复盘 |
| **输出** | `shared/stock-system/stock-wisdom.md` |

## 通信机制

### 基于文件队列

```
请求流程:
1. 用户 → 主 Agent 写入请求文件
   shared/stock-system/queue/requests/request-{timestamp}.md

2. 各分析 Agent Heartbeat 读取请求
   - 读取请求文件
   - 执行分析
   - 写入结果文件

3. 主 Agent 汇总结果
   - 读取所有结果文件
   - 综合决策
   - 写入验证队列

4. 复盘 Agent 定期验证
   - 检查到期预测
   - 获取真实数据
   - 更新验证状态
```

### 请求文件格式

```markdown
# 分析请求 request-20260308001900

## 请求信息
- 请求 ID: request-20260308001900
- 请求时间：2026-03-08 00:19:00
- 股票代码：600519
- 股票名称：贵州茅台

## 任务
- [ ] 基本面 Agent: 分析财报、估值、财务健康
- [ ] 技术面 Agent: 分析 K 线、技术指标
- [ ] 情绪 Agent: 分析舆情、市场热度

## 状态
- 基本面：⏳ 待处理
- 技术面：⏳ 待处理
- 情绪面：⏳ 待处理
- 汇总：⏳ 待处理
```

### 结果文件格式

```markdown
# 分析结果 result-20260308001900-fundamental

## 请求 ID
request-20260308001900

## Agent
基本面 Agent-v1.0

## 分析结果
- 评级：买入/持有/卖出
- 置信度：XX%
- 关键依据：...
- 风险点：...

## 时间戳
2026-03-08 00:19:30
```

## Heartbeat 配置

### 各 Agent Heartbeat

```markdown
# agents/stock-fundamental/HEARTBEAT.md
每 10 分钟检查请求队列，处理新请求

# agents/stock-technical/HEARTBEAT.md
每 10 分钟检查请求队列，处理新请求

# agents/stock-sentiment/HEARTBEAT.md
每 10 分钟检查请求队列，处理新请求

# agents/stock-coordinator/HEARTBEAT.md
每 5 分钟检查请求队列 + 汇总结果

# agents/stock-review/HEARTBEAT.md
每日 09:00 验证 + 每周五 20:00 复盘
```

## 会话管理

### 创建 Session

```bash
# 基本面 Agent
openclaw sessions spawn --runtime subagent --label "stock-fundamental" --task "基本面分析 Agent" --mode session

# 技术面 Agent
openclaw sessions spawn --runtime subagent --label "stock-technical" --task "技术面分析 Agent" --mode session

# 情绪 Agent
openclaw sessions spawn --runtime subagent --label "stock-sentiment" --task "情绪分析 Agent" --mode session

# 主 Agent
openclaw sessions spawn --runtime subagent --label "stock-coordinator" --task "股票分析协调 Agent" --mode session

# 复盘 Agent
openclaw sessions spawn --runtime subagent --label "stock-review" --task "股票复盘 Agent" --mode session
```

### 发送任务到 Session

```bash
# 通过 sessions_send 发送分析请求
openclaw sessions send --label "stock-coordinator" --message "分析 600519"
```

## 启动流程

1. **启动 5 个 Agent Session**
2. **配置各自 Heartbeat**
3. **测试请求流程**
4. **验证通信机制**

---

**下一步**: 创建工作区结构和配置文件
