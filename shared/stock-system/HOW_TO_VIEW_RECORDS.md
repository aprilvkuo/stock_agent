# 📊 查看记录 - 快速指南

## 🎯 快速查看命令

### 1. 查看最新分析结果

```bash
# 查看结果列表
ls -lt /Users/egg/.openclaw/workspace/agents/stock-coordinator/data/queue/results/

# 查看具体内容
cat /Users/egg/.openclaw/workspace/agents/stock-coordinator/data/queue/results/result-*-fundamental.md
```

### 2. 查看请求状态

```bash
# 查看请求列表
ls -lt /Users/egg/.openclaw/workspace/agents/stock-coordinator/data/queue/requests/

# 查看具体请求
cat /Users/egg/.openclaw/workspace/agents/stock-coordinator/data/queue/requests/request-*.md
```

### 3. 查看验证队列

```bash
cat /Users/egg/.openclaw/workspace/agents/stock-coordinator/data/validation-queue.md
```

### 4. 查看备份

```bash
# 查看备份列表
ls -lt /Users/egg/.openclaw/workspace/agents/stock-coordinator/data/backups/

# 恢复备份
cp /Users/egg/.openclaw/workspace/agents/stock-coordinator/data/backups/validation_backup_*.md \
   /Users/egg/.openclaw/workspace/agents/stock-coordinator/data/validation-queue.md
```

---

## 🖥️ 交互式查看工具

### 运行查看脚本

```bash
cd /Users/egg/.openclaw/workspace/agents/stock-coordinator/data/scripts
python3 view-records.py
```

**菜单选项**:
```
1. 最新分析结果      - 查看最新的 Agent 分析
2. 所有分析结果列表  - 查看所有分析记录
3. 请求处理状态      - 查看请求处理进度
4. 验证队列          - 查看待验证预测
5. 备份记录          - 查看备份历史
6. 系统状态          - 查看系统整体状态
0. 退出
```

---

## 📋 记录说明

### 分析结果文件

```
result-YYYYMMDDHHMMSS-fundamental.md  ← 基本面分析
result-YYYYMMDDHHMMSS-technical.md    ← 技术面分析
result-YYYYMMDDHHMMSS-sentiment.md    ← 情绪分析
```

**内容包含**:
- 请求 ID
- Agent 信息
- 分析时间
- 股票信息
- 评级和置信度
- 关键依据
- 风险点
- 详细数据

### 请求文件

```
request-YYYYMMDDHHMMSS.md
```

**内容包含**:
- 请求信息
- 股票代码和名称
- 各 Agent 处理状态
- 汇总结果

### 验证队列

```
validation-queue.md
```

**内容包含**:
- 预测内容
- 验证日期
- 验证状态 (⏳待验证 / ✅正确 / ❌错误)
- 实际结果
- 偏差分析

---

## 🔍 按股票查询

### 查询某只股票的所有分析

```bash
# 例如查询贵州茅台 (600519)
grep -l "600519" /Users/egg/.openclaw/workspace/agents/stock-coordinator/data/queue/requests/*.md
grep -l "600519" /Users/egg/.openclaw/workspace/agents/stock-coordinator/data/queue/results/*.md
```

### 查询某只股票的验证记录

```bash
grep "600519" /Users/egg/.openclaw/workspace/agents/stock-coordinator/data/validation-queue.md
```

---

## 📊 统计分析

### 统计已完成分析数量

```bash
ls /Users/egg/.openclaw/workspace/agents/stock-coordinator/data/queue/results/*.md | wc -l
```

### 统计待验证预测数量

```bash
grep "⏳ 待验证" /Users/egg/.openclaw/workspace/agents/stock-coordinator/data/validation-queue.md | wc -l
```

### 统计验证准确率

```bash
# 正确数量
grep "✅ 正确" /Users/egg/.openclaw/workspace/agents/stock-coordinator/data/validation-queue.md | wc -l

# 错误数量
grep "❌ 错误" /Users/egg/.openclaw/workspace/agents/stock-coordinator/data/validation-queue.md | wc -l
```

---

## 💡 常用场景

### 场景 1: 查看刚刚的分析结果

```bash
# 查看最新的基本面分析
cat $(ls -t /Users/egg/.openclaw/workspace/agents/stock-coordinator/data/queue/results/*-fundamental.md | head -1)
```

### 场景 2: 查看某只股票的完整分析

```bash
# 查看五粮液的所有分析
cat /Users/egg/.openclaw/workspace/agents/stock-coordinator/data/queue/results/*-000858-*.md
```

### 场景 3: 查看即将到期的验证

```bash
# 查看验证队列，找到最近到期的
cat /Users/egg/.openclaw/workspace/agents/stock-coordinator/data/validation-queue.md
```

### 场景 4: 检查系统运行状态

```bash
# 运行查看脚本
python3 /Users/egg/.openclaw/workspace/agents/stock-coordinator/data/scripts/view-records.py
```
选择选项 6 (系统状态)

---

## 📁 文件位置速查

| 记录类型 | 路径 |
|---------|------|
| **分析结果** | `agents/stock-coordinator/data/queue/results/` |
| **请求文件** | `agents/stock-coordinator/data/queue/requests/` |
| **验证队列** | `agents/stock-coordinator/data/validation-queue.md` |
| **备份** | `agents/stock-coordinator/data/backups/` |
| **查看脚本** | `agents/stock-coordinator/data/scripts/view-records.py` |

---

**快速查看，轻松管理！** 📊
