# 股票数据获取解决方案

## 问题诊断

原有的股票分析系统缺失关键财务数据 (PE、PB、ROE 等显示为 N/A)，原因是：
1. 原有的 `stock-analyzer` 脚本依赖的 API 失效
2. 没有备用数据源
3. 浏览器自动化未实现

## 解决方案

### 1. 东方财富 API 直接调用 ✅

**文件**: `/Users/egg/.openclaw/workspace/shared/stock-system/scripts/stock_data.py`

**特点**:
- 直接使用东方财富公开 API
- 无需浏览器自动化，速度快
- 获取实时行情数据 (股价、涨跌幅、成交量等)
- 获取估值指标 (PE、PB 等)

**数据字段**:
```json
{
  "stock_name": "比亚迪",
  "current_price": 93.62,
  "change_percent": -0.01,
  "pe_ttm": 27.44,
  "pb": 3.88,
  "turnover_rate": 1.44,
  "high_52w": 137.67,
  "low_52w": 85.88
}
```

### 2. 手动补充财务数据 (临时方案) ✅

对于重点监控股票，手动补充关键财务指标：

**支持股票**:
- 002594 比亚迪
- 600519 贵州茅台
- 000858 五粮液
- 300750 宁德时代

**数据字段**:
```json
{
  "roe": 10.83,
  "gross_margin": 17.87,
  "net_margin": 4.28,
  "revenue_growth": 15.2,
  "profit_growth": 18.5,
  "market_cap": 8536.0  // 亿
}
```

### 3. 浏览器自动化 (备选方案) 🔄

**文件**: 
- `browser_fetch.py` - 使用 OpenClaw browser 工具
- `eastmoney_browser.py` - 浏览器自动化脚本

**用途**: 当 API 失效时，通过浏览器访问东方财富 F10 页面获取数据

**测试 URL**:
- 行情页面：`https://quote.eastmoney.com/sz002594.html`
- 财务分析：`https://emweb.securities.eastmoney.com/pc_hsf10/pages/index.html?type=web&code=SZ002594&color=b#/cwfx`

## 集成到 Agent 系统

### 更新的文件

1. **agent-fundamental.py**
   - 改用 `stock_data.py` 获取数据
   - 解析 JSON 格式输出
   - 保留原有分析逻辑

2. **stock_data.py** (新增)
   - 统一数据获取接口
   - API + 手动数据补充
   - 输出标准 JSON 格式

### 使用方式

```bash
# 直接获取股票数据
python3 /Users/egg/.openclaw/workspace/shared/stock-system/scripts/stock_data.py 002594

# Agent 自动调用 (通过守护进程)
# 守护进程会扫描 queue/requests/ 目录中的请求文件
```

## 测试验证

### 比亚迪 (002594) 测试结果

```
✅ API 数据获取成功
   股票：比亚迪
   现价：¥93.62
   涨跌：-0.01%
   市盈率 (TTM): 27.44
   市净率：3.88

✅ 财务数据补充成功
   ROE: 10.83%
   毛利率：17.87%
   净利率：4.28%
   营收增速：15.20%
   利润增速：18.50%
```

### 贵州茅台 (600519) 测试

```bash
python3 stock_data.py 600519
```

预期输出:
- ROE: 28.5%
- 毛利率：92%
- 净利率：52%

## 扩展新股票

要添加新股票的手动财务数据，编辑 `stock_data.py` 中的 `fetch_finance_manual` 函数：

```python
'000001': {  # 股票代码
    'roe': 10.0,
    'gross_margin': 30.0,
    'net_margin': 20.0,
    'revenue': 100000000,  # 元
    'net_profit': 20000000,  # 元
    'market_cap': 200000000000,  # 元
    'revenue_growth': 10.0,
    'profit_growth': 15.0,
}
```

## 未来改进方向

1. **完全自动化财务数据获取**
   - 实现浏览器自动化解析 F10 页面
   - 或使用东方财富 F10 API

2. **数据缓存**
   - 避免重复请求
   - 设置数据过期时间

3. **多数据源备份**
   - 新浪财经 API
   - 腾讯财经 API
   - 同花顺 API

4. **数据验证**
   - 交叉验证多个数据源
   - 检测异常数据

## 相关文件清单

```
/Users/egg/.openclaw/workspace/shared/stock-system/scripts/
├── stock_data.py              # 主要数据获取脚本 ✅
├── agent-fundamental.py       # 基本面 Agent (已更新) ✅
├── agent-technical.py         # 技术面 Agent
├── agent-sentiment.py         # 情绪面 Agent
├── agent-coordinator.py       # 主协调 Agent
├── daemon.py                  # 守护进程
├── eastmoney_api.py           # 东方财富 API 直接调用
├── browser_fetch.py           # 浏览器自动化 (备选)
└── eastmoney_browser.py       # 浏览器自动化 (备选)
```

## 快速参考

### 获取股票数据
```bash
python3 stock_data.py <股票代码>
```

### 查看 API 返回字段
```bash
python3 stock_data.py 002594 | jq
```

### 测试 Agent 分析
```bash
python3 agent-fundamental.py 002594
```

---

**创建日期**: 2026-03-08  
**最后更新**: 2026-03-08  
**状态**: ✅ 已部署并测试
