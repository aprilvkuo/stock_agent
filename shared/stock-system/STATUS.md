# 🚀 股票多 Agent 系统 - 运行状态

## 系统状态

**状态**: 🟢 **完全自动化运行中**

**启动时间**: 2026-03-08 00:28

**架构版本**: v2.0 (多 Agent 多工作区)

---

## ✅ 已完成配置

### 5 个独立 Agent

| Agent | 工作区 | 脚本 | Heartbeat | 状态 |
|-------|--------|------|-----------|------|
| 基本面 Agent | `agents/stock-fundamental/` | `agent-fundamental.py` | 每 10 分钟 | ✅ 就绪 |
| 技术面 Agent | `agents/stock-technical/` | `agent-technical.py` | 每 10 分钟 | ✅ 就绪 |
| 情绪 Agent | `agents/stock-sentiment/` | `agent-sentiment.py` | 每 10 分钟 | ✅ 就绪 |
| 主 Agent | `agents/stock-coordinator/` | `agent-coordinator.py` | 每 5 分钟 | ✅ 就绪 |
| 复盘 Agent | `agents/stock-review/` | `agent-review.py` | 每日 + 每周 | ✅ 就绪 |

### 共享数据区

```
shared/stock-system/
├── scripts/           ✅ 5 个 Agent 脚本 + 启动脚本
├── queue/
│   ├── requests/      ✅ 请求队列
│   └── results/       ✅ 结果队列
├── validation-queue.md ✅ 验证队列 (2 项)
└── README.md          ✅ 使用文档
```

### 测试验证

✅ **完整流程测试通过**:
1. 创建请求 → 2. 基本面分析 → 3. 技术面分析 → 4. 情绪分析 → 5. 主 Agent 汇总 → 6. 添加验证队列

**测试案例**: 贵州茅台 (600519)
- 基本面：买入 (80%)
- 技术面：买入 (85%)
- 情绪：乐观 (65%)
- **综合**: 🟢 推荐 (78 分)
- 验证队列：2 项待验证

---

## 🔄 自动化流程

```
┌─────────────────────────────────────────────────────────────┐
│  用户创建请求文件                                            │
│  shared/stock-system/queue/requests/request-xxx.md          │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  Heartbeat 触发 (每 5-10 分钟)                                 │
└─────────────────────────┬───────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
   ┌────────────┐ ┌────────────┐ ┌────────────┐
   │ 基本面 Agent│ │ 技术面 Agent│ │ 情绪 Agent  │
   │ 读取请求   │ │ 读取请求   │ │ 读取请求   │
   │ 执行分析   │ │ 执行分析   │ │ 执行分析   │
   │ 写入结果   │ │ 写入结果   │ │ 写入结果   │
   └────────────┘ └────────────┘ └────────────┘
          │               │               │
          └───────────────┼───────────────┘
                          ▼
              ┌───────────────────────┐
              │   主 Agent            │
              │   读取所有结果        │
              │   综合决策            │
              │   写入验证队列        │
              └───────────┬───────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │   复盘 Agent          │
              │   每日 09:00 验证       │
              │   每周五 20:00 复盘     │
              │   更新规则库          │
              └───────────────────────┘
```

---

## 📊 当前数据

### 分析记录

| 指标 | 数值 |
|------|------|
| 总分析次数 | 1 (测试) |
| 待处理请求 | 0 |
| 已完成请求 | 1 |

### 验证队列

| 股票 | 预测 | 验证日 | 状态 |
|------|------|--------|------|
| 600519 茅台 | 突破 ¥1764 | 04-06 | ⏳ 待验证 |
| 600519 茅台 | 不跌破 ¥1596 | 04-06 | ⏳ 待验证 |

### Agent 表现

| Agent | 分析次数 | 准确率 | 状态 |
|-------|---------|--------|------|
| 基本面-v1.0 | 1 | 待验证 | 🟢 活跃 |
| 技术面-v1.0 | 1 | 待验证 | 🟢 活跃 |
| 情绪-v1.0 | 1 | 待验证 | 🟢 活跃 |

