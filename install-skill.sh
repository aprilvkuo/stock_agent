#!/bin/bash
# Skill 安装脚本
# 使用方法: ./install-skill.sh <作者>/<skill名称>
# 例如: ./install-skill.sh arun-8687/tavily-search

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# 检查参数
if [ $# -eq 0 ]; then
    print_error "请提供 skill 名称"
    echo "使用方法: ./install-skill.sh <作者>/<skill名称>"
    echo "例如: ./install-skill.sh arun-8687/tavily-search"
    exit 1
fi

SKILL_NAME="$1"
print_info "准备安装 skill: $SKILL_NAME"

# 设置目录
TEMP_DIR="/tmp/skill-install-$(date +%s)"
INSTALL_DIR="/opt/homebrew/lib/node_modules/openclaw/skills"

# 创建临时目录
mkdir -p "$TEMP_DIR"
cd "$TEMP_DIR"

print_info "下载 skill..."

# 尝试从 ClawHub 下载
CLAWHUB_URL="https://clawhub.ai/api/v1/skills/$SKILL_NAME/download"

if curl -L -o "$TEMP_DIR/skill-download.tmp" "$CLAWHUB_URL" 2>/dev/null; then
    # 检查下载的内容
    FILE_SIZE=$(stat -f%z "$TEMP_DIR/skill-download.tmp" 2>/dev/null || stat -c%s "$TEMP_DIR/skill-download.tmp" 2>/dev/null || echo "0")
    
    if [ "$FILE_SIZE" -lt 100 ]; then
        # 可能是错误信息
        CONTENT=$(cat "$TEMP_DIR/skill-download.tmp")
        if [[ "$CONTENT" == *"Not found"* ]] || [[ "$CONTENT" == *"error"* ]]; then
            print_error "从 ClawHub 下载失败: $CONTENT"
            rm -f "$TEMP_DIR/skill-download.tmp"
            
            # 尝试 GitHub
            print_info "尝试从 GitHub 下载..."
            GITHUB_URL="https://github.com/$(echo $SKILL_NAME | tr '/' '/').git"
            
            if git clone --depth 1 "$GITHUB_URL" "$TEMP_DIR/skill-source" 2>/dev/null; then
                print_success "从 GitHub 下载成功"
                cd "$TEMP_DIR/skill-source"
                
                # 打包成 .skill 文件
                zip -r "$TEMP_DIR/skill.zip" . -x ".git/*" 2>/dev/null
                mv "$TEMP_DIR/skill.zip" "$TEMP_DIR/skill-download.tmp"
            else
                print_error "无法从 GitHub 下载"
                exit 1
            fi
        fi
    fi
    
    mv "$TEMP_DIR/skill-download.tmp" "$TEMP_DIR/skill.zip"
    print_success "下载成功"
    
    # 解压并安装
    print_info "解压 skill..."
    SKILL_DIR_NAME=$(echo "$SKILL_NAME" | sed 's/\//-/g')
    sudo mkdir -p "$INSTALL_DIR/$SKILL_DIR_NAME"
    sudo unzip -o "$TEMP_DIR/skill.zip" -d "$INSTALL_DIR/$SKILL_DIR_NAME"
    
    print_success "安装成功: $SKILL_NAME"
    print_info "安装路径: $INSTALL_DIR/$SKILL_DIR_NAME"
    
    # 验证安装
    print_info "验证安装..."
    if openclaw skills list | grep -q "$SKILL_DIR_NAME"; then
        print_success "Skill 已成功安装并可用!"
    else
        print_warning "Skill 已安装，但可能需要重启 gateway"
        print_info "运行: openclaw gateway restart"
    fi
    
else
    print_error "下载失败"
    exit 1
fi

# 清理临时文件
rm -rf "$TEMP_DIR"
print_info "清理完成"

print_success "安装脚本执行完毕!"
