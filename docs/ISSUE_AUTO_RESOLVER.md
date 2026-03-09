# 🤖 Issue 自动化处理系统 - 正式文档

**版本**: v3.0  
**实施日期**: 2026-03-09  
**维护者**: 程序员 Agent  
**状态**: ✅ 生产就绪

---

## 📋 系统概述

Issue 自动化处理系统实现从 GitHub 自动抓取 Issue、验证有效性、分配给对应 Agent、自动修复、创建 PR 的完整流程。

### v3.0 新特性

- ✅ **单线程处理** - 一次只处理一个 Issue，避免冲突
- ✅ **优先级排序** - 按优先级标签自动排序
- ✅ **PR 审核等待** - 等待 PR 合并后继续处理下一个
- ✅ **实时监控** - 持续监控新 Issue 和 PR 状态

### 核心特性

- ✅ 自动抓取 GitHub Issue
- ✅ 智能验证有效性（区分有效/无效任务）
- ✅ 自动识别负责 Agent
- ✅ 自动创建修复分支
- ✅ 自动提交代码
- ✅ 自动推送分支
- ✅ 自动创建 PR
- ✅ 自动关闭已解决的 Issue

### 处理流程

```
1. 📋 实时监控（每 60 秒检查一次）
   ↓
2. 🔍 检查是否有未解决的 PR
   ├─ 有 PR → ⏳ 等待合并
   └─ 无 PR → 继续
   ↓
3. 📊 获取 Issue 并按优先级排序
   ↓
4. 🎯 选择优先级最高的 Issue
   ↓
5. 🔍 验证有效性
   ├─ ❌ 无效 → 自动关闭
   └─ ✅ 有效 → 继续
   ↓
6. 🤖 识别负责 Agent
   ↓
7. 🌿 创建分支
   ↓
8. 🔧 Agent 执行修复
   ↓
9. 💾 Git 提交
   ↓
10. 📤 推送分支
    ↓
11. 🔀 创建 PR
    ↓
12. 👁️ 等待人工 Review
    ↓
13. ✅ Merge → 自动处理下一个 Issue
```

---

## 🚀 快速开始

### 环境配置

**1. 安装依赖**:
```bash
pip3 install requests python-dotenv
```

**2. 配置 Token**:

方式 A: 系统环境变量（推荐）
```bash
# ~/.zshrc
export GITHUB_TOKEN="github_pat_xxx"
export GITHUB_REPO="aprilvkuo/stock_agent"
```

方式 B: .env 文件
```bash
# .env
GITHUB_TOKEN=github_pat_xxx
GITHUB_REPO=aprilvkuo/stock_agent
```

**3. Token 权限要求**:

| 权限 | 访问级别 | 用途 |
|------|---------|------|
| `Issues` | Read and write | 创建/关闭 Issue，添加评论 |
| `Pull requests` | Read and write | 创建 PR |
| `Contents` | Read and write | 读取/写入代码 |
| `Metadata` | Read only | 读取元数据 |

---

## 📖 使用指南

### 基础用法

```bash
cd /Users/egg/.openclaw/workspace

# 1. 预览模式（Dry Run）- 查看优先级排序
python3 scripts/auto_issue_resolver.py --dry-run

# 2. 处理单个 Issue（处理完停止）
python3 scripts/auto_issue_resolver.py

# 3. 实时监控模式（持续运行）
python3 scripts/auto_issue_resolver.py --monitor

# 4. 自定义监控间隔（每 30 秒检查一次）
python3 scripts/auto_issue_resolver.py --monitor --interval 30

# 5. 处理指定 Issue
python3 scripts/auto_issue_resolver.py --issue 2

# 6. 按标签过滤
python3 scripts/auto_issue_resolver.py --labels improvement-ticket
```

### 命令行参数

| 参数 | 说明 | 示例 | 默认值 |
|------|------|------|--------|
| `--dry-run` | 仅显示，不执行 | `--dry-run` | - |
| `--issue <N>` | 处理指定 Issue | `--issue 2` | - |
| `--labels <L>` | 过滤标签 | `--labels improvement-ticket` | - |
| `--monitor` | 启动实时监控 | `--monitor` | - |
| `--interval <S>` | 监控间隔（秒） | `--interval 30` | 60 |
| `--help` | 显示帮助 | `--help` | - |

---

## 🎯 单线程工作模式

### 核心原则

**一次只处理一个 Issue**，确保：
- ✅ 避免 Git 冲突
- ✅ 保证代码质量
- ✅ 便于问题追踪
- ✅ 降低系统复杂度

### 工作流程

```
开始
  ↓
检查是否有未解决的 PR？
  ├─ 是 → ⏳ 等待 PR 合并
  │        ↓
  │      PR 已合并？
  │        ├─ 是 → 继续
  │        └─ 否 → 继续等待
  │
  └─ 否 → 获取 Issue 列表
           ↓
         按优先级排序
           ↓
         选择优先级最高的 Issue
           ↓
         处理 Issue → 创建 PR
           ↓
         ⏳ 等待 PR 合并
           ↓
         PR 已合并？
           ├─ 是 → 处理下一个 Issue
           └─ 否 → 继续等待
```

