# 🚀 股票多 Agent 系统 v2.0 - 快速入门

**版本**: v2.0 (最优简洁架构)  
**更新时间**: 2026-03-09

---

## 📋 什么是 v2.0？

v2.0 是股票多 Agent 系统的**最优简洁架构**重构版本，核心特点：

1. **5 个 Agent** - 基本面/技术面/情绪面/风险评估师/CIO
2. **独立风控** - 风险评估师强制评估风险
3. **智能决策** - CIO 综合决策生成完整建议
4. **可执行输出** - BUY/HOLD/SELL + 仓位 + 目标价 + 止损价

---

## 🎯 快速开始

### 1. 分析股票

```bash
cd /Users/egg/.openclaw/workspace/memory/stock-system

# 分析贵州茅台
python3 scripts/auto_agent_v2.py analyze 600519

# 分析腾讯控股
python3 scripts/auto_agent_v2.py analyze 00700

# 分析五粮液
python3 scripts/auto_agent_v2.py analyze 000858
```

### 2. 查看结果

分析完成后会输出：
- 📊 各 Agent 分析结果
- 🛡️ 风险评估报告
- 👔 CIO 投资建议
- 📝 自动写入分析日志

### 3. 查看日志

```bash
# 查看最新分析日志
ls -lt analysis-log/ | head -5

# 查看验证队列
cat validation-queue.md
```

---

## 📊 输出示例

```
🔥 强烈买入 (STRONG_BUY)

| 项目 | 建议 |
|------|------|
| 建议仓位 | 25% |
| 目标价 | ¥1542.20 (+10.0%) |
| 止损价 | ¥1261.80 (-10.0%) |
| 置信度 | 73% |
| 持有周期 | 3-6 个月 |
```

---

## 🛠️ 配置文件

所有可调参数在 `config.json` 中：

```bash
# 查看配置
cat config.json

# 修改 Agent 权重
# 编辑 config.json → agents → fundamental/technical/sentiment/risk → weight
```

### 默认权重

| Agent | 权重 | 可调整范围 |
|-------|------|-----------|
| 基本面 | 30% | 20-40% |
| 技术面 | 25% | 15-35% |
| 情绪面 | 20% | 10-30% |
| 风险 | 15% | 10-20% |

---

## 📁 文件结构

```
memory/stock-system/
├── scripts/
│   ├── auto_agent_v2.py       # 主协调脚本 v2.0 ⭐
│   ├── risk_assessor.py       # 风险评估师 ⭐
│   ├── cio_decision.py        # CIO 决策 ⭐
│   ├── auto_agent.py          # v1.7 (保留)
│   └── ...
├── config.json                # 配置文件 ⭐
├── analysis-log/              # 分析日志
├── validation-queue.md        # 验证队列
├── HEARTBEAT.md               # 定时任务配置
├── SYSTEM_STATUS.md           # 系统状态
└── OPTIMIZATION_REPORT_V2.0.md # 升级报告
```

---

## 🔄 自动化任务

### 每日 09:00 - 自动验证
```bash
python3 scripts/auto_agent_v2.py daily
```

### 每周五 20:00 - 周度复盘
```bash
python3 scripts/auto_agent_v2.py weekly
```

---

## ⚠️ 注意事项

1. **支持股票**: 当前仅支持 5 只股票
   - 600519 贵州茅台
   - 000858 五粮液
   - 002230 科大讯飞
   - 00700 腾讯控股
   - 601138 工业富联

2. **验证周期**: 预测需要 30 天后验证

3. **风险提示**: 本系统仅供参考，不构成投资建议

---

## 📚 更多文档

- `OPTIMIZATION_REPORT_V2.0.md` - 升级报告
- `SYSTEM_STATUS.md` - 系统状态
- `HEARTBEAT.md` - 定时任务配置
- `config.json` - 配置文件

---

## 🆘 常见问题

### Q: 如何修改 Agent 权重？
A: 编辑 `config.json`，修改 `agents` 下的 `weight` 值

### Q: 如何添加新股票？
A: 需要 `stock-analyzer` 支持该股票

### Q: 验证结果在哪里？
A: `validation-queue.md` 文件中

### Q: 如何回退到 v1.7？
A: 使用 `auto_agent.py` 代替 `auto_agent_v2.py`

---

**有问题？查看 `OPTIMIZATION_REPORT_V2.0.md` 或联系小助理 🤖**
