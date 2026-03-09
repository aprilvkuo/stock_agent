# 🎯 Agent 状态更新集成指南

**版本**: v1.0  
**创建日期**: 2026-03-09  
**功能**: 实时监控 Agent 工作状态、进度条、运行时长

---

## 🚀 快速开始

### 1. 启动 Web 监控服务

```bash
cd /Users/egg/.openclaw/workspace/memory/stock-system
./start_monitor.sh
```

**访问**: http://localhost:5001

---

## 📝 集成到现有 Agent 脚本

### 方法 1: 使用状态更新工具（推荐）

在您的 Agent 脚本中导入并调用：

```python
import sys
sys.path.insert(0, '/Users/egg/.openclaw/workspace/memory/stock-system/scripts')
from update_agent_status import update_agent_status

# 开始任务
update_agent_status(
    agent_id="fundamental",  # fundamental/technical/sentiment/risk/cio
    status="running",
    current_task="分析贵州茅台 (600519) 财报数据",
    progress=0
)

# 任务执行中...更新进度
update_agent_status(
    agent_id="fundamental",
    status="running",
    current_task="分析贵州茅台 (600519) 财报数据",
    progress=50
)

# 任务完成
update_agent_status(
    agent_id="fundamental",
    status="idle",
    current_task="分析完成",
    progress=100
)
```

### 方法 2: 直接调用 API

```python
import requests

def update_status(agent_id, status, task, progress):
    requests.post(
        "http://localhost:5001/api/update-agent",
        json={
            "agent_id": agent_id,
            "status": status,
            "current_task": task,
            "progress": progress
        },
        timeout=5
    )

# 使用
update_status("technical", "running", "分析 K 线图", 30)
```

---

## 📊 Agent ID 映射

| Agent | agent_id | 说明 |
|-------|----------|------|
| 基本面分析师 | `fundamental` | 财报/估值分析 |
| 技术面分析师 | `technical` | K 线/技术指标 |
| 情绪面分析师 | `sentiment` | 市场情绪分析 |
| 风险评估师 | `risk` | 风险评估 |
| 首席投资官 | `cio` | 汇总决策 |

---

## 🎯 状态说明

| 状态 | 说明 | 前端显示 |
|------|------|----------|
| `idle` | 空闲 | 灰色标签 |
| `running` | 运行中 | 绿色标签（带脉冲动画） |
| `completed` | 已完成 | 蓝色标签 |

---

## 📈 进度条最佳实践

```python
# 0% - 开始
update_agent_status("fundamental", "running", "获取财报数据", 0)

# 25% - 数据获取完成
update_agent_status("fundamental", "running", "分析利润表", 25)

# 50% - 分析完成一半
update_agent_status("fundamental", "running", "分析现金流量表", 50)

# 75% - 生成评级
update_agent_status("fundamental", "running", "生成投资评级", 75)

# 100% - 完成
update_agent_status("fundamental", "idle", "分析完成", 100)
```

---

## 🔧 在 auto_agent.py 中集成

### 示例：修改 `analyze_stock()` 函数

```python
# 在 auto_agent.py 中找到 analyze_stock() 函数

def analyze_stock(stock_code):
    # 导入状态更新工具
    from update_agent_status import update_agent_status
    
    try:
        # 开始分析
        update_agent_status(
            agent_id="fundamental",
            status="running",
            current_task=f"分析{stock_code}",
            progress=0
        )
        
        # 获取数据
        data = get_stock_data(stock_code)
        update_agent_status("fundamental", "running", f"分析{stock_code}", 25)
        
        # 基本面分析
        fundamental_result = fundamental_analysis(data)
        update_agent_status("fundamental", "running", f"分析{stock_code}", 50)
        
        # 技术面分析
        update_agent_status("technical", "running", f"分析{stock_code}K 线", 0)
        technical_result = technical_analysis(data)
        update_agent_status("technical", "running", f"分析{stock_code}K 线", 100)
        
        # 情绪分析
        update_agent_status("sentiment", "running", f"分析{stock_code}情绪", 0)
        sentiment_result = sentiment_analysis(data)
        update_agent_status("sentiment", "running", f"分析{stock_code}情绪", 100)
        
        # 风险评估
        update_agent_status("risk", "running", f"评估{stock_code}风险", 0)
        risk_result = risk_assessment(data)
        update_agent_status("risk", "running", f"评估{stock_code}风险", 100)
        
        # CIO 汇总
        update_agent_status("cio", "running", f"汇总决策{stock_code}", 0)
        final_decision = cio_decision(fundamental_result, technical_result, sentiment_result, risk_result)
        update_agent_status("cio", "running", f"汇总决策{stock_code}", 100)
        
        return final_decision
        
    except Exception as e:
        # 错误处理
        update_agent_status("fundamental", "idle", f"分析失败：{e}", 0)
        raise
```

---

## 🎨 前端界面功能

### 实时监控
- ✅ Agent 状态（空闲/运行中/已完成）
- ✅ 当前任务描述
- ✅ 进度条（0-100%）
- ✅ 运行时长（自动计算）
- ✅ 最后更新时间

### 系统统计
- ✅ 系统版本
- ✅ 总分析次数
- ✅ 今日分析次数
- ✅ 待验证预测数量

### TODO List
- ✅ 自动解析 TODO.md
- ✅ 按优先级分组（P0/P1/P2/P3）
- ✅ 颜色编码（红/橙/蓝/绿）
- ✅ 完成标记（✅）

### 最新日志
- ✅ 显示最新 20 条分析日志
- ✅ 自动滚动
- ✅ 时间戳

---

## 🔄 自动刷新

- **数据刷新**: 每 5 秒自动刷新
- **进度条动画**: 平滑过渡
- **状态动画**: 运行中状态带脉冲效果

---

## 📱 响应式设计

- ✅ 桌面端完美显示
- ✅ 平板端自适应
- ✅ 手机端优化布局

---

## 🛠️ 故障排查

### Q: 页面无法访问？
A: 检查 Web 服务是否启动：
```bash
lsof -i :5001
```

### Q: 状态不更新？
A: 检查 API 调用是否成功：
```bash
curl http://localhost:5001/api/agent-status
```

### Q: Flask 未安装？
A: 运行安装命令：
```bash
pip3 install flask requests
```

---

## 🎯 下一步优化

### 已实现 ✅
- [x] Agent 实时状态展示
- [x] 进度条
- [x] 运行时长
- [x] TODO List 自动解析
- [x] 最新日志展示
- [x] 系统统计

### 待开发 📋
- [ ] 历史趋势图
- [ ] Agent 效率统计
- [ ] 告警通知
- [ ] 导出报告
- [ ] 多语言支持

---

## 📞 API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 监控主页 |
| `/api/agent-status` | GET | 获取 Agent 状态 |
| `/api/update-agent` | POST | 更新 Agent 状态 |
| `/api/todo-list` | GET | 获取 TODO List |
| `/api/logs` | GET | 获取分析日志 |
| `/api/stats` | GET | 获取系统统计 |
| `/api/health` | GET | 健康检查 |

---

**最后更新**: 2026-03-09  
**维护者**: 小助理 🤖  
**状态**: ✅ 已完成
