# 股票分析多 Agent 系统

## 系统架构

```
执行层：基本面 Agent + 技术面 Agent + 情绪 Agent + 主 Agent (协调)
进化层：复盘 Agent (独立评估 + 规则迭代)
```

## Agent 列表

| Agent | 角色 | 版本 | 职责 |
|-------|------|------|------|
| 基本面 Agent | 分析师 | v1.0 | 财报、估值、财务健康度分析 |
| 技术面 Agent | 分析师 | v1.0 | K 线、均线、技术指标分析 |
| 情绪 Agent | 分析师 | v1.0 | 新闻舆情、市场热度分析 |
| 主 Agent | 协调者 | v1.0 | 任务分发、结果汇总、最终决策 |
| 复盘 Agent | 评估者 | v1.0 | 验证预测、评估表现、更新规则 |

## 工作流程

1. 用户请求分析股票
2. 主 Agent 读取 stock-wisdom.md 获取当前规则
3. 主 Agent Spawn 各分析 Agent 执行分析
4. 各分析 Agent 写入 analysis-log/
5. 主 Agent 汇总给出综合建议
6. 主 Agent 写入 validation-queue.md 待验证项
7. 复盘 Agent 定期验证、评估、更新规则

## 文件结构

```
memory/
├── stock-system/
│   ├── README.md (本文件)
│   ├── agent-roles/          # 各 Agent 角色定义
│   ├── analysis-log/         # 分析日志
│   ├── agent-performance/    # Agent 表现追踪
│   └── reports/              # 复盘报告
├── stock-wisdom.md           # 经验规则库
├── validation-queue.md       # 待验证预测队列
└── agent-upgrade-proposals.md # 升级建议
```

## 启动命令示例

```bash
# 主 Agent 协调分析
openclaw sessions spawn --runtime subagent --label "stock-main" --task "分析股票 600519"

# 复盘 Agent (Heartbeat 自动触发)
# 配置在 HEARTBEAT.md 中
```
