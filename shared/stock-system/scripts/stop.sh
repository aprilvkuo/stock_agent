#!/bin/bash
# 股票多 Agent 系统 - 停止脚本

echo "🛑 停止股票多 Agent 系统..."
echo ""

# 查找并停止守护进程
PIDS=$(pgrep -f "daemon.py")

if [ -z "$PIDS" ]; then
    echo "⚠️  守护进程未运行"
    exit 0
fi

echo "找到进程：$PIDS"
echo ""

# 发送终止信号
kill $PIDS 2>/dev/null

# 等待进程结束
sleep 2

# 检查是否成功停止
if pgrep -f "daemon.py" > /dev/null; then
    echo "⚠️  进程未正常退出，强制终止..."
    pkill -9 -f "daemon.py"
fi

echo ""
echo "✅ 系统已停止"
