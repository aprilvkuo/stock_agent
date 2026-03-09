# 📋 Issue 自动化处理系统 - 使用规范

**版本**: v2.0  
**实施日期**: 2026-03-09  
**状态**: ✅ 生产就绪

---

## 🎯 系统定位

Issue 自动化处理系统是股票多 Agent 系统的核心组件，实现：

1. **自动抓取** - 从 GitHub 自动获取 Issue
2. **智能验证** - 区分有效/无效任务
3. **自动分配** - 识别并分配给对应 Agent
4. **自动修复** - Agent 执行修复逻辑
5. **自动 PR** - 创建 Pull Request
6. **人工 Review** - 必须人工审核后才能 Merge

---

## 📖 核心原则

### 1. 逐个处理原则

**规则**: Issue 必须一个个解决，不能批量处理

**原因**:
- 保证每个 Issue 都经过充分 Review
- 避免多个 Issue 相互影响
- 便于追踪和回滚

**实现**:
```bash
# ✅ 正确：一次处理一个
python3 scripts/auto_issue_resolver.py --issue 2

# ❌ 错误：批量处理
python3 scripts/auto_issue_resolver.py  # 会处理所有
```

### 2. 人工 Review 原则

**规则**: 所有 PR 必须经过人工 Review 才能 Merge

**原因**:
- 保证代码质量
- 防止自动化错误
- 知识共享和传承

**流程**:
```
自动创建 PR → 人工 Review → 提出修改意见 → 修改 → 再次 Review → Merge
```

### 3. 基于最新 main 原则

**规则**: 所有修复必须基于最新的 main 分支

**原因**:
- 避免代码冲突
- 确保使用最新代码
- 减少 Merge 问题

**实现**:
```bash
# 每次处理前更新
git checkout main
git pull origin main
```

---

## 🚀 标准操作流程

### Step 1: 准备环境

```bash
cd /Users/egg/.openclaw/workspace

# 更新到最新 main
git checkout main
git pull origin main
```

### Step 2: 查看待处理 Issue

```bash
# 预览模式（推荐）
python3 scripts/auto_issue_resolver.py --dry-run
```

**输出示例**:
```
Issue #2: 代码规范优化
  状态：✅ 有效
  负责 Agent: @programmer-agent
```

### Step 3: 处理指定 Issue

```bash
# 处理单个 Issue
python3 scripts/auto_issue_resolver.py --issue 2
```

**自动执行**:
1. ✅ 验证有效性
2. ✅ 识别负责 Agent
3. ✅ 创建分支
4. ✅ 执行修复
5. ✅ 提交代码
6. ✅ 推送分支
7. ✅ 创建 PR

### Step 4: 人工 Review

**访问 PR 页面**:
```
https://github.com/aprilvkuo/stock_agent/pull/8
```

**Review 检查清单**:
- [ ] 代码质量 OK
- [ ] 遵循规范
- [ ] 测试通过
- [ ] 无破坏性变更

### Step 5: Merge PR

**Review 通过后**:
```
点击 "Squash and merge" → "Confirm merge"
```

**Merge 后**:
- ✅ PR 关闭
- ✅ Issue 自动关闭（因为有 `Closes #2`）
- ✅ 分支自动删除（可选）

### Step 6: 处理下一个 Issue

```bash
# 重复 Step 1-5
git checkout main
git pull origin main
python3 scripts/auto_issue_resolver.py --issue 3
```

---

## 📊 工作流程图

```
┌─────────────────────────────────────┐
│  1. git pull origin main           │
│     (基于最新 main)                 │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  2. python3 auto_issue_resolver.py │
│     --dry-run                      │
│     (预览待处理 Issue)              │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  3. python3 auto_issue_resolver.py │
│     --issue <N>                    │
│     (处理指定 Issue)                │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  4. 自动执行:                       │
│     - 验证有效性                    │
│     - 识别 Agent                    │
│     - 创建分支                      │
│     - 执行修复                      │
│     - 创建 PR                       │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  5. 人工 Review PR                  │
│     - 代码质量                      │
│     - 遵循规范                      │
│     - 测试验证                      │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  6. Merge PR                        │
│     - Squash and merge             │
│     - Issue 自动关闭                │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  7. 处理下一个 Issue                │
│     (回到 Step 1)                   │
└─────────────────────────────────────┘
```

---

## 🔧 配置管理

### 环境变量

```bash
# ~/.zshrc
export GITHUB_TOKEN="github_pat_xxx"
export GITHUB_REPO="aprilvkuo/stock_agent"
```

### Token 权限

| 权限 | 访问级别 | 用途 |
|------|---------|------|
| `Issues` | Read and write | 创建/关闭 Issue |
| `Pull requests` | Read and write | 创建 PR |
| `Contents` | Read and write | 读写代码 |

### Agent 配置

```python
# scripts/auto_issue_resolver.py
AGENT_KEYWORDS = {
    'programmer': ['代码', '重构', '优化'],
    'fundamental': ['财报', '估值'],
    # ...
}
```

---

## 📝 最佳实践

### ✅ 推荐

1. **每天执行一次** - 定期处理 Issue
2. **Dry Run 先行** - 先预览再执行
3. **逐个处理** - 一次一个 Issue
4. **人工 Review** - 必须审核
5. **基于最新** - 总是基于最新 main
6. **记录日志** - 保存执行记录

### ❌ 避免

1. **批量处理** - 不要一次处理多个
2. **自动 Merge** - 必须人工审核
3. **跳过更新** - 必须先 pull
4. **忽略错误** - 处理异常
5. **频繁执行** - 避免 API 限流

---

## 🔍 故障排查

### 问题 1: 403 权限不足

```
403 Client Error: Forbidden
```

**解决**:
- 检查 Token 权限
- 添加必要权限

### 问题 2: 冲突

```
CONFLICT (content): Merge conflict
```

**解决**:
```bash
git stash
git checkout main
git pull origin main
git checkout -b fix/issue-xxx
git stash pop
# 解决冲突
```

### 问题 3: 无法识别 Agent

```
未匹配到具体 Agent
```

**解决**:
- 在 Issue 中 @mention
- 添加 improvement-ticket 标签

---

## 📖 相关文档

- [ISSUE_AUTO_RESOLVER.md](./docs/ISSUE_AUTO_RESOLVER.md) - 完整技术文档
- [CONTRIBUTING.md](./CONTRIBUTING.md) - 贡献指南
- [BRANCH_NAMING.md](./BRANCH_NAMING.md) - 分支命名

---

## 🎯 版本历史

### v2.0 (2026-03-09)

- ✅ 添加 Issue 验证
- ✅ 自动关闭无效 Issue
- ✅ 自动创建 PR
- ✅ 完整文档

---

**维护者**: 程序员 Agent  
**最后更新**: 2026-03-09  
**状态**: ✅ 生产就绪
