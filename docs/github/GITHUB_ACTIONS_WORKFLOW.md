# 🤖 GitHub Actions 自动化工单方案

**版本**: v1.0  
**实施日期**: 2026-03-09  
**状态**: ✅ 已实施

---

## 🎯 方案概述

使用 **GitHub Actions** 自动创建改进工单，无需注册 Bot 账号！

### 核心优势

| 特性 | 个人 Token | Bot 账号 | GitHub Actions |
|------|-----------|---------|----------------|
| 注册账号 | ❌ 不需要 | ✅ 需要 | ❌ **不需要** |
| Token 管理 | ⚠️ 手动 | ⚠️ 手动 | ✅ **自动** |
| 创建者显示 | `aprilvkuo` | `stock-agent-bot` | `github-actions[bot]` |
| 安全性 | 🟡 中等 | 🟡 中等 | 🟢 **高** |
| 维护成本 | 🟡 中等 | 🟡 中等 | 🟢 **低** |

---

## 📋 工作原理

### 触发方式

工作流支持 3 种触发方式：

#### 1️⃣ 手动触发（测试用）

```
GitHub → Actions → auto-improvement-ticket → Run workflow
```

填写表单：
- Provider（乙方 Agent）
- Consumer（甲方 Agent）
- Service Type（服务类型）
- Score（评分 1-5）
- Feedback（问题描述）

#### 2️⃣ 定时触发（自动检查）

```yaml
schedule:
  - cron: '0 9 * * *'  # 每天 9:00 UTC
```

可以配置为：
- 每天检查低分评价
- 每周生成质量报告
- 每月汇总改进项

#### 3️⃣ API 触发（程序调用）

从本地脚本触发：
```python
import requests

# 触发 GitHub Actions
requests.post(
    "https://api.github.com/repos/aprilvkuo/stock_agent/dispatches",
    headers={"Authorization": f"Bearer {TOKEN}"},
    json={
        "event_type": "create-improvement-ticket",
        "client_payload": {
            "provider": "programmer",
            "consumer": "coordinator",
            "service_type": "code_structure",
            "score": 2,
            "feedback": "需要改进"
        }
    }
)
```

---

## 🎭 创建者身份

### 显示效果

使用 GitHub Actions 创建的 Issue 会显示为：

```
🤖 github-actions[bot]
```

这是 **GitHub 官方的 Bot 账号**，所有 Actions 都使用这个身份。

### 示例

**Issue 创建者**:
```
github-actions[bot]
```

**Issue 内容标注**:
```markdown
**乙方**: @programmer-agent
**甲方**: @coordinator-agent
**触发方式**: GitHub Actions 自动化
```

---

## 🚀 使用方法

### 方法 1: 手动触发（推荐测试）

1. 访问：https://github.com/aprilvkuo/stock_agent/actions
2. 选择 **🎫 自动改进工单创建** 工作流
3. 点击 **Run workflow**
4. 填写表单：
   - **Provider**: `programmer`
   - **Consumer**: `coordinator`
   - **Service Type**: `code_structure`
   - **Score**: `2`
   - **Feedback**: `代码规范性不足`
5. 点击 **Run workflow**

**结果**:
- ✅ Issue 自动创建
- ✅ 创建者：`github-actions[bot]`
- ✅ 自动 @programmer-agent
- ✅ Label 自动添加

---

### 方法 2: 本地脚本触发

**Python 示例**:

```python
import requests
import os

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = "aprilvkuo/stock_agent"

def create_improvement_ticket(provider, consumer, service_type, score, feedback):
    """通过 GitHub Actions 创建改进工单"""
    
    url = f"https://api.github.com/repos/{REPO}/dispatches"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    
    payload = {
        "event_type": "create-improvement-ticket",
        "client_payload": {
            "provider": provider,
            "consumer": consumer,
            "service_type": service_type,
            "score": score,
            "feedback": feedback
        }
    }
    
    r = requests.post(url, headers=headers, json=payload)
    
    if r.status_code == 204:
        print("✅ 工单已触发创建")
    else:
        print(f"❌ 失败：{r.status_code}")
        print(r.json())

# 使用示例
create_improvement_ticket(
    provider="programmer",
    consumer="coordinator",
    service_type="code_structure",
    score=2,
    feedback="代码规范性不足，需要改进"
)
```

