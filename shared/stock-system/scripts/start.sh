#!/bin/bash
# 股票多 Agent 系统 - 启动脚本

SCRIPTS_DIR="/Users/egg/.openclaw/workspace/shared/stock-system/scripts"
DATA_DIR="/Users/egg/.openclaw/workspace/agents/stock-coordinator/data"
LOGS_DIR="$DATA_DIR/logs"

# 创建日志目录
mkdir -p "$LOGS_DIR"

echo "🚀 股票多 Agent 系统启动中..."
echo ""

# 检查是否已经在运行
if pgrep -f "daemon.py" > /dev/null; then
    echo "⚠️  守护进程已在运行"
    echo ""
    ps aux | grep daemon.py | grep -v grep
    echo ""
    echo "要重启，先运行：./stop.sh"
    exit 0
fi

# 启动守护进程
echo "📊 启动守护进程..."
cd "$SCRIPTS_DIR"
nohup python3 daemon.py > "$LOGS_DIR/daemon.log" 2>&1 &

PID=$!
echo "✅ 守护进程已启动 (PID: $PID)"
echo ""

# 等待 2 秒检查是否成功启动
sleep 2
if ps -p $PID > /dev/null; then
    echo "🟢 系统运行正常"
    echo ""
    echo "📊 监控网站：http://localhost:5001"
    echo "🤖 Agent 状态：http://localhost:5001/agents"
    echo ""
    echo "📝 日志文件：$LOGS_DIR/daemon.log"
    echo ""
    echo "要停止系统，运行：./stop.sh"
else
    echo "❌ 守护进程启动失败"
    echo "查看日志：cat $LOGS_DIR/daemon.log"
fi
