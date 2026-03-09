# 🌐 Web 服务器配置说明

**配置日期**: 2026-03-08 13:54  
**配置版本**: v1.0  
**绑定地址**: `0.0.0.0:5001` (所有网络接口)

---

## ✅ 当前配置

### 绑定地址
```python
host='0.0.0.0'  # 所有网络接口
port=5001       # 端口号
```

### 访问地址

| 访问方式 | URL | 说明 |
|----------|-----|------|
| **本地访问** | http://localhost:5001 | 本机浏览器访问 |
| **局域网访问** | http://0.0.0.0:5001 | 绑定地址 |
| **IP 访问** | http://<你的 IP>:5001 | 从其他设备访问 |

---

## 🎯 获取本机 IP 地址

### macOS
```bash
# WiFi 接口
ipconfig getifaddr en0

# 有线网络
ipconfig getifaddr en1
```

### Linux
```bash
hostname -I | awk '{print $1}'
```

### 示例
如果你的 IP 是 `192.168.1.100`，则访问：
```
http://192.168.1.100:5001
```

---

## 📁 配置文件位置

| 文件 | 路径 | 说明 |
|------|------|------|
| **主程序** | `/Users/egg/.openclaw/workspace/shared/stock-system/web/app.py` | Flask 应用 |
| **启动脚本** | `/Users/egg/.openclaw/workspace/shared/stock-system/web/start.sh` | 启动脚本 |
| **日志文件** | `/tmp/flask.log` | 运行日志 |

---

## 🚀 启动方式

### 方式 1: 直接启动
```bash
cd /Users/egg/.openclaw/workspace/shared/stock-system/web
python3 app.py
```

### 方式 2: 使用启动脚本
```bash
cd /Users/egg/.openclaw/workspace/shared/stock-system/web
./start.sh
```

### 方式 3: 后台运行
```bash
cd /Users/egg/.openclaw/workspace/shared/stock-system/web
nohup python3 app.py > /tmp/flask.log 2>&1 &
```

---

## 🔧 修改端口

如需修改端口号（例如改为 5000），编辑 `app.py`：

```python
# 修改前
app.run(host='0.0.0.0', port=5001, debug=True)

# 修改后
app.run(host='0.0.0.0', port=5000, debug=True)
```

然后重启服务器。

---

## 🔒 安全说明

### 当前配置
- ✅ **绑定地址**: `0.0.0.0` (允许外部访问)
- ✅ **端口**: 5001
- ⚠️ **Debug 模式**: 开启（开发环境）

### 生产环境建议
如果部署到公网，建议：
1. 关闭 Debug 模式
2. 添加防火墙规则
3. 使用 Nginx 反向代理
4. 启用 HTTPS

```python
# 生产环境配置
app.run(host='0.0.0.0', port=5001, debug=False)
```

---

## 📊 可用页面

| 页面 | URL | 功能 |
|------|-----|------|
| **主页** | http://localhost:5001/ | 系统监控首页 |
| **持仓管理** | http://localhost:5001/holdings | 持仓股票管理 |
| **Agent 状态** | http://localhost:5001/agents | Agent 运行状态 |
| **Agent 能力** | http://localhost:5001/agents-capability | Agent 能力说明 |
| **进化报告** | http://localhost:5001/evolution | 系统进化报告 |

---

## 🔍 故障排查

### 1. 无法访问
```bash
# 检查进程
ps aux | grep app.py

# 检查端口占用
lsof -i :5001

# 查看日志
cat /tmp/flask.log
```

### 2. 端口被占用
```bash
# 杀掉旧进程
pkill -9 -f "python3 app.py"

# 重新启动
python3 app.py
```

### 3. 外部设备无法访问
```bash
# 检查防火墙
sudo ufw status  # Linux
sudo pfctl -s rules  # macOS

# 开放端口
sudo ufw allow 5001  # Linux
```

---

## 📝 配置历史

| 日期 | 变更 | 说明 |
|------|------|------|
| 2026-03-08 13:54 | 绑定地址改为 0.0.0.0 | 支持外部访问 |
| 2026-03-08 13:54 | 更新启动提示 | 显示多种访问方式 |

---

## ✅ 配置确认

**当前状态**:
- [x] 绑定地址：`0.0.0.0`
- [x] 端口号：`5001`
- [x] 支持本地访问
- [x] 支持局域网访问
- [x] 支持外部 IP 访问

**配置已永久生效！** 🎉

---

**文档版本**: v1.0  
**最后更新**: 2026-03-08 13:54  
**维护位置**: `/Users/egg/.openclaw/workspace/shared/stock-system/web/WEB_SERVER_CONFIG.md`
