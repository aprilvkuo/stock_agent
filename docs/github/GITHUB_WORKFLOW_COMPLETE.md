# ✅ GitHub Issues + PR 工作流 - 配置完成

**配置日期**: 2026-03-09 17:11  
**系统版本**: v2.0 (GitHub 集成版)  
**状态**: ✅ 已完成并推送

---

## 🎉 配置完成确认

### ✅ 已完成步骤

1. **GitHub Token 配置**
   - ✅ Fine-grained token 已生成
   - ✅ Workflows 权限已添加（Read and write）
   - ✅ Token 已关联 `aprilvkuo/stock_agent` 仓库

2. **工作流文件推送**
   - ✅ `.github/workflows/issue-notify.yml` - Issue 自动通知
   - ✅ `.github/workflows/pr-auto.yml` - PR 自动处理
   - ✅ 推送到 GitHub 成功

3. **模板文件**
   - ✅ `.github/ISSUE_TEMPLATE/improvement-ticket.yml` - 改进工单模板
   - ✅ `.github/ISSUE_TEMPLATE/feature-request.yml` - 功能建议模板
   - ✅ `.github/pull_request_template.md` - PR 模板

4. **核心模块**
   - ✅ `memory/stock-system/scripts/github_issue_manager.py` - GitHub API 封装
   - ✅ `improvement_ticket.py` - 工单系统集成

5. **安全配置**
   - ✅ `.env.github` 已加入 `.gitignore`
   - ✅ Token 不会被推送到 GitHub

---

## 🚀 立即测试

### 测试 1: 查看 GitHub Actions

访问：https://github.com/aprilvkuo/stock_agent/actions

确认工作流已启用：
- ✅ 🎫 Issue 自动通知
- ✅ 🔀 PR 自动处理

### 测试 2: 创建测试 Issue

```bash
cd /Users/egg/.openclaw/workspace/memory/stock-system

# 运行测试脚本
python3 scripts/github_issue_manager.py
```

**预期结果**:
- ✅ 看到 "✅ Issue 已创建：#xxx"
- ✅ GitHub 上出现新 Issue
- ✅ Issue 中包含 @data-fetcher

### 测试 3: 完整工单流程

```bash
cd /Users/egg/.openclaw/workspace/memory/stock-system

python3 << 'EOF'
from improvement_ticket import ticket_system

ticket = ticket_system.create_ticket(
    provider_id='data-fetcher',
    consumer_id='fundamental',
    service_type='financial_data',
    rating={
        'overall_score': 2,
        'feedback': '测试工单 - 数据缺少指标',
        'suggestions': ['添加 ROE', '添加毛利率']
    }
)

print(f"✅ 工单已创建：{ticket['id']}")
if 'github_issue' in ticket:
    print(f"   GitHub Issue: #{ticket['github_issue']['number']}")
    print(f"   链接：{ticket['github_issue']['url']}")
EOF
```

**预期结果**:
- ✅ 本地工单已创建
- ✅ GitHub Issue 已创建
- ✅ Issue 已 @data-fetcher
- ✅ Git 提交已记录

---

## 📊 完整工作流

```
Agent 评分 ≤ 3
    ↓
improvement_ticket.py
    ↓
github_issue_manager.py
    ↓
GitHub API → 创建 Issue #123
    ↓
GitHub Actions → issue-notify.yml
    ↓
自动评论 + @对应 Agent
    ↓
Agent 接收任务
    ↓
创建 Branch: fix/improve-xxx
    ↓
解决问题 → 提交代码
    ↓
创建 PR → 关联 Issue (Closes #123)
    ↓
GitHub Actions → pr-auto.yml
    ↓
验证 + 通知 Reviewer
    ↓
Code Review → Merge
    ↓
自动关闭 Issue #123
    ↓
本地工单状态更新
    ↓
Git 提交记录
```

---

## 🎯 使用场景

### 场景 1: 低分自动触发

```python
# agent_rating.py 中评分 ≤ 3 时
from improvement_ticket import ticket_system

ticket_system.create_ticket(
    provider_id='sentiment',  # 情绪 Agent 需要改进
    consumer_id='coordinator',
    service_type='sentiment_analysis',
    rating={'overall_score': 2, 'feedback': '情绪分析不准确'}
)
```

