# 🤖 Issue 自动化处理系统 - 正式文档

**版本**: v2.0  
**实施日期**: 2026-03-09  
**维护者**: 程序员 Agent  
**状态**: ✅ 生产就绪

---

## 📋 系统概述

Issue 自动化处理系统实现从 GitHub 自动抓取 Issue、验证有效性、分配给对应 Agent、自动修复、创建 PR 的完整流程。

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
1. 📋 自动抓取 Issue
   ↓
2. 🔍 验证有效性
   ├─ ❌ 无效 → 自动关闭
   └─ ✅ 有效 → 继续
   ↓
3. 🤖 识别负责 Agent
   ↓
4. 🌿 创建分支
   ↓
5. 🔧 Agent 执行修复
   ↓
6. 💾 Git 提交
   ↓
7. 📤 推送分支
   ↓
8. 🔀 创建 PR
   ↓
9. 👁️ 人工 Review
   ↓
10. ✅ Merge → 自动关闭 Issue
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

# 1. 预览模式（Dry Run）
python3 scripts/auto_issue_resolver.py --dry-run

# 2. 自动处理所有 Issue
python3 scripts/auto_issue_resolver.py

# 3. 处理指定 Issue
python3 scripts/auto_issue_resolver.py --issue 2

# 4. 按标签过滤
python3 scripts/auto_issue_resolver.py --labels improvement-ticket
```

### 命令行参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--dry-run` | 仅显示，不执行 | `--dry-run` |
| `--issue <N>` | 处理指定 Issue | `--issue 2` |
| `--labels <L>` | 过滤标签 | `--labels improvement-ticket` |
| `--help` | 显示帮助 | `--help` |

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

### 2. Agent 识别器

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

### 3. 自动修复执行器

**当前实现**:

```python
def execute_fix(self, issue, agent_id):
    if agent_id == "programmer":
        return self._programmer_fix(issue)
    elif agent_id == "data-fetcher":
        return self._data_fetcher_fix(issue)
    # ... 其他 Agent
```

**扩展方法**: 添加新的 Agent 修复逻辑
```python
def _programmer_fix(self, issue):
    # 实现程序员的自动修复逻辑
    pass
```

---

## 📊 工作流程详解

### Step 1: 抓取 Issue

```python
issues = self.get_open_issues(labels=["improvement-ticket"])
```

**API**: `GET /repos/{owner}/{repo}/issues?state=open`

### Step 2: 验证有效性

```python
is_valid, reason = self.validator.is_valid_issue(issue)
```

**判断逻辑**:
- 检查无效关键词
- 检查内容长度
- 检查创建时间
- 检查有效特征

### Step 3: 识别 Agent

```python
agent_id = self.identify_responsible_agent(issue)
```

**识别顺序**:
1. @mention 提取
2. 表格字段提取
3. 关键词匹配

### Step 4: 创建分支

```python
branch_name = f"fix/issue-{issue_number}-{safe_title}"
git checkout -b {branch_name}
```

**命名规范**: `fix/issue-{编号}-{描述}`

### Step 5: 执行修复

```python
fix_success = self.execute_fix(issue, agent_id)
```

**扩展点**: 实现不同 Agent 的修复逻辑

### Step 6-8: Git 操作

```python
git add -A
git commit -m "[{Agent}] 自动修复 Issue #{number}"
git push -u origin {branch_name}
```

### Step 9: 创建 PR

```python
pr_data = {
    "title": f"[Fix] 自动修复 Issue #{number}",
    "body": "...",
    "head": branch_name,
    "base": "main"
}
```

### Step 10: 添加评论

```python
comment = f"""
## 🤖 自动处理完成
**PR**: #{pr_number}
请 Review 后合并。
"""
```

---

## 🎯 最佳实践

### ✅ 推荐

1. **定期执行** - 每天执行一次
2. **Dry Run 先行** - 首次使用先预览
3. **人工 Review** - PR 必须人工审核
4. **逐个处理** - Issue 一个个解决
5. **记录日志** - 保存执行日志

### ❌ 避免

1. **过于频繁** - 避免 API 限流
2. **完全自动** - 保留人工审核
3. **批量 Merge** - 逐个 Review 合并
4. **忽略错误** - 处理异常情况

---

## 📝 配置管理

### 环境变量

```bash
# 必需
GITHUB_TOKEN=github_pat_xxx
GITHUB_REPO=aprilvkuo/stock_agent

# 可选
WORKSPACE=/Users/egg/.openclaw/workspace
```

### Agent 配置

```python
AGENT_GITHUB = {
    'fundamental': 'fundamental-agent',
    'programmer': 'programmer-agent',
    # ...
}
```

### 验证规则

```python
INVALID_KEYWORDS = ['spam', '广告', 'test', '测试']
VALID_PATTERNS = ['改进工单', 'optimization', 'bug']
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

---

## 📈 监控和日志

### 执行日志

```bash
# 查看执行结果
python3 scripts/auto_issue_resolver.py --dry-run

# 查看 Issue 状态
gh issue list --state open
```

### 统计信息

```
总计：4 个 Issue
关闭（无效）: 2
已修复：2
失败：0
```

---

## 🔄 扩展开发

### 添加新的 Agent

**1. 添加 Agent 映射**:
```python
AGENT_GITHUB['new_agent'] = 'new-agent'
```

**2. 添加关键词**:
```python
AGENT_KEYWORDS['new_agent'] = ['关键词 1', '关键词 2']
```

**3. 实现修复逻辑**:
```python
def _new_agent_fix(self, issue):
    # 实现修复逻辑
    pass
```

### 添加验证规则

```python
def is_valid_issue(self, issue):
    # 添加新的验证逻辑
    if new_condition:
        return False, "原因"
```

---

## 📖 相关文档

- [CONTRIBUTING.md](./CONTRIBUTING.md) - 贡献指南
- [BRANCH_NAMING.md](./BRANCH_NAMING.md) - 分支命名
- [CODE_REVIEW.md](./CODE_REVIEW.md) - Code Review 指南

---

## 🎯 版本历史

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
