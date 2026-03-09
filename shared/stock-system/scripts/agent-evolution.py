#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
进化 Agent - 监督和优化其他 Agent（包括质检 Agent）

核心职责:
1. 监督质检 Agent 的检测准确率
2. 评估各 Agent 表现
3. 调整权重和阈值
4. 创建优化工单
5. 生成进化报告

进化机制:
质检 Agent → 监督其他 Agent
进化 Agent → 监督质检 Agent
主 Agent   → 综合决策
"""

import os, sys, json, re
from datetime import datetime, timedelta

# 配置
WORKSPACE = '/Users/egg/.openclaw/workspace'
DATA_DIR = os.path.join(WORKSPACE, 'agents/stock-coordinator/data')
LOGS_DIR = os.path.join(DATA_DIR, 'logs')
SYSTEM_DIR = os.path.join(WORKSPACE, 'shared/stock-system')
TICKETS_DIR = os.path.join(SYSTEM_DIR, 'tickets')
MONITOR_DIR = os.path.join(SYSTEM_DIR, 'monitor')

def log(message, level='INFO'):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{ts}] [{level}] {message}")

def review_qa_agent():
    """审查质检 Agent 的表现"""
    log("🔍 审查质检 Agent...", 'INFO')
    
    # 1. 读取质检历史报告
    report_file = os.path.join(MONITOR_DIR, 'quality_report.json')
    if not os.path.exists(report_file):
        log("   无质检报告，无法审查", 'WARNING')
        return {'status': 'no_data'}
    
    with open(report_file, 'r') as f:
        report = json.load(f)
    
    # 2. 分析质检准确率
    total_checks = report.get('summary', {}).get('total_checks', 0)
    critical_issues = report.get('summary', {}).get('critical_issues', 0)
    warnings = report.get('summary', {}).get('warnings', 0)
    health_score = report.get('summary', {}).get('health_score', 100)
    
    # 3. 检查工单创建情况
    tickets_dir = os.path.join(SYSTEM_DIR, 'tickets')
    qa_tickets = [f for f in os.listdir(tickets_dir) if 'TICKET-QA' in f and f.endswith('.json')]
    
    # 4. 评估质检表现
    review = {
        'agent': '质检 Agent',
        'total_checks': total_checks,
        'issues_found': critical_issues + warnings,
        'tickets_created': len(qa_tickets),
        'health_score': health_score,
        'performance': 'unknown'
    }
    
    # 5. 判断表现
    if total_checks > 0 and len(qa_tickets) == 0 and critical_issues == 0:
        # 可能是系统健康，也可能是质检不力
        log("   质检 Agent 未创建工单", 'INFO')
        log("   可能原因：系统健康 OR 质检不力", 'INFO')
        review['performance'] = 'needs_review'
    elif critical_issues > 0 and len(qa_tickets) > 0:
        log(f"   质检 Agent 发现{critical_issues}个严重问题，创建{len(qa_tickets)}个工单", 'SUCCESS')
        review['performance'] = 'good'
    else:
        review['performance'] = 'unknown'
    
    # 6. 自我反思检查
    self_reflection = report.get('self_reflection', {})
    if self_reflection.get('check_accuracy') == '待统计':
        log("   ⚠️ 质检 Agent 自我反思未完成", 'WARNING')
        review['needs_improvement'] = 'self_reflection'
    
    return review

def evaluate_all_agents():
    """评估所有 Agent 表现"""
    log("📊 评估所有 Agent...", 'INFO')
    
    today = datetime.now().strftime('%Y-%m-%d')
    log_file = os.path.join(LOGS_DIR, f'daemon-{today}.log')
    
    if not os.path.exists(log_file):
        return {}
    
    with open(log_file, 'r') as f:
        lines = f.readlines()
    
    agents = {
        'fundamental': {'name': '基本面 Agent', 'pattern': 'fundamental Agent 完成'},
        'technical': {'name': '技术面 Agent', 'pattern': 'technical Agent 完成'},
        'sentiment': {'name': '情绪 Agent', 'pattern': 'sentiment Agent 完成'},
        'coordinator': {'name': '主 Agent', 'pattern': '主 Agent 汇总完成'},
        'qa': {'name': '质检 Agent', 'pattern': '质检 Agent 完成'},
        'programmer': {'name': '程序员 Agent', 'pattern': '程序员 Agent 完成'},
    }
    
    evaluations = {}
    
    for agent_id, config in agents.items():
        run_count = sum(1 for line in lines if config['pattern'] in line and 'SUCCESS' in line)
        error_count = sum(1 for line in lines if config['pattern'] in line and 'ERROR' in line)
        
        success_rate = run_count * 100 / (run_count + error_count) if (run_count + error_count) > 0 else 0
        
        evaluations[agent_id] = {
            'name': config['name'],
            'run_count': run_count,
            'error_count': error_count,
            'success_rate': round(success_rate, 1),
            'performance': 'excellent' if success_rate >= 95 else 'good' if success_rate >= 80 else 'needs_improvement'
        }
    
    return evaluations

def create_optimization_ticket(agent, issue, suggestion):
    """创建优化建议工单"""
    log(f"🎫 创建优化工单：{agent} - {issue[:30]}...", 'INFO')
    
    ticket_id = f"TICKET-EVOLUTION-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    ticket = {
        'id': ticket_id,
        'title': f"[进化建议] {agent} - {issue[:40]}",
        'description': f"{issue}\n\n建议：{suggestion}",
        'error_type': 'optimization',
        'error_message': issue,
        'severity': 'suggestion',
        'status': 'open',
        'assign_to': '程序员 Agent',
        'created_at': datetime.now().isoformat(),
        'auto_created': True,
        'source': '进化 Agent',
        'priority': 'P3',
        'suggestion': suggestion
    }
    
    ticket_file = os.path.join(TICKETS_DIR, f"{ticket_id}.json")
    
    try:
        os.makedirs(TICKETS_DIR, exist_ok=True)
        with open(ticket_file, 'w', encoding='utf-8') as f:
            json.dump(ticket, f, ensure_ascii=False, indent=2)
        log(f"✅ 优化工单已创建：{ticket_id}", 'SUCCESS')
        return ticket_id
    except Exception as e:
        log(f"❌ 创建工单失败：{e}", 'ERROR')
        return None

def generate_evolution_report(reviews, evaluations):
    """生成进化报告"""
    log("📊 生成进化报告...", 'INFO')
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'version': '1.0',
        'qa_review': reviews,
        'agent_evaluations': evaluations,
        'optimizations': [],
        'recommendations': []
    }
    
    # 分析需要优化的 Agent
    for agent_id, eval_data in evaluations.items():
        if eval_data['performance'] == 'needs_improvement':
            suggestion = f"建议优化{eval_data['name']}，当前成功率{eval_data['success_rate']}%"
            report['optimizations'].append({
                'agent': agent_id,
                'issue': f"成功率{eval_data['success_rate']}%低于 80%",
                'suggestion': suggestion
            })
            report['recommendations'].append(f"🟡 {eval_data['name']}需要优化")
    
    # 检查质检 Agent
    if reviews.get('performance') == 'needs_review':
        report['recommendations'].append("🔍 质检 Agent 需要审查")
    
    if not report['recommendations']:
        report['recommendations'].append("✅ 所有 Agent 表现良好")
    
    # 保存报告
    report_file = os.path.join(MONITOR_DIR, 'evolution_report.json')
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    log(f"✅ 进化报告已保存：{report_file}", 'SUCCESS')
    log(f"   Agent 评估：{len(evaluations)}个", 'INFO')
    log(f"   优化建议：{len(report['optimizations'])}项", 'INFO')
    
    return report

def main():
    """主函数"""
    log("=" * 60, 'INFO')
    log("🧬 进化 Agent - 监督和优化其他 Agent", 'INFO')
    log("=" * 60, 'INFO')
    
    # 1. 审查质检 Agent
    qa_review = review_qa_agent()
    
    # 2. 评估所有 Agent
    evaluations = evaluate_all_agents()
    
    # 3. 生成进化报告
    report = generate_evolution_report(qa_review, evaluations)
    
    # 4. 创建优化工单
    for opt in report.get('optimizations', []):
        create_optimization_ticket(opt['agent'], opt['issue'], opt['suggestion'])
    
    log("=" * 60, 'INFO')
    log("✅ 进化 Agent 执行完成", 'SUCCESS')
    log(f"   审查质检 Agent: {qa_review.get('performance', 'unknown')}", 'INFO')
    log(f"   评估 Agent: {len(evaluations)}个", 'INFO')
    log(f"   优化建议：{len(report.get('optimizations', []))}项", 'INFO')
    log("=" * 60, 'INFO')

if __name__ == '__main__':
    main()
