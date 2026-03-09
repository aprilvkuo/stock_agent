# 📁 项目目录结构规范

**版本**: v1.0  
**创建日期**: 2026-03-09  
**目的**: 保持项目目录整洁，便于维护和协作

---

## 🎯 核心原则

1. **根目录最小化** - 只保留核心配置文件
2. **分类清晰** - 按功能模块组织文件
3. **命名规范** - 文件和目录名称要有意义
4. **文档归档** - 所有文档必须放入对应目录

---

## 📂 目录结构总览

```
/Users/egg/.openclaw/workspace/
│
├── 📄 核心配置文件（根目录仅允许这些）
│   ├── AGENTS.md              # Agent 配置
│   ├── SOUL.md                # 人格定义
│   ├── USER.md                # 用户信息
│   ├── TOOLS.md               # 工具配置
│   ├── IDENTITY.md            # 身份定义
│   ├── HEARTBEAT.md           # 心跳任务
│   ├── CONTRIBUTING.md        # 贡献指南
│   ├── .gitignore             # Git 忽略规则
│   └── .env                   # 环境变量（敏感信息）
│
├── 🗂️ 系统目录
│   ├── .github/               # GitHub 配置
│   │   ├── ISSUE_TEMPLATE/    # Issue 模板
│   │   ├── workflows/         # GitHub Actions
│   │   └── pull_request_template.md
│   ├── .openclaw/             # OpenClaw 运行时配置
│   └── .backup/               # 自动备份目录
│
├── 🤖 Agent 配置
│   └── agents/
│       ├── stock-coordinator/ # 协调 Agent
│       ├── stock-programmer/  # 程序员 Agent
│       ├── stock-fundamental/ # 基本面 Agent
│       ├── stock-technical/   # 技术面 Agent
│       └── stock-sentiment/   # 情绪 Agent
│
├── 📚 项目文档
│   └── docs/
│       ├── github/            # GitHub 工作流文档
│       │   ├── GITHUB_WORKFLOW_COMPLETE.md
│       │   ├── GITHUB_BOT_SETUP.md
│       │   ├── BRANCH_NAMING.md
│       │   ├── BRANCH_PROTECTION.md
│       │   ├── ISSUE_AUTOMATION_GUIDE.md
│       │   └── ISSUE_TEMPLATE_FINAL.md
│       ├── stock-system/      # 股票系统文档
│       │   └── (系统相关文档)
│       └── guides/            # 使用指南和报告
│           ├── CODE_STRUCTURE.md
│           ├── KEY_ROLES.md
│           ├── GITHUB_IMPLEMENTATION_REPORT.md
│           └── GITHUB_TOKEN_SECURITY.md
│
├── 🧠 记忆系统
│   └── memory/
│       ├── YYYY-MM-DD.md      # 每日记忆
│       └── stock-system/      # 股票系统记忆
│           ├── agent-roles/   # Agent 角色定义
│           ├── scripts/       # 分析脚本
│           ├── analysis-log/  # 分析日志
│           ├── reports/       # 周度/月度报告
│           ├── validation-queue.md
│           └── SYSTEM_STATUS.md
│
├── 🔧 脚本工具
│   └── scripts/
│       ├── auto_agent.py      # 自动分析脚本
│       └── (其他可执行脚本)
│
├── 📦 共享数据
│   └── shared/
│       └── stock-system/      # 股票系统共享数据
│
├── 🎯 技能包
│   └── skills/
│       ├── stock-analyzer/    # 股票分析技能
│       ├── stock-monitor-skill/ # 股票监控技能
│       └── (其他技能)
│
└── 🧪 开发实验区
    └── dev/
        ├── experiments/       # 实验性代码
        ├── drafts/            # 草稿文件
        └── testing/           # 测试脚本
            ├── verify_bot_token.py
            └── test_actions_workflow.py
```

---

## ✅ 文件归档规则

### 根目录清理清单

**保留**（核心配置）：
- ✅ AGENTS.md
- ✅ SOUL.md
- ✅ USER.md
- ✅ TOOLS.md
- ✅ IDENTITY.md
- ✅ HEARTBEAT.md
- ✅ CONTRIBUTING.md
- ✅ .gitignore
- ✅ .env

