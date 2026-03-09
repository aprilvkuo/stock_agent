# 🤖 多 Agent 自主优化系统 - 改进方案

**制定日期**: 2026-03-09 11:15  
**当前版本**: v2.0  
**目标版本**: v3.0 (自主进化版)

---

## 📊 当前系统诊断

### ✅ 已有能力

| 模块 | 状态 | 说明 |
|------|------|------|
| 5 个 Agent | ✅ | 基本面/技术面/情绪面/风险评估/CIO |
| 固定权重 | ✅ | 30%/25%/20%/15%/10% |
| 分析日志 | ✅ | 每次分析生成 MD+JSON |
| 验证队列 | ✅ | 26 项待验证（验证日 04-08） |
| Heartbeat | ✅ | 每日 09:00 验证，每周五 20:00 复盘 |
| Web 监控 | ✅ | 5001 端口，含 TODO List |

### ❌ 自主优化缺失

| 能力 | 状态 | 影响 |
|------|------|------|
| 动态权重调整 | ❌ | Agent 表现好坏权重不变 |
| 准确率统计 | ❌ | 无法量化 Agent 能力 |
| 规则自动提炼 | ❌ | 成功经验无法沉淀 |
| 策略自动优化 | ❌ | 错误无法触发策略调整 |
| 对抗训练 | ❌ | 无法识别市场风格变化 |
| 知识库自更新 | ❌ | 知识靠手动积累 |

---

## 🎯 自主优化系统架构（v3.0）

```
┌─────────────────────────────────────────────────────────────┐
│                    自主优化闭环系统                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│  │ 决策执行 │───▶│ 结果验证 │───▶│ 效果评估 │              │
│  └──────────┘    └──────────┘    └──────────┘              │
│       ▲                               │                     │
│       │                               ▼                     │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│  │ 策略调整 │◀───│ 规则提炼 │◀───│ 归因分析 │              │
│  └──────────┘    └──────────┘    └──────────┘              │
│       │                               │                     │
│       ▼                               ▼                     │
│  ┌──────────────────────────────────────────┐              │
│  │          知识库 + 规则库 + 模型库          │              │
│  └──────────────────────────────────────────┘              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 核心改进模块

### 模块 1: Agent 表现追踪系统 🔴 高优先级

**问题**: 无法量化每个 Agent 的准确率

**解决方案**:

```python
# agent_performance_tracker.py

