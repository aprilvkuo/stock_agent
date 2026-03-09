#!/bin/bash
# 测试 Web 访问

echo "=== 测试 Web 服务访问 ==="
echo ""

# 测试本地访问
echo "1. 测试本地访问 (127.0.0.1)..."
curl -s -o /dev/null -w "HTTP 状态码：%{http_code}\n" "http://127.0.0.1:5001/api/v2/logs?limit=1"

# 测试局域网访问
echo "2. 测试局域网访问..."
LOCAL_IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo "unknown")
if [ "$LOCAL_IP" != "unknown" ]; then
    curl -s -o /dev/null -w "HTTP 状态码：%{http_code}\n" "http://$LOCAL_IP:5001/api/v2/logs?limit=1"
    echo "   局域网 IP: $LOCAL_IP"
else
    echo "   无法获取局域网 IP"
fi

# 测试公网访问
echo "3. 测试公网访问..."
curl -s --connect-timeout 5 -o /dev/null -w "HTTP 状态码：%{http_code}\n" "http://103.151.172.86:5001/api/v2/logs?limit=1"
echo "   公网 IP: 103.151.172.86"

echo ""
echo "=== 完成 ==="
