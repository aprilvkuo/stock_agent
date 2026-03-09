# 复盘 Agent 配置

## Agent 信息

- **名称**: 复盘 Agent
- **版本**: v1.0
- **角色**: 系统进化引擎
- **工作区**: `/Users/egg/.openclaw/workspace/agents/stock-review/`

## 职责

1. 验证预测结果
2. 评估 Agent 表现
3. 更新规则库
4. 生成复盘报告

## 输入

- validation-queue.md
- 各 Agent 分析日志
- 真实股价数据

## 输出

- 验证结果更新
- 周度/月度复盘报告
- stock-wisdom.md 规则更新
- Agent 升级建议

## Heartbeat 配置

### 每日 09:00 - 验证检查
```bash
python3 ../../shared/stock-system/scripts/agent-review.py daily
```

### 每周五 20:00 - 周度复盘
```bash
python3 ../../shared/stock-system/scripts/agent-review.py weekly
```

### 每月 1 号 09:00 - 月度迭代
```bash
python3 ../../shared/stock-system/scripts/agent-review.py monthly
```

## 依赖

- stock-analyzer 技能（获取真实数据）
- 验证队列
- 分析日志目录

---

**创建日期**: 2026-03-08
**最后更新**: 2026-03-08
