# 📊 Agent TODO 迁移摘要

**迁移日期**: 2026-03-09 21:53  
**来源**: `shared/stock-system/agent-todos/`  
**目标**: GitHub Issues

---

## 📋 迁移统计

| 指标 | 数量 |
|------|------|
| 总任务数 | 5 |
| 涉及 Agent | 5 |
| 高优先级 | 2 |
| 中优先级 | 2 |
| 低优先级 | 1 |

---

## 🤖 各 Agent 任务分布

### @qa-agent

1. 🔴 [质检 Agent] 检查系统健康

### @technical-agent

1. 🟡 [技术面 Agent] 分析 00700 腾讯控股 K 线

### @programmer-agent

1. 🟡 [程序员 Agent] 修复 Bug

### @fundamental-agent

1. 🔴 [基本面 Agent] 分析 600519 贵州茅台财报

### @sentiment-agent

1. 🟢 [情绪 Agent] 监控市场舆情


---

## 📁 生成的 Issue 文件

所有 Issue 数据文件已保存到：`.github/ISSUE_TEMPLATE/migrated-issues/`

文件格式：`issue-XXX.json`

---

## 🚀 下一步

### 方法 1: 使用 GitHub CLI 批量创建

```bash
cd /Users/egg/.openclaw/workspace/.github/ISSUE_TEMPLATE/migrated-issues

for file in issue-*.json; do
    title=$(jq -r '.title' "$file")
    body=$(jq -r '.body' "$file")
    labels=$(jq -r '.labels | join(",")' "$file")
    assignee=$(jq -r '.assignee' "$file")
    
    gh issue create         --title "$title"         --body "$body"         --label "$labels"         --assignee "$assignee"
done
```

### 方法 2: 手动创建

访问 https://github.com/aprilvkuo/stock_agent/issues/new/choose

选择对应模板，复制粘贴 Issue 内容。

---

## ✅ 迁移完成标准

- [ ] 所有 Issue 已创建到 GitHub
- [ ] 所有 Issue 已分配给对应 Agent
- [ ] 所有 Issue 已添加正确标签
- [ ] 本地 agent-todos 已归档

---

*生成日期：{datetime.now().strftime('%Y-%m-%d %H:%M')}*