class AgentPerformanceTracker:
    """Agent 表现追踪器"""
    
    def __init__(self):
        self.stats_file = 'agent-performance/stats.json'
        self.history_file = 'agent-performance/history.md'
    
    def record_prediction(self, agent_id, stock_code, prediction, confidence):
        """记录 Agent 预测"""
        data = {
            'timestamp': datetime.now().isoformat(),
            'agent_id': agent_id,
            'stock_code': stock_code,
            'prediction': prediction,
            'confidence': confidence,
            'verified': False
        }
        # 写入预测记录
        self._append_prediction(data)
    
    def verify_prediction(self, agent_id, stock_code, actual_result):
        """验证预测并更新统计"""
        # 找到对应预测
        prediction = self._find_prediction(agent_id, stock_code)
        
        # 计算准确度
        accuracy = self._calculate_accuracy(prediction, actual_result)
        
        # 更新统计
        self._update_stats(agent_id, accuracy)
        
        # 记录验证结果
        self._append_verification({
            'agent_id': agent_id,
            'accuracy': accuracy,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_agent_stats(self, agent_id):
        """获取 Agent 统计数据"""
        stats = self._load_stats()
        agent_stats = stats.get(agent_id, {
            'total_predictions': 0,
            'correct_predictions': 0,
            'accuracy': 0,
            'avg_confidence': 0,
            'recent_accuracy': []  # 最近 10 次准确率
        })
        
        # 计算趋势
        if len(agent_stats['recent_accuracy']) >= 5:
            recent_5 = sum(agent_stats['recent_accuracy'][-5:]) / 5
            agent_stats['trend'] = 'up' if recent_5 > agent_stats['accuracy'] else 'down'
        
        return agent_stats
    
    def get_all_agents_ranking(self):
        """获取所有 Agent 排名"""
        stats = self._load_stats()
        ranking = []
        for agent_id, agent_stats in stats.items():
            ranking.append({
                'agent_id': agent_id,
                'accuracy': agent_stats['accuracy'],
                'total_predictions': agent_stats['total_predictions'],
                'trend': agent_stats.get('trend', 'stable')
            })
        return sorted(ranking, key=lambda x: x['accuracy'], reverse=True)
```

**预期效果**:
- 每个 Agent 的准确率实时可查
- 最近 5 次/10 次/30 次准确率趋势
- Agent 能力排行榜

---

### 模块 2: 动态权重调整系统 🔴 高优先级

**问题**: Agent 权重固定，表现好的 Agent 没有更大话语权

**解决方案**:

```python
# dynamic_weight_adjuster.py

class DynamicWeightAdjuster:
    """动态权重调整器"""
    
    def __init__(self):
        self.config_file = 'config.json'
        self.adjustment_history = []
    
    def adjust_weights(self, agent_stats):
        """根据 Agent 表现调整权重"""
        current_weights = self._load_weights()
        new_weights = {}
        
        # 计算所有 Agent 的平均准确率
        accuracies = [stats['accuracy'] for stats in agent_stats.values()]
        avg_accuracy = sum(accuracies) / len(accuracies) if accuracies else 0.5
        
        total_weight = 0
        
        for agent_id, stats in agent_stats.items():
            current_weight = current_weights.get(agent_id, 0.2)
            accuracy = stats['accuracy']
            
            # 表现优于平均，提升权重
            if accuracy > avg_accuracy + 0.1:  # 高于平均 10%
                adjustment = 0.05
            elif accuracy > avg_accuracy:
                adjustment = 0.02
            elif accuracy < avg_accuracy - 0.1:  # 低于平均 10%
                adjustment = -0.05
            elif accuracy < avg_accuracy:
                adjustment = -0.02
            else:
                adjustment = 0
            
            # 应用调整（限制在合理范围）
            new_weight = max(0.1, min(0.4, current_weight + adjustment))
            new_weights[agent_id] = round(new_weight, 2)
            total_weight += new_weights[agent_id]
        
        # 归一化（确保总和为 1）
        for agent_id in new_weights:
            new_weights[agent_id] = round(new_weights[agent_id] / total_weight, 2)
        
        # 保存新权重
        self._save_weights(new_weights)
        
        # 记录调整历史
        self._record_adjustment(agent_stats, new_weights)
        
        return new_weights
    
    def should_adjust(self, agent_stats):
        """判断是否应该调整权重"""
        # 至少需要 10 次预测记录才调整
        for stats in agent_stats.values():
            if stats['total_predictions'] < 10:
                return False
        
        # 或者准确率变化超过阈值
        for stats in agent_stats.values():
            if len(stats['recent_accuracy']) >= 5:
                recent = sum(stats['recent_accuracy'][-5:]) / 5
                if abs(recent - stats['accuracy']) > 0.15:
                    return True
        
        return False
```

**调整规则**:
| 场景 | 调整幅度 | 触发条件 |
|------|----------|----------|
| 表现优异 | +5% | 准确率>平均 10% |
| 表现良好 | +2% | 准确率>平均 |
| 表现一般 | 0% | 准确率=平均 |
| 表现较差 | -2% | 准确率<平均 |
| 表现糟糕 | -5% | 准确率<平均 10% |

**权重限制**: 10% - 40%（防止单一 Agent 主导）

---

### 模块 3: 规则自动提炼系统 🟡 中优先级

**问题**: 成功经验无法沉淀为可复用规则

**解决方案**:

```python
# rule_extractor.py

class RuleExtractor:
    """规则自动提炼器"""
    
    def __init__(self):
        self.rules_file = 'knowledge/trading-rules.md'
    
    def extract_from_success(self, analysis_log, actual_result):
        """从成功案例提炼规则"""
        # 分析成功预测的特征
        features = {
            'market_condition': self._analyze_market(analysis_log),
            'agent_consensus': self._analyze_consensus(analysis_log),
            'confidence_level': self._analyze_confidence(analysis_log),
            'stock_characteristics': self._analyze_stock(analysis_log)
        }
        
        # 生成规则
        rule = {
            'id': self._generate_rule_id(),
            'type': 'success_pattern',
            'condition': self._format_condition(features),
            'action': 'follow_prediction',
            'confidence_boost': 0.1,  # 类似情况下提升置信度
            'created_at': datetime.now().isoformat(),
            'success_count': 1
        }
        
        self._save_rule(rule)
        return rule
    
    def extract_from_failure(self, analysis_log, actual_result):
        """从失败案例提炼教训"""
        # 分析失败原因
        failure_reason = self._analyze_failure_reason(analysis_log, actual_result)
        
        # 生成警示规则
        rule = {
            'id': self._generate_rule_id(),
            'type': 'warning_pattern',
            'condition': self._format_condition(failure_reason),
            'action': 'reduce_confidence',
            'confidence_reduction': 0.2,  # 类似情况下降低置信度
            'created_at': datetime.now().isoformat(),
            'trigger_count': 1
        }
        
        self._save_rule(rule)
        return rule
    
    def get_applicable_rules(self, current_context):
        """获取适用于当前情境的规则"""
        all_rules = self._load_rules()
        applicable = []
        
        for rule in all_rules:
            if self._match_condition(rule, current_context):
                applicable.append(rule)
        
        return applicable
```

**规则示例**:
```markdown
## 成功规则 #001
**触发条件**: 
- 基本面 Agent 评级=neutral
- 技术面 Agent 评级=neutral  
- 情绪面 Agent 评级=bullish
- CIO 最终决策=HOLD
- 置信度>65%

**历史表现**: 成功 7 次，失败 2 次，准确率 77.8%

**应用效果**: 类似情况下，置信度提升 10%

---

## 警示规则 #001
**触发条件**:
- 技术面 Agent 评级=bullish
- 但 RSI>75 (超买)
- 成交量萎缩

**历史表现**: 成功 2 次，失败 8 次，准确率 20%

**应用效果**: 类似情况下，置信度降低 20%
```

---

### 模块 4: 策略自动优化系统 🟡 中优先级

**问题**: 错误无法触发策略自动调整

**解决方案**:

```python
# strategy_optimizer.py

class StrategyOptimizer:
    """策略自动优化器"""
    
    def __init__(self):
        self.strategy_file = 'strategies/current_strategy.json'
    
    def analyze_failure_pattern(self, failures):
        """分析失败模式"""
        patterns = {
            'overconfidence': 0,  # 过度自信（高置信度但失败）
            'sector_bias': {},    # 行业偏见
            'market_condition': {},  # 市场风格不适应
            'agent_weakness': {}  # 特定 Agent 弱点
        }
        
        for failure in failures:
            # 检测过度自信
            if failure['confidence'] > 0.8:
                patterns['overconfidence'] += 1
            
            # 检测行业偏见
            sector = failure['sector']
            patterns['sector_bias'][sector] = patterns['sector_bias'].get(sector, 0) + 1
            
            # 检测市场风格
            market_condition = failure['market_condition']
            patterns['market_condition'][market_condition] = \
                patterns['market_condition'].get(market_condition, 0) + 1
        
        return patterns
    
    def suggest_optimization(self, patterns):
        """基于失败模式建议优化"""
        suggestions = []
        
        # 过度自信问题
        if patterns['overconfidence'] > 5:
            suggestions.append({
                'type': 'confidence_adjustment',
                'action': 'reduce_base_confidence',
                'value': 0.1,
                'reason': '检测到过度自信模式，建议降低基础置信度 10%'
            })
        
        # 行业偏见
        for sector, count in patterns['sector_bias'].items():
            if count > 3:
                suggestions.append({
                    'type': 'sector_caution',
                    'action': 'add_sector_filter',
                    'sector': sector,
                    'reason': f'{sector}行业连续失败{count}次，建议增加过滤条件'
                })
        
        # 市场风格不适应
        for condition, count in patterns['market_condition'].items():
            if count > 5:
                suggestions.append({
                    'type': 'market_adaptation',
                    'action': 'adjust_for_market',
                    'market_condition': condition,
                    'reason': f'在{condition}市场环境下表现不佳，需要调整策略'
                })
        
        return suggestions
    
    def auto_apply_optimization(self, suggestion):
        """自动应用优化（需要配置允许）"""
        if suggestion['type'] == 'confidence_adjustment':
            self._adjust_confidence(suggestion['value'])
        elif suggestion['type'] == 'sector_caution':
            self._add_sector_filter(suggestion['sector'])
        elif suggestion['type'] == 'market_adaptation':
            self._adapt_to_market(suggestion['market_condition'])
```

---

### 模块 5: 知识库自更新系统 🟢 低优先级

**问题**: 知识靠手动积累，无法自动更新

**解决方案**:

```python
# knowledge_base_updater.py

class KnowledgeBaseUpdater:
    """知识库自更新系统"""
    
    def __init__(self):
        self.knowledge_dir = 'knowledge/'
        self.wisdom_file = 'knowledge/stock-wisdom.md'
    
    def add_case_study(self, analysis_log, result):
        """添加案例研究"""
        case = {
            'id': self._generate_case_id(),
            'date': analysis_log['date'],
            'stock': analysis_log['stock'],
            'analysis': analysis_log,
            'result': result,
            'lessons': self._extract_lessons(analysis_log, result)
        }
        self._save_case(case)
    
    def update_stock_wisdom(self):
        """更新股票智慧（从案例中提炼）"""
        cases = self._load_all_cases()
        
        # 统计每只股票的成功模式
        stock_patterns = {}
        for case in cases:
            stock = case['stock']
            if stock not in stock_patterns:
                stock_patterns[stock] = {'success': [], 'failure': []}
            
            if case['result']['success']:
                stock_patterns[stock]['success'].append(case)
            else:
                stock_patterns[stock]['failure'].append(case)
        
        # 生成智慧规则
        wisdom = []
        for stock, patterns in stock_patterns.items():
            if len(patterns['success']) >= 3:
                success_pattern = self._find_common_pattern(patterns['success'])
                wisdom.append({
                    'stock': stock,
                    'type': 'success_pattern',
                    'pattern': success_pattern,
                    'confidence': len(patterns['success']) / (len(patterns['success']) + len(patterns['failure']))
                })
        
        self._save_wisdom(wisdom)
```

---

## 📅 实施路线图

### 阶段 1: 基础追踪（1-2 周）🔴

| 任务 | 预计时间 | 优先级 |
|------|----------|--------|
| 实现 Agent 表现追踪器 | 2 天 | P0 |
| 集成到验证流程 | 1 天 | P0 |
| 添加准确率统计 API | 1 天 | P0 |
| 前端展示准确率面板 | 1 天 | P1 |

**交付物**:
- `agent_performance_tracker.py`
- `/api/agent-accuracy` API
- 监控页面准确率面板

---

### 阶段 2: 动态权重（2-3 周）🔴

| 任务 | 预计时间 | 优先级 |
|------|----------|--------|
| 实现权重调整器 | 2 天 | P0 |
| 设置调整规则 | 1 天 | P0 |
| 集成到 CIO 决策 | 1 天 | P0 |
| 权重变化历史记录 | 1 天 | P1 |
| 前端展示权重变化 | 1 天 | P2 |

**交付物**:
- `dynamic_weight_adjuster.py`
- 权重自动调整功能
- 权重变化历史图表

---

### 阶段 3: 规则提炼（3-4 周）🟡

| 任务 | 预计时间 | 优先级 |
|------|----------|--------|
| 实现规则提取器 | 3 天 | P0 |
| 从历史案例提炼规则 | 2 天 | P0 |
| 规则应用集成 | 2 天 | P0 |
| 规则效果追踪 | 1 天 | P1 |
| 前端展示规则库 | 2 天 | P2 |

**交付物**:
- `rule_extractor.py`
- 规则库（trading-rules.md）
- 规则应用日志

---

### 阶段 4: 策略优化（4-6 周）🟡

| 任务 | 预计时间 | 优先级 |
|------|----------|--------|
| 实现策略优化器 | 3 天 | P0 |
| 失败模式分析 | 2 天 | P0 |
| 自动优化建议 | 2 天 | P0 |
| 人工审核流程 | 1 天 | P1 |
| 自动应用（可选） | 2 天 | P2 |

**交付物**:
- `strategy_optimizer.py`
- 策略优化建议报告
- 策略版本历史

---

### 阶段 5: 知识自更新（6-8 周）🟢

| 任务 | 预计时间 | 优先级 |
|------|----------|--------|
| 实现知识库更新器 | 3 天 | P0 |
| 案例自动归档 | 2 天 | P0 |
| 智慧规则提炼 | 2 天 | P0 |
| 知识库搜索功能 | 2 天 | P1 |
| 前端展示知识库 | 2 天 | P2 |

**交付物**:
- `knowledge_base_updater.py`
- 案例库
- 股票智慧库

---

## 🎯 成功指标

### 准确率指标
| 指标 | 当前 | 目标（3 个月） |
|------|------|---------------|
| 整体预测准确率 | 未知 | >60% |
| 最佳 Agent 准确率 | 未知 | >70% |
| 最差 Agent 准确率 | 未知 | >45% |

### 自主优化指标
| 指标 | 当前 | 目标（3 个月） |
|------|------|---------------|
| 规则库规模 | 0 条 | >20 条 |
| 策略优化次数 | 0 次 | >5 次 |
| 知识库案例 | 0 个 | >50 个 |

### 系统健康度
| 指标 | 当前 | 目标（3 个月） |
|------|------|---------------|
| 健康分数 | 100 | >90 |
| 错误率 | <5% | <3% |
| 自动化率 | 60% | >85% |

---

## ⚠️ 风险与对策

### 风险 1: 过度优化
**问题**: 频繁调整权重导致系统不稳定

**对策**:
- 设置调整冷却期（至少 7 天）
- 设置调整幅度上限（单次±5%）
- 保留手动覆盖能力

### 风险 2: 数据不足
**问题**: 验证数据太少，统计无意义

**对策**:
- 设置最小样本量（至少 10 次）
- 使用贝叶斯平滑（先验分布）
- 早期使用固定权重

### 风险 3: 规则过拟合
**问题**: 从少量案例提炼的规则泛化能力差

**对策**:
- 设置规则生效阈值（至少 3 次成功）
- 持续追踪规则效果
- 自动淘汰失效规则

---

## 🚀 立即行动计划

### 本周（2026-03-09 至 2026-03-15）

1. **创建 agent_performance_tracker.py** (2 天)
2. **集成到验证流程** (1 天)
3. **添加准确率统计 API** (1 天)
4. **前端展示准确率** (1 天)

### 下周（2026-03-16 至 2026-03-22）

1. **创建 dynamic_weight_adjuster.py** (2 天)
2. **集成到 CIO 决策** (1 天)
3. **测试权重调整** (2 天)

### 下下周（2026-03-23 至 2026-03-29）

1. **创建 rule_extractor.py** (2 天)
2. **从历史案例提炼规则** (2 天)
3. **规则应用集成** (1 天)

---

## 📊 预期收益

### 短期（1 个月）
- ✅ Agent 准确率可量化
- ✅ 权重动态调整
- ✅ 初步规则库建立

### 中期（2-3 个月）
- ✅ 整体准确率提升至 60%+
- ✅ 规则库规模 20+ 条
- ✅ 策略自动优化 5+ 次

### 长期（6 个月）
- ✅ 系统自进化能力形成
- ✅ 准确率稳定在 70%+
- ✅ 知识库案例 100+ 个

---

**最后更新**: 2026-03-09 11:15  
**维护者**: 小助理 🤖  
**状态**: 📋 待执行

---

## 🎯 下一步

**郭小主，建议按以下顺序实施**:

1. **立即执行**（本周）: Agent 表现追踪系统
2. **然后执行**（下周）: 动态权重调整系统
3. **最后执行**（下下周）: 规则自动提炼系统

**您要我立即开始实施哪个模块？** 🚀
