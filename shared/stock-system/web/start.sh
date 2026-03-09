#!/bin/bash
# 股票监控系统启动脚本

echo "🚀 启动股票多 Agent 系统监控网站..."
echo "📊 访问地址："
echo "   本地访问：http://localhost:5001"
echo "   局域网访问：http://0.0.0.0:5001"
echo "   本机 IP：http://$(ipconfig getifaddr en0 2>/dev/null || hostname -I | awk '{print $1}'):5001"
echo "📁 工作目录：$(cd $(dirname $0) && pwd)"
echo "🔒 绑定地址：0.0.0.0 (所有网络接口，支持外部访问)"
echo ""

cd "$(dirname $0)"
python3 app.py
