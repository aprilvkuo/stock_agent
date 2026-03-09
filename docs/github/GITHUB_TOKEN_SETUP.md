# ⚠️  GitHub Token 配置指南

## 问题

Push 失败，提示需要 `workflow` 权限：

```
refusing to allow a Personal Access Token to create or update workflow 
`.github/workflows/issue-notify.yml` without `workflow` scope
```

---

## 解决方案

### 1️⃣ 重新生成 GitHub Token

访问：https://github.com/settings/tokens

**选择 Fine-grained tokens**（新版）

### 2️⃣ 配置权限

**Repository permissions**:

| 权限 | 访问级别 | 说明 |
|------|---------|------|
| `Actions` | Read and write | **必需** - 运行工作流 |
| `Administration` | Read only | 仓库管理 |
| `Contents` | Read and write | **必需** - 读写代码 |
| `Issues` | Read and write | **必需** - 创建 Issue |
| `Pull requests` | Read and write | **必需** - 创建 PR |
| `Workflows` | Read and write | **必需** - 更新工作流 |
| `Metadata` | Read only | 读取元数据 |

**或经典 Token（Classic）** - 选择 scopes:
- ✅ `repo` (Full control of private repositories)
- ✅ `workflow` (Update GitHub Actions workflows)

### 3️⃣ 更新配置

```bash
cd /Users/egg/.openclaw/workspace

# 编辑配置文件
vim .env.github
# 或
nano .env.github
```

**填入新 Token**:
```bash
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
GITHUB_REPO=aprilvkuo/stock_agent
```

### 4️⃣ 重新推送

```bash
cd /Users/egg/.openclaw/workspace
git push origin main
```

---

## 验证配置

```bash
cd /Users/egg/.openclaw/workspace/memory/stock-system
python3 scripts/github_issue_manager.py
```

如果看到测试输出，说明配置成功！

---

## 临时方案（跳过工作流文件）

如果暂时无法配置 workflow 权限，可以先推送其他文件：

```bash
# 暂时移除工作流文件
git rm --cached .github/workflows/*.yml
git commit -m "temp: 移除工作流文件（等待 Token 配置）"
git push origin main
```

等 Token 配置好后再添加工作流文件：
```bash
git add .github/workflows/*.yml
git commit -m "add: GitHub Actions 工作流"
git push origin main
```

---

## 完整权限列表

**Fine-grained token 权限**:

```
Account permissions:
- No permissions needed

Repository access:
- Only select repositories → stock_agent

Repository permissions:
- Actions: Read and write ⭐
- Administration: Read only
- Contents: Read and write ⭐
- Issues: Read and write ⭐
- Metadata: Read only
- Pull requests: Read and write ⭐
- Workflows: Read and write ⭐
```

**带 ⭐ 的为必需权限**

---

**配置完成后，系统将自动创建 GitHub Issue 和 PR！** 🚀
