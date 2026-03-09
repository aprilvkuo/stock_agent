#!/bin/bash

# 📁 目录规范化提交脚本
# 使用方式：./scripts/commit_cleanup.sh

set -e

echo "📁 目录规范化提交脚本"
echo "======================"
echo ""

# 检查是否在正确的目录
if [ ! -f "AGENTS.md" ] || [ ! -f "SOUL.md" ]; then
    echo "❌ 错误：请在 workspace 根目录运行此脚本"
    exit 1
fi

# 检查 Git 状态
echo "📊 当前 Git 状态："
git status --short
echo ""

# 确认提交
read -p "✅ 确认要提交目录规范化改动吗？(y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 已取消"
    exit 1
fi

# 分批提交
echo ""
echo "📝 开始分批提交..."
echo ""

# 1. 根目录核心配置
if git diff --name-only | grep -E "^(AGENTS|SOUL|USER|TOOLS|IDENTITY|HEARTBEAT|CONTRIBUTING)\.md$"; then
    echo "1️⃣  提交根目录核心配置..."
    git add AGENTS.md SOUL.md USER.md TOOLS.md IDENTITY.md HEARTBEAT.md CONTRIBUTING.md
    git commit -m "chore: 保持根目录核心配置"
    echo "   ✅ 完成"
fi

# 2. GitHub 文档
if git diff --name-only | grep "^docs/github/"; then
    echo "2️⃣  提交 GitHub 文档..."
    git add docs/github/
    git commit -m "docs(github): 归档 GitHub 工作流文档"
    echo "   ✅ 完成"
fi

# 3. 指南文档
if git diff --name-only | grep "^docs/guides/"; then
    echo "3️⃣  提交使用指南..."
    git add docs/guides/
    git commit -m "docs(guides): 添加使用指南和报告"
    echo "   ✅ 完成"
fi

# 4. 目录结构文档
if git diff --name-only | grep "^docs/DIRECTORY_STRUCTURE.md$"; then
    echo "4️⃣  提交目录结构规范..."
    git add docs/DIRECTORY_STRUCTURE.md
    git commit -m "docs: 创建目录结构规范文档"
    echo "   ✅ 完成"
fi

# 5. 测试脚本
if git diff --name-only | grep "^dev/testing/"; then
    echo "5️⃣  提交测试脚本..."
    git add dev/testing/
    git commit -m "chore(testing): 移动测试脚本到 dev/testing"
    echo "   ✅ 完成"
fi

# 6. 其他 docs
if git diff --name-only | grep "^docs/" | grep -v "^docs/github/" | grep -v "^docs/guides/" | grep -v "^docs/DIRECTORY_STRUCTURE.md$"; then
    echo "6️⃣  提交其他文档..."
    git add docs/
    git commit -m "docs: 更新项目文档"
    echo "   ✅ 完成"
fi

echo ""
echo "✅ 所有改动已提交！"
echo ""
echo "📋 下一步："
echo "   1. git push origin <branch-name>"
echo "   2. 创建 Pull Request"
echo "   3. 等待 Review"
echo "   4. Merge 到 main"
echo ""
