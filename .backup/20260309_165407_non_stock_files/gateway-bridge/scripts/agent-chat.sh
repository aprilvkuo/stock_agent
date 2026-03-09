#!/bin/bash
# Agent Chat - 快速与其他 Agent 对话的 CLI 工具

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NODE_SCRIPT="$SCRIPT_DIR/gateway-bridge.js"

case "$1" in
  list|ls)
    node "$NODE_SCRIPT" list
    ;;
  send|msg)
    shift
    node "$NODE_SCRIPT" send "$@"
    ;;
  help|--help|-h)
    cat << 'EOF'
Agent Chat - 与其他 Agent 通话

命令:
  agent-chat list              # 列出所有可用的 Agent
  agent-chat send <目标> <消息> # 向指定 Agent 发送消息

示例:
  agent-chat list
  agent-chat send researcher "请帮我搜索最新的 AI 论文"
  agent-chat send ai_scientist "分析完成，结果如下..."

目标可以是:
  - Agent 标签 (label)
  - 会话 ID (sessionKey)
EOF
    ;;
  *)
    echo "未知命令: $1"
    echo "运行 'agent-chat help' 查看用法"
    exit 1
    ;;
esac
