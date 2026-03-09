# 🤝 贡献指南 (Contributing Guide)

**版本**: v1.1  
**实施日期**: 2026-03-09  
**最后更新**: 2026-03-09 (v1.1 添加目录规范)  
**适用范围**: 股票多 Agent 系统团队

---

## 📁 目录结构规范

### 根目录规则

**允许在根目录的文件**（仅限以下核心配置）：

| 文件 | 用途 |
|------|------|
| `AGENTS.md` | Agent 配置 |
| `SOUL.md` | 人格定义 |
| `USER.md` | 用户信息 |
| `TOOLS.md` | 工具配置 |
| `IDENTITY.md` | 身份定义 |
| `HEARTBEAT.md` | 心跳任务 |
| `CONTRIBUTING.md` | 贡献指南 |
| `.gitignore` | Git 忽略 |
| `.env` | 环境变量 |
| `.github/` | GitHub 配置 |
| `.openclaw/` | OpenClaw 配置 |

**禁止在根目录**：
- ❌ 临时文件
- ❌ 测试脚本
- ❌ 报告文档
- ❌ 功能文档

### 目录结构

```
workspace/
├── .github/              # GitHub 配置（ISSUE_TEMPLATE, workflows）
├── .openclaw/           # OpenClaw 运行时配置
├── agents/              # Agent 配置文件
│   ├── stock-coordinator/
│   ├── stock-programmer/
│   └── ...
├── docs/                # 项目文档
│   ├── github/          # GitHub 工作流相关文档
│   ├── stock-system/    # 股票系统文档
│   └── guides/          # 使用指南和报告
├── memory/              # 记忆和日志
│   ├── stock-system/    # 股票系统记忆
│   └── YYYY-MM-DD.md    # 每日记忆
├── scripts/             # 可执行脚本
│   └── auto_agent.py
├── shared/              # 共享数据
├── skills/              # 技能包
├── dev/                 # 开发实验区
│   ├── experiments/     # 实验性代码
│   ├── drafts/          # 草稿
│   └── testing/         # 测试脚本
└── .backup/             # 备份目录
```

### 文档归档规则

| 文档类型 | 存放位置 | 示例 |
|---------|---------|------|
| GitHub 配置文档 | `docs/github/` | `GITHUB_WORKFLOW_COMPLETE.md` |
| 分支规范 | `docs/github/` | `BRANCH_NAMING.md` |
| Issue 模板 | `docs/github/` | `ISSUE_TEMPLATE_FINAL.md` |
| 使用指南 | `docs/guides/` | `CODE_STRUCTURE.md` |
| 实现报告 | `docs/guides/` | `GITHUB_IMPLEMENTATION_REPORT.md` |
| 安全文档 | `docs/guides/` | `GITHUB_TOKEN_SECURITY.md` |
| 股票系统文档 | `memory/stock-system/` 或 `docs/stock-system/` | `OPTIMIZATION_REPORT.md` |

---

## 🎯 开发流程

### 标准流程（必须遵守）

```
1. 创建/接收 Issue
   ↓
2. 创建分支
   ↓
3. 开发 + 提交
   ↓
4. 推送分支
   ↓
5. 创建 PR
   ↓
6. Code Review
   ↓
7. Merge 到 main
   ↓
8. 删除分支
```

---

## 📋 详细步骤

### Step 1: 获取任务

**来源**:
- GitHub Issues: https://github.com/aprilvkuo/stock_agent/issues
- 改进工单（自动创建）
- 团队分配

**确认任务**:
- 在 Issue 中评论：`我来处理这个`
- 或 Assign 给自己

---

### Step 2: 创建分支

**从 main 创建分支**:

```bash
# 确保是最新的 main
git checkout main
git pull origin main

# 创建分支
git checkout -b <branch-name>
```

**分支命名规范**:

