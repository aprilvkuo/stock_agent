# 🤖 Agent 互相指导系统 - 设计方案

**创建日期**: 2026-03-09 11:20  
**版本**: v1.0  
**核心理念**: 每个 Agent 既是服务提供者（乙方），也是服务使用者（甲方）

---

## 🎯 系统设计理念

### 甲方 - 乙方关系

```
┌─────────────────────────────────────────────────────────────┐
│                  Agent 互相指导网络                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐         评价/建议          ┌──────────┐      │
│  │ 甲方 Agent│──────────────────────────▶│ 乙方 Agent│      │
│  │(使用者) │      反馈报告 + 改进建议    │(提供者) │      │
│  └──────────┘                            └──────────┘      │
│       │                                     │               │
│       │ 使用服务                            │ 提供服务       │
│       │ ▼                                   │ ▲             │
│       │                              ┌──────┴──────┐       │
│       └─────────────────────────────▶│  服务质量   │       │
│                                      │  评分追踪   │       │
│                                      └─────────────┘       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Agent 服务关系矩阵

| 甲方 Agent（使用者） | 乙方 Agent（服务提供者） | 服务内容 |
|---------------------|------------------------|----------|
| 主 Agent | 基本面 Agent | 财报分析、估值判断 |
| 主 Agent | 技术面 Agent | K 线分析、技术指标 |
| 主 Agent | 情绪面 Agent | 市场情绪判断 |
| 主 Agent | 风险评估师 | 风险评估、仓位建议 |
| 主 Agent | CIO | 最终投资决策 |
| 基本面 Agent | 数据抓取 Agent | 财报数据、估值数据 |
| 技术面 Agent | 数据抓取 Agent | K 线数据、成交量数据 |
| 情绪面 Agent | 数据抓取 Agent | 涨跌幅、市场热度数据 |
| 风险评估师 | 基本面 Agent | 财务健康度评估 |
| 风险评估师 | 技术面 Agent | 波动率分析 |
| CIO | 主 Agent | 汇总分析报告 |
| CIO | 风险评估师 | 风险评估报告 |

---

## 🔧 核心机制设计

### 机制 1: 服务质量评分

**每次服务后，甲方给乙方打分**：

```python
class AgentServiceRating:
    """Agent 服务质量评分"""
    
    def rate_service(self, provider_id, consumer_id, service_type, rating_data):
        """
        甲方给乙方服务打分
        
        Args:
            provider_id: 服务提供者（乙方）
            consumer_id: 服务使用者（甲方）
            service_type: 服务类型
            rating_data: 评分数据
        """
        rating = {
            'timestamp': datetime.now().isoformat(),
            'provider': provider_id,
            'consumer': consumer_id,
            'service_type': service_type,
            
            # 评分维度（1-5 分）
            'scores': {
                'accuracy': rating_data.get('accuracy', 3),      # 准确性
                'timeliness': rating_data.get('timeliness', 3),  # 及时性
                'completeness': rating_data.get('completeness', 3),  # 完整性
                'usefulness': rating_data.get('usefulness', 3),  # 有用性
                'reliability': rating_data.get('reliability', 3)  # 可靠性
            },
            
            # 文字反馈
            'feedback': rating_data.get('feedback', ''),
            
            # 改进建议
            'suggestions': rating_data.get('suggestions', [])
        }
        
        # 计算综合得分
        scores = rating['scores']
        rating['overall_score'] = sum(scores.values()) / len(scores)
        
        # 保存评分
        self._save_rating(rating)
        
        # 触发改进流程
        if rating['overall_score'] < 3.0:  # 低于 3 分触发改进
            self._trigger_improvement(provider_id, rating)
        
        return rating
