# 🌿 分支命名规范 (Branch Naming Convention)

**版本**: v1.0  
**实施日期**: 2026-03-09

---

## 🎯 命名格式

```
<type>/<description>[-<issue-number>]
```

### 组成部分

| 部分 | 说明 | 示例 |
|------|------|------|
| `type` | 分支类型 | `feature`, `fix`, `improve` |
| `/` | 分隔符 | 必须 |
| `description` | 简短描述 | 使用小写，连字符分隔 |
| `-<issue-number>` | 关联 Issue（可选） | `-123` |

---

## 📋 分支类型

### Feature（新功能）

```
feature/<description>
```

**示例**:
```
feature/ai-coding-integration
feature/github-actions-workflow
feature/improvement-ticket-system
feature/ai-coding-456           # 关联 Issue #456
```

**使用场景**:
- 添加新功能
- 扩展现有功能
- 新增 Agent 角色

---

### Fix（Bug 修复）

```
fix/<description>
```

**示例**:
```
fix/github-actions-yaml-error
fix/issue-creation-failure
fix/token-permission-issue
fix/yaml-syntax-123             # 关联 Issue #123
```

**使用场景**:
- 修复 Bug
- 修正错误
- 解决故障

---

### Improve（改进优化）

```
improve/<description>
```

**示例**:
```
improve/code-structure
improve/issue-template
improve/git-workflow
improve/code-style-456          # 关联 Issue #456
```

**使用场景**:
- 代码优化
- 性能提升
- 体验改进

---

### Refactor（重构）

```
refactor/<description>
```

**示例**:
```
refactor/auto-agent-scripts
refactor/git-version-control
refactor/ai-tool-selector
```

**使用场景**:
- 代码重构
- 架构调整
- 模块拆分

---

### Docs（文档）

```
docs/<description>
```

**示例**:
```
docs/add-contributing-guide
docs/update-readme
docs/git-workflow-guide
```

**使用场景**:
- 添加文档
- 更新文档
- 修正文档错误

---

### Test（测试）

```
test/<description>
```

**示例**:
```
test/add-unit-tests
test/github-actions-ci
test/integration-tests
```

**使用场景**:
- 添加测试
- 完善测试覆盖
- CI/CD 配置

---

### Hotfix（紧急修复）

```
hotfix/<description>
```

**示例**:
```
hotfix/critical-security-issue
hotfix/production-bug-fix
hotfix/data-loss-prevention
```

**使用场景**:
- 生产环境紧急问题
- 安全漏洞
- 数据丢失风险

**注意**: Hotfix 需要快速 Review 和 Merge

---

### Chore（日常维护）

```
chore/<description>
```

**示例**:
```
chore/update-dependencies
chore/cleanup-unused-code
chore/update-gitignore
```

**使用场景**:
- 更新依赖
- 清理代码
- 工具配置

---

## 📊 完整示例

### 好的分支名

```
✅ feature/ai-coding-integration
✅ fix/github-actions-yaml-error
✅ improve/code-structure-123
✅ refactor/auto-agent-scripts
✅ docs/add-contributing-guide
✅ test/add-unit-tests
✅ hotfix/critical-bug-fix
✅ chore/update-dependencies
```

### 不好的分支名

```
❌ my-feature              # 没有类型前缀
❌ feature/MyFeature       # 应该小写
❌ feature/my_feature      # 应该用连字符
❌ feature/fix-bug         # 类型混淆
❌ fix/fix-the-thing       # 描述不清晰
❌ test                    # 缺少描述
❌ feature/very-long-branch-name-that-is-hard-to-read  # 太长
```

---

## 🎯 最佳实践

### ✅ 推荐

1. **简短清晰** - 控制在 50 字符内
2. **使用连字符** - `my-feature` 而不是 `my_feature`
3. **全部小写** - `feature/ai-coding` 而不是 `feature/AI-Coding`
4. **关联 Issue** - 如果有关联的 Issue，加上编号
5. **动词开头** - `add-`, `fix-`, `update-`

### ❌ 避免

1. **太长** - 超过 50 字符
2. **太短** - 描述不清晰
3. **特殊字符** - 只用字母、数字、连字符
4. **类型混淆** - fix 分支做 feature 的事
5. **个人化** - 不要用名字命名分支

---

## 🔧 实用命令

### 创建分支

```bash
# 标准格式
git checkout -b feature/ai-coding-integration

# 关联 Issue
git checkout -b fix/yaml-error-123
```

### 查看分支

```bash
# 查看所有分支
git branch -a

# 查看特定类型的分支
git branch --list 'feature/*'
git branch --list 'fix/*'
```

### 删除分支

```bash
# 删除本地分支
git branch -d feature/ai-coding-integration

# 强制删除（如果未合并）
git branch -D feature/ai-coding-integration

# 删除远程分支
git push origin --delete feature/ai-coding-integration
```

---

## 📖 相关文档

- [CONTRIBUTING.md](./CONTRIBUTING.md) - 贡献指南
- [BRANCH_PROTECTION.md](./BRANCH_PROTECTION.md) - 分支保护规则
- [GIT_WORKFLOW.md](./GIT_WORKFLOW.md) - Git 工作流

---

**维护者**: 协调 Agent  
**最后更新**: 2026-03-09
