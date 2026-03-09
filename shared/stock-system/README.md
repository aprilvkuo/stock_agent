# 📊 股票多 Agent 系统 - 快速入门

欢迎使用股票多 Agent 系统！这是一个会自我进化的智能股票分析系统。

---

## 🚀 快速启动

### 方式 1: 使用启动脚本 (推荐)

```bash
cd /Users/egg/.openclaw/workspace/shared/stock-system
./start.sh
```

然后选择选项 `1)` 启动所有服务。

### 方式 2: 手动启动

**启动守护进程**:
```bash
cd /Users/egg/.openclaw/workspace/shared/stock-system/scripts
nohup python3 daemon.py > /tmp/stock-daemon.log 2>&1 &
```

**启动 Web 服务器**:
```bash
cd /Users/egg/.openclaw/workspace/shared/stock-system/web
nohup python3 app.py > /tmp/stock-web.log 2>&1 &
```

---

## 🌐 访问系统

服务启动后，访问以下网址：

- **监控首页**: http://localhost:5001
- **进化报告**: http://localhost:5001/evolution
- **Agent 状态**: http://localhost:5001/agents
- **个股报告**: http://localhost:5001/report/600519 (示例)

---

## 📖 重要文档

### 必读文档
1. **[PROJECT-SNAPSHOT.md](./PROJECT-SNAPSHOT.md)** ⭐
   - 完整的项目快照
   - 当前进展和待办事项
   - 下次启动前请先阅读

2. **[SELF-EVOLUTION-GUIDE.md](./SELF-EVOLUTION-GUIDE.md)**
   - 自我进化系统使用指南
   - 了解系统如何自主学习

3. **[FRONTEND-OPTIMIZATION.md](./FRONTEND-OPTIMIZATION.md)**
   - 前端优化总结
   - 了解界面功能

### 技术文档
- **[SOLUTION.md](./SOLUTION.md)** - 数据获取解决方案
- **[EVOLUTION-INTEGRATION.md](./EVOLUTION-INTEGRATION.md)** - 进化报告集成

---

## 💡 常用操作

### 添加新股票
在请求队列目录创建请求文件：
```bash
cat > /Users/egg/.openclaw/workspace/agents/stock-coordinator/data/queue/requests/request-20260308120000.md << EOF
# 分析请求 request-20260308120000

## 请求信息
- 请求 ID: request-20260308120000
- 请求时间：2026-03-08 12:00:00
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

守护进程会自动检测并处理新请求。

### 手动触发进化
```bash
cd /Users/egg/.openclaw/workspace/shared/stock-system/scripts
python3 self-evolution.py
```

### 查看日志
```bash
# 守护进程日志
tail -f /Users/egg/.openclaw/workspace/agents/stock-coordinator/data/logs/daemon-2026-03-08.log

# Web 服务器日志
tail -f /tmp/stock-web.log
```

### 检查进程
```bash
# 查看守护进程
pgrep -f "daemon.py"

# 查看 Web 服务器
pgrep -f "app.py"
```

---

## 📊 当前监控股票

### A 股 (4 只)
- 600519 贵州茅台
- 000858 五粮液
- 300750 宁德时代
- 002594 比亚迪

### 港股 (2 只)
- 00700 腾讯控股
- 09988 阿里巴巴

### 待确认 (1 只)
- 范式智能 (需要股票代码)

---

## 🔧 故障排查

### 问题 1: 服务无法启动
**检查端口是否被占用**:
```bash
lsof -i :5001
```

**解决**: 停止占用端口的进程或修改 `app.py` 中的端口号

### 问题 2: API 获取数据失败
**现象**: 日志显示 "Remote end closed connection"

**解决**: 
- 等待 60 秒后重试 (API 限流)
- 检查网络连接
- 使用手动数据补充

### 问题 3: 网页无法访问
**检查**: 
```bash
# 确认 Web 服务器运行
pgrep -f "app.py"

# 查看 Web 日志
tail /tmp/stock-web.log
```

### 问题 4: 守护进程不处理请求
**检查**:
```bash
# 查看守护进程日志
tail -20 /Users/egg/.openclaw/workspace/agents/stock-coordinator/data/logs/daemon-2026-03-08.log

# 确认请求文件格式
cat /Users/egg/.openclaw/workspace/agents/stock-coordinator/data/queue/requests/request-*.md
```

---

## 📁 重要目录

```
/Users/egg/.openclaw/workspace/
├── agents/stock-coordinator/data/
│   ├── queue/requests/          # 分析请求队列
│   ├── queue/results/           # 分析结果
│   ├── logs/                    # 日志文件
│   ├── knowledge/               # 知识库
│   └── evolution-*.md           # 进化报告
│
└── shared/stock-system/
    ├── scripts/                 # 脚本文件
    ├── web/                     # Web 服务器
    └── *.md                     # 文档
```

---

## 🎯 系统特性

1. **多 Agent 协作** - 基本面/技术面/情绪面三个 Agent 分工合作
2. **自我进化** - 空闲时自动学习、复盘、改进
3. **实时监控** - 完整的监控报表系统
4. **持续改进** - 定期复盘和知识库更新
5. **文档完善** - 详细的使用和技术文档

---

## 📞 获取帮助

### 查看项目快照
```bash
cat /Users/egg/.openclaw/workspace/shared/stock-system/PROJECT-SNAPSHOT.md
```

### 查看进化报告
访问 http://localhost:5001/evolution

### 查看知识库
```bash
cat /Users/egg/.openclaw/workspace/agents/stock-coordinator/data/knowledge/stock-wisdom.md
```

---

## 🎉 开始使用

1. 运行 `./start.sh` 启动服务
2. 访问 http://localhost:5001 查看系统状态
3. 添加新股票到请求队列
4. 等待系统自动处理
5. 查看分析结果和进化报告

**祝你使用愉快！** 🚀

---

**最后更新**: 2026-03-08  
**版本**: v2.0  
**状态**: ✅ 运行良好
