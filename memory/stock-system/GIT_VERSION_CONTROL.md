# Git 版本控制规范 - 股票多 Agent 系统

**版本**: v1.0 (2026-03-09)  
**状态**: ✅ 已实施

---

## 🎯 目标

通过 Git 版本控制记录每个 Agent 的重大决策和系统更新，实现：
- ✅ 决策可追溯
- ✅ 版本可对比
- ✅ 历史可审计
- ✅ 责任可定位

---

## 📋 Agent Git User 映射

每个 Agent 都有独立的 Git 身份：

| Agent 名称 | Git User Name | Git Email |
|-----------|---------------|-----------|
| 技术 Agent | 技术 Agent | tech-agent@stock-system.local |
| 情绪 Agent | 情绪 Agent | emotion-agent@stock-system.local |
| 资金 Agent | 资金 Agent | fund-agent@stock-system.local |
| 估值 Agent | 估值 Agent | valuation-agent@stock-system.local |
| 协调 Agent | 协调 Agent | coordinator@stock-system.local |
| 系统 Agent | 系统 Agent | system-agent@stock-system.local |

---

## 🔄 触发 Git 提交的场景

### 1️⃣ 股票分析完成
**触发 Agent**: 协调 Agent  
**提交时机**: 每次 `analyze` 命令执行完成  
**提交信息格式**: `[协调 Agent] YYYY-MM-DD HH:MM:SS - 分析 贵州茅台 (600519) - 评级：🟢 推荐`

### 2️⃣ 每日验证执行
**触发 Agent**: 系统 Agent  
**提交时机**: 每日自动验证完成后  
**提交信息格式**: `[系统 Agent] YYYY-MM-DD HH:MM:SS - 每日验证 (2026-03-09)`

### 3️⃣ 周度复盘报告
**触发 Agent**: 系统 Agent  
**提交时机**: 每周五 20:00 复盘完成后  
**提交信息格式**: `[系统 Agent] YYYY-MM-DD HH:MM:SS - 周度复盘报告 (03-03~03-09) - 准确率：85.0%`

### 4️⃣ 规则库更新
**触发 Agent**: 系统 Agent  
**提交时机**: `stock-wisdom.md` 或规则文件更新时  
**提交信息格式**: `[系统 Agent] YYYY-MM-DD HH:MM:SS - 规则库更新：新增突破确认规则`

### 5️⃣ 系统配置变更
**触发 Agent**: 系统 Agent  
**提交时机**: `config.json` 或系统配置更新时  
**提交信息格式**: `[系统 Agent] YYYY-MM-DD HH:MM:SS - 配置更新：调整动态权重阈值`

---

## 🛠️ 使用方法

### 查看提交历史

```bash
cd /Users/egg/.openclaw/workspace/memory/stock-system

# 查看最近 10 条提交
python3 scripts/git_version_control.py history

# 查看最近 20 条提交
python3 scripts/git_version_control.py history 20

# 查看特定 Agent 的提交
python3 scripts/git_version_control.py history 10 "协调 Agent"

# 查看系统 Agent 的所有提交
python3 scripts/git_version_control.py history 100 "系统 Agent"
```

### 在代码中使用

```python
from git_version_control import GitVersionControl

# 初始化
git = GitVersionControl()

# 提交变更
git.commit(
    agent_name="协调 Agent",
    message="分析完成",
    files=None,  # None 表示 add -A，或指定文件列表
    auto_push=True  # 自动 push 到远程
)

# 查看历史
history = git.get_history(limit=10, agent="系统 Agent")
```

---

## 📊 提交流程

标准 Git 提交流程：

```
1. git add -A              # 添加所有变更
2. git config user.name    # 设置 Agent 名称
3. git config user.email   # 设置 Agent 邮箱
4. git commit -m           # 提交
5. git push origin main    # 推送到远程
6. 记录提交历史到 .git-commits.json
```

---

## 📁 重要文件

| 文件 | 说明 |
|------|------|
| `scripts/git_version_control.py` | Git 版本控制核心模块 |
| `.git-commits.json` | 提交历史记录（JSON 格式） |
| `.git/` | Git 仓库目录 |

---

## 🔍 提交历史示例

```bash
$ python3 scripts/git_version_control.py history 5

================================================================================
📤 [2026-03-09 16:45:23] 协调 Agent
   a3f8b2c1: 分析 贵州茅台 (600519) - 评级：🟢 推荐
--------------------------------------------------------------------------------
📤 [2026-03-09 14:30:15] 系统 Agent
   7d9e4f12: 每日验证 (2026-03-09)
--------------------------------------------------------------------------------
📤 [2026-03-08 20:00:42] 系统 Agent
   2b5c8a91: 周度复盘报告 (03-01~03-08) - 准确率：82.5%
--------------------------------------------------------------------------------
📤 [2026-03-08 15:22:10] 协调 Agent
   9f3e1d74: 分析 腾讯控股 (00700) - 评级：🟡 中性
--------------------------------------------------------------------------------
📤 [2026-03-08 11:05:33] 系统 Agent
   4c6a2b89: 规则库更新：新增 RSI 超买判断规则
--------------------------------------------------------------------------------
```

---

## ⚠️ 注意事项

1. **自动 Push**: 默认启用自动 Push，确保远程仓库可访问
2. **无变更跳过**: 如果没有文件变更，会自动跳过提交
3. **错误处理**: 提交失败不影响主流程，仅记录警告
4. **本地测试**: 可设置 `auto_push=False` 进行本地测试
5. **网络问题**: Push 失败时，提交仍会保存在本地仓库

---

## 🚀 未来扩展

- [ ] 为每次分析创建独立 Branch
- [ ] 添加 Git Tag 标记重要版本
- [ ] 实现 Branch 对比功能
- [ ] 自动生成 Changelog
- [ ] 支持多远程仓库同步

---

## 📖 相关文档

- [AUTO_AGENT.md](./AUTO_AGENT.md) - 主协调脚本说明
- [SYSTEM_STATUS.md](./SYSTEM_STATUS.md) - 系统状态总览
- [OPTIMIZATION_ROADMAP.md](./OPTIMIZATION_ROADMAP.md) - 优化路线图

---

**实施日期**: 2026-03-09  
**实施版本**: v1.7  
**维护者**: 系统 Agent
