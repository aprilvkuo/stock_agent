# 📋 股票多 Agent 系统 - 优化 TODO 清单

**创建日期**: 2026-03-08  
**最后更新**: 2026-03-08 01:02

---

## 🔴 高优先级（本周完成）

### ✅ 1. 守护进程开机自启

**状态**: 🟡 进行中  
**文件**: `com.stock-system.daemon.plist`

```bash
# 安装 launchd 配置
cp com.stock-system.daemon.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.stock-system.daemon.plist

# 验证
launchctl list | grep stock-system

# 卸载（如需要）
launchctl unload ~/Library/LaunchAgents/com.stock-system.daemon.plist
```

---

### ✅ 2. 错误通知机制

**状态**: 🟡 进行中  
**文件**: `notifier.py`

**集成到 daemon.py**:
```python
from notifier import notify_agent_failure, notify_agent_recovery

# 在 Agent 执行失败时调用
if not success:
    notify_agent_failure(agent_name, error_msg)
```

**测试**:
```bash
python3 notifier.py
```

---

### ⏳ 3. Agent 执行日志

**状态**: ⏳ 待开始

**任务**:
- [ ] 修改每个 Agent 脚本写入独立日志
- [ ] 日志格式：`[时间] [Agent 名] [级别] 消息`
- [ ] 日志文件：`logs/agent-fundamental-2026-03-08.log`

---

### ⏳ 4. 验证自动化

**状态**: ⏳ 待开始

**任务**:
- [ ] 配置每日 09:00 自动验证
- [ ] 添加 cron 任务或 launchd 配置
- [ ] 验证后发送摘要通知

---

## 🟡 中优先级（本月完成）

### ⏳ 5. 监控网站 WebSocket 实时推送

**当前**: 30 秒轮询  
**目标**: WebSocket 实时推送

**收益**:
- 更流畅的实时体验
- 减少服务器压力
- 即时显示 Agent 状态变化

---

### ⏳ 6. 股价数据缓存

**当前**: 每次调用 API  
**目标**: 缓存 5 分钟

**实现**:
```python
import pickle
from datetime import datetime, timedelta

CACHE = {}
CACHE_FILE = 'data/price_cache.pkl'

def get_price_cached(stock_code):
    now = datetime.now()
    
    # 检查缓存
    if stock_code in CACHE:
        cached_time, price = CACHE[stock_code]
        if now - cached_time < timedelta(minutes=5):
            return price
    
    # 调用 API 获取
    price = fetch_price_from_api(stock_code)
    
    # 更新缓存
    CACHE[stock_code] = (now, price)
    save_cache()
    
    return price
```

---

### ⏳ 7. 备份自动清理

**当前**: 无限累积  
**目标**: 自动删除 30 天前备份

**实现**:
```python
def cleanup_old_backups(days=30):
    cutoff = datetime.now() - timedelta(days=days)
    for f in os.listdir(BACKUP_DIR):
        filepath = os.path.join(BACKUP_DIR, f)
        mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
        if mtime < cutoff:
            os.remove(filepath)
            log(f"清理旧备份：{f}")
```

---

### ⏳ 8. Agent 表现统计图表

**当前**: 基础统计  
**目标**: 可视化图表

**功能**:
- 准确率趋势图
- 各 Agent 对比
- 月度/周度统计

**技术**: Chart.js 或 ECharts

---

### ⏳ 9. 配置文件集中管理

**当前**: 硬编码路径  
**目标**: config.yaml

**示例**:
```yaml
paths:
  workspace: /Users/egg/.openclaw/workspace
  data: agents/stock-coordinator/data
  scripts: shared/stock-system/scripts

intervals:
  check_requests: 60      # 秒
  coordinator: 300        # 秒
  validation: 86400       # 天
  cleanup: 2592000        # 30 天

notification:
  enabled: true
  agent_failure: true
  daily_summary: true
```

---

## 🟢 低优先级（有空再做）

### ⏳ 10. 周报自动生成

**功能**:
- 每周分析股票数量
- 预测准确率统计
- 最佳/最差预测
- Agent 表现排名

**发送**: 每周五 20:00

---

### ⏳ 11. 导出功能

**格式**:
- Excel (.xlsx)
- CSV
- PDF 报告

**内容**:
- 分析历史
- 验证记录
- 统计数据

---

### ⏳ 12. 多股票对比分析

**功能**:
- 选择 2-5 只股票
- 并排对比各项指标
- 雷达图可视化

---

### ⏳ 13. 移动端优化

**当前**: 基础响应式  
**目标**: 完美移动端体验

**优化**:
- 触摸友好的表格
- 移动端导航
- PWA 支持

---

### ⏳ 14. 历史回测

**功能**:
- 回测历史预测
- 计算理论收益
- 优化策略参数

---

## 📊 进度追踪

| 优先级 | 总数 | 已完成 | 进行中 | 待开始 | 完成率 |
|--------|------|--------|--------|--------|--------|
| 🔴 高 | 4 | 0 | 2 | 2 | 0% |
| 🟡 中 | 5 | 0 | 0 | 5 | 0% |
| 🟢 低 | 5 | 0 | 0 | 5 | 0% |
| **总计** | **14** | **0** | **2** | **12** | **0%** |

---

## 🎯 下一步行动

1. **立即**: 安装 launchd 配置（开机自启）
2. **今天**: 集成错误通知到 daemon.py
3. **本周**: 完成 Agent 独立日志
4. **下周**: 配置验证自动化

---

## 💡 贡献想法

有新的优化想法？添加到对应优先级的待开始列表中！