---

## 🎯 使用方式

### 方式 1: 创建请求文件（推荐）

```bash
# 创建请求
cat > /Users/egg/.openclaw/workspace/shared/stock-system/queue/requests/request-$(date +%Y%m%d%H%M%S).md << 'EOF'
# 分析请求 request-xxx

## 请求信息
- 请求时间：2026-03-08
- 股票代码：600519
- 股票名称：贵州茅台

## 状态
- 基本面：⏳ 待处理
- 技术面：⏳ 待处理
- 情绪面：⏳ 待处理
- 汇总：⏳ 待处理
EOF
```

然后等待 Heartbeat 自动处理（5-10 分钟）。

### 方式 2: 手动触发

```bash
cd /Users/egg/.openclaw/workspace/shared/stock-system/scripts

# 依次运行
python3 agent-fundamental.py
python3 agent-technical.py
python3 agent-sentiment.py
python3 agent-coordinator.py
```

### 方式 3: 一键启动

```bash
python3 scripts/start-system.py
```

---

## 📅 Heartbeat 时间表

| 任务 | 频率 | 时间 | 脚本 |
|------|------|------|------|
| 基本面检查 | 每 10 分钟 | 自动 | `agent-fundamental.py` |
| 技术面检查 | 每 10 分钟 | 自动 | `agent-technical.py` |
| 情绪检查 | 每 10 分钟 | 自动 | `agent-sentiment.py` |
| 主 Agent 汇总 | 每 5 分钟 | 自动 | `agent-coordinator.py` |
| 复盘验证 | 每日 | 09:00 | `agent-review.py daily` |
| 周度复盘 | 每周 | 周五 20:00 | `agent-review.py weekly` |

---

## 📈 自我进化机制

### 每日验证

- 复盘 Agent 自动检查到期预测
- 获取真实股价数据
- 更新验证状态 (✅正确 / ❌错误)
- 记录偏差分析

### 周度复盘

- 统计各 Agent 表现
- 识别失败模式
- 生成复盘报告
- 提出改进建议

### 规则进化

- 连续 5 次成功 → 新增规则
- 连续 3 次失败 → 废弃规则
- Agent 准确率>80% → 提高权重
- Agent 准确率<60% → 降低权重

---

## 🔧 监控和维护

### 查看状态

```bash
# 系统状态
cat shared/stock-system/README.md

# 请求队列
ls -la shared/stock-system/queue/requests/

# 结果
ls -la shared/stock-system/queue/results/

# 验证队列
cat shared/stock-system/validation-queue.md
```

### 手动触发验证

```bash
cd shared/stock-system/scripts
python3 agent-review.py daily
```

### 查看 Agent 日志

```bash
# 各 Agent 工作区
cat agents/stock-fundamental/MEMORY.md
cat agents/stock-technical/MEMORY.md
cat agents/stock-sentiment/MEMORY.md
cat agents/stock-coordinator/MEMORY.md
cat agents/stock-review/MEMORY.md
```

---

## 🎉 里程碑

- ✅ 2026-03-08 00:03 - 单进程模拟版本完成
- ✅ 2026-03-08 00:15 - 自动化脚本完成
- ✅ 2026-03-08 00:20 - 多 Agent 架构设计完成
- ✅ 2026-03-08 00:25 - **5 个 Agent 脚本全部完成**
- ✅ 2026-03-08 00:26 - **完整流程测试通过**
- ✅ 2026-03-08 00:28 - **系统正式启动**

---

## 📝 下一步

1. **继续分析股票** - 积累更多案例
2. **等待首次验证** - 2026-04-06
3. **生成首份复盘报告** - 2026-03-13 (周五)
4. **提炼首批规则** - 积累 20+ 案例后

---

**系统已完全自动化，可以持续运行并自我优化！** 🚀

---

**最后更新**: 2026-03-08 00:28
**版本**: v2.0
