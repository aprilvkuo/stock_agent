#!/usr/bin/env python3
"""自动告警系统 - 发现问题自动创建工单"""

import os, json
from datetime import datetime

STATS_FILE = '/Users/egg/.openclaw/workspace/shared/stock-system/stats/agent_stats.json'
TICKETS_DIR = '/Users/egg/.openclaw/workspace/shared/stock-system/tickets'

def create_ticket(anomaly):
    ticket_id = f"TICKET-AUTO-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    ticket = {
        'id': ticket_id,
        'title': f"[自动告警] {anomaly['message']}",
        'description': anomaly['message'],
        'error_type': 'auto_alert',
        'severity': anomaly['type'],
        'status': 'open',
        'assign_to': '程序员 Agent',
        'created_at': datetime.now().isoformat(),
        'auto_created': True,
        'source': '自动告警系统',
        'priority': 'P1' if anomaly['type'] == 'critical' else 'P2'
    }
    
    os.makedirs(TICKETS_DIR, exist_ok=True)
    with open(os.path.join(TICKETS_DIR, f"{ticket_id}.json"), 'w') as f:
        json.dump(ticket, f, ensure_ascii=False, indent=2)
    
    return ticket_id

def main():
    print("🚨 自动告警系统运行中...")
    
    if not os.path.exists(STATS_FILE):
        print("⚠️ 无统计数据，跳过")
        return
    
    with open(STATS_FILE, 'r') as f:
        report = json.load(f)
    
    anomalies = report.get('anomalies', [])
    tickets_created = 0
    
    for anomaly in anomalies:
        ticket_id = create_ticket(anomaly)
        print(f"✅ 创建工单：{ticket_id}")
        print(f"   - {anomaly['message']}")
        tickets_created += 1
    
    print(f"\n✅ 告警完成：创建{tickets_created}个工单")

if __name__ == '__main__':
    main()