| 类型 | 格式 | 示例 |
|------|------|------|
| 功能 | `feature/xxx` | `feature/ai-coding-integration` |
| 修复 | `fix/xxx` | `fix/github-actions-yaml-error` |
| 改进 | `improve/xxx` | `improve/code-structure` |
| 文档 | `docs/xxx` | `docs/add-contributing-guide` |
| 测试 | `test/xxx` | `test/add-unit-tests` |
| 重构 | `refactor/xxx` | `refactor/auto-agent-scripts` |

**关联 Issue**:

```bash
# 如果对应 Issue #123
git checkout -b fix/improve-123
# 或
git checkout -b feature/ai-coding-123
```

---

### Step 3: 开发 + 提交

**开发规范**:

```bash
# 使用 ai_coding 辅助开发（可选）
python3 -c "
from agents.stock_programmer.ai_coding import ai_coding
ai_coding('帮我实现 xxx 功能')
"

# 或手动开发
vim path/to/file.py
```

**提交规范**:

```bash
# 添加文件
git add -A

# 提交（遵循 Conventional Commits）
git commit -m "<type>: <description>"
```

**Commit 类型**:

| Type | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat: 添加 ai_coding 工具` |
| `fix` | Bug 修复 | `fix: 修复 YAML 语法错误` |
| `docs` | 文档更新 | `docs: 更新 README` |
| `style` | 代码格式 | `style: 格式化代码` |
| `refactor` | 重构 | `refactor: 优化代码结构` |
| `test` | 测试 | `test: 添加单元测试` |
| `chore` | 构建/工具 | `chore: 更新依赖` |

**关联 Issue**:

```bash
# 在 commit 中关联 Issue #123
git commit -m "feat: 添加 ai_coding 工具

- 实现自动工具选择
- 支持 Codex 和 Claude Code
- Closes #123"
```

---

### Step 4: 推送分支

```bash
# 推送到远程
git push origin <branch-name>

# 示例
git push origin fix/improve-code-structure
```

**首次推送**:

```bash
# 如果是新分支，设置 upstream
git push -u origin <branch-name>
```

---

### Step 5: 创建 PR

**GitHub 网页操作**:

1. 访问：https://github.com/aprilvkuo/stock_agent
2. 点击 "Pull requests" → "New pull request"
3. 选择分支：
   - base: `main`
   - compare: `<your-branch>`
4. 填写 PR 信息（使用模板）
5. 点击 "Create pull request"

**PR 标题格式**:

```
[Type] 简短描述 | 关联 Issue

示例:
[Fix] 修复 GitHub Actions YAML 错误 | #123
[Feat] 添加 ai_coding 工具 | #456
```

**PR 描述模板**:

```markdown
## 🎫 关联 Issue

Closes #123

## 📝 改进内容

- ✅ 添加 xxx 功能
- ✅ 修复 xxx 问题
- ✅ 优化 xxx 性能

## ✅ 自查清单

- [x] 代码已通过本地测试
- [x] 已添加必要的文档
- [x] 遵循代码规范
- [x] 无破坏性变更

## 📊 影响范围

- [x] 核心功能
- [ ] Agent 分析逻辑
- [ ] 数据获取
- [x] 文档更新

## 🧪 测试说明

测试步骤:
1. ...
2. ...

预期结果:
...

---

**改进工单 ID**: IMPROVE-xxx
**开发者**: @your-name
```

---

### Step 6: Code Review

**等待 Review**:

- GitHub 自动通知 Reviewer
- 或手动 @相关人员

**Reviewer 职责**:

- 检查代码质量
- 验证功能正确性
- 确认测试覆盖
- 提出改进建议

**回复 Review 意见**:

```markdown
@reviewer 谢谢建议！已修改：
- 添加了类型注解
- 优化了错误处理
- 补充了单元测试
```

**修改代码**:

```bash
# 根据 Review 意见修改
vim path/to/file.py

# 提交修改
git add -A
git commit -m "review: 根据反馈优化代码"

