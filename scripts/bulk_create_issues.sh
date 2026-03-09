#!/bin/bash

# 🚀 批量创建 GitHub Issues 脚本
# 从迁移的 JSON 文件创建 Issues

set -e

ISSUE_DIR="/Users/egg/.openclaw/workspace/.github/ISSUE_TEMPLATE/migrated-issues"

echo "============================================================"
echo "🚀 批量创建 GitHub Issues"
echo "============================================================"
echo ""

# 检查 GitHub CLI 是否安装
if ! command -v gh &> /dev/null; then
    echo "❌ 错误：GitHub CLI (gh) 未安装"
    echo ""
    echo "请安装 GitHub CLI:"
    echo "  macOS: brew install gh"
    echo "  或者访问：https://cli.github.com/"
    exit 1
fi

# 检查是否已认证
if ! gh auth status &> /dev/null; then
    echo "❌ 错误：GitHub CLI 未认证"
    echo ""
    echo "请运行：gh auth login"
    exit 1
fi

# 切换到 Issue 目录
cd "$ISSUE_DIR"

echo "📁 目录：$ISSUE_DIR"
echo ""

# 统计
created=0
errors=0

# 遍历所有 Issue JSON 文件
for file in issue-*.json; do
    if [ ! -f "$file" ]; then
        continue
    fi
    
    echo "📝 处理：$file"
    
    # 提取字段
    title=$(jq -r '.title' "$file")
    body=$(jq -r '.body' "$file")
    assignee=$(jq -r '.assignee' "$file")
    
    # 提取标签（逗号分隔）
    labels=$(jq -r '.labels | join(",")' "$file")
    
    # 创建 Issue
    echo "   标题：$title"
    echo "   分配：@$assignee"
    echo "   标签：$labels"
    
    # 使用 gh issue create
    if gh issue create \
        --title "$title" \
        --body "$body" \
        --label "$labels" \
        --assignee "$assignee"; then
        
        echo "   ✅ 创建成功"
        ((created++))
    else
        echo "   ❌ 创建失败"
        ((errors++))
    fi
    
    echo ""
done

# 显示统计
echo "============================================================"
echo "📊 统计"
echo "============================================================"
echo "✅ 成功创建：$created 个 Issue"
echo "❌ 失败：$errors 个"
echo "============================================================"
echo ""

if [ $created -gt 0 ]; then
    echo "🎉 迁移完成！"
    echo ""
    echo "🔗 查看 Issues:"
    echo "   https://github.com/aprilvkuo/stock_agent/issues?q=label:migrated"
    echo ""
fi
