# HEARTBEAT.md - 股票多 Agent 系统自动任务

**系统版本**: v1.7 (2026-03-08 13:35 优化)  
**优化详情**: 见 `shared/stock-system/OPTIMIZATION_REPORT_V1.7.md`  
**核心改进**: 数据缓存 + 配置集中管理

---

## 📈 股票多 Agent 系统

### 每日 09:00 - 自动验证 ✅

**命令**:
```bash
cd /Users/egg/.openclaw/workspace/memory/stock-system
python3 scripts/auto_agent.py daily
```

**执行内容**:
1. 读取 `validation-queue.md`
2. 检查到期预测（验证日期 <= 今日）
3. 调用 `stock-analyzer` 获取真实股价
4. 对比预测 vs 实际
5. 更新验证状态 (✅正确 / ⚠️部分正确 / ❌错误)
6. **自动写入文件** (v1.1 新增)

---

### 每周五 20:00 - 周度复盘 ✅

**命令**:
```bash
cd /Users/egg/.openclaw/workspace/memory/stock-system
python3 scripts/auto_agent.py weekly
```

**执行内容**:
1. 统计本周所有分析记录
2. 计算各 Agent 准确率
3. **生成周度复盘报告** (v1.1 新增)
4. 更新表现追踪

---

## 📝 使用说明

### 手动分析股票

```bash
cd /Users/egg/.openclaw/workspace/memory/stock-system
python3 scripts/auto_agent.py analyze <股票代码>

# 示例
python3 scripts/auto_agent.py analyze 600519  # 贵州茅台
python3 scripts/auto_agent.py analyze 00700   # 腾讯控股
python3 scripts/auto_agent.py analyze 000858  # 五粮液
python3 scripts/auto_agent.py analyze 601138  # 工业富联
python3 scripts/auto_agent.py analyze 002230  # 科大讯飞
```

### 查看系统状态

```bash
# 系统状态
cat SYSTEM_STATUS.md

# 优化路线图
cat OPTIMIZATION_ROADMAP.md

# 验证队列
cat validation-queue.md

# 分析日志
ls -la analysis-log/

# 周度报告
ls -la reports/
```

---

## ⚠️ 注意事项

1. **真实数据**: 所有分析使用 `stock-analyzer` 技能获取真实股价和财报数据
2. **验证时间**: 预测验证需要等到验证日期后才能执行（首批：2026-04-07）
3. **Heartbeat**: 确保 OpenClaw Gateway 正常运行以自动触发 Heartbeat
4. **支持股票**: 当前支持 5 只股票（茅台/五粮液/科大讯飞/腾讯/工业富联）

---

## 🎯 当前状态

- ✅ 验证结果自动写入 (v1.1)
- ✅ 周度复盘功能 (v1.1)
- ⏳ 待实施：情绪 Agent 增强、动态权重调整、并发优化
