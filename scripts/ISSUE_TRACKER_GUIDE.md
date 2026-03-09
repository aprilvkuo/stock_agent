# 📋 Issue 自动跟踪和分配流程

**版本**: v1.0  
**实施日期**: 2026-03-09  
**脚本**: `scripts/issue_tracker.py`

---

## 🎯 功能概述

自动化的 Issue 处理流程：

```
获取未解决 Issue → 识别负责 Agent → 通知 Agent → 跟踪 PR → 自动合并
```

---

## 🚀 使用方法

### 基础用法

```bash
cd /Users/egg/.openclaw/workspace

# 查看所有未解决的改进工单
python3 scripts/issue_tracker.py

# Dry run 模式（仅显示，不执行）
python3 scripts/issue_tracker.py --dry-run

# 自动合并满足条件的 PR
python3 scripts/issue_tracker.py --auto-merge
```

### 输出示例

```
============================================================
🚀 Issue 自动跟踪和分配
============================================================

📋 获取到 3 个未解决的 Issue

============================================================
处理 Issue #2: [HIGH] @programmer-agent 待优化：code_structure
============================================================

  匹配到负责 Agent: programmer (关键词：代码开发)

🔔 通知 programmer-agent:
   Issue: #2
   标题：[HIGH] @programmer-agent 待优化：code_structure
   链接：https://github.com/aprilvkuo/stock_agent/issues/2
   ✅ 评论已添加

🔀 关联 PR 状态:
   PR: #5
   状态：open
   链接：https://github.com/aprilvkuo/stock_agent/pull/5
   正在合并 PR...
   ✅ PR 已合并

============================================================
✅ Issue 处理完成！
============================================================
```

---

## 📋 完整流程

### Step 1: 获取未解决 Issue

```python
tracker = IssueTracker()
issues = tracker.get_open_issues(labels=["improvement-ticket"])
```

**过滤条件**:
- 状态：open
- 标签：improvement-ticket（可选）

---

### Step 2: 识别负责 Agent

**识别逻辑**:

1. **从 Issue 内容提取**
   ```markdown
   | 负责方 | @programmer-agent |
   ```

2. **从标题提取**
   ```
   [HIGH] @programmer-agent 待优化：code_structure
   ```

3. **关键词匹配**
   ```python
   AGENT_RESPONSIBILITIES = {
       'programmer': ['代码开发', 'Bug 修复', '重构'],
       'fundamental': ['财报分析', '估值判断'],
       ...
   }
   ```

---

### Step 3: 通知负责 Agent

**自动添加评论**:

```markdown
## 🤖 自动通知

@programmer-agent 你好！

这个改进工单已分配给你，请处理：

### 📋 处理流程
1. 确认接收任务
2. 创建 Branch: `fix/issue-2`
3. 解决问题
4. 创建 PR: 关联此 Issue
5. Code Review
6. Merge 关闭
```

---

### Step 4: 跟踪 PR 状态

**检查项**:
- PR 是否已创建
- PR 状态（open/closed/merged）
- PR 是否可合并
- CI 状态（待实现）
- Review 状态（待实现）

---

### Step 5: 自动合并（可选）

**合并条件**:
- [x] PR 状态为 open
- [x] 无代码冲突
- [ ] CI 测试通过（待实现）
- [ ] 有 Review 批准（待实现）

**合并方式**: Squash merge

---

## ⚙️ 配置说明

### 环境变量

```bash
# .env 文件
GITHUB_TOKEN=github_pat_xxx
GITHUB_REPO=aprilvkuo/stock_agent
```

### Agent 映射

```python
AGENT_GITHUB = {
    'fundamental': 'fundamental-agent',
    'programmer': 'programmer-agent',
    ...
}
```

### 职责映射

```python
AGENT_RESPONSIBILITIES = {
    'programmer': ['代码开发', 'Bug 修复', '重构'],
    'fundamental': ['财报分析', '估值判断'],
    ...
}
```

---

## 🔧 高级用法

### 定时执行（Cron）

**每天 9:00 执行**:

```bash
# crontab -e
0 9 * * * cd /Users/egg/.openclaw/workspace && python3 scripts/issue_tracker.py
```

### 作为 GitHub Actions

```yaml
name: Issue Auto Tracker

on:
  schedule:
    - cron: '0 9 * * *'  # 每天 9:00
  workflow_dispatch:      # 手动触发

jobs:
  track-issues:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run Issue Tracker
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          python3 scripts/issue_tracker.py --auto-merge
```

### 集成到 Agent 系统

```python
from scripts.issue_tracker import IssueTracker

# 程序员 Agent 使用
tracker = IssueTracker()
tracker.process_issues(auto_merge=True)
```

---

## 📊 命令行参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--dry-run` | 仅显示，不执行 | `--dry-run` |
| `--auto-merge` | 自动合并 PR | `--auto-merge` |
| `--help` | 显示帮助 | `--help` |

---

## 🎯 最佳实践

### ✅ 推荐

1. **定时执行** - 每天执行一次
2. **Dry run 测试** - 首次使用先测试
3. **监控日志** - 记录执行情况
4. **渐进自动化** - 先手动，后自动

### ❌ 避免

1. **过于频繁** - 避免 API 限流
2. **完全自动** - 保留人工审核
3. **忽略错误** - 处理异常情况

---

## 🔍 故障排查

### 问题 1: API 限流

**症状**:
```
403 Client Error: rate limit exceeded
```

**解决**:
- 添加延时：`time.sleep(1)`
- 使用 Token 认证
- 降低执行频率

### 问题 2: 权限不足

**症状**:
```
403 Client Error: requires one of these scopes: [public_repo, repo]
```

**解决**:
- 检查 Token 权限
- 添加 repo 权限

### 问题 3: 无法识别负责 Agent

**症状**:
```
未匹配到具体 Agent，默认分配给 coordinator
```

**解决**:
- 在 Issue 中明确标注负责方
- 添加更多关键词到职责映射

---

## 📖 扩展功能（待实现）

### 已规划

- [ ] CI 状态检查
- [ ] Review 批准检查
- [ ] 邮件通知
- [ ] 钉钉/企业微信通知
- [ ] Issue 优先级排序
- [ ] 超时自动升级

### 欢迎贡献

如果你有其他想法，欢迎创建 Issue 或 PR！

---

## 📖 相关文档

- [CONTRIBUTING.md](./CONTRIBUTING.md) - 贡献指南
- [BRANCH_NAMING.md](./BRANCH_NAMING.md) - 分支命名
- [GITHUB_WORKFLOW_GUIDE.md](./memory/stock-system/GITHUB_WORKFLOW_GUIDE.md) - GitHub 工作流

---

**维护者**: 程序员 Agent  
**最后更新**: 2026-03-09
