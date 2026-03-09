# 🤖 GitHub Bot 账号配置指南

**版本**: v1.0  
**更新日期**: 2026-03-09  
**状态**: ⏳ 待配置

---

## 🎯 为什么使用 Bot 账号？

### 优势

1. **专业化** - Issue 创建者显示为 Bot，不是个人账号
2. **职责分离** - 个人账号用于开发，Bot 账号用于自动化
3. **清晰标识** - 一眼看出哪些是自动化创建的 Issue
4. **符合最佳实践** - GitHub 官方推荐的自动化方案
5. **易于管理** - 独立的 Token，独立的权限控制

### 对比

| 方案 | 创建者显示 | 管理复杂度 | 推荐度 |
|------|-----------|-----------|--------|
| 个人账号 | `aprilvkuo` | ⭐ 简单 | ⭐⭐ |
| Bot 账号 | `stock-agent-bot` | ⭐⭐ 中等 | ⭐⭐⭐⭐⭐ |
| 多 Agent 账号 | `programmer-agent` 等 | ⭐⭐⭐⭐ 复杂 | ⭐⭐ |

---

## 📋 配置步骤

### Step 1: 注册 Bot 账号

**访问**: https://github.com/signup

**填写信息**:

| 字段 | 建议值 | 说明 |
|------|--------|------|
| Username | `stock-agent-bot` | 如果已被占用，尝试 `stock-agent-bot-cn` |
| Email | `stock-agent-bot@proton.me` | 建议使用专门邮箱 |
| Password | (生成强密码) | 保存到密码管理器 |

**验证邮箱**:
- 检查邮箱
- 点击验证链接

---

### Step 2: 完善 Bot Profile

登录后：https://github.com/settings/profile

**建议配置**:

```
Name: Stock Agent Bot
Bio: Automated bot for Stock Multi-Agent System - Creating issues, managing workflow, and tracking improvements.
Location: China
Website: https://github.com/aprilvkuo/stock_agent
```

**头像**（可选）:
- 使用机器人相关的图片
- 或者 AI 生成的 logo
- 建议尺寸：400x400

---

### Step 3: 生成 Bot Token

**访问**: https://github.com/settings/tokens

**选择**: Fine-grained tokens → Generate new token

#### 基础配置

| 字段 | 值 |
|------|-----|
| Token name | `stock-workflow-bot` |
| Expiration | No expiration (或 1 年) |
| Repository access | Only select repositories |
| Select repositories | `aprilvkuo/stock_agent` |

#### Permissions（关键）

**Repository permissions**:

| 权限 | 访问级别 | 说明 |
|------|---------|------|
| `Actions` | Read and write | 运行工作流 |
| `Contents` | Read and write | 读写代码 |
| `Issues` | Read and write | 创建 Issue ⭐ |
| `Pull requests` | Read and write | 创建 PR ⭐ |
| `Workflows` | Read and write | 更新工作流 ⭐ |
| `Metadata` | Read only | 读取元数据 |

**生成 Token**:
- 点击 **Generate token**
- **立即复制 Token**（格式：`github_pat_xxx`）
- ⚠️ **只显示一次**，丢失需要重新生成

---

### Step 4: 配置到系统环境变量

**编辑** `~/.zshrc`:

```bash
vim ~/.zshrc
```

**添加**:

```bash
# GitHub Bot Token (用于自动化创建 Issue/PR)
export GITHUB_BOT_TOKEN="github_pat_BOT_TOKEN_HERE"
export GITHUB_BOT_USERNAME="stock-agent-bot"

# 个人 Token (用于日常开发，可选)
# export GITHUB_TOKEN="github_pat_PERSONAL_TOKEN"
```

**立即生效**:

```bash
source ~/.zshrc
```

**验证**:

```bash
echo $GITHUB_BOT_TOKEN
# 应该显示：github_pat_xxx...

echo $GITHUB_BOT_USERNAME
# 应该显示：stock-agent-bot
```

---

### Step 5: 测试 Bot 账号

**测试脚本**:

