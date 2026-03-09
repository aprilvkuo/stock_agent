# Issue: 项目目录结构混乱，需要规范化

## 📋 问题描述

当前工作区根目录存在大量散乱文件，主要包括：
- GitHub 相关文档（10+ 个.md 文件）
- 临时测试脚本（verify_bot_token.py, test_actions_workflow.py）
- 各类报告文档散落根目录

## 🎯 目标

1. **清理根目录** - 只保留核心配置文件
2. **建立规范目录** - 按功能分类归档文档
3. **制定提交规范** - 确保未来 commit 保持目录整洁

## 📁 建议的新目录结构

```
/Users/egg/.openclaw/workspace/
├── .github/              # GitHub 相关配置（已有）
├── .openclaw/           # OpenClaw 配置（已有）
├── agents/              # Agent 配置（已有）
├── docs/                # 项目文档
│   ├── github/          # GitHub 工作流相关文档
│   ├── stock-system/    # 股票系统文档
│   └── guides/          # 使用指南
├── memory/              # 记忆和日志（已有）
├── scripts/             # 脚本工具（已有）
├── shared/              # 共享数据（已有）
├── skills/              # 技能包（已有）
├── dev/                 # 开发实验区（已有）
├── .backup/             # 备份目录（已有）
│
├── AGENTS.md            # 核心配置
├── SOUL.md              # 核心配置
├── USER.md              # 核心配置
├── TOOLS.md             # 核心配置
├── IDENTITY.md          # 核心配置
├── HEARTBEAT.md         # 核心配置
├── CONTRIBUTING.md      # 贡献指南
├── .gitignore           # Git 忽略配置
└── .env                 # 环境变量
```

## ✅ 执行步骤

### 步骤 1: 创建文档目录结构
```bash
mkdir -p docs/github docs/stock-system docs/guides
```

### 步骤 2: 移动 GitHub 相关文档
将所有 GitHub 相关的.md 文件移动到 `docs/github/`

### 步骤 3: 移动临时脚本
将测试脚本移动到 `dev/testing/` 或删除

### 步骤 4: 整理股票系统文档
将股票系统相关的报告移动到 `docs/stock-system/` 或 `memory/stock-system/`

### 步骤 5: 制定提交规范
创建 `.github/CODEOWNERS` 和更新 `CONTRIBUTING.md`

## 📝 提交规范要求

### Commit Message 格式
```
<type>(<scope>): <subject>

type: feat|fix|docs|style|refactor|test|chore
scope: 影响的范围（可选）
subject: 简短描述
```

### 目录规范
- **根目录**：只保留核心配置文件（AGENTS.md, SOUL.md, USER.md, TOOLS.md, IDENTITY.md, HEARTBEAT.md, CONTRIBUTING.md）
- **docs/**: 所有项目文档
- **scripts/**: 所有可执行脚本
- **dev/**: 临时文件、测试、实验性代码
- **memory/**: 系统记忆和日志

### 禁止行为
❌ 不允许在根目录创建临时文件
❌ 不允许将文档散落在根目录
❌ 不允许提交无意义的 commit message（如 "update", "fix"）

## 🏷️ Labels
- priority: high
- type: cleanup
- area: project-structure

## 📅 截止日期
2026-03-10