### PR 等待机制

**等待超时**: 24 小时（可配置）

**等待行为**:
- 每分钟检查一次 PR 状态
- 显示等待进度
- PR 合并后自动继续
- PR 关闭或超时后暂停

---

## 📊 优先级排序

### 优先级标签

| 标签 | 优先级 | 说明 |
|------|--------|------|
| `critical` | 1 | 紧急 - 最优先处理 |
| `high` | 2 | 高优先级 |
| `medium` / `improvement-ticket` / `task` | 3 | 中优先级（默认） |
| `low` | 4 | 低优先级 |

### 排序规则

1. **优先级标签** - 数字越小越优先
2. **创建时间** - 同优先级下，创建越早越优先

### 示例

```bash
# Dry Run 模式查看优先级排序
python3 scripts/auto_issue_resolver.py --dry-run

# 输出:
📊 Issue 优先级排序:
   1. #15 [critical] 修复严重 Bug
   2. #12 [high] 优化性能
   3. #10 [medium] 改进文档
   4. #8 [medium] 添加功能
   5. #5 [low] 代码清理
```

---

## 🔧 核心组件

### 1. Issue 验证器 (IssueValidator)

**位置**: `scripts/auto_issue_resolver.py`

**功能**: 验证 Issue 是否为有效任务

**验证规则**:

**无效任务特征**:
- ❌ 包含无效关键词：`test`, `测试`, `spam`, `广告`, `demo`
- ❌ 内容过短（<10 字符）
- ❌ 超过 90 天未处理
- ❌ 无法识别为有效任务

**有效任务特征**:
- ✅ 有 `improvement-ticket` 标签
- ✅ 包含有效关键词：`改进`, `优化`, `bug`, `fix`, `添加`
- ✅ 明确 @mention 指定 Agent

### 2. 优先级排序器

**位置**: `scripts/auto_issue_resolver.py`

**功能**: 按优先级排序 Issue

```python
def get_priority(self, issue: dict) -> int:
    labels = [l["name"].lower() for l in issue.get("labels", [])]
    
    for label, priority in PRIORITY_LABELS.items():
        if label in labels:
            return priority
    
    return 3  # 默认中优先级
```

### 3. Agent 识别器

**职责映射**:

```python
AGENT_KEYWORDS = {
    'programmer': ['代码', '重构', '优化', 'bug', 'fix', 'dev', 'structure'],
    'fundamental': ['财报', '估值', '基本面', 'financial'],
    'technical': ['k 线', '技术指标', '技术面', 'macd', 'rsi'],
    'sentiment': ['情绪', '市场', 'sentiment', '热度'],
    'data-fetcher': ['数据', 'api', '抓取', 'data'],
    'qa': ['测试', '质量', 'review', 'qa'],
    'coordinator': ['协调', '分配', 'coordinator'],
    'cio': ['投资', '策略', 'risk']
}
```

**识别优先级**:
1. 从 @mention 提取（如 @programmer-agent）
2. 从表格字段提取（负责方）
3. 关键词匹配

### 4. PR 等待器

**功能**: 等待 PR 合并后继续

```python
def wait_for_pr_merge(self, pr_number: int, timeout_hours: int = 24) -> bool:
    """等待 PR 被合并"""
    start_time = datetime.now()
    timeout = timedelta(hours=timeout_hours)
    
    while True:
        # 检查超时
        elapsed = datetime.now() - start_time
        if elapsed > timeout:
            return False  # 超时
        
        # 检查 PR 状态
        pr_status = self.check_pr_status(pr_number)
        
        if pr_status['merged']:
            return True  # 已合并
        
        if pr_status['state'] == 'closed':
            return False  # 已关闭
        
        # 等待 1 分钟
        time.sleep(60)
```

---

## 📖 实时监控模式

### 启动监控

```bash
# 基础监控（60 秒间隔）
python3 scripts/auto_issue_resolver.py --monitor

# 快速监控（30 秒间隔）
python3 scripts/auto_issue_resolver.py --monitor --interval 30

# 慢速监控（5 分钟间隔）
python3 scripts/auto_issue_resolver.py --monitor --interval 300
```

### 监控行为

**每次循环**:
1. 检查未解决的 PR
2. 如果有 PR，等待合并
3. 如果没有 PR，处理下一个 Issue
4. 等待指定间隔后继续

**停止条件**:
- 用户按 Ctrl+C
- 达到最大重试次数（3 次）
- 发生严重错误

### 监控日志

```
🚀 Issue 自动化处理系统 v3.0（单线程实时监控版）
============================================================

📊 配置信息:
   监控间隔：60 秒
   最大重试：3 次
   仓库：aprilvkuo/stock_agent

📋 工作模式:
   ✅ 单线程 - 一次只处理一个 Issue
   ✅ 优先级排序 - 按优先级选择 Issue
   ✅ PR 等待 - 等待 PR 合并后继续
   ✅ 实时监控 - 持续监控新 Issue

按 Ctrl+C 停止监控

============================================================
处理 Issue #15: 修复严重 Bug
============================================================
...
```

