#!/bin/bash
# 启动所有自动任务

# 停止旧进程
pkill -9 -f "daemon.py" 2>/dev/null
pkill -9 -f "auto_task_queue.py" 2>/dev/null

sleep 2

# 启动守护进程
cd /Users/egg/.openclaw/workspace/shared/stock-system/scripts
nohup python3 daemon.py > /tmp/daemon.log 2>&1 &

# 启动定时任务队列（每 5 分钟）
while true; do
    python3 /Users/egg/.openclaw/workspace/shared/stock-system/scripts/auto_task_queue.py >> /tmp/daemon.log 2>&1
    sleep 300
done &

echo "✅ 所有服务已启动"