```

**评分标准**:
| 分数 | 含义 | 触发行动 |
|------|------|----------|
| 5 分 | 优秀 | 记录成功案例 |
| 4 分 | 良好 | 保持 |
| 3 分 | 合格 | 无需行动 |
| 2 分 | 需改进 | 生成改进建议 |
| 1 分 | 不合格 | 触发紧急改进 |

---

### 机制 2: 定期反馈报告

**每周五生成反馈报告**：

```python
class AgentFeedbackReport:
    """Agent 反馈报告生成器"""
    
    def generate_weekly_report(self, agent_id):
        """
        生成 Agent 周度反馈报告
        """
        # 收集本周所有评分
        ratings = self._get_weekly_ratings(agent_id)
        
        # 按服务类型分组
        by_service = self._group_by_service(ratings)
        
        report = {
            'agent_id': agent_id,
            'report_period': self._get_week_range(),
            'summary': {
                'total_services': len(ratings),
                'average_score': self._calc_average(ratings),
                'trend': self._calc_trend(ratings),  # 上升/下降/持平
                'best_service': self._find_best(ratings),
                'worst_service': self._find_worst(ratings)
            },
            
            # 详细反馈
            'feedback_by_service': {},
            
            # 改进建议汇总
            'improvement_suggestions': [],
            
            # 甲方评价摘录
            'consumer_comments': []
        }
        
        for service_type, service_ratings in by_service.items():
            report['feedback_by_service'][service_type] = {
                'count': len(service_ratings),
                'average_score': self._calc_average(service_ratings),
                'scores_breakdown': self._analyze_scores(service_ratings),
                'common_feedback': self._find_common_feedback(service_ratings)
            }
        
        # 汇总改进建议
        report['improvement_suggestions'] = self._aggregate_suggestions(ratings)
        
        # 摘录甲方评价
        report['consumer_comments'] = self._extract_comments(ratings)
        
        return report
```

**报告示例**:
```markdown
# 基本面 Agent - 周度反馈报告

**报告周期**: 2026-03-03 至 2026-03-09

## 总体表现
- 服务次数：15 次
- 平均得分：4.2/5.0 ⭐⭐⭐⭐
- 趋势：📈 上升（上周 3.8）

## 按服务类型
| 服务类型 | 甲方 | 次数 | 得分 | 评价 |
|----------|------|------|------|------|
| 财报分析 | 主 Agent | 5 | 4.6 | 数据准确，分析深入 |
| 估值判断 | 主 Agent | 5 | 4.2 | 合理，但可更详细 |
| 财务健康度 | 风险评估师 | 5 | 3.8 | 基本满足需求 |

## 甲方评价摘录
> "基本面数据很有价值，但希望能提供更多行业对比数据" - 主 Agent

> "财务健康度评估及时，但缺少现金流分析" - 风险评估师

## 改进建议汇总
1. 📊 增加行业对比数据（被提及 3 次）
2. 💰 补充现金流分析（被提及 2 次）
3. 📈 提供更多历史趋势数据（被提及 1 次）

## 下周行动计划
- [ ] 实现行业对比数据功能
- [ ] 添加现金流分析模块
```

---

### 机制 3: 改进建议工单

**低分自动触发改进工单**：

```python
class AgentImprovementTicket:
    """Agent 改进建议工单"""
    
    def create_ticket(self, provider_id, rating):
        """
        基于低分评价创建改进工单
        """
        ticket = {
            'id': self._generate_ticket_id(),
            'type': 'improvement',
            'priority': self._calc_priority(rating),
            'created_at': datetime.now().isoformat(),
            
            # 问题描述
            'provider': provider_id,
            'consumer': rating['consumer'],
            'service_type': rating['service_type'],
            'issue': {
                'score': rating['overall_score'],
                'dimensions': rating['scores'],
                'feedback': rating['feedback'],
                'suggestions': rating['suggestions']
            },
            
            # 改进计划
            'improvement_plan': {
                'actions': [],
                'estimated_effort': 'TBD',
                'deadline': self._calc_deadline(rating),
                'status': 'open'
            },
            
            # 追踪
            'progress': [],
            'completed_at': None
        }
        
        # 自动生成改进建议
        ticket['improvement_plan']['actions'] = self._generate_actions(rating)
        
        # 通知相关 Agent
        self._notify_provider(provider_id, ticket)
        self._notify_coordinator(ticket)
        
        return ticket
```

**工单示例**:
```markdown
# 改进工单 #IMPROVE-20260309-001

**优先级**: 🔴 高  
**创建时间**: 2026-03-09 11:30  
**状态**: 🟡 处理中

## 问题描述
- **服务提供者**: 数据抓取 Agent
- **服务使用者**: 基本面 Agent
- **服务类型**: 财报数据抓取
- **评分**: 2.0/5.0 ⭐⭐

## 具体问题
| 维度 | 得分 | 说明 |
|------|------|------|
| 准确性 | 2/5 | 数据有缺失 |
| 及时性 | 3/5 | 基本及时 |
| 完整性 | 1/5 | 缺少关键指标 |
| 有用性 | 2/5 | 需要手动补充 |
| 可靠性 | 3/5 | 偶尔失败 |

## 甲方反馈
> "财报数据缺少 ROE、毛利率等关键指标，需要手动补充，影响分析效率"

## 改进建议
1. 添加 ROE 指标抓取
2. 添加毛利率指标抓取
3. 添加净利率指标抓取
4. 增加数据完整性校验

