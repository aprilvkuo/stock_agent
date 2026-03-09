# HEARTBEAT.md - 股票多 Agent 系统自动任务

**系统版本**: v2.0 (GitHub Issues 完全迁移)  
**更新日期**: 2026-03-09 22:17  
**核心改进**: 工单系统完全迁移到 GitHub Issues

---

## 📈 任务管理新流程

### ✅ 所有任务统一到 GitHub Issues

**本地工单系统已废弃**，所有任务通过 GitHub Issues 管理：

- **创建任务**: https://github.com/aprilvkuo/stock_agent/issues/new/choose
- **查看所有任务**: https://github.com/aprilvkuo/stock_agent/issues
- **改进工单**: https://github.com/aprilvkuo/stock_agent/issues?q=label:improvement-ticket
- **任务**: https://github.com/aprilvkuo/stock_agent/issues?q=label:task

### 🤖 Agent 工作流程

1. **拉取任务** - 从 GitHub Issues 获取分配给自己的任务
2. **创建 Branch** - `fix/issue-<issue_number>`
3. **开发** - 实现功能/修复问题
4. **提交 PR** - 关联 Issue (`Closes #xxx`)
5. **Review** - Code Review
6. **Merge** - 合并后 Issue 自动关闭

---

## 📋 每日 09:00 - 自动检查 ✅

**GitHub Actions 自动执行**:

```yaml
# .github/workflows/daily-issue-check.yml
name: 每日 Issue 检查
on:
  schedule:
    - cron: '0 1 * * *'  # 每天 09:00 (UTC+8)
```

**执行内容**:
1. 检查逾期 Issues
2. 生成日报
3. 发送通知

---

## 🆕 Issue 自动化

**GitHub Actions 自动处理**:

```yaml
# .github/workflows/issue-automation.yml
name: Issue 自动化处理
on:
  issues:
    types: [opened, labeled, assigned]
```

**执行内容**:
1. 自动分配负责 Agent
2. 添加评论通知
3. 跟踪 PR 状态

---

## 📊 当前迁移状态

### 已迁移任务

| 批次 | 内容 | 数量 | Issues |
|------|------|------|--------|
| #1 | Agent TODO | 5 个 | #13-#17 |
| #2 | Web 工单 | 7 个 | #24-#29, #31 |
| **总计** | | **12 个** | |

### 本地状态

- ✅ 本地工单系统已删除
- ✅ 备份已创建 (`.backup/old-ticket-system/`)
- ✅ 所有任务已迁移到 GitHub

---

## 🎯 手动分析股票

```bash
cd /Users/egg/.openclaw/workspace/memory/stock-system
python3 scripts/auto_agent.py analyze <股票代码>

# 示例
python3 scripts/auto_agent.py analyze 600519  # 贵州茅台
python3 scripts/auto_agent.py analyze 00700   # 腾讯控股
```

---

## 📝 查看系统状态

```bash
# 系统状态
cat SYSTEM_STATUS.md

# 优化路线图
cat OPTIMIZATION_ROADMAP.md

# 验证队列
cat validation-queue.md

# 分析日志
ls -la analysis-log/

# 周度报告
ls -la reports/
```

---

## ⚠️ 注意事项

1. **任务管理**: 所有任务通过 GitHub Issues，不再使用本地工单系统
2. **Commit 规范**: 遵循 Conventional Commits
3. **PR 流程**: 所有改动必须通过 PR，关联 Issue
4. **分支保护**: main 分支受保护，禁止直接 push

---

## 🔗 相关链接

- [迁移完成报告](./docs/github/TICKET_MIGRATION_COMPLETE.md)
- [迁移指南](./docs/github/TODO_MIGRATION_GUIDE.md)
- [Issue 模板](./.github/ISSUE_TEMPLATE/)
- [GitHub Issues](https://github.com/aprilvkuo/stock_agent/issues)

---

**最后更新**: 2026-03-09 22:17  
**下次检查**: 每日 09:00 自动执行
