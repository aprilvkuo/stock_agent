# 🌐 外网访问配置指南

**更新时间**: 2026-03-09  
**公网 IP**: 103.151.172.86  
**服务端口**: 5001

---

## 📍 访问地址

### 本地访问（局域网内）
```
http://localhost:5001
http://127.0.0.1:5001
```

### 外网访问（任何地方）
```
http://103.151.172.86:5001
```

### v2.0 报告页面
```
http://103.151.172.86:5001/v2-reports
```

---

## 🔧 方案一：直接访问（推荐 ⭐）

### 当前配置

Web 服务已绑定到 `0.0.0.0:5001`，允许所有网络接口访问。

**验证配置**:
```bash
# 查看 app.py 中的绑定地址
grep "app.run" /Users/egg/.openclaw/workspace/shared/stock-system/web/app.py

# 应该显示：
# app.run(host='0.0.0.0', port=5001, debug=False)
```

### 防火墙设置

如果外网无法访问，可能需要开放端口：

**macOS 防火墙**:
1. 系统偏好设置 → 安全性与隐私 → 防火墙
2. 防火墙选项 → 添加 Python
3. 允许传入连接

**或者临时关闭防火墙测试**:
```bash
# 系统偏好设置中关闭
```

### 路由器端口转发（如果在内网）

如果服务器在路由器后面，需要在路由器设置端口转发：

1. 登录路由器管理页面（通常 192.168.1.1）
2. 找到"端口转发"或"虚拟服务器"
3. 添加规则：
   - 外部端口：5001
   - 内部 IP: 服务器的局域网 IP
   - 内部端口：5001
   - 协议：TCP

---

## 🔧 方案二：使用 Cloudflare Tunnel（最安全 ⭐⭐⭐）

**优点**:
- ✅ 无需开放端口
- ✅ 免费 HTTPS
- ✅ 隐藏真实 IP
- ✅ 自带 DDOS 防护

### 安装 cloudflared

```bash
# macOS
brew install cloudflared

# 或者下载
curl -L --output /usr/local/bin/cloudflared https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-arm64
chmod +x /usr/local/bin/cloudflared
```

### 创建 Tunnel

```bash
# 登录 Cloudflare
cloudflared tunnel login

# 创建 tunnel
cloudflared tunnel create stock-web
```

### 配置 config.yml

创建 `~/.cloudflared/config.yml`:

```yaml
tunnel: stock-web
credentials-file: /Users/egg/.cloudflared/stock-web.json

ingress:
  - hostname: stock.yourdomain.com
    service: http://localhost:5001
  - service: http_status:404
```

### 运行 Tunnel

```bash
# 前台运行
cloudflared tunnel run stock-web

# 后台运行
nohup cloudflared tunnel run stock-web > /tmp/cloudflared.log 2>&1 &
```

### 访问地址

配置 DNS 后访问：
```
https://stock.yourdomain.com
```

---

## 🔧 方案三：使用 ngrok（快速测试 ⭐⭐）

**优点**:
- ✅ 快速设置
- ✅ 免费 HTTPS
- ✅ 临时测试完美

### 安装 ngrok

```bash
# macOS
brew install ngrok

# 或者下载
curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc
```

### 运行 ngrok

```bash
# 启动隧道
ngrok http 5001
```

### 访问地址

ngrok 会生成一个随机域名：
```
https://xxxx-xxxx-xxxx.ngrok.io
```

---

## 🔧 方案四：使用 frp 内网穿透（国内速度快 ⭐⭐）

### 配置 frpc

创建 `/Users/egg/.openclaw/workspace/shared/stock-system/web/frpc.ini`:

```ini
[common]
server_addr = your-frp-server.com
server_port = 7000
token = your-token

[stock-web]
type = tcp
local_ip = 127.0.0.1
local_port = 5001
remote_port = 5001
```

### 运行 frpc

```bash
frpc -c frpc.ini
```

### 访问地址

```
http://your-frp-server.com:5001
```

---

## 🔒 安全建议

### 1. 启用 HTTPS（强烈推荐）

**使用 Let's Encrypt**:

```bash
# 安装 certbot
brew install certbot

# 获取证书
sudo certbot certonly --standalone -d yourdomain.com

# 配置 Nginx 反向代理 + SSL
```

### 2. 添加基础认证

修改 `app.py` 添加简单密码保护：

```python
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    if username == "admin" and password == "your-password":
        return username

@app.route('/v2-reports')
@auth.login_required
def v2_reports():
    return render_template('v2-reports.html')
```

### 3. 限制访问 IP

在防火墙中只允许信任的 IP：

```bash
# macOS 防火墙
# 系统偏好设置 → 安全性与隐私 → 防火墙 → 防火墙选项
# 添加特定 IP 允许规则
```

### 4. 使用反向代理（Nginx）

安装 Nginx：
```bash
brew install nginx
```

配置 `/usr/local/etc/nginx/nginx.conf`:
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

启动 Nginx：
```bash
brew services start nginx
```

---

## 📊 当前状态检查

### 检查 Web 服务是否运行

```bash
ps aux | grep "app.py" | grep -v grep
```

### 检查端口监听

```bash
lsof -i :5001
```

### 测试本地访问

```bash
curl http://localhost:5001/api/v2/logs?limit=1
```

### 测试外网访问

从手机或其他网络访问：
```
http://103.151.172.86:5001/v2-reports
```

---

## 🐛 故障排查

### Q: 外网无法访问？

**检查步骤**:
1. 确认 Web 服务正在运行
2. 确认绑定到 `0.0.0.0` 而不是 `127.0.0.1`
3. 检查防火墙是否开放 5001 端口
4. 检查路由器端口转发（如果在内网）
5. 测试本地访问是否正常

### Q: 访问速度慢？

**解决方案**:
1. 使用 Cloudflare Tunnel（有 CDN 加速）
2. 使用国内 frp 服务器
3. 优化图片/资源大小

### Q: 如何限制只允许特定 IP 访问？

**方案**:
1. 使用 Nginx 的 `allow/deny` 指令
2. 使用防火墙规则
3. 在 app.py 中添加 IP 白名单中间件

---

## 📱 推荐方案

### 个人使用（临时）
→ **ngrok**（快速、简单）

### 长期使用（生产）
→ **Cloudflare Tunnel**（安全、免费、HTTPS）

### 国内用户
→ **frp**（速度快）

### 有域名
→ **Nginx 反向代理 + Let's Encrypt SSL**

---

## 🎯 快速开始

**最简单的方式**（直接访问）:

1. 确认 Web 服务运行
2. 外网访问：`http://103.151.172.86:5001/v2-reports`
3. 如果无法访问，检查防火墙

**最安全的方式**（Cloudflare Tunnel）:

1. 安装 cloudflared
2. 创建 tunnel
3. 配置域名
4. 访问：`https://stock.yourdomain.com`

---

**维护者**: 小助理 🤖  
**最后更新**: 2026-03-09
