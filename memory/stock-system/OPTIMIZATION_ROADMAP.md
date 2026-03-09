# 股票多 Agent 系统 - 优化路线图

**制定日期**: 2026-03-08  
**当前版本**: v1.0  
**目标版本**: v2.0

---

## 📊 当前系统状态

### ✅ 已完成
| 模块 | 状态 | 说明 |
|------|------|------|
| 基础架构 | ✅ | 5 个 Agent 角色定义完成 |
| 自动化脚本 | ✅ | auto_agent.py, validate_predictions.py, run_review.py |
| Heartbeat 配置 | ✅ | 每日 09:00 验证，每周五 20:00 复盘 |
| 分析日志 | ✅ | 已完成 3 次分析（茅台/腾讯/五粮液） |
| 验证队列 | ✅ | 10 项待验证预测 |

### ⏳ 待完善
| 模块 | 优先级 | 说明 |
|------|--------|------|
| 验证结果自动写入 | 🔴 高 | validate_predictions.py 只打印不更新文件 |
| 周度复盘功能 | 🔴 高 | weekly 功能未完成 |
| 动态权重调整 | 🟡 中 | 当前权重固定，需根据表现调整 |
| 情绪 Agent 增强 | 🟡 中 | 仅基于涨跌幅，需增加维度 |
| 并发优化 | 🟡 中 | 当前顺序执行，可改为并发 |
| 实时监控预警 | 🟢 低 | 缺少股价监控和预警 |
| 支持股票扩展 | 🟢 低 | 需 stock-analyzer 支持更多股票 |

---

## 🎯 优化目标

### 短期（1-2 周）- v1.1
1. **修复验证流程** - 验证结果自动写入文件
2. **完成周度复盘** - 实现 weekly 功能
3. **增强情绪分析** - 加入更多情绪维度

### 中期（1 个月）- v1.5
1. **动态权重系统** - 根据 Agent 表现自动调整权重
2. **并发执行优化** - 多 Agent 并行分析
3. **规则库自动更新** - 从验证结果自动提炼规则

### 长期（2-3 个月）- v2.0
1. **实时监控预警** - 股价异动自动提醒
2. **Agent 自进化** - 基于历史表现自动优化策略
3. **支持更多股票** - 扩展 stock-analyzer 覆盖范围

---

## 🔧 具体优化方案

### 1. 验证结果自动写入（优先级：🔴 高）

**问题**: validate_predictions.py 只打印结果，不更新 validation-queue.md

**解决方案**:
```python
def update_validation_status(stock_code, prediction, status, analysis):
    """更新验证队列中的状态"""
    queue_path = os.path.join(STOCK_SYSTEM, 'validation-queue.md')
    
    with open(queue_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 找到对应行并更新
    for i, line in enumerate(lines):
        if stock_code in line and prediction in line and '待验证' in line:
            # 更新状态和实际结果
            parts = line.split('|')
            parts[5] = f' {status} '
            parts[6] = f' {analysis} '
            lines[i] = '|'.join(parts)
            break
    
    with open(queue_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
```

**预期效果**: 验证后自动更新队列状态，无需手动操作

---

### 2. 周度复盘功能（优先级：🔴 高）

**问题**: auto_agent.py 中 weekly 功能只是 TODO

**解决方案**:
```python
def run_weekly_review():
    """执行周度复盘"""
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    
    # 1. 统计本周分析记录
    analysis_count = 0
    stocks_analyzed = []
    
    for f in os.listdir(ANALYSIS_LOG_DIR):
        if f.endswith('.md') and not f.startswith('分析日志模板'):
            file_date = datetime.strptime(f[:10], '%Y-%m-%d')
            if file_date >= week_start:
                analysis_count += 1
                stocks_analyzed.append(f)
    
    # 2. 统计验证结果
    validated_count = 0
    correct_count = 0
    
    with open(os.path.join(STOCK_SYSTEM, 'validation-queue.md'), 'r') as f:
        for line in f:
            if '✅ 正确' in line:
                validated_count += 1
                correct_count += 1
            elif '❌ 错误' in line:
                validated_count += 1
    
    # 3. 生成周度报告
    report_path = os.path.join(REPORTS_DIR, f'weekly_{today.strftime("%Y-%m-%d")}.md')
    
    content = f"""# 周度复盘报告

**周期**: {week_start.strftime('%Y-%m-%d')} 至 {today.strftime('%Y-%m-%d')}

## 核心指标

| 指标 | 数值 |
|------|------|
| 分析次数 | {analysis_count} |
| 验证次数 | {validated_count} |
| 准确率 | {correct_count/validated_count*100 if validated_count > 0 else 0:.1f}% |

## 分析股票列表
{chr(10).join(['- ' + s for s in stocks_analyzed])}

## Agent 表现
| Agent | 分析次数 | 准确率 | 权重调整建议 |
|-------|---------|--------|-------------|
| 基本面 | {analysis_count} | 待验证 | 保持 50% |
| 技术面 | {analysis_count} | 待验证 | 保持 30% |
| 情绪 | {analysis_count} | 待验证 | 保持 20% |

## 改进建议
- 继续积累验证数据
- 等待首批验证结果（预计 2026-04-07）
"""
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return report_path
```

