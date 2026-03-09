# 📊 核心股票池 - 固定配置说明

**版本**: v2.0  
**创建日期**: 2026-03-09  
**保护级别**: ⭐⭐⭐⭐⭐ (升级不受影响)

---

## 🎯 核心股票池 (4 只)

| # | 代码 | 名称 | 市场 | 行业 | 权重 |
|---|------|------|------|------|------|
| 1 | 600519 | **贵州茅台** | A 股 | 白酒 | 30% |
| 2 | 00700 | **腾讯控股** | 港股 | 互联网 | 25% |
| 3 | AAPL | **苹果公司** | 美股 | 科技 | 25% |
| 4 | BABA | **阿里巴巴** | 美股 | 电商/云 | 20% |

---

## 🚀 快速使用

### 一键分析全部核心股票

```bash
cd /Users/egg/.openclaw/workspace/memory/stock-system

# 方法 1: 使用独立脚本 (推荐 ⭐)
python3 scripts/analyze_core_pool.py

# 方法 2: 使用主脚本
python3 scripts/auto_agent_v2.py pool
```

### 分析单只股票

```bash
# 茅台
python3 scripts/auto_agent_v2.py analyze 600519

# 腾讯
python3 scripts/auto_agent_v2.py analyze 00700

# 苹果
python3 scripts/auto_agent_v2.py analyze AAPL

# 阿里
python3 scripts/auto_agent_v2.py analyze BABA
```

---

## 📁 配置文件

### 主配置文件

**路径**: `stock-pool.json`

```json
{
  "core_pool": [
    {
      "code": "600519",
      "name": "贵州茅台",
      "market": "A",
      "industry": "白酒",
      "weight": 0.30,
      "priority": "high"
    },
    {
      "code": "00700",
      "name": "腾讯控股",
      "market": "HK",
      "industry": "互联网",
      "weight": 0.25,
      "priority": "high"
    },
    {
      "code": "AAPL",
      "name": "苹果公司",
      "market": "US",
      "industry": "科技",
      "weight": 0.25,
      "priority": "high"
    },
    {
      "code": "BABA",
      "name": "阿里巴巴",
      "market": "US",
      "industry": "电商/云",
      "weight": 0.20,
      "priority": "high"
    }
  ]
}
```

### 修改股票池

直接编辑 `stock-pool.json`，添加或删除股票即可。

---

## 🛡️ 升级保护机制

### 文件保护层级

```
🔒 受保护文件 (升级不受影响):
├── stock-pool.json          ⭐⭐⭐⭐⭐ 核心配置
├── POOL_PROTECTION.md       ⭐⭐⭐⭐⭐ 保护说明
└── CORE_POOL_README.md      ⭐⭐⭐⭐⭐ 本文件

⚙️ 系统文件 (升级可能修改):
├── scripts/auto_agent_v2.py
├── scripts/risk_assessor.py
├── scripts/cio_decision.py
└── config.json
```

### 升级流程

**系统升级前**:
```bash
# 备份配置文件 (可选，因为 stock-pool.json 是独立的)
cp stock-pool.json stock-pool.json.backup
```

**系统升级后**:
```bash
# 验证配置是否保留
cat stock-pool.json | grep "core_pool"

# 如有问题，恢复备份
cp stock-pool.json.backup stock-pool.json
```

---

## 📊 分析结果示例

```
======================================================================
📋 核心股票池分析汇总
======================================================================

| # | 股票 | 行动 | 仓位 | 目标价 | 止损价 | 置信度 |
|---|------|------|------|--------|--------|--------|
| 1 | 贵州茅台 | 持有 | 10% | ¥1472.10 | ¥1261.80 | 73% |
| 2 | 腾讯控股 | 持有 | 10% | ¥544.95 | ¥467.10 | 77% |
| 3 | 苹果公司 | 持有 | 10% | ¥183.75 | ¥157.50 | 69% |
| 4 | 阿里巴巴 | 持有 | 10% | ¥89.25 | ¥76.50 | 69% |

统计:
  总计：4 只
  买入：0 只
  持有：4 只
  卖出：0 只
  失败：0 只
```

---

## ⚠️ 注意事项

### 数据源支持

| 市场 | 支持情况 | 说明 |
|------|----------|------|
| A 股 | ✅ 完全支持 | stock-analyzer 原生支持 |
| 港股 | ✅ 完全支持 | stock-analyzer 原生支持 |
| 美股 | ⚠️ 降级数据 | 使用缓存数据，需手动更新 |

### 美股数据问题

如果 `stock-analyzer` 不支持美股，系统会使用降级数据：
- AAPL: $175 (需更新为真实股价)
- BABA: $85 (需更新为真实股价)

**解决方案**:
1. 等待 `stock-analyzer` 扩展支持美股
2. 或手动更新 `get_fallback_data()` 中的价格
3. 或暂时移除美股，只分析 A 股 + 港股

---

## 📈 投资建议

### 仓位配置建议

基于核心股票池的建议配置：

| 股票 | 基础权重 | 风险调整后 |
|------|----------|------------|
| 贵州茅台 | 30% | 20-30% |
| 腾讯控股 | 25% | 15-25% |
| 苹果公司 | 25% | 15-25% |
| 阿里巴巴 | 20% | 10-20% |

**总仓位**: 根据风险评估动态调整 (0-100%)

### 再平衡建议

- **频率**: 每季度或半年
- **方法**: 根据最新分析调整仓位
- **触发**: 单只股票涨幅超过 50% 时再平衡

---

## 🔧 高级用法

### 自定义分析频率

编辑 `stock-pool.json` 中的 `analysis_schedule`:

```json
{
  "analysis_schedule": {
    "daily": ["600519", "00700"],      // 每日分析
    "weekly": ["AAPL", "BABA"]         // 每周分析
  }
}
```

### 添加新股票

在 `core_pool` 数组中添加:

```json
{
  "code": "000858",
  "name": "五粮液",
  "market": "A",
  "industry": "白酒",
  "weight": 0.10,
  "priority": "medium"
}
```

### 设置优先级

- `high`: 每次必分析
- `medium`: 按需分析
- `low`: 月度分析

---

## 📞 问题排查

### Q: 分析失败怎么办？
A: 检查 `stock-analyzer` 是否支持该股票市场

### Q: 如何更新美股价格？
A: 编辑 `auto_agent_v2.py` 中的 `get_fallback_data()` 函数

### Q: 股票池配置不生效？
A: 检查 `stock-pool.json` 格式是否正确 (JSON 格式)

### Q: 如何恢复默认配置？
A: 删除 `stock-pool.json`，重新运行 `analyze_core_pool.py` 会自动生成

---

## 📚 相关文档

- `stock-pool.json` - 股票池配置文件
- `POOL_PROTECTION.md` - 升级保护说明
- `QUICKSTART_V2.md` - v2.0 快速入门
- `OPTIMIZATION_REPORT_V2.0.md` - v2.0 升级报告

---

**最后更新**: 2026-03-09  
**维护者**: 小助理 🤖  
**状态**: ✅ 正常运行
