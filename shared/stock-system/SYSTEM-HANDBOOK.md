# 📊 股票多 Agent 系统 - 完整手册

**创建时间**: 2026-03-08  
**版本**: v2.0  
**状态**: ✅ 运行中

---

## 🎯 快速索引

| 章节 | 内容 |
|------|------|
| [1. 系统概述](#1-系统概述) | 架构、组件、工作原理 |
| [2. 快速启动](#2-快速启动) | 启动/停止/重启服务 |
| [3. Agent 配置](#3-agent-配置) | 5 个 Agent 的详细配置 |
| [4. 数据目录](#4-数据目录) | 文件结构、队列机制 |
| [5. 监控网站](#5-监控网站) | 访问地址、页面功能 |
| [6. 股票池](#6-股票池) | 当前监控的股票列表 |
| [7. 常用命令](#7-常用命令) | 运维命令速查 |
| [8. 故障排查](#8-故障排查) | 常见问题及解决方案 |
| [9. 待办事项](#9-待办事项) | 下一步优化计划 |

---

## 1. 系统概述

### 架构图

```
OpenClaw Gateway
       │
       ├─→ stock-fundamental (基本面 Agent) ──┐
       ├─→ stock-technical (技术面 Agent) ────┼─→ 主 Agent 汇总
       ├─→ stock-sentiment (情绪 Agent) ──────┘
       ├─→ stock-coordinator (主 Agent)
       └─→ stock-review (复盘 Agent)
```

### 工作流程

```
1. 用户创建请求 → queue/requests/request-XXX.md
2. 守护进程检测 → 分发任务给 3 个分析 Agent
3. Agent 并行分析 → 写入 queue/results/
4. 主 Agent 汇总 → 生成综合建议
5. 写入验证队列 → 等待复盘验证
6. 空闲时自我进化 → 更新知识库
```

### 核心特性

- ✅ **多 Agent 协作** - 基本面/技术面/情绪面分工
- ✅ **自我进化** - 自动学习、复盘、改进
- ✅ **实时监控** - Web 面板实时查看状态
- ✅ **智能频率** - 交易时间 5 分钟，空闲时 1 小时
- ✅ **A 股 + 港股** - 支持两地股票市场

---

## 2. 快速启动

### 方式 1: 启动脚本（推荐）

```bash
cd /Users/egg/.openclaw/workspace/shared/stock-system
./start.sh
# 选择 1) 启动所有服务
```

### 方式 2: 手动启动

```bash
# 启动守护进程
cd /Users/egg/.openclaw/workspace/shared/stock-system/scripts
nohup python3 daemon.py > /tmp/stock-daemon.log 2>&1 &

# 启动 Web 服务器
cd /Users/egg/.openclaw/workspace/shared/stock-system/web
nohup python3 app.py > /tmp/stock-web.log 2>&1 &
```

### 停止服务

```bash
# 停止守护进程
pkill -f "daemon.py"

# 停止 Web 服务器
pkill -f "app.py"
```

### 检查状态

```bash
# 查看进程
pgrep -f "daemon.py" && echo "✅ 守护进程运行中" || echo "❌ 守护进程未运行"
pgrep -f "app.py" && echo "✅ Web 服务器运行中" || echo "❌ Web 服务器未运行"

# 查看日志
tail -20 /tmp/stock-daemon.log
tail -20 /tmp/stock-web.log
```

---

## 3. Agent 配置

### 3.1 基本面 Agent

| 配置项 | 值 |
|--------|-----|
| **名称** | 基本面 Agent |
| **脚本** | `scripts/agent-fundamental.py` |
| **工作区** | `agents/stock-fundamental/` |
| **职责** | 财报分析、估值判断、财务健康 |
| **Heartbeat** | 每 10 分钟检查请求队列 |
| **输出** | 评级、置信度、目标价、止损价 |

### 3.2 技术面 Agent

| 配置项 | 值 |
|--------|-----|
| **名称** | 技术面 Agent |
| **脚本** | `scripts/agent-technical.py` |
| **工作区** | `agents/stock-technical/` |
| **职责** | K 线分析、技术指标、买卖点 |
| **Heartbeat** | 每 10 分钟检查请求队列 |
| **输出** | 评级、置信度、支撑位、阻力位 |

### 3.3 情绪 Agent

| 配置项 | 值 |
|--------|-----|
| **名称** | 情绪 Agent |
| **脚本** | `scripts/agent-sentiment.py` |
| **工作区** | `agents/stock-sentiment/` |
| **职责** | 舆情分析、市场热度、资金流向 |
| **Heartbeat** | 每 10 分钟检查请求队列 |
| **输出** | 评级、置信度、情绪指标 |

### 3.4 主 Agent (协调者)

| 配置项 | 值 |
|--------|-----|
| **名称** | 主 Agent / 协调者 |
| **脚本** | `scripts/agent-coordinator.py` |
| **工作区** | `agents/stock-coordinator/` |
| **职责** | 任务分发、结果汇总、最终决策 |
| **Heartbeat** | 每 5 分钟检查 + 汇总 |
| **输出** | 综合投资建议、验证队列更新 |

### 3.5 复盘 Agent

| 配置项 | 值 |
|--------|-----|
| **名称** | 复盘 Agent |
| **脚本** | `scripts/agent-review.py` |
| **工作区** | `agents/stock-review/` |
| **职责** | 验证预测、评估表现、更新规则 |
| **Heartbeat** | 每日 09:00 验证 + 每周五 20:00 复盘 |
| **输出** | 验证结果、知识库更新 |

---

## 4. 数据目录

### 完整结构

```
/Users/egg/.openclaw/workspace/
├── agents/
│   ├── stock-coordinator/
│   │   ├── data/
│   │   │   ├── queue/
│   │   │   │   ├── requests/      # 分析请求队列
│   │   │   │   ├── results/       # 分析结果
│   │   │   │   └── verify/        # 验证队列
│   │   │   ├── logs/              # 日志文件
│   │   │   ├── knowledge/         # 知识库
│   │   │   │   └── stock-wisdom.md
│   │   │   └── evolution-*.md     # 进化报告
│   │   ├── MEMORY.md
│   │   ├── config.md
│   │   └── HEARTBEAT.md
│   │
│   ├── stock-fundamental/
│   │   ├── MEMORY.md
│   │   ├── config.md
│   │   └── HEARTBEAT.md
│   │
│   ├── stock-technical/
│   │   ├── MEMORY.md
│   │   ├── config.md
│   │   └── HEARTBEAT.md
│   │
│   ├── stock-sentiment/
│   │   ├── MEMORY.md
│   │   ├── config.md
│   │   └── HEARTBEAT.md
│   │
│   └── stock-review/
│       ├── MEMORY.md
│       ├── config.md
│       └── HEARTBEAT.md
│
└── shared/stock-system/
    ├── scripts/
    │   ├── agent-coordinator.py   # 主 Agent
    │   ├── agent-fundamental.py   # 基本面 Agent
    │   ├── agent-technical.py     # 技术面 Agent
    │   ├── agent-sentiment.py     # 情绪 Agent
    │   ├── agent-review.py        # 复盘 Agent
    │   ├── daemon.py              # 守护进程
    │   ├── self-evolution.py      # 自我进化
    │   ├── notifier.py            # 通知模块
    │   ├── stock_data.py          # 数据获取
    │   ├── eastmoney_api.py       # API 调用
    │   └── start.sh               # 启动脚本
    │
    ├── web/
    │   ├── app.py                 # Web 服务器
    │   └── templates/
    │       ├── index.html         # 首页
    │       ├── agents.html        # Agent 状态
    │       ├── evolution.html     # 进化报告
    │       └── report.html        # 个股报告
    │
    └── *.md                       # 文档
```

### 请求文件格式

```markdown
# 分析请求 request-20260308120000

## 请求信息
- 请求 ID: request-20260308120000
- 请求时间：2026-03-08 12:00:00
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
# 分析结果 result-20260308120000-fundamental

## 请求 ID
request-20260308120000

## Agent
基本面 Agent-v1.0

## 分析结果
- 评级：买入
- 置信度：85%
- 关键依据：ROE 优秀、营收增长稳健
- 风险点：PE 偏高
- 目标价：1800
- 止损价：1500

## 时间戳
2026-03-08 12:00:30
```

---

## 5. 监控网站

### 访问地址

| 设备 | 地址 |
|------|------|
| 本机 | http://localhost:5001 |
| 局域网 | http://198.18.0.1:5001 |

### 页面列表

| 页面 | 路径 | 功能 |
|------|------|------|
| **首页** | `/` | 系统监控、分析历史、验证队列 |
| **Agent 状态** | `/agents` | 5 个 Agent 实时状态 |
| **进化报告** | `/evolution` | 自我进化历史记录 |
| **个股报告** | `/report/<代码>` | 股票详细分析报告 |

### API 端点

| 端点 | 说明 |
|------|------|
| `GET /api/data` | 系统完整数据 |
| `GET /api/analysis` | 分析历史列表 |
| `GET /api/validation` | 验证队列 |
| `GET /api/evolution` | 进化报告列表 |
| `GET /api/evolution/<filename>` | 进化报告详情 |
| `GET /api/report/<code>` | 个股详细报告 |
| `GET /api/logs` | 活动日志 |

---

## 6. 股票池

### 当前监控列表

| 代码 | 名称 | 市场 | 状态 |
|------|------|------|------|
| 600519 | 贵州茅台 | A 股 | ✅ 已分析 |
| 000858 | 五粮液 | A 股 | ✅ 已分析 |
| 300750 | 宁德时代 | A 股 | ✅ 已分析 |
| 002594 | 比亚迪 | A 股 | ✅ 已分析 |
| 00700 | 腾讯控股 | 港股 | ✅ 已分析 |
| 09988 | 阿里巴巴 | 港股 | ✅ 已分析 |

### 待添加

| 名称 | 状态 | 备注 |
|------|------|------|
| 范式智能 | ⏳ 待确认 | 需要股票代码 |

---

## 7. 常用命令

### 服务管理

```bash
# 启动所有服务
cd /Users/egg/.openclaw/workspace/shared/stock-system && ./start.sh

# 重启守护进程
pkill -f "daemon.py" && cd /Users/egg/.openclaw/workspace/shared/stock-system/scripts && nohup python3 daemon.py > /tmp/stock-daemon.log 2>&1 &

# 重启 Web 服务器
pkill -f "app.py" && cd /Users/egg/.openclaw/workspace/shared/stock-system/web && nohup python3 app.py > /tmp/stock-web.log 2>&1 &

# 查看进程
pgrep -af "daemon.py|app.py"
```

### 日志查看

```bash
# 守护进程日志
tail -f /Users/egg/.openclaw/workspace/agents/stock-coordinator/data/logs/daemon-$(date +%Y-%m-%d).log

# Web 服务器日志
tail -f /tmp/stock-web.log

# 查看最新进化报告
ls -lt /Users/egg/.openclaw/workspace/agents/stock-coordinator/data/evolution-*.md | head -1 | awk '{print $NF}' | xargs cat
```

### 手动操作

```bash
# 手动触发进化
cd /Users/egg/.openclaw/workspace/shared/stock-system/scripts && python3 self-evolution.py

# 添加新股票
cat > /Users/egg/.openclaw/workspace/agents/stock-coordinator/data/queue/requests/request-$(date +%Y%m%d%H%M%S).md << 'EOF'
# 分析请求 request-XXX

## 请求信息
- 请求 ID: request-XXX
- 请求时间：$(date '+%Y-%m-%d %H:%M:%S')
- 股票代码：XXXXXX
- 股票名称：XXX

## 任务
- [ ] 基本面 Agent: 分析财报、估值、财务健康
- [ ] 技术面 Agent: 分析 K 线、技术指标
- [ ] 情绪 Agent: 分析舆情、市场热度

## 状态
- 基本面：⏳ 待处理
- 技术面：⏳ 待处理
- 情绪面：⏳ 待处理
- 汇总：⏳ 待处理
EOF

# 查看验证队列
cat /Users/egg/.openclaw/workspace/agents/stock-coordinator/data/validation-queue.md
```

---

## 8. 故障排查

### 问题 1: 服务无法启动

**检查端口占用**:
```bash
# Mac 替代 netstat
lsof -i :5001
# 或
nc -z localhost 5001 && echo "端口被占用" || echo "端口空闲"
```

**解决**: 停止占用进程或修改 `app.py` 端口

### 问题 2: API 获取数据失败

**现象**: 日志显示 "Remote end closed connection"

**解决**:
- 等待 60 秒后重试（API 限流）
- 检查网络连接
- 使用手动数据补充

### 问题 3: 网页无法访问

**检查**:
```bash
pgrep -f "app.py"
tail /tmp/stock-web.log
```

**解决**: 重启 Web 服务器

### 问题 4: 守护进程不处理请求

**检查**:
```bash
tail -20 /Users/egg/.openclaw/workspace/agents/stock-coordinator/data/logs/daemon-*.log
cat /Users/egg/.openclaw/workspace/agents/stock-coordinator/data/queue/requests/request-*.md
```

**解决**: 检查请求文件格式是否正确

### 问题 5: 防火墙阻止访问

**解决**:
1. 系统设置 → 网络 → 防火墙 → 选项
2. 添加 Python 应用
3. 设置为"允许传入连接"

---

## 9. 待办事项

### 高优先级 🔴

| # | 任务 | 状态 | 备注 |
|---|------|------|------|
| 1 | 确认范式智能股票代码 | ⏳ | 需要股票代码 |
| 2 | API 限流优化 | ⚠️ | 增加重试机制 |
| 3 | 港股数据完整获取 | 🔄 | 优化 API 调用 |

### 中优先级 🟡

| # | 任务 | 预计 | 备注 |
|---|------|------|------|
| 4 | 数据缓存机制 | 1-2 周 | 避免重复请求 |
| 5 | 多数据源备份 | 2-3 周 | 新浪/腾讯财经 |
| 6 | 错误处理优化 | 1 周 | 友好提示 |
| 7 | 验证系统完善 | 2 周 | 自动验证 |

### 低优先级 🟢

| # | 任务 | 预计 | 备注 |
|---|------|------|------|
| 8 | 机器学习模型 | 3-6 月 | 预测模型 |
| 9 | 预测验证系统 | 2-3 月 | 自动追踪 |
| 10 | 股票评分体系 | 2-3 月 | 综合评分 |

---

## 📚 相关文档

| 文档 | 说明 |
|------|------|
| [README.md](./README.md) | 快速入门 |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | 架构设计 |
| [PROJECT-SNAPSHOT.md](./PROJECT-SNAPSHOT.md) | 项目快照 |
| [SELF-EVOLUTION-GUIDE.md](./SELF-EVOLUTION-GUIDE.md) | 自我进化指南 |
| [FRONTEND-OPTIMIZATION.md](./FRONTEND-OPTIMIZATION.md) | 前端优化 |

---

## 🎯 下次启动清单

启动系统前，请按顺序检查：

- [ ] 确认守护进程运行：`pgrep -f "daemon.py"`
- [ ] 确认 Web 服务器运行：`pgrep -f "app.py"`
- [ ] 查看最新日志：`tail -20 /tmp/stock-daemon.log`
- [ ] 访问监控网站：http://localhost:5001
- [ ] 检查待办事项：确认高优先级任务
- [ ] 查看进化报告：了解系统最新改进

---

**最后更新**: 2026-03-08  
**维护者**: 股票多 Agent 系统  
**联系方式**: 通过 OpenClaw 会话管理