**移动**（归档到对应目录）：
- 📦 GitHub 相关文档 → `docs/github/`
- 📦 指南和报告 → `docs/guides/`
- 📦 测试脚本 → `dev/testing/`
- 📦 股票系统文档 → `memory/stock-system/` 或 `docs/stock-system/`

**删除**（不再需要）：
- 🗑️ 临时文件
- 🗑️ 过时的报告
- 🗑️ 重复的文档

---

## 📝 Commit 规范

### Commit Message 格式

遵循 [Conventional Commits](https://www.conventionalcommits.org/)：

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

### Type 类型

| Type | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat: 添加自动验证脚本` |
| `fix` | Bug 修复 | `fix: 修复股价获取错误` |
| `docs` | 文档更新 | `docs: 更新目录结构规范` |
| `style` | 代码格式 | `style: 格式化 Python 代码` |
| `refactor` | 重构 | `refactor: 优化 Agent 架构` |
| `test` | 测试 | `test: 添加单元测试` |
| `chore` | 构建/工具 | `chore: 更新依赖版本` |
| `ci` | CI 配置 | `ci: 添加 GitHub Actions` |
| `perf` | 性能优化 | `perf: 优化数据缓存` |

### Scope 范围

| Scope | 说明 |
|-------|------|
| `dir` | 目录结构调整 |
| `agent` | Agent 相关 |
| `stock` | 股票分析 |
| `github` | GitHub 配置 |
| `docs` | 文档 |
| `scripts` | 脚本工具 |

### 示例

```bash
# 目录结构调整
git commit -m "chore(dir): 整理根目录文件结构"

# 添加新功能
git commit -m "feat(agent): 添加情绪分析 Agent"

# 文档更新
git commit -m "docs: 添加目录结构规范文档"

# Bug 修复
git commit -m "fix(stock): 修复股价数据缓存问题"

# 多行 commit（推荐）
git commit -m "chore(dir): 规范化项目目录结构

- 移动 GitHub 文档到 docs/github/
- 移动测试脚本到 dev/testing/
- 更新 CONTRIBUTING.md
- 创建 DIRECTORY_STRUCTURE.md

Closes #123"
```

---

## 🚫 禁止行为

### ❌ 不允许的操作

1. **根目录乱放文件**
   ```bash
   # ❌ 错误
   workspace/
     ├── my_test.py          # 应该放到 dev/testing/
     ├── report.md           # 应该放到 docs/guides/
     └── notes.txt           # 应该放到 memory/
   ```

2. **模糊的 Commit Message**
   ```bash
   # ❌ 错误
   git commit -m "fix"
   git commit -m "update"
   git commit -m "修改了一些东西"
   
   # ✅ 正确
   git commit -m "fix(stock): 修复茅台股价获取超时问题"
   ```

3. **大而无当的提交**
   ```bash
   # ❌ 错误：一次提交 100 个文件
   git add -A
   git commit -m "huge update"
   
   # ✅ 正确：分多次小提交
   git add docs/github/*.md
   git commit -m "docs: 归档 GitHub 文档"
   
   git add dev/testing/*.py
   git commit -m "chore: 移动测试脚本"
   ```

4. **直接 push 到 main**
   ```bash
   # ❌ 错误（会被分支保护阻止）
   git checkout main
   git push origin main
   
   # ✅ 正确：通过 PR 流程
   git checkout -b feature/xxx
   git push origin feature/xxx
   # 然后创建 PR
   ```

---

## 🔍 检查清单

### 提交前检查

在 commit 之前，问自己：

- [ ] 文件是否放在了正确的目录？
- [ ] Commit message 是否清晰描述了改动？
- [ ] 是否遵循了 Conventional Commits 格式？
- [ ] 是否有不必要的文件（临时文件、测试数据）？
- [ ] 是否更新了相关文档？

### 目录整洁度检查

定期运行：

```bash
# 查看根目录文件
ls -la /Users/egg/.openclaw/workspace/

# 只应该看到核心配置文件
# 如果发现其他.md 或 .py 文件，需要归档
```

---

## 📖 相关文档

- [CONTRIBUTING.md](./CONTRIBUTING.md) - 贡献指南
- [BRANCH_NAMING.md](./docs/github/BRANCH_NAMING.md) - 分支命名规范
- [BRANCH_PROTECTION.md](./docs/github/BRANCH_PROTECTION.md) - 分支保护规则

---

**维护者**: 协调 Agent  
**最后更新**: 2026-03-09
