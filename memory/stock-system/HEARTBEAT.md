# HEARTBEAT.md - 股票多 Agent 系统 v2.0 自动任务

**系统版本**: v2.0 (2026-03-09 重构)  
**架构**: 最优简洁架构 (5 Agent)  
**核心改进**: 风险评估师 + CIO 决策 + 完整投资建议

---

## 📈 股票多 Agent 系统 v2.0

### 每日 09:00 - 自动验证 ✅

**命令**:
```bash
cd /Users/egg/.openclaw/workspace/memory/stock-system
python3 scripts/auto_agent_v2.py daily
```

**执行内容**:
1. 读取 `validation-queue.md`
2. 检查到期预测（验证日期 <= 今日）
3. 调用 `stock-analyzer` 获取真实股价
4. 对比预测 vs 实际
5. 更新验证状态 (✅正确 / ⚠️部分正确 / ❌错误)
6. 更新 Agent 表现追踪

---

### 每周五 20:00 - 周度复盘 ✅

**命令**:
```bash
cd /Users/egg/.openclaw/workspace/memory/stock-system
python3 scripts/auto_agent_v2.py weekly
```

**执行内容**:
1. 统计本周所有分析记录
2. 计算各 Agent 准确率
3. 生成周度复盘报告
4. 更新表现追踪
5. 调整 Agent 权重（如需要）

---

## 📝 使用说明

### 手动分析股票 (v2.0)

```bash
cd /Users/egg/.openclaw/workspace/memory/stock-system

# 分析单只股票
python3 scripts/auto_agent_v2.py analyze <股票代码>

# 示例
python3 scripts/auto_agent_v2.py analyze 600519  # 贵州茅台
python3 scripts/auto_agent_v2.py analyze 00700   # 腾讯控股
python3 scripts/auto_agent_v2.py analyze 000858  # 五粮液
python3 scripts/auto_agent_v2.py analyze 601138  # 工业富联
python3 scripts/auto_agent_v2.py analyze 002230  # 科大讯飞
```

### 查看系统状态

```bash
# 系统状态
cat SYSTEM_STATUS.md

# 优化报告
cat OPTIMIZATION_REPORT_V2.0.md

# 验证队列
cat validation-queue.md

# 分析日志
ls -la analysis-log/

# 配置文件
cat config.json
```

---

## 🎯 v2.0 架构

### 5 个 Agent

| Agent | 权重 | 职责 |
|-------|------|------|
| 基本面分析师 | 30% | 价值评估 (ROE/PE/PB) |
| 技术面分析师 | 25% | 趋势判断 (均线/MACD/RSI) |
| 情绪面分析师 | 20% | 市场热度 (涨跌/成交量) |
| 风险评估师 ⭐ | 15% | 风险控制 (仓位/止损) |
| 首席投资官 ⭐ | 10% | 最终决策 (BUY/HOLD/SELL) |

### 输出结果

完整投资建议包含:
- ✅ 行动：STRONG_BUY/BUY/HOLD/SELL
- ✅ 仓位：建议仓位百分比
- ✅ 目标价：止盈价位
- ✅ 止损价：止损价位
- ✅ 置信度：决策置信度
- ✅ 持有周期：建议持有时间

---

## ⚠️ 注意事项

1. **真实数据**: 所有分析使用 `stock-analyzer` 获取真实股价和财报数据
2. **验证时间**: 预测验证需要等到验证日期后才能执行（首批：2026-04-08）
3. **Heartbeat**: 确保 OpenClaw Gateway 正常运行以自动触发 Heartbeat
4. **支持股票**: 当前支持 5 只股票（茅台/五粮液/科大讯飞/腾讯/工业富联）
5. **配置文件**: 权重和阈值在 `config.json` 中配置

---

## 🎉 当前状态

- ✅ v2.0 架构重构完成 (2026-03-09)
- ✅ 风险评估师模块上线
- ✅ CIO 决策模块上线
- ✅ 配置文件集中管理
- ⏳ 待积累：验证数据 (首批 2026-04-08)
- ⏳ 待实施：动态权重调整、规则库自动更新

---

**最后更新**: 2026-03-09 08:30  
**更新者**: 小助理 🤖
