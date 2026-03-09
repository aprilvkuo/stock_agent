# Git 版本控制 - 快速参考

## 📋 常用命令

### 查看提交历史
```bash
cd /Users/egg/.openclaw/workspace/memory/stock-system

# 查看最近 10 条
python3 scripts/git_version_control.py history

# 查看最近 20 条
python3 scripts/git_version_control.py history 20

# 查看特定 Agent 的提交
python3 scripts/git_version_control.py history 10 "协调 Agent"
```

### 分析股票（自动 Git 提交）
```bash
python3 scripts/auto_agent.py analyze 600519
```

### 每日验证（自动 Git 提交）
```bash
python3 scripts/auto_agent.py daily
```

### 周度复盘（自动 Git 提交）
```bash
python3 scripts/auto_agent.py weekly
```

---

## 🎯 Agent Git 身份

| 场景 | 使用 Agent | Git User |
|------|-----------|----------|
| 股票分析 | 协调 Agent | 协调 Agent <coordinator@stock-system.local> |
| 每日验证 | 系统 Agent | 系统 Agent <system-agent@stock-system.local> |
| 周度复盘 | 系统 Agent | 系统 Agent <system-agent@stock-system.local> |
| 规则更新 | 系统 Agent | 系统 Agent <system-agent@stock-system.local> |

---

## 📊 提交流程

```
分析/验证完成
    ↓
写入文件（日志/报告/队列）
    ↓
调用 git.commit(agent_name, message)
    ↓
git add -A
git config user.name "Agent 名称"
git config user.email "agent@stock-system.local"
git commit -m "[Agent] 时间 - 消息"
git push origin main
    ↓
记录到 .git-commits.json
```

---

## 🔍 查看 Git 原生日志

```bash
# 最近 5 条提交
git log --oneline -5

# 带完整消息
git log -3

# 特定 Agent 的提交
git log --author="协调 Agent" --oneline

# 图形化展示
git log --graph --oneline -10
```

---

## ⚠️ 故障排查

### Push 失败
```bash
# 检查远程仓库连接
git remote -v

# 手动测试 Push
git push origin main
```

### 提交被跳过
- 原因：没有文件变更
- 解决：正常现象，无需处理

### 查看提交历史文件
```bash
cat scripts/.git-commits.json | jq .
```

---

## 📖 完整文档

- [GIT_VERSION_CONTROL.md](./GIT_VERSION_CONTROL.md) - 详细规范
- [GIT_IMPLEMENTATION_SUMMARY.md](./GIT_IMPLEMENTATION_SUMMARY.md) - 实施报告

---

**版本**: v1.0  
**更新**: 2026-03-09
