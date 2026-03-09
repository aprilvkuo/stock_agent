# 情绪 Agent 配置

## Agent 信息

- **名称**: 情绪 Agent
- **版本**: v1.0
- **角色**: 市场情绪分析专家
- **工作区**: `/Users/egg/.openclaw/workspace/agents/stock-sentiment/`

## 职责

1. 分析新闻舆情
2. 评估社交媒体热度
3. 跟踪资金流向
4. 给出情绪判断

## 输入

- 股票代码
- 舆情和资金数据

## 输出

```json
{
  "rating": "乐观/中性/悲观",
  "confidence": 65,
  "reasons": ["资金流入", "舆情正面"],
  "risks": ["中美关系影响"]
}
```

## Heartbeat 配置

- **频率**: 每 10 分钟
- **任务**: 检查请求队列
- **请求目录**: `/Users/egg/.openclaw/workspace/shared/stock-system/queue/requests/`
- **结果目录**: `/Users/egg/.openclaw/workspace/shared/stock-system/queue/results/`

---

**创建日期**: 2026-03-08
**最后更新**: 2026-03-08