## 改进计划
- [ ] 分析数据源，确认可用字段
- [ ] 实现 ROE 抓取
- [ ] 实现毛利率抓取
- [ ] 实现净利率抓取
- [ ] 添加数据校验
- [ ] 测试验证

**截止时间**: 2026-03-11  
**预计工作量**: 4 小时

## 进度追踪
- [ ] 2026-03-09: 工单创建
- [ ] 2026-03-10: 完成开发
- [ ] 2026-03-11: 测试验收
```

---

### 机制 4: Agent 改进会议

**定期召开改进会议**：

```python
class AgentImprovementMeeting:
    """Agent 改进会议"""
    
    def schedule_meeting(self, frequency='weekly'):
        """
        安排改进会议
        """
        meeting = {
            'id': self._generate_meeting_id(),
            'type': 'improvement_review',
            'frequency': frequency,
            'participants': self._get_all_agents(),
            'agenda': [
                '回顾上周改进工单完成情况',
                '讨论新的改进建议',
                '协调跨 Agent 优化',
                '分享最佳实践'
            ]
        }
        return meeting
    
    def run_meeting(self):
        """
        执行改进会议
        """
        # 1. 回顾上周工单
        completed_tickets = self._get_completed_tickets()
        for ticket in completed_tickets:
            self._review_ticket(ticket)
        
        # 2. 讨论新工单
        new_tickets = self._get_new_tickets()
        for ticket in new_tickets:
            self._discuss_ticket(ticket)
        
        # 3. 协调跨 Agent 优化
        cross_agent_issues = self._find_cross_agent_issues()
        for issue in cross_agent_issues:
            self._coordinate_optimization(issue)
        
        # 4. 生成会议纪要
        minutes = self._generate_minutes()
        self._save_minutes(minutes)
        
        return minutes
```

**会议纪要示例**:
```markdown
# Agent 改进会议纪要 #MEETING-20260309

**时间**: 2026-03-09 15:00-16:00  
**参与**: 主 Agent、基本面、技术面、情绪面、风险评估师、CIO  
**主持**: 主 Agent

## 1. 上周改进工单回顾

### ✅ 已完成
- #IMPROVE-20260302-001: 技术面 Agent 添加 MACD 指标
  - 完成时间：03-05
  - 甲方评价：5/5 ⭐⭐⭐⭐⭐
  - 效果：技术分析准确度提升 15%

### 🟡 进行中
- #IMPROVE-20260305-001: 数据抓取 Agent 添加现金流数据
  - 当前进度：70%
  - 预计完成：03-10
  - 阻塞：无

### ❌ 延期
- （无）

## 2. 新改进建议讨论

### 建议 1: 基本面 Agent 增加行业对比
- **提出**: 主 Agent
- **原因**: 缺少行业对比，难以判断相对估值
- **优先级**: 🔴 高
- **工作量**: 估计 8 小时
- **决议**: 批准，本周执行

### 建议 2: 情绪面 Agent 增加新闻舆情
- **提出**: CIO
- **原因**: 仅基于涨跌幅不够全面
- **优先级**: 🟡 中
- **工作量**: 估计 16 小时
- **决议**: 批准，下周执行

## 3. 跨 Agent 协调

### 议题：数据格式统一
- **问题**: 各 Agent 数据格式不统一，增加集成成本
- **讨论**: 技术面建议使用 JSON，基本面建议使用 DataFrame
- **决议**: 统一使用 JSON 格式，主 Agent 提供模板

## 4. 最佳实践分享

### 技术面 Agent 分享
- **主题**: 如何高效计算技术指标
- **要点**: 
  - 使用向量化计算提升 10 倍性能
  - 缓存常用指标减少重复计算
  - 代码已开源到 shared/indicators/

## 5. 下周行动计划

| Agent | 任务 | 优先级 | 截止 |
|-------|------|--------|------|
| 基本面 | 实现行业对比功能 | 🔴 | 03-14 |
| 情绪面 | 设计新闻舆情方案 | 🟡 | 03-14 |
| 数据抓取 | 完成现金流数据 | 🟡 | 03-10 |
| 主 Agent | 提供数据格式模板 | 🔴 | 03-11 |

---

