#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主 Agent (协调者) - 独立执行脚本
负责：接收请求、分发任务、汇总结果、写入验证队列

遵循五步工作法:
1️⃣ UPDATE → 2️⃣ READ → 3️⃣ DO → 4️⃣ CHECK → 5️⃣ REVIEW
"""

import os
import sys
import json
from datetime import datetime, timedelta
import subprocess
import re

# 五步工作法检查点
FIVE_STEP_CHECKLIST = {
    'update': False,
    'read': False,
    'do': False,
    'check': False,
    'review': False
}

# 导入协作模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from agent_collaboration import AgentCollaboration

# 导入五步工作法监控
from five_step_monitor import record_task
import time

# 配置
WORKSPACE = '/Users/egg/.openclaw/workspace'
COORDINATOR_DIR = os.path.join(WORKSPACE, 'agents/stock-coordinator')
DATA_DIR = os.path.join(COORDINATOR_DIR, 'data')
QUEUE_DIR = os.path.join(DATA_DIR, 'queue')
REQUESTS_DIR = os.path.join(QUEUE_DIR, 'requests')
RESULTS_DIR = os.path.join(QUEUE_DIR, 'results')
VALIDATION_QUEUE = os.path.join(DATA_DIR, 'validation-queue.md')
BACKUP_DIR = os.path.join(DATA_DIR, 'backups')

def create_request(stock_code, stock_name=''):
    """创建分析请求"""
    request_id = f"request-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    request_file = os.path.join(REQUESTS_DIR, f"{request_id}.md")
    
    content = f"""# 分析请求 {request_id}

## 请求信息
- 请求 ID: {request_id}
- 请求时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 股票代码：{stock_code}
- 股票名称：{stock_name}

## 任务
- [ ] 基本面 Agent: 分析财报、估值、财务健康
- [ ] 技术面 Agent: 分析 K 线、技术指标
- [ ] 情绪 Agent: 分析舆情、市场热度

