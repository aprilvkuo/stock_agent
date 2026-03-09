# 📊 股票多 Agent 系统监控网站

## 🚀 快速启动

### 方式 1: 直接启动

```bash
cd /Users/egg/.openclaw/workspace/shared/stock-system/web
python3 app.py
```

### 方式 2: 使用启动脚本

```bash
./start.sh
```

### 方式 3: 后台运行

```bash
nohup python3 app.py > monitor.log 2>&1 &
```

## 🌐 访问地址

启动后访问：**http://localhost:5001**

> 💡 如果 5001 端口被占用，修改 `app.py` 中的端口号即可

## 📁 文件结构

```
web/
├── app.py              # Flask 后端
├── templates/
│   └── index.html      # 主页面
├── start.sh            # 启动脚本
└── README.md           # 说明文档
```

## 🎯 功能特性

- ✅ 实时显示系统状态（各 Agent 就绪情况）
- ✅ 已完成分析列表（表格展示）
- ✅ 待验证预测追踪
- ✅ 自动刷新（每 30 秒）
- ✅ 红涨绿跌配色（符合中国投资者习惯）
- ✅ 响应式设计（支持手机/平板/桌面）

## 📊 数据源

从以下目录读取数据：
```
/Users/egg/.openclaw/workspace/agents/stock-coordinator/data/
├── queue/requests/       # 请求文件
├── queue/results/        # 分析结果
└── validation-queue.md   # 验证队列
```

## 🔧 依赖

- Python 3.8+
- Flask

安装依赖：
```bash
pip3 install flask
```

## 🎨 界面预览

- **深色主题**：护眼，适合长时间查看
- **Tailwind CSS**：现代化 UI
- **自动刷新**：无需手动刷新页面

---

*股票多 Agent 系统 · 实时监控*