**结果**:
- 本地工单已创建
- GitHub Issue #xxx 已创建
- @sentiment-agent 收到通知

### 场景 2: 手动创建 Issue

访问：https://github.com/aprilvkuo/stock_agent/issues/new/choose

选择 **"🎫 改进工单"** 模板，填写：
- 优先级
- 乙方 Agent
- 甲方 Agent
- 问题描述
- 改进建议

### 场景 3: 处理 Issue

1. **接收任务**
   - 在 Issue 中评论：`收到，立即处理`
   
2. **创建 Branch**
   ```bash
   git checkout -b fix/improve-20260309131544
   ```

3. **解决问题**
   ```bash
   # 修改代码
   vim skills/stock-analyzer/xxx.py
   
   # 提交
   git add -A
   git commit -m "fix: 添加 ROE 指标"
   git push origin fix/improve-20260309131544
   ```

4. **创建 PR**
   - 访问 GitHub PR 页面
   - 填写 PR 描述
   - 添加 `Closes #123`

5. **等待 Review**
   - @coordinator-agent 和 @qa-agent 会收到通知
   - Review 通过后 Merge

---

## 🏷️ Label 自动管理

### Issue Label

| Label | 自动添加条件 |
|-------|-------------|
| `🔴 high-priority` | 评分 ≤ 2 |
| `🚨 critical` | 评分 ≤ 1 |
| `🟠 medium-priority` | 评分 2-3 |
| `📊 基本面分析` | service_type = financial_* |
| `📈 技术面分析` | service_type = technical_* |
| `😊 情绪分析` | service_type = sentiment_* |

### PR Label

- `🔧 pending-review` - 自动添加
- 复制关联 Issue 的所有 Label

---

## 📖 查看和管理

### 查看所有改进工单

https://github.com/aprilvkuo/stock_agent/issues?q=is%3Aopen+label%3Aimprovement-ticket

### 查看已完成的改进

https://github.com/aprilvkuo/stock_agent/issues?q=is%3Aclosed+label%3Aimprovement-ticket

### 使用 GitHub CLI

```bash
# 查看进行中的工单
gh issue list --label improvement-ticket --state open

# 查看工单详情
gh issue view 123

# 创建评论
gh issue comment 123 --body "收到，立即处理"

# 关闭 Issue
gh issue close 123
```

---

## ⚠️ 故障排查

### Issue 未自动创建

**检查**:
```bash
cd /Users/egg/.openclaw/workspace/memory/stock-system
python3 -c "
from github_issue_manager import issue_manager
print('Token:', '已配置' if issue_manager.headers else '未配置')
print('Repo:', issue_manager._request('GET', ''))
"
```

**解决**: 检查 `.env.github` 中 Token 是否正确

### Actions 未触发

**检查**:
1. 访问 https://github.com/aprilvkuo/stock_agent/actions
2. 确认工作流已启用
3. 查看 Actions 日志

**解决**: 如果是首次使用，可能需要手动触发一次

### PR 未自动关联 Issue

**原因**: PR 描述中缺少 `Closes #xxx`

**解决**: 编辑 PR 描述，添加关联语句

---

## 📊 配置清单

- [x] GitHub Token 已生成（带 Workflows 权限）
- [x] Token 已关联仓库
- [x] 工作流文件已推送
- [x] Issue 模板已创建
- [x] PR 模板已创建
- [x] 核心模块已集成
- [x] `.env.github` 已加入 `.gitignore`
- [x] 本地测试通过

---

## 🎉 总结

**系统版本**: v2.0 (GitHub 集成版)  
**配置状态**: ✅ 完成  
**下一步**: 开始使用！

**核心功能**:
- ✅ 低分自动创建 GitHub Issue
- ✅ 自动 @对应 Agent
- ✅ GitHub Actions 自动通知
- ✅ PR 流程自动化
- ✅ Issue 和 PR 模板
- ✅ 完整文档

**现在可以开始使用 GitHub Issues + PR 工作流了！** 🚀

---

**配置完成时间**: 2026-03-09 17:11  
**配置者**: 系统 Agent