```bash
cd /Users/egg/.openclaw/workspace/memory/stock-system
python3 << 'EOF'
import requests
import os

token = os.getenv("GITHUB_BOT_TOKEN")
username = os.getenv("GITHUB_BOT_USERNAME")
repo = "aprilvkuo/stock_agent"

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json"
}

# 测试 1: 验证 Bot 身份
print("Test 1: Verify Bot Identity")
r = requests.get("https://api.github.com/user", headers=headers)
if r.status_code == 200:
    user = r.json()
    print(f"  ✅ Bot: {user['login']}")
    print(f"  匹配：{user['login'] == username}")
else:
    print(f"  ❌ 失败：{r.status_code}")

# 测试 2: 创建测试 Issue
print("\nTest 2: Create Test Issue")
data = {
    "title": "[BOT TEST] Bot 账号测试",
    "body": f"这是由 Bot 账号 @{username} 创建的测试 Issue"
}
r = requests.post(f"https://api.github.com/repos/{repo}/issues", 
                  headers=headers, json=data)
if r.status_code == 201:
    issue = r.json()
    print(f"  ✅ Issue 创建成功")
    print(f"  编号：#{issue['number']}")
    print(f"  创建者：{issue['user']['login']}")
    print(f"  链接：{issue['html_url']}")
else:
    print(f"  ❌ 失败：{r.json()}")
EOF
```

**预期结果**:

```
Test 1: Verify Bot Identity
  ✅ Bot: stock-agent-bot
  匹配：True

Test 2: Create Test Issue
  ✅ Issue 创建成功
  编号：#3
  创建者：stock-agent-bot
  链接：https://github.com/aprilvkuo/stock_agent/issues/3
```

---

## 🔍 验证配置

### 检查清单

- [ ] Bot 账号已注册
- [ ] Bot Profile 已完善
- [ ] Bot Token 已生成
- [ ] Token 已添加到 `~/.zshrc`
- [ ] 运行 `source ~/.zshrc`
- [ ] 测试脚本通过
- [ ] Issue 创建者显示为 Bot

### 验证命令

```bash
# 检查环境变量
echo $GITHUB_BOT_TOKEN | head -c 20 && echo "..."
echo $GITHUB_BOT_USERNAME

# 检查代码配置
cd /Users/egg/.openclaw/workspace/memory/stock-system
grep "GITHUB_BOT" scripts/github_issue_manager.py
```

---

## 📊 效果对比

### Before（个人账号）

```
Issue #2 created by aprilvkuo
```

### After（Bot 账号）

```
Issue #3 created by stock-agent-bot
```

---

## 🛡️ 安全建议

### Bot Token 安全

1. **不要分享** - Bot Token 和个人 Token 一样重要
2. **定期轮换** - 每 6-12 个月更换一次
3. **最小权限** - 只给必要的权限
4. **监控使用** - 定期检查 Bot 活动

### 账号安全

1. **启用 2FA** - Bot 账号也要开启两步验证
2. **专门邮箱** - 使用独立的邮箱注册
3. **强密码** - 使用密码管理器生成
4. **限制访问** - 只有授权人员知道密码

---

## 🔄 故障排查

### 问题 1: Token 无效

**症状**:
```
401 Unauthorized
```

**解决**:
1. 检查 Token 是否正确复制
2. 检查 Token 是否过期
3. 重新生成 Token

### 问题 2: 权限不足

**症状**:
```
403 Forbidden
```

**解决**:
1. 检查 Repository access 是否包含目标仓库
2. 检查 Permissions 是否正确配置
3. 确认 Bot 账号已添加到仓库协作者（如果需要）

### 问题 3: 环境变量未生效

**症状**:
```bash
echo $GITHUB_BOT_TOKEN
# 显示为空
```

**解决**:
1. 确认 `~/.zshrc` 已保存
2. 运行 `source ~/.zshrc`
3. 重启终端

---

## 📖 相关文档

- [GITHUB_TOKEN_SECURITY.md](./GITHUB_TOKEN_SECURITY.md) - Token 安全配置
- [GITHUB_WORKFLOW_GUIDE.md](./memory/stock-system/GITHUB_WORKFLOW_GUIDE.md) - 工作流使用指南
- [GITHUB_WORKFLOW_COMPLETE.md](./GITHUB_WORKFLOW_COMPLETE.md) - 配置完成报告

---

## 🎯 下一步

配置完成后：

1. ✅ 运行测试脚本验证
2. ✅ 创建一个新的改进工单测试
3. ✅ 确认 Issue 创建者显示为 Bot
4. ✅ 更新文档记录配置信息

---

**配置日期**: 2026-03-09  
**维护者**: 系统 Agent  
**Bot 账号**: @stock-agent-bot（待创建）
