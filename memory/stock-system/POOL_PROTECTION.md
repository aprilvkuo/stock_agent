# 🛡️ 固定股票池配置 - 升级保护说明

**文件**: `stock-pool.json`  
**版本**: v2.0  
**创建日期**: 2026-03-09

---

## 📋 核心股票池 (4 只)

| 代码 | 名称 | 市场 | 权重 | 优先级 |
|------|------|------|------|--------|
| 600519 | 贵州茅台 | A 股 | 30% | 🔴 高 |
| 00700 | 腾讯控股 | 港股 | 25% | 🔴 高 |
| AAPL | 苹果公司 | 美股 | 25% | 🔴 高 |
| BABA | 阿里巴巴 | 美股 | 20% | 🔴 高 |

---

## 🎯 可选股票池 (3 只)

| 代码 | 名称 | 市场 | 权重 | 优先级 |
|------|------|------|------|--------|
| 000858 | 五粮液 | A 股 | 10% | 🟡 中 |
| 002230 | 科大讯飞 | A 股 | 10% | 🟡 中 |
| 601138 | 工业富联 | A 股 | 10% | 🟡 中 |

---

## 🛡️ 升级保护机制

### 独立配置文件

`stock-pool.json` 是**独立配置文件**，与系统代码分离：

```
memory/stock-system/
├── scripts/
│   ├── auto_agent_v2.py      # 系统升级可能修改
│   ├── risk_assessor.py      # 系统升级可能修改
│   └── ...
├── config.json               # 系统升级可能修改
├── stock-pool.json           # ⭐ 独立配置，升级不受影响！
└── POOL_PROTECTION.md        # 本文件
```

### 保护规则

1. **系统升级时**:
   - ✅ `stock-pool.json` 保持不变
   - ✅ 核心股票池保持不变
   - ✅ 用户配置不受影响

2. **修改股票池**:
   - 直接编辑 `stock-pool.json`
   - 修改后无需重启，下次分析生效

3. **系统重置**:
   - 如需重置，备份 `stock-pool.json`
   - 重置后恢复备份即可

---

## 📝 使用说明

### 分析核心股票池

```bash
cd /Users/egg/.openclaw/workspace/memory/stock-system

# 一键分析 4 只核心股票
python3 scripts/auto_agent_v2.py pool
```

### 分析单只股票

```bash
# 分析茅台
python3 scripts/auto_agent_v2.py analyze 600519

# 分析腾讯
python3 scripts/auto_agent_v2.py analyze 00700

# 分析苹果
python3 scripts/auto_agent_v2.py analyze AAPL

# 分析阿里
python3 scripts/auto_agent_v2.py analyze BABA
```

### 修改股票池

1. 编辑 `stock-pool.json`
2. 在 `core_pool` 数组中添加/修改股票
3. 保存即可，无需重启

示例 - 添加新股票:
```json
{
  "code": "00700",
  "name": "腾讯控股",
  "market": "HK",
  "industry": "互联网",
  "weight": 0.25,
  "priority": "high",
  "added_date": "2026-03-08"
}
```

---

## ⚠️ 注意事项

### 数据源依赖

- **A 股** (600519, 000858, etc.): ✅ stock-analyzer 支持
- **港股** (00700): ✅ stock-analyzer 支持
- **美股** (AAPL, BABA): ⚠️ 需要 stock-analyzer 支持

### 如果 stock-analyzer 不支持美股

临时方案：
1. 使用 `fallback_data` 降级数据
2. 或手动输入股价数据
3. 或等待 stock-analyzer 扩展支持

---

## 🔄 系统升级流程

### 升级前

```bash
# 备份股票池配置
cp stock-pool.json stock-pool.json.backup
```

### 升级后

```bash
# 验证配置是否保留
cat stock-pool.json | grep "core_pool"

# 如有需要，恢复备份
cp stock-pool.json.backup stock-pool.json
```

---

## 📊 分析频率建议

### 核心股票池
- **每日**: 盘后分析一次 (09:00 Heartbeat)
- **每周**: 深度复盘一次 (周五 20:00)

### 可选股票池
- **每周**: 分析一次
- **或**: 按需分析

---

## 🎯 投资组合建议

基于核心股票池的建议配置：

| 股票 | 建议仓位 | 说明 |
|------|----------|------|
| 贵州茅台 | 30% | 消费龙头，稳健 |
| 腾讯控股 | 25% | 互联网龙头，成长 |
| 苹果公司 | 25% | 全球科技龙头 |
| 阿里巴巴 | 20% | 电商 + 云，价值修复 |

**总仓位**: 根据风险评估动态调整 (0-100%)

---

## 📞 问题排查

### Q: 股票池配置不生效？
A: 检查 `stock-pool.json` 格式是否正确 (JSON 格式)

### Q: 分析美股失败？
A: stock-analyzer 可能不支持美股，需要扩展数据源

### Q: 如何删除某只股票？
A: 在 `stock-pool.json` 中删除对应条目即可

---

**最后更新**: 2026-03-09  
**维护者**: 小助理 🤖