# 推送到同一分支（PR 会自动更新）
git push origin <branch-name>
```

---

### Step 7: Merge 到 main

**Review 通过后**:

1. 点击 "Squash and merge" 或 "Create a merge commit"
2. 确认合并信息
3. 点击 "Confirm merge"

**合并后**:

- ✅ Issue 自动关闭（如果 PR 描述有 `Closes #xxx`）
- ✅ 代码进入 main 分支
- ✅ CI 自动运行测试

---

### Step 8: 删除分支

**GitHub 网页**:

- PR 合并后会显示 "Delete branch" 按钮
- 点击删除

**本地清理**:

```bash
# 删除本地分支
git branch -d <branch-name>

# 删除远程分支（如果 GitHub 没自动删）
git push origin --delete <branch-name>

# 更新本地 main
git checkout main
git pull origin main
```

---

## 🎯 特殊情况处理

### 紧急 Hotfix

```bash
# 1. 从 main 创建 hotfix 分支
git checkout -b hotfix/critical-issue

# 2. 快速修复
vim path/to/file.py
git add -A
git commit -m "hotfix: 紧急修复 xxx 问题"

# 3. 推送
git push origin hotfix/critical-issue

# 4. 创建 PR（标注紧急）
# 标题：[HOTFIX] 紧急修复 xxx

# 5. 快速 Review（15 分钟内）
# 6. Merge

# 7. 删除分支
```

### 大型重构

```bash
# 1. 创建长期分支
git checkout -b refactor/major-refactor

# 2. 分多次小提交
git commit -m "refactor: 第一步 - 提取公共函数"
git commit -m "refactor: 第二步 - 添加类型注解"
git commit -m "refactor: 第三步 - 优化错误处理"

# 3. 定期同步 main
git checkout main
git pull origin main
git checkout refactor/major-refactor
git merge main

# 4. 完成后创建 PR
# 5. 详细测试
# 6. Review 通过后 Merge
```

### 冲突解决

```bash
# 1. 同步 main
git checkout main
git pull origin main

# 2. 切换回分支
git checkout <branch-name>

# 3. 合并 main
git merge main

# 4. 解决冲突
vim path/to/conflicted-file.py

# 5. 标记解决
git add path/to/conflicted-file.py

# 6. 完成合并
git commit -m "merge: 解决与 main 的冲突"

# 7. 推送
git push origin <branch-name>
```

---

## 📊 质量要求

### Code Review 检查清单

- [ ] 代码功能正确
- [ ] 代码风格一致
- [ ] 有必要的注释
- [ ] 有单元测试
- [ ] 文档已更新
- [ ] 无破坏性变更
- [ ] 性能无明显下降

### CI 检查项

- [ ] 代码格式化检查
- [ ] 单元测试通过
- [ ] 集成测试通过
- [ ] 文档构建成功
- [ ] 无安全漏洞

---

## 🎯 最佳实践

### ✅ 推荐

1. **小步提交** - 每次提交小而专注
2. **频繁同步** - 经常合并 main 避免冲突
3. **清晰描述** - Commit 和 PR 描述要清楚
4. **及时 Review** - 收到 Review 请求 24 小时内响应
5. **测试先行** - 先写测试再实现功能

### ❌ 避免

1. **大提交** - 一次提交几百个文件
2. **长期分支** - 分支存在超过 1 周
3. **模糊描述** - "fix bug"、"update code"
4. **跳过测试** - 不写测试直接提交
5. **直接 push main** - 违反分支保护规则

---

## 📖 相关文档

- [BRANCH_PROTECTION.md](./BRANCH_PROTECTION.md) - 分支保护规则
- [BRANCH_NAMING.md](./BRANCH_NAMING.md) - 分支命名规范
- [CODE_REVIEW.md](./CODE_REVIEW.md) - Code Review 指南
- [PULL_REQUEST_TEMPLATE.md](./.github/pull_request_template.md) - PR 模板

---

**维护者**: 协调 Agent  
**最后更新**: 2026-03-09