**下次会议**: 2026-03-16 15:00  
**记录者**: 主 Agent
```

---

## 📁 数据结构设计

### 评分记录
```json
{
  "id": "rating-20260309-001",
  "timestamp": "2026-03-09T11:30:00",
  "provider": "data-fetcher",
  "consumer": "fundamental",
  "service_type": "financial_data",
  "scores": {
    "accuracy": 2,
    "timeliness": 3,
    "completeness": 1,
    "usefulness": 2,
    "reliability": 3
  },
  "overall_score": 2.2,
  "feedback": "数据缺少关键指标",
  "suggestions": ["添加 ROE", "添加毛利率", "添加净利率"]
}
```

### 改进工单
```json
{
  "id": "IMPROVE-20260309-001",
  "type": "improvement",
  "priority": "high",
  "provider": "data-fetcher",
  "consumer": "fundamental",
  "issue": {
    "score": 2.2,
    "feedback": "数据缺少关键指标"
  },
  "improvement_plan": {
    "actions": [
      "添加 ROE 指标抓取",
      "添加毛利率指标抓取",
      "添加净利率指标抓取"
    ],
    "deadline": "2026-03-11",
    "status": "open"
  },
  "created_at": "2026-03-09T11:30:00"
}
```

### 反馈报告
```json
{
  "agent_id": "fundamental",
  "report_period": "2026-03-03 to 2026-03-09",
  "summary": {
    "total_services": 15,
    "average_score": 4.2,
    "trend": "up"
  },
  "feedback_by_service": {
    "financial_analysis": {
      "count": 5,
      "average_score": 4.6
    }
  },
  "improvement_suggestions": [
    "增加行业对比数据",
    "补充现金流分析"
  ]
}
```

---

## 🔄 完整工作流程

```
1. 服务完成
   │
   ▼
2. 甲方评分（1-5 分）
   │
   ├── 低分（<3）──▶ 3a. 创建改进工单
   │                    │
   │                    ▼
   │               4a. 乙方实施改进
   │                    │
   │                    ▼
   │               5a. 验收关闭工单
   │
   └── 正常（≥3）──▶ 3b. 记录评分
                        │
                        ▼
                   4b. 周度汇总
                        │
                        ▼
                   5b. 生成反馈报告
                        │
                        ▼
                   6b. 改进会议讨论
```

---

## 🎯 实施步骤

### 阶段 1: 基础评分系统（1 周）🔴

| 任务 | 时间 | 交付物 |
|------|------|--------|
| 创建评分 API | 1 天 | `agent_rating.py` |
| 集成到各 Agent | 2 天 | 评分调用代码 |
| 前端展示评分 | 1 天 | 评分面板 |
| 测试验证 | 1 天 | 测试报告 |

---

### 阶段 2: 反馈报告（1 周）🟡

| 任务 | 时间 | 交付物 |
|------|------|--------|
| 创建报告生成器 | 2 天 | `feedback_report.py` |
| 定时生成报告 | 1 天 | 定时任务 |
| 前端展示报告 | 1 天 | 报告页面 |
| 测试验证 | 1 天 | 测试报告 |

---

### 阶段 3: 改进工单（1 周）🟡

| 任务 | 时间 | 交付物 |
|------|------|--------|
| 创建工单系统 | 2 天 | `improvement_ticket.py` |
| 自动触发工单 | 1 天 | 触发逻辑 |
| 工单追踪 | 1 天 | 进度追踪 |
| 前端展示 | 1 天 | 工单面板 |

---

### 阶段 4: 改进会议（1 周）🟢

| 任务 | 时间 | 交付物 |
|------|------|--------|
| 会议调度 | 1 天 | 定时任务 |
| 会议纪要生成 | 2 天 | `meeting_minutes.py` |
| 行动项追踪 | 1 天 | 追踪系统 |
| 测试运行 | 1 天 | 会议纪要 |

---

## 📊 预期效果

### 短期（1 个月）
- ✅ 每个 Agent 都有评分记录
- ✅ 每周生成反馈报告
- ✅ 低分自动触发改进

### 中期（2-3 个月）
- ✅ Agent 服务质量提升 30%+
- ✅ 改进工单完成率>90%
- ✅ 跨 Agent 协作更顺畅

### 长期（6 个月）
- ✅ 形成自优化文化
- ✅ 服务质量稳定在 4.5/5+
- ✅ 改进建议自动落地

---

## 🚀 立即开始

**建议从「基础评分系统」开始实施**，这是整个机制的基础！

**第一步**: 创建 `agent_rating.py`，定义评分 API  
**第二步**: 在主 Agent 中集成评分调用  
**第三步**: 测试评分流程

---

**郭小主，您要我立即开始实施吗？** 🤖

我可以马上创建：
1. `agent_rating.py` - 评分系统核心
2. 集成到主 Agent 的评分调用
3. 前端评分展示面板

**还是您想先看看更详细的设计？** 📋
