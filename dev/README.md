# 🚧 草稿区 (Development Area)

**职责**: 开发中、实验性、未完成的代码

**状态**: ✅ 正式启用  
**创建日期**: 2026-03-09  
**维护者**: 程序员 Agent

---

## 📁 目录结构

```
dev/
├── README.md              # 本说明文档
├── experiments/           # 实验性代码
│   └── experiment-xxx/    # 实验项目
├── drafts/                # 草稿文件
│   └── draft-xxx.md       # 草稿文档
└── testing/               # 测试代码
    └── test-xxx.py        # 测试脚本
```

---

## 📋 使用规范

### ✅ 允许

- 实验性代码（新想法验证）
- 未完成的草稿
- 测试代码和脚本
- 原型验证
- 临时文件

### ❌ 禁止

- 生产代码（应放在正式目录）
- 已验证的功能（应迁移到正式目录）
- 大型数据文件
- 敏感信息（密码、Token 等）

---

## 🔄 迁移流程

### 从 dev/ 迁移到正式目录

```
1. 在 dev/ 中开发和测试
   ↓
2. 功能验证通过
   ↓
3. 迁移到正式目录（memory/, skills/, agents/）
   ↓
4. Git 提交
   ↓
5. 清理 dev/ 中的旧文件
```

### 示例

```bash
# 1. 在 dev/ 中开发
dev/experiments/ai-coding-test/

# 2. 验证通过

# 3. 迁移到正式目录
mv dev/experiments/ai-coding-test agents/stock-programmer/

# 4. Git 提交
git add agents/stock-programmer/ai-coding-test
git commit -m "feat: 添加 ai_coding 测试功能"

# 5. 清理
rm -rf dev/experiments/ai-coding-test
```

---

## 📝 命名规范

### 实验项目

```
experiments/
└── <type>-<description>-<date>/
    └── README.md
```

**示例**:
```
experiments/
└── feature-ai-coding-20260309/
    ├── README.md
    ├── main.py
    └── test.py
```

### 草稿文件

```
drafts/
└── draft-<type>-<description>-<date>.md
```

**示例**:
```
drafts/
├── draft-feature-design-20260309.md
├── draft-api-spec-20260309.md
└── draft-meeting-notes-20260309.md
```

### 测试脚本

```
testing/
└── test-<description>.py
```

**示例**:
```
testing/
├── test-api-connection.py
├── test-git-workflow.py
└── test-issue-tracker.py
```

---

## 🗑️ 清理规则

### 定期清理

- **实验项目**: 超过 30 天未更新
- **草稿文件**: 超过 14 天未更新
- **测试脚本**: 已集成到正式测试套件

### 清理流程

```bash
# 1. 检查过期文件
find dev/experiments -type d -mtime +30
find dev/drafts -type f -mtime +14

# 2. 确认是否需要保留
# 3. 迁移有价值的内容
# 4. 删除过期文件
```

---

## 📊 状态追踪

### 当前项目

| 项目 | 类型 | 创建日期 | 状态 | 下一步 |
|------|------|---------|------|--------|
| ai-coding-integration | experiment | 2026-03-09 | ✅ 已完成 | 迁移到正式目录 |
| issue-tracker | experiment | 2026-03-09 | ✅ 已完成 | 已集成 |

### 历史记录

查看 Git 历史了解已迁移的项目：

```bash
git log -- dev/experiments/
git log -- dev/drafts/
```

---

## 💡 最佳实践

### ✅ 推荐

1. **及时更新** - 保持实验项目活跃
2. **添加 README** - 说明实验目的和进展
3. **定期清理** - 删除过期的草稿
4. **及时迁移** - 验证通过的功能尽快迁移
5. **版本控制** - dev/ 也要 Git 管理

### ❌ 避免

1. **长期不更新** - 超过 30 天无进展
2. **缺少文档** - 不写 README
3. **混乱命名** - 不使用规范命名
4. **忘记迁移** - 验证通过不迁移
5. **直接删除** - 不迁移就直接删除

---

## 🔗 相关文档

- [CODE_STRUCTURE.md](../CODE_STRUCTURE.md) - 代码结构规范
- [CONTRIBUTING.md](../CONTRIBUTING.md) - 贡献指南
- [BRANCH_NAMING.md](../BRANCH_NAMING.md) - 分支命名

---

## 📝 更新日志

### v1.0 - 2026-03-09

- ✅ 创建草稿区基本结构
- ✅ 添加实验、草稿、测试目录
- ✅ 编写使用规范文档
- ✅ 定义命名规范
- ✅ 建立清理规则

---

**维护者**: 程序员 Agent  
**最后更新**: 2026-03-09