---

## 🎯 最佳实践

### ✅ 推荐

1. **使用实时监控** - 保持系统持续运行
2. **合理设置间隔** - 60-300 秒为宜
3. **设置优先级标签** - 确保重要 Issue 优先处理
4. **及时 Review PR** - 避免阻塞后续 Issue
5. **监控日志** - 定期检查执行日志

### ❌ 避免

1. **间隔过短** - <30 秒可能导致 API 限流
2. **间隔过长** - >300 秒可能错过紧急 Issue
3. **批量处理** - 违反单线程原则
4. **跳过 Review** - 降低代码质量

---

## 📊 配置管理

### 环境变量

```bash
# 必需
GITHUB_TOKEN=github_pat_xxx
GITHUB_REPO=aprilvkuo/stock_agent

# 可选
WORKSPACE=/Users/egg/.openclaw/workspace
```

### 监控配置

```python
# 脚本内配置
MONITOR_INTERVAL = 60  # 监控间隔（秒）
MAX_RETRY = 3  # 最大重试次数
```

### 优先级配置

```python
PRIORITY_LABELS = {
    'critical': 1,      # 紧急
    'high': 2,          # 高
    'medium': 3,        # 中
    'low': 4,           # 低
    'improvement-ticket': 3,
    'task': 3,
}
```

---

## 🔍 故障排查

### 问题 1: 403 权限不足

**症状**:
```
403 Client Error: Forbidden
```

**解决**:
- 检查 Token 权限
- 添加 `issues:write`, `pull_requests:write`, `contents:write`

### 问题 2: 422 验证失败

**症状**:
```
422 Validation Failed: No commits between main and branch
```

**解决**:
- 确保分支有实际提交
- 分支基于最新 main

### 问题 3: 无法识别 Agent

**症状**:
```
未匹配到具体 Agent，默认：coordinator
```

**解决**:
- 在 Issue 中明确 @mention
- 添加 `improvement-ticket` 标签
- 丰富 Issue 描述

### 问题 4: PR 等待超时

**症状**:
```
❌ 等待超时（24.0 小时）
```

**解决**:
- 及时 Review 和合并 PR
- 检查 PR 是否有冲突
- 联系 Reviewer 加快审核

---

## 📈 监控和日志

### 执行日志

```bash
# 查看当前 Issue 状态
gh issue list --state open

# 查看当前 PR 状态
gh pr list --state open

# 查看监控日志（后台运行时）
tail -f /var/log/issue_resolver.log
```

### 后台运行

```bash
# 使用 nohup 后台运行
nohup python3 scripts/auto_issue_resolver.py --monitor > issue_resolver.log 2>&1 &

# 查看进程
ps aux | grep auto_issue_resolver

# 停止进程
kill $(ps aux | grep auto_issue_resolver | grep -v grep | awk '{print $2}')
```

### 统计信息

```
总计：4 个 Issue
关闭（无效）: 2
已修复：2
等待 PR: 1
失败：0
```

---

## 🔄 扩展开发

### 添加新的优先级

```python
PRIORITY_LABELS['urgent'] = 0  # 最高优先级
```

### 添加新的 Agent

```python
AGENT_GITHUB['new_agent'] = 'new-agent'
AGENT_KEYWORDS['new_agent'] = ['关键词 1', '关键词 2']
```

### 自定义等待超时

```python
def wait_for_pr_merge(self, pr_number: int, timeout_hours: int = 12) -> bool:
    # 修改默认超时时间
```

---

## 📖 相关文档

- [CONTRIBUTING.md](./CONTRIBUTING.md) - 贡献指南
- [BRANCH_NAMING.md](./BRANCH_NAMING.md) - 分支命名
- [CODE_REVIEW.md](./CODE_REVIEW.md) - Code Review 指南
- [PROJECT_OWNERS.md](./PROJECT_OWNERS.md) - 项目归属人

---

## 🎯 版本历史

### v3.0 (2026-03-09)

- ✅ 单线程处理 - 一次只处理一个 Issue
- ✅ 优先级排序 - 按优先级标签自动排序
- ✅ PR 审核等待 - 等待 PR 合并后继续
- ✅ 实时监控 - 持续监控新 Issue 和 PR 状态
- ✅ 可配置监控间隔
- ✅ 改进错误处理

### v2.0 (2026-03-09)

- ✅ 添加 Issue 验证器
- ✅ 自动区分有效/无效任务
- ✅ 自动关闭无效 Issue
- ✅ 自动创建 PR
- ✅ 完整自动化流程

### v1.0 (2026-03-09)

- ✅ 基础 Issue 处理
- ✅ Agent 识别
- ✅ 分支创建

---

**维护者**: 程序员 Agent  
**最后更新**: 2026-03-09  
**状态**: ✅ 生产就绪
