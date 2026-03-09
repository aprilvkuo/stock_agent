# 🚀 股票多 Agent 系统 - 快速启动指南

## ✅ 问题已解决

**原因**：之前没有运行守护进程，Agent 脚本不会自动执行

**解决**：创建了 `daemon.py` 持续监控请求队列

---

## 📊 启动系统

### 方式 1: 使用启动脚本（推荐）

```bash
cd /Users/egg/.openclaw/workspace/shared/stock-system/scripts
./start.sh
```

### 方式 2: 直接运行守护进程

```bash
cd /Users/egg/.openclaw/workspace/shared/stock-system/scripts
python3 daemon.py
```

### 方式 3: 后台运行

```bash
nohup python3 daemon.py > /Users/egg/.openclaw/workspace/agents/stock-coordinator/data/logs/daemon.log 2>&1 &
```

---

## 🛑 停止系统

```bash
cd /Users/egg/.openclaw/workspace/shared/stock-system/scripts
./stop.sh
```

---

## 🌐 监控地址

| 页面 | 地址 | 说明 |
|------|------|------|
| 首页 | http://localhost:5001 | 分析结果 + 验证队列 |
| Agent 监控 | http://localhost:5001/agents | **实时查看 Agent 状态** |

---

## 📝 日志文件

```
/Users/egg/.openclaw/workspace/agents/stock-coordinator/data/logs/
├── daemon.log              # 守护进程日志
├── daemon-2026-03-08.log   # 按日期分类的日志
└── agent-*.md              # Agent 执行日志
```

### 查看实时日志

```bash
tail -f /Users/egg/.openclaw/workspace/agents/stock-coordinator/data/logs/daemon-$(date +%Y-%m-%d).log
```

---

## 🔄 工作原理

```
1. 创建请求文件
   ↓
2. 守护进程检测到新请求（每 60 秒）
   ↓
3. 依次调用 3 个 Agent：
   - 基本面 Agent
   - 技术面 Agent
   - 情绪 Agent
   ↓
4. 主 Agent 汇总结果（每 300 秒）
   ↓
5. 写入验证队列
```

---

## ✅ 创建新分析请求

### 方式 1: 在 webchat 中告诉我

```
"分析 600519"
"分析贵州茅台"
"分析宁德时代"
```

### 方式 2: 手动创建请求文件

```bash
cat > /Users/egg/.openclaw/workspace/agents/stock-coordinator/data/queue/requests/request-$(date +%Y%m%d%H%M%S).md << EOF
# 分析请求 request-xxx

## 请求信息
- 请求 ID: request-xxx
- 请求时间：$(date '+%Y-%m-%d %H:%M:%S')
- 股票代码：600519
- 股票名称：贵州茅台

## 任务
- [ ] 基本面 Agent: 分析财报、估值、财务健康
- [ ] 技术面 Agent: 分析 K 线、技术指标
- [ ] 情绪 Agent: 分析舆情、市场热度

## 状态
- 基本面：⏳ 待处理
- 技术面：⏳ 待处理
- 情绪面：⏳ 待处理
- 汇总：⏳ 待处理
EOF
```

---

## 🔍 检查系统状态

### 1. 检查守护进程

```bash
ps aux | grep daemon.py
```

### 2. 查看 Agent 状态

访问 http://localhost:5001/agents

- 🟢 绿色 = 运行中（10 分钟内有活动）
- 🟡 黄色 = 空闲
- 🔴 红色 = 离线

### 3. 查看日志

```bash
cat /Users/egg/.openclaw/workspace/agents/stock-coordinator/data/logs/daemon-$(date +%Y-%m-%d).log
```

---

## ⚙️ 配置选项

编辑 `daemon.py` 可调整：

```python
check_interval = 60      # 检查请求间隔（秒）
coordinator_interval = 300  # 汇总间隔（秒）
```

---

## 🎯 现在 Agent 正在工作！

访问 http://localhost:5001/agents 查看实时状态！

日志显示：
```
[SUCCESS] fundamental Agent 完成：600519 贵州茅台
[SUCCESS] technical Agent 完成：600519 贵州茅台
[SUCCESS] sentiment Agent 完成：600519 贵州茅台
```

**Agent 没有罢工，只是在正常工作！** 🟢
