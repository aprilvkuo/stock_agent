#!/bin/bash
# 股票多 Agent 系统 - 快速启动脚本

echo "🚀 股票多 Agent 系统 - 快速启动"
echo "================================"
echo ""

# 检查进程
echo "📊 检查当前运行状态..."
DAEMON_PID=$(pgrep -f "daemon.py" | head -1)
WEB_PID=$(pgrep -f "app.py" | head -1)

if [ -n "$DAEMON_PID" ]; then
    echo "✅ 守护进程已运行 (PID: $DAEMON_PID)"
else
    echo "⚠️  守护进程未运行"
fi

if [ -n "$WEB_PID" ]; then
    echo "✅ Web 服务器已运行 (PID: $WEB_PID)"
else
    echo "⚠️  Web 服务器未运行"
fi

echo ""
echo "请选择操作:"
echo "1) 启动所有服务"
echo "2) 重启所有服务"
echo "3) 停止所有服务"
echo "4) 查看状态"
echo "5) 查看日志"
echo "6) 手动触发进化"
echo "q) 退出"
echo ""
read -p "请输入选项 (1-6 或 q): " choice

case $choice in
    1)
        echo ""
        echo "📦 启动所有服务..."
        
        # 启动守护进程
        echo "   启动守护进程..."
        cd /Users/egg/.openclaw/workspace/shared/stock-system/scripts
        nohup python3 daemon.py > /tmp/stock-daemon.log 2>&1 &
        sleep 2
        
        # 启动 Web 服务器
        echo "   启动 Web 服务器..."
        cd /Users/egg/.openclaw/workspace/shared/stock-system/web
        nohup python3 app.py > /tmp/stock-web.log 2>&1 &
        sleep 2
        
        # 验证启动
        if pgrep -f "daemon.py" > /dev/null && pgrep -f "app.py" > /dev/null; then
            echo ""
            echo "✅ 所有服务已启动!"
            echo ""
            echo "📊 访问地址:"
            echo "   监控首页：http://localhost:5001"
            echo "   进化报告：http://localhost:5001/evolution"
            echo "   Agent 状态：http://localhost:5001/agents"
        else
            echo ""
            echo "❌ 服务启动失败，请查看日志"
        fi
        ;;
        
    2)
        echo ""
        echo "🔄 重启所有服务..."
        
        # 停止现有服务
        pkill -f "daemon.py" 2>/dev/null
        pkill -f "app.py" 2>/dev/null
        sleep 1
        
        # 启动新服务
        cd /Users/egg/.openclaw/workspace/shared/stock-system/scripts
        nohup python3 daemon.py > /tmp/stock-daemon.log 2>&1 &
        sleep 2
        
        cd /Users/egg/.openclaw/workspace/shared/stock-system/web
        nohup python3 app.py > /tmp/stock-web.log 2>&1 &
        sleep 2
        
        echo ""
        echo "✅ 服务已重启!"
        echo ""
        echo "📊 访问地址:"
        echo "   监控首页：http://localhost:5001"
        echo "   进化报告：http://localhost:5001/evolution"
        ;;
        
    3)
        echo ""
        echo "🛑 停止所有服务..."
        pkill -f "daemon.py" 2>/dev/null
        pkill -f "app.py" 2>/dev/null
        sleep 1
        
        if ! pgrep -f "daemon.py" > /dev/null && ! pgrep -f "app.py" > /dev/null; then
            echo "✅ 所有服务已停止"
        else
            echo "⚠️  部分服务未停止，请检查进程"
        fi
        ;;
        
    4)
        echo ""
        echo "📊 系统状态:"
        echo ""
        
        # 守护进程状态
        if pgrep -f "daemon.py" > /dev/null; then
            echo "✅ 守护进程：运行中"
            echo "   PID: $(pgrep -f 'daemon.py' | tr '\n' ' ')"
        else
            echo "❌ 守护进程：未运行"
        fi
        
        # Web 服务器状态
        if pgrep -f "app.py" > /dev/null; then
            echo "✅ Web 服务器：运行中"
            echo "   PID: $(pgrep -f 'app.py' | tr '\n' ' ')"
        else
            echo "❌ Web 服务器：未运行"
        fi
        
        echo ""
        echo "📁 数据目录:"
        echo "   请求队列：$(ls /Users/egg/.openclaw/workspace/agents/stock-coordinator/data/queue/requests/*.md 2>/dev/null | wc -l) 个请求"
        echo "   分析结果：$(ls /Users/egg/.openclaw/workspace/agents/stock-coordinator/data/queue/results/*.md 2>/dev/null | wc -l) 份报告"
        echo "   进化报告：$(ls /Users/egg/.openclaw/workspace/agents/stock-coordinator/data/evolution-*.md 2>/dev/null | wc -l) 份报告"
        
        echo ""
        echo "📊 最新日志:"
        tail -5 /Users/egg/.openclaw/workspace/agents/stock-coordinator/data/logs/daemon-2026-03-08.log 2>/dev/null | sed 's/^/   /'
        ;;
        
    5)
        echo ""
        echo "📝 查看日志 (最近 20 行):"
        echo ""
        tail -20 /Users/egg/.openclaw/workspace/agents/stock-coordinator/data/logs/daemon-2026-03-08.log 2>/dev/null
        ;;
        
    6)
        echo ""
        echo "🧬 手动触发自我进化..."
        cd /Users/egg/.openclaw/workspace/shared/stock-system/scripts
        python3 self-evolution.py
        ;;
        
    q|Q)
        echo ""
        echo "👋 再见!"
        exit 0
        ;;
        
    *)
        echo ""
        echo "❌ 无效选项，请重新运行脚本"
        exit 1
        ;;
esac

echo ""
echo "📖 更多信息请查看:"
echo "   /Users/egg/.openclaw/workspace/shared/stock-system/PROJECT-SNAPSHOT.md"
echo ""