## 状态
- 基本面：⏳ 待处理
- 技术面：⏳ 待处理
- 情绪面：⏳ 待处理
- 汇总：⏳ 待处理
"""
    
    with open(request_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 创建请求：{request_id}.md")
    return request_id

def check_results(request_id):
    """检查结果是否完成"""
    fundamental_done = False
    technical_done = False
    sentiment_done = False
    
    fundamental_result = None
    technical_result = None
    sentiment_result = None
    
    for f in os.listdir(RESULTS_DIR):
        if f.endswith('.md'):
            filepath = os.path.join(RESULTS_DIR, f)
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
                # 检查是否包含请求 ID
                if request_id not in content:
                    continue
            filepath = os.path.join(RESULTS_DIR, f)
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
                
                if '基本面' in content:
                    fundamental_done = True
                    fundamental_result = parse_result(content)
                elif '技术面' in content:
                    technical_done = True
                    technical_result = parse_result(content)
                elif '情绪面' in content:
                    sentiment_done = True
                    sentiment_result = parse_result(content)
    
    return {
        'fundamental': {'done': fundamental_done, 'result': fundamental_result},
        'technical': {'done': technical_done, 'result': technical_result},
        'sentiment': {'done': sentiment_done, 'result': sentiment_result},
        'all_done': fundamental_done and technical_done and sentiment_done
    }

def parse_result(content):
    """解析结果文件"""
    result = {}
    
    # 评级
    rating_match = re.search(r'\| 评级 \| (.+?) \|', content)
    if rating_match:
        result['rating'] = rating_match.group(1).strip()
    
    # 置信度
    confidence_match = re.search(r'\| 置信度 \| (\d+)%', content)
    if confidence_match:
        result['confidence'] = int(confidence_match.group(1))
    
    # 依据
    reasons_match = re.search(r'\| 关键依据 \| (.+?) \|', content)
    if reasons_match:
        result['reasons'] = reasons_match.group(1).strip()
    
    return result

def make_decision_from_collab(final_judgments, stock_data):
    """基于协作后的判断做决策（新增）"""
    scores = {}
    weights = {
        '基本面 Agent': 0.35,
        '技术面 Agent': 0.30,
        '情绪 Agent': 0.20,
        '资金面 Agent': 0.15
    }
    
    total_score = 0
    total_weight = 0
    
    for agent_name, judgment in final_judgments.items():
        weight = weights.get(agent_name, 0.25)
        rating = judgment.get('rating', '持有')
        confidence = judgment.get('confidence', 50) / 100.0
        
        # 评级转分数
        rating_scores = {'买入': 100, '推荐': 80, '持有': 60, '中性': 50, '回避': 30, '卖出': 10}
        base_score = rating_scores.get(rating, 50)
        score = base_score * confidence
        
        scores[agent_name] = score
        total_score += score * weight
        total_weight += weight
    
    if total_weight > 0:
        total_score /= total_weight
    
    # 转评级
    if total_score >= 75:
        final_rating = '🟢 推荐'
        position = '10-15%'
    elif total_score >= 60:
        final_rating = '🟡 中性'
        position = '5-10%'
    else:
        final_rating = '🔴 回避'
        position = '0%'
    
    current_price = stock_data.get('price', 0)
    target_price = current_price * 1.05 if current_price else 0
    stop_price = current_price * 0.95 if current_price else 0
    
    return {
        'score': total_score,
        'rating': final_rating,
        'position': position,
        'target_price': target_price,
        'stop_price': stop_price,
        'breakdown': scores,
        'collab_used': True
    }

def make_decision(results, stock_data):
    """综合决策"""
    # 权重
    weights = {'fundamental': 0.5, 'technical': 0.3, 'sentiment': 0.2}
    
    # 评级转分数
    rating_to_score = {
        '买入': 80, '强烈推荐': 90,
        '持有': 50, '中性': 50,
        '卖出': 20, '回避': 20,
        '乐观': 70, '悲观': 30,
    }
    
    scores = {}
    confidences = {}
    
    for agent in ['fundamental', 'technical', 'sentiment']:
        data = results.get(agent, {})
        if isinstance(data, dict) and data.get('done') and data.get('result'):
            rating = data['result'].get('rating', '持有')
            confidence = data['result'].get('confidence', 60) / 100
            scores[agent] = rating_to_score.get(rating, 50)
            confidences[agent] = confidence
    
    # 加权计算
    total_score = sum(scores.get(k, 50) * weights.get(k, 0.33) for k in ['fundamental', 'technical', 'sentiment'])
    avg_confidence = sum(confidences.values()) / len(confidences) if confidences else 0.6
    
    # 综合评级
    if total_score >= 70:
        final_rating = '🟢 推荐'
        position = '10-15%'
    elif total_score >= 55:
        final_rating = '🟡 中性'
        position = '5-10%'
    else:
        final_rating = '🔴 回避'
        position = '0%'
    
    # 计算目标价和止损价
    current_price = stock_data.get('price', 0)
    target_price = current_price * 1.05 if current_price else 0
    stop_price = current_price * 0.95 if current_price else 0
    
    return {
        'score': total_score,
        'rating': final_rating,
        'position': position,
        'target_price': target_price,
        'stop_price': stop_price,
        'breakdown': scores,
    }

def backup_data():
    """备份数据"""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(BACKUP_DIR, f'validation_backup_{timestamp}.md')
    
    if os.path.exists(VALIDATION_QUEUE):
        with open(VALIDATION_QUEUE, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(content)

def add_to_validation_queue(stock_code, stock_name, decision):
    """添加待验证项"""
    # 先备份
    backup_data()
    
    today = datetime.now().strftime('%m-%d')
    validate_date = (datetime.now() + timedelta(days=30)).strftime('%m-%d')
    
    if not os.path.exists(VALIDATION_QUEUE):
        # 创建文件
        with open(VALIDATION_QUEUE, 'w', encoding='utf-8') as f:
            f.write("# 待验证预测队列\n\n")
            f.write("| 日期 | 股票 | 预测内容 | 验证日 | 状态 | 实际结果 | 偏差分析 |\n")
            f.write("|------|------|----------|--------|------|----------|----------|\n")
    
    with open(VALIDATION_QUEUE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 添加新行
    target = decision['target_price']
    stop = decision['stop_price']
    
    new_lines = [
        f"| {today} | {stock_code} {stock_name} | 突破 ¥{target:.0f} | {validate_date} | ⏳ 待验证 | | |",
        f"| {today} | {stock_code} {stock_name} | 不跌破 ¥{stop:.0f} | {validate_date} | ⏳ 待验证 | | |",
    ]
    
    # 插入到表格中
    lines = content.split('\n')
    new_content = []
    inserted = False
    
    for line in lines:
        new_content.append(line)
        if line.startswith('|') and '待验证' in line and not inserted:
            for nl in reversed(new_lines):
                new_content.insert(-1, nl)
            inserted = True
    
    if not inserted:
        # 添加到末尾
        new_content.extend(new_lines)
    
    with open(VALIDATION_QUEUE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_content))

def process_pending():
    """处理待汇总的请求"""
    for f in os.listdir(REQUESTS_DIR):
        if f.endswith('.md'):
            filepath = os.path.join(REQUESTS_DIR, f)
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
                
                # 检查是否已完成所有分析但尚未汇总
                if '汇总：⏳ 待处理' in content:
                    request_id = f.replace('.md', '')
                    
                    # 检查结果
                    results = check_results(request_id)
                    
                    if results['all_done']:
                        print(f"\n📋 汇总请求：{request_id}")
                        
                        # 提取股票信息
                        stock_match = re.search(r'股票代码：(\d+)', content)
                        name_match = re.search(r'股票名称：(.+)', content)
                        stock_code = stock_match.group(1) if stock_match else 'Unknown'
                        stock_name = name_match.group(1).strip() if name_match else ''
                        
                        # 获取股价数据（用于计算目标价）
                        stock_data = get_stock_data(stock_code)
                        
                        # === 新增：Agent 协作流程 ===
                        print(f"\n🤝 启动 Agent 协作...")
                        collab = AgentCollaboration(request_id)
                        
                        # 1. 各 Agent 注册初始判断
                        for agent_name, result_data in results.items():
                            if agent_name != 'all_done' and result_data:
                                judgment = {
                                    'rating': result_data.get('rating', '持有'),
                                    'confidence': result_data.get('confidence', 50),
                                    'reasons': result_data.get('reasons', []),
                                    'data_quality': result_data.get('data_quality', 'medium')
                                }
                                collab.register_agent(agent_name, judgment)
                        
                        # 2. 共享上下文，允许 Agent 调整判断
                        for agent_name in results.keys():
                            if agent_name == 'all_done':
                                continue
                            
                            # 获取其他 Agent 的判断
                            context = collab.share_context(agent_name)
                            
                            # 简单规则：如果大多数 Agent 看好，低置信度的 Agent 可以调整
                            positive_count = sum(1 for a, d in context['other_agents'].items() 
                                               if d['rating'] in ['买入', '推荐'])
                            total = len(context['other_agents'])
                            
                            if positive_count > total * 0.5:  # 超过一半看好
                                # 获取当前 Agent 的判断
                                current = results[agent_name]
                                if current.get('confidence', 50) < 70 and current.get('rating') != '买入':
                                    # 调整判断
                                    adjusted = current.copy()
                                    adjusted['rating'] = '买入'
                                    adjusted['confidence'] = min(current.get('confidence', 50) + 10, 80)
                                    collab.adjust_judgment(agent_name, adjusted, 
                                                         f"参考其他 Agent 判断（{positive_count}/{total} 看好）")
                        
                        # 3. 添加讨论记录
                        collab.add_discussion('主 Agent', f'启动协作流程，共{len(results)-1}个 Agent 参与', 'comment')
                        
                        # 4. 获取最终判断（使用调整后的）
                        final_judgments = collab.get_final_judgments()
                        
                        # 5. 生成协作报告
                        discussion_log = collab.get_discussion_log()
                        print(f"  💬 讨论记录：{len(collab.data['discussion'])} 条")
                        
                        # ===========================
                        
                        # 综合决策（使用协作后的判断）
                        decision = make_decision_from_collab(final_judgments, stock_data or {})
                        
                        print(f"  综合评分：{decision['score']:.1f}")
                        print(f"  评级：{decision['rating']}")
                        
                        # 更新请求状态
                        new_content = content.replace('汇总：⏳ 待处理', 
                                                    f"汇总：✅ 已完成 - {decision['rating']}\n\n## Agent 协作记录\n{discussion_log}")
                        with open(filepath, 'w', encoding='utf-8') as file:
                            file.write(new_content)
                        
                        # 添加到验证队列
                        add_to_validation_queue(stock_code, stock_name, decision)
                        print(f"  ✅ 已添加到验证队列")
                        
                        # 完成协作
                        collab.finalize(decision)

def get_stock_data(stock_code):
    """获取股票数据"""
    try:
        result = subprocess.run(
            ['python3', '/Users/egg/.openclaw/workspace/skills/stock-analyzer/scripts/analyze_stock.py', stock_code],
            capture_output=True, text=True, timeout=60
        )
        output = result.stdout
        
        data = {}
        price_match = re.search(r'当前股价：¥([\d.]+)', output)
        if price_match:
            data['price'] = float(price_match.group(1))
        return data
    except:
        return {}

def main():
    start_time = time.time()
    
    print(f"\n{'='*50}")
    print(f"🎯 主 Agent - 协调者")
    print(f"{'='*50}\n")
    
    # 1️⃣ UPDATE
    print("📋 五步工作法：UPDATE - 更新状态")
    
    # 2️⃣ READ
    print("📋 五步工作法：READ - 读取任务")
    
    # 3️⃣ DO
    print("📋 五步工作法：DO - 执行任务")
    process_pending()
    
    # 4️⃣ CHECK
    print("📋 五步工作法：CHECK - 检查结果")
    
    # 5️⃣ REVIEW
    print("📋 五步工作法：REVIEW - 复盘优化")
    
    # 记录五步工作法执行
    duration = time.time() - start_time
    record_task('主 Agent', '协调股票分析', 
               ['UPDATE', 'READ', 'DO', 'CHECK', 'REVIEW'], 
               duration)
    
    print(f"\n{'='*50}")
    print(f"✅ 主 Agent 执行完成 (耗时：{duration:.2f}秒)")
    print(f"{'='*50}\n")

if __name__ == '__main__':
    main()
