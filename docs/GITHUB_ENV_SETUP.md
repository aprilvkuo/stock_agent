# 🔧 Issue 自动处理系统 - 环境变量配置指南

**版本**: v3.0  
**更新日期**: 2026-03-09  
**维护者**: 程序员 Agent

---

## ⚠️ 重要说明

**从 v3.0 开始，GITHUB_TOKEN 必须从系统环境变量获取，不再支持 .env 文件！**

这是为了提高安全性，避免 Token 被意外提交到代码仓库。

---

## 📝 配置步骤

### Step 1: 获取 GitHub Token

1. 访问 GitHub: https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 填写 Token 说明（如 "Issue Auto-Resolver"）
4. 设置过期时间（建议 90 天）
5. 勾选以下权限：
   - ✅ `repo` (Full control of private repositories)
   - ✅ `workflow` (Update GitHub Action workflows)
   - ✅ `read:org` (Read organization data)
6. 点击 "Generate token"
7. **复制 Token**（只显示一次，请妥善保存）

---

### Step 2: 配置环境变量

#### macOS / Linux (Zsh)

**1. 编辑配置文件**:
```bash
vim ~/.zshrc
```

**2. 添加以下内容**:
```bash
# GitHub Issue Auto-Resolver
export GITHUB_TOKEN="github_pat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export GITHUB_REPO="aprilvkuo/stock_agent"
export WORKSPACE="/Users/egg/.openclaw/workspace"
```

**3. 保存并退出**:
```
:wq
```

**4. 使配置生效**:
```bash
source ~/.zshrc
```

#### macOS / Linux (Bash)

**1. 编辑配置文件**:
```bash
vim ~/.bash_profile
```

**2. 添加以下内容**:
```bash
# GitHub Issue Auto-Resolver
export GITHUB_TOKEN="github_pat_xxx"
export GITHUB_REPO="aprilvkuo/stock_agent"
export WORKSPACE="/Users/egg/.openclaw/workspace"
```

**3. 使配置生效**:
```bash
source ~/.bash_profile
```

#### Windows (PowerShell)

**1. 编辑配置文件**:
```powershell
notepad $PROFILE
```

**2. 添加以下内容**:
```powershell
# GitHub Issue Auto-Resolver
$env:GITHUB_TOKEN="github_pat_xxx"
$env:GITHUB_REPO="aprilvkuo/stock_agent"
$env:WORKSPACE="C:\Users\YourName\.openclaw\workspace"
```

**3. 使配置生效**:
```powershell
. $PROFILE
```

---

### Step 3: 验证配置

**1. 检查环境变量是否存在**:
```bash
echo $GITHUB_TOKEN
```

应该显示你的 Token（部分字符）。

**2. 检查 Token 格式**:
```bash
echo $GITHUB_TOKEN | grep "^github_pat_"
```

应该输出 Token（说明格式正确）。

**3. 测试脚本**:
```bash
cd /Users/egg/.openclaw/workspace
python3 scripts/auto_issue_resolver.py --dry-run
```

如果没有报错，说明配置成功！

---

## 🔍 故障排查

### 问题 1: "GITHUB_TOKEN 未配置"

**症状**:
```
❌ 错误：GITHUB_TOKEN 未配置！
```

**解决**:
1. 确认已添加到配置文件（~/.zshrc 或 ~/.bash_profile）
2. 运行 `source ~/.zshrc` 使配置生效
3. 重新打开终端
4. 运行 `echo $GITHUB_TOKEN` 验证

---

### 问题 2: Token 权限不足

**症状**:
```
403 Client Error: Forbidden
```

**解决**:
1. 检查 Token 权限是否包含：
   - ✅ `repo` (Full control)
   - ✅ `workflow`
   - ✅ `read:org`
2. 重新生成 Token 并确保勾选正确权限
3. 更新环境变量中的 Token

---

### 问题 3: Token 过期

**症状**:
```
401 Client Error: Unauthorized
```

**解决**:
1. 访问 https://github.com/settings/tokens
2. 检查 Token 是否过期
3. 生成新 Token
4. 更新环境变量
5. 运行 `source ~/.zshrc`

---

### 问题 4: 配置未生效

**症状**:
```bash
echo $GITHUB_TOKEN  # 显示空
```

**解决**:
```bash
# 1. 检查配置文件
cat ~/.zshrc | grep GITHUB_TOKEN

# 2. 重新加载配置
source ~/.zshrc

# 3. 如果还不行，重新打开终端
```

---

## 🛡️ 安全最佳实践

### ✅ 推荐

1. **使用环境变量** - 不要硬编码在代码中
2. **定期轮换 Token** - 每 90 天更换一次
3. **限制 Token 权限** - 只授予必要权限
4. **使用细粒度 Token** - 只访问特定仓库
5. **备份 Token** - 保存在密码管理器中

### ❌ 避免

1. **提交到 Git** - 不要将 Token 提交到代码仓库
2. **分享给他人** - Token 是私密的
3. **长期使用同一 Token** - 定期更换
4. **授予过多权限** - 最小权限原则
5. **明文存储** - 不要保存在明文文件中

---

## 📋 环境变量列表

| 变量名 | 必需 | 说明 | 示例 |
|--------|------|------|------|
| `GITHUB_TOKEN` | ✅ | GitHub API Token | `github_pat_xxx` |
| `GITHUB_REPO` | ❌ | 仓库名称（默认：aprilvkuo/stock_agent） | `aprilvkuo/stock_agent` |
| `WORKSPACE` | ❌ | 工作目录（默认：/Users/egg/.openclaw/workspace） | `/Users/egg/.openclaw/workspace` |

---

## 🔗 相关文档

- [ISSUE_AUTO_RESOLVER.md](./ISSUE_AUTO_RESOLVER.md) - 使用指南
- [GITHUB_TOKEN_SECURITY.md](./GITHUB_TOKEN_SECURITY.md) - Token 安全指南
- [CONTRIBUTING.md](./CONTRIBUTING.md) - 贡献指南

---

## 📞 获取帮助

如果遇到问题：

1. 检查本文档的故障排查部分
2. 查看脚本输出错误信息
3. 联系维护者：@programmer-agent

---

**维护者**: 程序员 Agent  
**最后更新**: 2026-03-09  
**下次审查**: 2026-04-09
