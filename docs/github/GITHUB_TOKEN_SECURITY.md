# 🔐 GitHub Token 安全配置指南

**更新日期**: 2026-03-09 18:45  
**安全级别**: ✅ 系统环境变量（推荐）

---

## ⚠️ 为什么不用 .env 文件？

### 风险
1. **Git 误提交** - 即使有 `.gitignore`，也可能误操作
2. **文件泄露** - 备份、同步时可能泄露
3. **权限问题** - 其他用户可能读取文件
4. **GitHub Secret Scanning** - 会被检测并阻止推送

### 更好的方案
✅ **系统环境变量** - 最安全，不会进入文件系统

---

## 🚀 配置方法（3 选 1）

### 方案 1：~/.zshrc（推荐 - 永久生效）

**设置**：
```bash
# 添加到 ~/.zshrc
echo 'export GITHUB_TOKEN="github_pat_xxxxxxxxxxxxx"' >> ~/.zshrc
echo 'export GITHUB_REPO="aprilvkuo/stock_agent"' >> ~/.zshrc

# 立即生效
source ~/.zshrc

# 验证
echo $GITHUB_TOKEN
```

**优点**：
- ✅ 永久生效
- ✅ 所有终端会话共享
- ✅ 不会进入 Git
- ✅ 系统级别安全

**缺点**：
- ⚠️ 需要重启终端或 source

---

### 方案 2：当前会话（临时测试）

**设置**：
```bash
export GITHUB_TOKEN="github_pat_xxxxxxxxxxxxx"
export GITHUB_REPO="aprilvkuo/stock_agent"
```

**优点**：
- ✅ 快速测试
- ✅ 不影响其他会话

**缺点**：
- ❌ 关闭终端后失效
- ❌ 每个新终端都要设置

---

### 方案 3：macOS 钥匙串（最安全）

**设置**：
```bash
# 存储到钥匙串
security add-generic-password -s github_token -a stock_agent -w "github_pat_xxxxxxxxxxxxx"

# 读取（在脚本中）
GITHUB_TOKEN=$(security find-generic-password -s github_token -a stock_agent -w)
export GITHUB_TOKEN
```

**优点**：
- ✅ macOS 系统级加密存储
- ✅ 最安全
- ✅ 永久保存

**缺点**：
- ⚠️ 需要额外命令读取
- ⚠️ 仅 macOS 支持

---

## 📝 代码读取方式

### Python

```python
import os

# 直接从系统环境变量读取
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')

# 如果为空，提示用户
if not GITHUB_TOKEN:
    print("⚠️  请设置 GITHUB_TOKEN 环境变量")
    print("   echo 'export GITHUB_TOKEN=xxx' >> ~/.zshrc")
```

### Shell 脚本

```bash
#!/bin/bash

# 读取环境变量
TOKEN="${GITHUB_TOKEN}"

if [ -z "$TOKEN" ]; then
    echo "⚠️  请设置 GITHUB_TOKEN 环境变量"
    exit 1
fi
```

---

## ✅ 当前配置（已设置）

**系统**: macOS  
**Shell**: zsh  
**配置文件**: `~/.zshrc`

**已设置变量**：
```bash
export GITHUB_TOKEN="github_pat_YOUR_TOKEN_HERE"  # 替换为你的真实 Token
export GITHUB_REPO="aprilvkuo/stock_agent"
```

**验证**：
```bash
$ echo $GITHUB_TOKEN
github_pat_11ACIBDCY...  # 显示完整 token

$ echo $GITHUB_REPO
aprilvkuo/stock_agent
```

---

## 🔍 安全检查

### 检查是否已设置

```bash
if [ -n "$GITHUB_TOKEN" ]; then
    echo "✅ GITHUB_TOKEN 已设置"
else
    echo "❌ GITHUB_TOKEN 未设置"
fi
```

### 检查是否泄露到 Git

```bash
cd /Users/egg/.openclaw/workspace

# 检查 Git 历史
git log --all --full-history -- .env.github

# 检查当前文件
git ls-files | grep -i env

# 应该没有任何输出
```

### 检查 GitHub 是否检测到

访问：https://github.com/aprilvkuo/stock_agent/security/secret-scanning

应该显示 "No secrets detected"

---

## 🛡️ 安全最佳实践

### ✅ 推荐做法

1. **使用系统环境变量** - 最安全
2. **定期轮换 Token** - 每 3-6 个月
3. **最小权限原则** - 只给必要权限
4. **监控 Token 使用** - GitHub Security 页面
5. **使用 Fine-grained Token** - 更细粒度控制

### ❌ 避免做法

1. **不要提交到 Git** - 即使有 .gitignore
2. **不要明文存储** - 避免 .env 文件
3. **不要分享 Token** - 每人独立 Token
4. **不要硬编码** - 代码中不要出现
5. **不要截图** - 包含 Token 的截图

---

## 🔄 Token 轮换流程

### 1. 生成新 Token

访问：https://github.com/settings/tokens

### 2. 更新系统变量

```bash
# 备份旧配置
cp ~/.zshrc ~/.zshrc.backup

# 更新 Token
sed -i '' 's/GITHUB_TOKEN="github_pat_.*/GITHUB_TOKEN="github_pat_NEW_TOKEN"/' ~/.zshrc

# 重新加载
source ~/.zshrc

# 验证
echo $GITHUB_TOKEN
```

### 3. 撤销旧 Token

访问：https://github.com/settings/tokens

找到旧 Token → 点击 **Delete**

### 4. 测试

```bash
cd /Users/egg/.openclaw/workspace/memory/stock-system
python3 scripts/github_issue_manager.py
```

---

## 📖 相关文档

- [GITHUB_WORKFLOW_COMPLETE.md](./GITHUB_WORKFLOW_COMPLETE.md) - 完整工作流指南
- [GITHUB_TOKEN_SETUP.md](./GITHUB_TOKEN_SETUP.md) - 原始配置指南（已废弃）

---

## 🎯 总结

**当前配置**：
- ✅ 系统环境变量（~/.zshrc）
- ✅ 不会进入 Git
- ✅ 所有终端共享
- ✅ 永久生效

**安全级别**：⭐⭐⭐⭐⭐（最高）

**下一步**：开始安全使用 GitHub Issues + PR 工作流！🚀

---

**配置日期**: 2026-03-09 18:45  
**配置者**: 系统 Agent
