# 🚀 股票多 Agent 系统 - 快速启动指南

## 系统已自动化运行！

---

## 📋 当前状态

- **系统状态**: 🟢 自动化运行中
- **Heartbeat**: ✅ 已配置 (每日 09:00 自动验证)
- **已分析股票**: 3 只 (茅台、腾讯、五粮液)
- **待验证预测**: 10 项
- **首次验证日**: 2026-04-07

---

## 🎯 快速命令

### 1. 分析新股票

```bash
cd /Users/egg/.openclaw/workspace/memory/stock-system
python3 scripts/auto_agent.py analyze <股票代码>
```

**支持的股票**:
```bash
python3 scripts/auto_agent.py analyze 600519  # 贵州茅台
python3 scripts/auto_agent.py analyze 00700   # 腾讯控股
python3 scripts/auto_agent.py analyze 000858  # 五粮液
python3 scripts/auto_agent.py analyze 002230  # 科大讯飞
python3 scripts/auto_agent.py analyze 601138  # 工业富联
```

### 2. 手动触发验证

```bash
# 每日验证
python3 scripts/auto_agent.py daily

# 周度复盘
python3 scripts/auto_agent.py weekly
```

### 3. 查看状态

```bash
# 系统状态
cat SYSTEM_STATUS.md

# 验证队列
cat validation-queue.md

# 最新分析
ls -lt analysis-log/ | head -5
```

---

## 🔄 自动化流程

```
每天 09:00 (Heartbeat 自动触发)
    ↓
auto_agent.py daily
    ↓
检查到期预测 → 获取真实股价 → 更新验证状态
    ↓
写入文件 (可追溯)
```

---

## 📊 分析结果示例

```bash
$ python3 scripts/auto_agent.py analyze 000858

Step 1: 获取真实数据...
✅ 五粮液 当前价：¥145.6 (+0.85%)

Step 2: Agent 分析...
   基本面：买入 (70%)
   技术面：买入 (75%)
   情绪面：中性 (55%)

Step 3: 综合决策...
   综合评分：74.0
   评级：🟢 推荐
   建议仓位：10-15%

Step 4-6: 自动记录完成 ✅
```

---

## 📁 关键文件

| 文件 | 说明 |
|------|------|
| `scripts/auto_agent.py` | 主协调脚本 (自动化核心) |
| `validation-queue.md` | 待验证预测队列 |
| `analysis-log/` | 分析日志目录 |
| `SYSTEM_STATUS.md` | 系统运行状态 |
| `HEARTBEAT.md` | Heartbeat 配置 |

---

## ⏰ 重要时间

| 时间 | 事件 |
|------|------|
| 每日 09:00 | 自动验证 (Heartbeat) |
| 每周五 20:00 | 周度复盘 (Heartbeat) |
| 2026-04-07 | 首批预测到期验证 |

---

## 💡 提示

1. **分析更多股票**: 积累 20+ 案例后开始提炼规则
2. **查看日志**: `analysis-log/` 目录有完整分析记录
3. **验证追踪**: `validation-queue.md` 追踪所有预测
4. **Heartbeat**: 确保 OpenClaw Gateway 正常运行

---

## 🎉 系统特点

- ✅ **真实数据**: 调用 stock-analyzer 获取实时股价
- ✅ **自动分析**: 3 个 Agent 独立分析 + 主 Agent 决策
- ✅ **自动记录**: 分析日志 + 验证队列自动更新
- ✅ **自动验证**: Heartbeat 定时触发验证
- ✅ **可追溯**: 所有结果写入文件，可查询可审计

---

**开始使用吧！** 📈

```bash
# 分析一只股票试试
python3 scripts/auto_agent.py analyze 600519
```
