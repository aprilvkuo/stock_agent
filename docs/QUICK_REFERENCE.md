# 📋 目录规范快速参考

**打印此页贴在办公桌前！**

---

## 🎯 根目录只允许这些文件

```
✅ AGENTS.md
✅ SOUL.md
✅ USER.md
✅ TOOLS.md
✅ IDENTITY.md
✅ HEARTBEAT.md
✅ CONTRIBUTING.md
✅ .gitignore
✅ .env
```

**其他所有文件 → 移动到对应目录！**

---

## 📁 文件归档速查表

| 文件类型 | 放到哪里 | 示例 |
|---------|---------|------|
| GitHub 文档 | `docs/github/` | `GITHUB_WORKFLOW.md` |
| 使用指南 | `docs/guides/` | `CODE_STRUCTURE.md` |
| 测试脚本 | `dev/testing/` | `test_xxx.py` |
| 股票系统文档 | `memory/stock-system/` | `OPTIMIZATION_REPORT.md` |
| 临时文件 | `dev/drafts/` | `draft.md` |
| 实验代码 | `dev/experiments/` | `experiment.py` |

---

## ✍️ Commit Message 模板

```bash
# 新功能
git commit -m "feat(agent): 添加 xxx 功能"

# Bug 修复
git commit -m "fix(stock): 修复 xxx 问题"

# 文档更新
git commit -m "docs: 更新 xxx 文档"

# 目录调整
git commit -m "chore(dir): 整理 xxx 目录"

# 重构
git commit -m "refactor(agent): 优化 xxx 代码"
```

---

## 🚫 禁止行为

```bash
# ❌ 禁止在根目录创建临时文件
touch workspace/my_test.py  # 错！

# ❌ 禁止模糊的 commit message
git commit -m "fix"         # 错！
git commit -m "update"      # 错！

# ❌ 禁止大提交
git add -A                  # 错！（除非真的只有小改动）
git commit -m "huge update" # 错！
```

---

## ✅ 正确做法

```bash
# ✅ 临时文件放到 dev/testing/
touch dev/testing/my_test.py

# ✅ 清晰的 commit message
git commit -m "fix(stock): 修复茅台股价获取超时问题"

# ✅ 小步提交，分批提交
git add docs/github/*.md
git commit -m "docs(github): 归档 GitHub 文档"

git add dev/testing/*.py
git commit -m "chore(testing): 移动测试脚本"
```

---

## 🔍 检查命令

```bash
# 检查根目录（应该只有 9 个文件）
ls -la /Users/egg/.openclaw/workspace/*.md

# 查看 Git 状态
git status --short

# 检查提交历史
git log --oneline -10
```

---

## 📖 完整文档

- [DIRECTORY_STRUCTURE.md](./docs/DIRECTORY_STRUCTURE.md) - 完整目录结构
- [CONTRIBUTING.md](./CONTRIBUTING.md) - 贡献指南
- [DIR_CLEANUP_REPORT.md](./docs/guides/DIR_CLEANUP_REPORT.md) - 整理报告

---

**记住：根目录 = 客厅，保持整洁！** 🏠