---

### 3. 情绪 Agent 增强（优先级：🟡 中）

**问题**: 当前仅基于涨跌幅判断情绪，过于简单

**优化方案**:
```python
def analyze_sentiment_enhanced(data):
    """增强版情绪 Agent 分析"""
    rating = '中性'
    confidence = 55
    reasons = []
    risks = []
    
    # 1. 涨跌幅分析（原有）
    if data.get('change_pct'):
        change = data['change_pct']
        if change > 5:
            reasons.append(f"大涨{change}%，市场情绪高涨")
            rating = '乐观'
            confidence = 70
        elif change > 2:
            reasons.append(f"上涨{change}%，情绪偏乐观")
            rating = '乐观'
            confidence = 65
        elif change < -5:
            reasons.append(f"大跌{change}%，市场情绪悲观")
            rating = '悲观'
            confidence = 70
        elif change < -2:
            reasons.append(f"下跌{change}%，情绪偏悲观")
            rating = '悲观'
            confidence = 65
        else:
            reasons.append(f"震荡{change}%，情绪中性")
    
    # 2. 成交量分析（新增）
    if data.get('volume'):
        # 可对比历史平均成交量
        reasons.append(f"成交量{data['volume']}手")
    
    # 3. 资金流向（新增，需数据源支持）
    # TODO: 获取北向资金、主力资金流向
    
    # 4. 市场热度（新增）
    # TODO: 获取换手率、量比等指标
    
    # 5. 消息面（新增）
    # TODO: 抓取相关新闻，进行情感分析
    
    risks.append("情绪面变化快，需结合基本面和技术面")
    
    return {
        'rating': rating,
        'confidence': confidence,
        'reasons': reasons,
        'risks': risks,
    }
```

---

### 4. 动态权重调整（优先级：🟡 中）

**问题**: 当前 Agent 权重固定（50%/30%/20%），无法根据表现优化

**解决方案**:
```python
def calculate_dynamic_weights():
    """根据历史表现计算动态权重"""
    tracker_path = os.path.join(STOCK_SYSTEM, 'agent-performance/agent-performance-tracker.md')
    
    # 基础权重
    base_weights = {
        'fundamental': 0.5,
        'technical': 0.3,
        'sentiment': 0.2,
    }
    
    # 从 performance tracker 读取准确率
    # TODO: 解析 agent-performance-tracker.md
    
    # 根据准确率调整
    adjustments = {
        'fundamental': 0.0,  # >80%: +0.1, <60%: -0.1
        'technical': 0.0,
        'sentiment': 0.0,
    }
    
    # 归一化
    total = sum(base_weights[k] + adjustments[k] for k in base_weights)
    
    return {
        k: (base_weights[k] + adjustments[k]) / total
        for k in base_weights
    }
```

---

### 5. 并发执行优化（优先级：🟡 中）

**问题**: 当前 3 个 Agent 顺序执行，耗时较长

**解决方案**:
```python
import concurrent.futures

def analyze_stock_parallel(stock_code):
    """并发执行多 Agent 分析"""
    # 获取数据
    data = get_stock_data(stock_code)
    
    # 并发执行 3 个 Agent
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_agent = {
            executor.submit(analyze_fundamental, data): 'fundamental',
            executor.submit(analyze_technical, data): 'technical',
            executor.submit(analyze_sentiment_enhanced, data): 'sentiment',
        }
        
        results = {}
        for future in concurrent.futures.as_completed(future_to_agent):
            agent_name = future_to_agent[future]
            results[agent_name] = future.result()
    
    # 主 Agent 决策
    decision = make_decision(
        results['fundamental'],
        results['technical'],
        results['sentiment']
    )
    
    return data, results, decision
```

