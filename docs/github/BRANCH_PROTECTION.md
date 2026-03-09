# 🛡️ Main 分支保护规则

**配置位置**: GitHub → Settings → Branches → Add rule

---

## 📋 必须配置的规则

### Branch name pattern

```
main
```

### Protection rules（勾选以下选项）

#### ✅ Require a pull request before merging

- [x] **Require a pull request before merging**
  - 强制要求 PR，禁止直接 push

- [x] **Require approvals**
  - Required number of approvals: `1`
  - 至少需要 1 人审核

- [ ] **Dismiss stale pull request approvals when new commits are pushed**
  - 新提交后撤销旧的批准（可选）

- [x] **Require review from Code Owners**
  - 需要代码所有者审核（如果配置了 CODEOWNERS）

#### ✅ Require status checks to pass before merging

- [x] **Require status checks to pass before merging**
  - CI 测试必须通过

- [x] **Require branches to be up to date before merging**
  - 分支必须是最新的

- **Status checks that are required**:
  - （配置 CI 后会自动显示）

#### ✅ Require conversation resolution before merging

- [x] **Require conversation resolution before merging**
  - 所有评论必须解决后才能合并

#### ✅ Include administrators

- [x] **Include administrators**
  - 管理员也要遵守规则（重要！）

---

## 🔒 额外安全规则（可选）

### ✅ Restrict who can push to matching branches

- [ ] **Restrict who can push to matching branches**
  - 限制谁能 push
  - 添加：协调 Agent、质检 Agent

### ✅ Require linear history

- [ ] **Require linear history**
  - 要求线性历史（禁止 merge commit）
  - 强制使用 rebase 或 squash

### ✅ Require signed commits

- [ ] **Require signed commits**
  - 要求签名提交（高安全场景）

### ✅ Require deployments to succeed

- [ ] **Require deployments to succeed before merging**
  - 部署成功后才能合并

---

## 📊 配置后效果

### Before（无保护）

```bash
# 任何人都可以直接 push
git checkout main
git commit -m "随便改改"
git push origin main  # ✅ 成功（危险！）
```

### After（有保护）

```bash
# 尝试直接 push
git checkout main
git commit -m "随便改改"
git push origin main  # ❌ 失败！

# 错误信息：
# remote: error: protected branch hook declined
# remote: error: GH006: Protected branch update failed
# To https://github.com/xxx/xxx.git
#  ! [remote rejected] main -> main (protected branch hook declined)
```

### 正确做法

```bash
# 1. 创建分支
git checkout -b feature/xxx

# 2. 开发提交
git add -A
git commit -m "feat: 添加 xxx 功能"

# 3. 推送分支
git push origin feature/xxx

# 4. GitHub 创建 PR
# 5. Code Review
# 6. Merge 到 main
```

---

## 🎯 配置步骤

### 1. 访问分支设置

```
https://github.com/aprilvkuo/stock_agent/settings/branches
```

### 2. 添加规则

1. 点击 **Add rule**
2. Branch name pattern: `main`
3. 勾选上述规则
4. 点击 **Create**

### 3. 验证配置

```bash
# 尝试直接 push 到 main
git checkout main
git commit --allow-empty -m "test: 测试分支保护"
git push origin main

# 应该被拒绝：
# ! [remote rejected] main -> main (protected branch hook declined)
```

---

## 📖 相关文档

- [CONTRIBUTING.md](./CONTRIBUTING.md) - 贡献指南
- [PULL_REQUEST_TEMPLATE.md](./.github/pull_request_template.md) - PR 模板
- [BRANCH_NAMING.md](./BRANCH_NAMING.md) - 分支命名规范

---

## ⚠️ 注意事项

1. **配置前通知团队** - 避免影响正在进行的工作
2. **先配置 CI** - 否则无法合并（状态检查会失败）
3. **测试规则** - 配置后验证是否生效
4. **例外情况** - 紧急 hotfix 可以临时关闭规则

---

**配置完成后，团队开发流程就规范了！** 🎉
