#!/usr/bin/env python3
"""数据统计系统 - 自动记录所有 Agent 表现"""

import os, json, re
from datetime import datetime

LOGS_DIR = '/Users/egg/.openclaw/workspace/agents/stock-coordinator/data/logs'
STATS_DIR = '/Users/egg/.openclaw/workspace/shared/stock-system/stats'

def collect_stats():
    today = datetime.now().strftime('%Y-%m-%d')
    log_file = os.path.join(LOGS_DIR, f'daemon-{today}.log')
    
    if not os.path.exists(log_file):
        return {}
    
    with open(log_file, 'r') as f:
        lines = f.readlines()
    
    agents = {
        'fundamental': {'name': '基本面 Agent', 'success': 0, 'error': 0},
        'technical': {'name': '技术面 Agent', 'success': 0, 'error': 0},
        'sentiment': {'name': '情绪 Agent', 'success': 0, 'error': 0},
        'coordinator': {'name': '主 Agent', 'success': 0, 'error': 0},
        'qa': {'name': '质检 Agent', 'success': 0, 'error': 0},
        'programmer': {'name': '程序员 Agent', 'success': 0, 'error': 0},
    }
    
    for line in lines:
        for agent_id in agents:
            if agent_id in line.lower() or agents[agent_id]['name'] in line:
                if 'SUCCESS' in line or '完成' in line:
                    agents[agent_id]['success'] += 1
                elif 'ERROR' in line or '失败' in line:
                    agents[agent_id]['error'] += 1
    
    # 计算成功率
    stats = {}
    for agent_id, data in agents.items():
        total = data['success'] + data['error']
        stats[agent_id] = {
            'name': data['name'],
            'success': data['success'],
            'error': data['error'],
            'total': total,
            'success_rate': round(data['success'] * 100 / total, 1) if total > 0 else 0,
            'error_rate': round(data['error'] * 100 / total, 1) if total > 0 else 0
        }
    
    return stats

def check_anomalies(stats):
    """检查异常"""
    anomalies = []
    thresholds = {
        'error_rate_warning': 10,
        'error_rate_critical': 20,
        'success_rate_min': 60
    }
    
    for agent_id, data in stats.items():
        if data['error_rate'] > thresholds['error_rate_critical']:
            anomalies.append({
                'agent': agent_id,
                'type': 'critical',
                'message': f"{data['name']}错误率{data['error_rate']}%超过严重阈值"
            })
        elif data['error_rate'] > thresholds['error_rate_warning']:
            anomalies.append({
                'agent': agent_id,
                'type': 'warning',
                'message': f"{data['name']}错误率{data['error_rate']}%超过警告阈值"
            })
        elif data['success_rate'] < thresholds['success_rate_min'] and data['total'] > 0:
            anomalies.append({
                'agent': agent_id,
                'type': 'warning',
                'message': f"{data['name']}成功率{data['success_rate']}%低于最低阈值"
            })
    
    return anomalies

def save_stats(stats, anomalies):
    os.makedirs(STATS_DIR, exist_ok=True)
    report = {
        'timestamp': datetime.now().isoformat(),
        'stats': stats,
        'anomalies': anomalies
    }
    
    with open(os.path.join(STATS_DIR, 'agent_stats.json'), 'w') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    return report

def main():
    print("📊 数据统计系统运行中...")
    stats = collect_stats()
    anomalies = check_anomalies(stats)
    report = save_stats(stats, anomalies)
    
    print(f"✅ 统计完成：{len(stats)}个 Agent")
    print(f"⚠️ 发现异常：{len(anomalies)}个")
    for a in anomalies:
        print(f"   - {a['message']}")

if __name__ == '__main__':
    main()
