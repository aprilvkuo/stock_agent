#!/bin/bash
# GitHub 环境变量快速配置脚本
# 用法：./setup_github_env.sh <your_github_token>

set -e

echo "============================================================"
echo "🔧 GitHub Issue Auto-Resolver - 环境变量配置工具"
echo "============================================================"
echo ""

# 检查参数
if [ -z "$1" ]; then
    echo "❌ 用法：$0 <your_github_token>"
    echo ""
    echo "示例:"
    echo "  $0 github_pat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    echo ""
    echo "获取 Token: https://github.com/settings/tokens"
    exit 1
fi

GITHUB_TOKEN="$1"
GITHUB_REPO="aprilvkuo/stock_agent"
WORKSPACE="/Users/egg/.openclaw/workspace"

# 检测 Shell 类型
if [ -f ~/.zshrc ]; then
    PROFILE_FILE=~/.zshrc
    SHELL_TYPE="zsh"
elif [ -f ~/.bash_profile ]; then
    PROFILE_FILE=~/.bash_profile
    SHELL_TYPE="bash"
elif [ -f ~/.bashrc ]; then
    PROFILE_FILE=~/.bashrc
    SHELL_TYPE="bash"
else
    echo "❌ 未找到 Shell 配置文件（~/.zshrc 或 ~/.bash_profile）"
    exit 1
fi

echo "✅ 检测到 Shell: $SHELL_TYPE"
echo "✅ 配置文件：$PROFILE_FILE"
echo ""

# 检查是否已配置
if grep -q "GITHUB_TOKEN" "$PROFILE_FILE"; then
    echo "⚠️  检测到 GITHUB_TOKEN 已配置"
    echo ""
    read -p "是否要更新配置？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ 取消配置"
        exit 0
    fi
    
    # 删除旧配置
    echo "🗑️  删除旧配置..."
    sed -i.bak '/^export GITHUB_TOKEN=/d' "$PROFILE_FILE"
    sed -i.bak '/^export GITHUB_REPO=/d' "$PROFILE_FILE"
    sed -i.bak '/^export WORKSPACE=/d' "$PROFILE_FILE"
    rm -f "${PROFILE_FILE}.bak"
fi

# 添加新配置
echo "📝 添加新配置到 $PROFILE_FILE..."
cat >> "$PROFILE_FILE" << EOF

# GitHub Issue Auto-Resolver (added by setup script on $(date))
export GITHUB_TOKEN="$GITHUB_TOKEN"
export GITHUB_REPO="$GITHUB_REPO"
export WORKSPACE="$WORKSPACE"
EOF

echo "✅ 配置已添加到 $PROFILE_FILE"
echo ""

# 使配置生效
echo "🔄 使配置生效..."
source "$PROFILE_FILE"

# 验证配置
echo ""
echo "🔍 验证配置..."
if [ -n "$GITHUB_TOKEN" ]; then
    echo "✅ GITHUB_TOKEN: 已配置 (${#GITHUB_TOKEN} 字符)"
else
    echo "❌ GITHUB_TOKEN: 未生效"
    echo ""
    echo "⚠️  请手动运行：source $PROFILE_FILE"
    exit 1
fi

if [ "$GITHUB_REPO" = "aprilvkuo/stock_agent" ]; then
    echo "✅ GITHUB_REPO: $GITHUB_REPO"
else
    echo "❌ GITHUB_REPO: 配置错误"
    exit 1
fi

if [ "$WORKSPACE" = "/Users/egg/.openclaw/workspace" ]; then
    echo "✅ WORKSPACE: $WORKSPACE"
else
    echo "❌ WORKSPACE: 配置错误"
    exit 1
fi

echo ""
echo "============================================================"
echo "✅ 配置完成！"
echo "============================================================"
echo ""
echo "📝 下一步:"
echo "  1. 测试脚本：cd $WORKSPACE && python3 scripts/auto_issue_resolver.py --dry-run"
echo "  2. 启动监控：python3 scripts/auto_issue_resolver.py --monitor"
echo ""
echo "📖 详细文档：docs/GITHUB_ENV_SETUP.md"
echo ""