**预期效果**: 分析时间减少 50-60%

---

### 6. 规则库自动更新（优先级：🟡 中）

**问题**: stock-wisdom.md 需要手动更新

**解决方案**:
```python
def auto_update_rules(validated_predictions):
    """根据验证结果自动更新规则库"""
    rules_path = os.path.join(STOCK_SYSTEM, 'stock-wisdom.md')
    
    # 分析验证结果，识别模式
    patterns = {
        'success': [],
        'failure': [],
    }
    
    for pred in validated_predictions:
        if pred['status'] == '✅ 正确':
            patterns['success'].append(pred)
        elif pred['status'] == '❌ 错误':
            patterns['failure'].append(pred)
    
    # 提炼规则
    new_rules = []
    
    # 成功案例：提取共同特征
    if len(patterns['success']) >= 3:
        # 找到共同点（如：ROE>20% 且 PE<30 时预测准确率高）
        # TODO: 实现模式识别算法
        pass
    
    # 失败案例：提取教训
    if len(patterns['failure']) >= 3:
        # 找到共同点（如：情绪面权重过高导致误判）
        # TODO: 实现模式识别算法
        pass
    
    # 写入规则库
    # TODO: 更新 stock-wisdom.md
```

---

### 7. 实时监控预警（优先级：🟢 低）

**新增功能**: 股价异动自动提醒

**实现方案**:
```python
# 新增文件：scripts/price_monitor.py

def monitor_prices():
    """监控持仓股票价格"""
    # 读取持仓配置
    holdings = [
        {'code': '600519', 'target': 1720, 'stop': 1580},
        {'code': '00700', 'target': 320, 'stop': 270},
    ]
    
    for stock in holdings:
        data = get_stock_data(stock['code'])
        
        if data['price'] >= stock['target']:
            send_alert(f"🎯 {stock['code']} 已突破目标价 {stock['target']}元")
        
        if data['price'] <= stock['stop']:
            send_alert(f"⚠️ {stock['code']} 已触及止损位 {stock['stop']}元")
```

**Heartbeat 配置**:
```markdown
## 每小时 - 价格监控
- [ ] 检查持仓股票价格
- [ ] 触发预警（如需要）
```

---

### 8. 支持股票扩展（优先级：🟢 低）

**问题**: stock-analyzer 当前仅支持 5 只股票

**解决方案**:
1. 增强 stock-analyzer 数据源（接入更多 API）
2. 或添加股票数据缓存机制
3. 或支持用户自定义股票数据输入

---

## 📅 实施计划

### 第 1 周（2026-03-08 ~ 2026-03-14）
- [ ] 修复验证结果自动写入
- [ ] 完成周度复盘功能
- [ ] 首次 Heartbeat 执行（03-09 09:00）

### 第 2 周（2026-03-15 ~ 2026-03-21）
- [ ] 增强情绪 Agent
- [ ] 实现动态权重调整
- [ ] 首次周度复盘（03-13 20:00）

### 第 3-4 周（2026-03-22 ~ 2026-04-04）
- [ ] 并发执行优化
- [ ] 规则库自动更新
- [ ] 积累 20+ 分析案例

### 第 5-8 周（2026-04-05 ~ 2026-05-02）
- [ ] 首批验证（04-07 开始）
- [ ] 实时监控预警
- [ ] 支持股票扩展
- [ ] v2.0 发布

---

## 📈 成功指标

| 指标 | 当前 | 目标（v2.0） |
|------|------|-------------|
| 分析速度 | ~30 秒/股 | <15 秒/股 |
| 支持股票 | 5 只 | 50+ 只 |
| 规则数量 | 0 条 | 20+ 条 |
| 验证准确率 | 待验证 | >70% |
| 自动化程度 | 70% | 95% |

---

## ⚠️ 风险与注意事项

1. **数据源依赖**: stock-analyzer 数据源稳定性影响系统可靠性
2. **验证周期长**: 首批验证需等到 04-07，优化效果验证需要时间
3. **过度拟合风险**: 规则提炼需避免过度拟合历史数据
4. **市场风险**: 系统仅提供参考，不构成投资建议

---

**制定者**: 小助理 🤖  
**最后更新**: 2026-03-08