---

### 方法 3: 集成到现有系统

**修改 `improvement_ticket.py`**:

```python
import requests
import os

def create_ticket_via_actions(provider, consumer, service_type, rating):
    """通过 GitHub Actions 创建工单（替代直接 API 调用）"""
    
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    REPO = "aprilvkuo/stock_agent"
    
    url = f"https://api.github.com/repos/{REPO}/dispatches"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    
    payload = {
        "event_type": "create-improvement-ticket",
        "client_payload": {
            "provider": provider,
            "consumer": consumer,
            "service_type": service_type,
            "score": rating.get('overall_score', 2),
            "feedback": rating.get('feedback', '需要改进')
        }
    }
    
    r = requests.post(url, headers=headers, json=payload)
    return r.status_code == 204
```

---

## 📊 完整流程对比

### 方案 A: 直接 API 调用（之前）

```
本地脚本 → GitHub API → Issue 创建
创建者：aprilvkuo（个人账号）
```

### 方案 B: Bot 账号（需要注册）

```
本地脚本 → Bot Token → GitHub API → Issue 创建
创建者：stock-agent-bot（需注册）
```

### 方案 C: GitHub Actions（推荐）⭐

```
本地脚本 → Repository Dispatch → GitHub Actions → Issue 创建
创建者：github-actions[bot]（官方 Bot）
```

---

## ✅ 优势总结

### 为什么选择 GitHub Actions？

1. **无需注册 Bot 账号** - 使用官方 `github-actions[bot]`
2. **Token 自动管理** - GitHub 处理权限和安全性
3. **更专业** - 显示为自动化系统创建
4. **易于扩展** - 可以轻松添加定时任务、自动检查等
5. **审计友好** - 所有操作都有 Actions 日志
6. **成本低** - 免费额度足够使用

### 适用场景

- ✅ 自动化改进工单创建
- ✅ 定时质量检查
- ✅ 低分评价自动触发
- ✅ 周期性报告生成
- ✅ 跨仓库协调

---

## 🔧 配置说明

### 权限要求

工作流使用默认的 `GITHUB_TOKEN`，具有以下权限：
- ✅ Issues: Read and write
- ✅ Contents: Read and write
- ✅ Pull requests: Read and write

### 自定义权限（如需要）

如果 Actions 权限不足，可以在 `.github/workflows/auto-improvement-ticket.yml` 中添加：

```yaml
permissions:
  issues: write
  contents: read
  pull-requests: write
```

---

## 📖 使用示例

### 示例 1: 低分自动触发

当 Agent 评分 ≤ 3 时：

```python
if rating['overall_score'] <= 3:
    create_improvement_ticket(
        provider=agent_id,
        consumer=evaluator_id,
        service_type=service,
        score=rating['overall_score'],
        feedback=rating.get('feedback', '')
    )
```

### 示例 2: 定时质量检查

每周自动检查：

```yaml
schedule:
  - cron: '0 20 * * 5'  # 每周五 20:00 UTC
```

### 示例 3: 手动触发测试

在 GitHub Actions 页面手动运行，填写测试数据。

---

## 🎯 下一步

1. **测试工作流** - 手动触发一次
2. **验证 Issue 创建** - 确认创建者为 `github-actions[bot]`
3. **集成到现有系统** - 修改 `improvement_ticket.py`
4. **配置定时任务** - 设置自动检查时间

---

**文档版本**: v1.0  
**实施日期**: 2026-03-09  
**维护者**: 系统 Agent
