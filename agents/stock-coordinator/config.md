# 主 Agent (协调者) 配置

## Agent 信息

- **名称**: 主 Agent / 协调者
- **版本**: v1.0
- **角色**: 多 Agent 系统指挥中心
- **工作区**: `/Users/egg/.openclaw/workspace/agents/stock-coordinator/`

## 职责

1. 接收用户请求
2. 创建分析任务
3. 等待各 Agent 结果
4. 汇总并决策
5. 写入验证队列

## 输入

- 用户分析请求（股票代码）

## 输出

- 综合投资建议
- 分析日志
- 验证队列更新

## Heartbeat 配置

- **频率**: 每 5 分钟
- **任务**: 
  - 检查新请求
  - 检查 Agent 结果
  - 汇总决策

**命令**:
```bash
cd /Users/egg/.openclaw/workspace/agents/stock-coordinator
python3 ../../shared/stock-system/scripts/agent-coordinator.py
```

## 依赖

- 3 个分析 Agent
- 共享队列目录
- stock-wisdom.md 规则库

---

**创建日期**: 2026-03-08
**最后更新**: 2026-03-08
