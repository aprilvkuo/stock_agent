#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新仪表盘 - 从数据文件生成可视化报告
"""

import os
import re
from datetime import datetime

WORKSPACE = '/Users/egg/.openclaw/workspace'
DATA_DIR = os.path.join(WORKSPACE, 'agents/stock-coordinator/data')
DASHBOARD_FILE = os.path.join(WORKSPACE, 'shared/stock-system/dashboard.md')

def get_analysis_summary():
    """获取分析摘要"""
    results_dir = os.path.join(DATA_DIR, 'queue/results')
    requests_dir = os.path.join(DATA_DIR, 'queue/requests')
    
    if not os.path.exists(results_dir):
        return []
    
    # 按请求分组
    requests = {}
    for f in os.listdir(results_dir):
        if f.endswith('.md'):
            filepath = os.path.join(results_dir, f)
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
                
                # 提取请求 ID
                req_match = re.search(r'请求 ID\n(.+)', content)
                if req_match:
                    req_id = req_match.group(1).strip()
                    if req_id not in requests:
                        requests[req_id] = {}
                    
                    # 提取评级
                    rating_match = re.search(r'\| 评级 \| (.+?) \|', content)
                    confidence_match = re.search(r'\| 置信度 \| (\d+)%', content)
                    
                    if 'fundamental' in f:
                        requests[req_id]['fundamental'] = {
                            'rating': rating_match.group(1) if rating_match else 'N/A',
                            'confidence': confidence_match.group(1) if confidence_match else 'N/A'
                        }
                    elif 'technical' in f:
                        requests[req_id]['technical'] = {
                            'rating': rating_match.group(1) if rating_match else 'N/A',
                            'confidence': confidence_match.group(1) if confidence_match else 'N/A'
                        }
                    elif 'sentiment' in f:
                        requests[req_id]['sentiment'] = {
                            'rating': rating_match.group(1) if rating_match else 'N/A',
                            'confidence': confidence_match.group(1) if confidence_match else 'N/A'
                        }
    
    # 关联请求信息
    summary = []
    for req_id, agents in sorted(requests.items(), reverse=True):
        req_file = os.path.join(requests_dir, f"{req_id}.md")
        if os.path.exists(req_file):
            with open(req_file, 'r', encoding='utf-8') as f:
                content = f.read()
                stock_match = re.search(r'股票代码：(\d+)', content)
                name_match = re.search(r'股票名称：(.+)', content)
                time_match = re.search(r'请求时间：(.+)', content)
                status_match = re.search(r'汇总：✅ 已完成 - (.+)', content)
                
                summary.append({
                    'time': time_match.group(1).strip() if time_match else 'Unknown',
                    'code': stock_match.group(1) if stock_match else 'Unknown',
                    'name': name_match.group(1).strip() if name_match else '',
                    'rating': status_match.group(1).strip() if status_match else 'N/A',
                    'agents': agents
                })
    
    return summary

def get_validation_summary():
    """获取验证摘要"""
    validation_file = os.path.join(DATA_DIR, 'validation-queue.md')
    if not os.path.exists(validation_file):
        return {'pending': 0, 'correct': 0, 'wrong': 0, 'items': []}
    
    with open(validation_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    pending = content.count('⏳ 待验证')
    correct = content.count('✅ 正确')
    wrong = content.count('❌ 错误')
    
    # 提取待验证项
    items = []
    for line in content.split('\n'):
        if '⏳ 待验证' in line:
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 5:
                items.append({
                    'stock': parts[2],
                    'prediction': parts[3],
                    'date': parts[4]
                })
    
    return {
        'pending': pending,
        'correct': correct,
        'wrong': wrong,
        'items': items[:10]  # 只显示前 10 项
    }

def get_backup_summary():
    """获取备份摘要"""
    backup_dir = os.path.join(DATA_DIR, 'backups')
    if not os.path.exists(backup_dir):
        return []
    
    backups = []
    for f in sorted(os.listdir(backup_dir), reverse=True)[:5]:
        if f.endswith('.md'):
            filepath = os.path.join(backup_dir, f)
            mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
            backups.append({
                'name': f,
                'time': mtime.strftime('%m-%d %H:%M')
            })
    
    return backups

def generate_dashboard():
    """生成仪表盘"""
    analysis = get_analysis_summary()
    validation = get_validation_summary()
    backups = get_backup_summary()
    
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    # 构建表格
    analysis_table = "| 时间 | 股票 | 基本面 | 技术面 | 情绪 | 综合评级 | 建议仓位 |\n"
    analysis_table += "|------|------|--------|--------|------|----------|----------|\n"
    
    for item in analysis:
        agents = item['agents']
        fundamental = f"{agents.get('fundamental', {}).get('rating', 'N/A')} ({agents.get('fundamental', {}).get('confidence', 'N/A')}%)"
        technical = f"{agents.get('technical', {}).get('rating', 'N/A')} ({agents.get('technical', {}).get('confidence', 'N/A')}%)"
        sentiment = f"{agents.get('sentiment', {}).get('rating', 'N/A')} ({agents.get('sentiment', {}).get('confidence', 'N/A')}%)"
        
        # 从评级提取仓位
        position = "10-15%" if "推荐" in item['rating'] else "5-10%"
        
        analysis_table += f"| {item['time']} | {item['code']} {item['name']} | {fundamental} | {technical} | {sentiment} | {item['rating']} | {position} |\n"
    
    # 验证表格
    validation_table = "| 股票 | 预测 | 验证日 | 状态 |\n"
    validation_table += "|------|------|--------|------|\n"
    
    for item in validation['items']:
        validation_table += f"| {item['stock']} | {item['prediction']} | {item['date']} | ⏳ 待验证 |\n"
    
    # 备份表格
    backup_table = "| 备份时间 | 文件 |\n"
    backup_table += "|---------|------|\n"
    
    for backup in backups:
        backup_table += f"| {backup['time']} | {backup['name']} |\n"
    
    # 生成完整仪表盘
    dashboard = f"""# 📊 股票多 Agent 系统 - 实时仪表盘

**最后更新**: {now}

---

## 🎯 系统状态

| 组件 | 状态 |
|------|------|
| 基本面 Agent | 🟢 就绪 |
| 技术面 Agent | 🟢 就绪 |
| 情绪 Agent | 🟢 就绪 |
| 主 Agent | 🟢 就绪 |
| 复盘 Agent | 🟢 就绪 |

---

## 📈 已完成分析

{analysis_table}

---

## ⏳ 待验证预测

**统计**: 待验证 {validation['pending']} 项 | 已验证正确 {validation['correct']} 项 | 已验证错误 {validation['wrong']} 项

{validation_table}

---

## 📊 Agent 表现追踪

| Agent | 分析次数 | 待验证 | 准确率 |
|-------|---------|--------|--------|
| 基本面-v1.0 | {len(analysis)} | {validation['pending']} | 待验证 |
| 技术面-v1.0 | {len(analysis)} | {validation['pending']} | 待验证 |
| 情绪-v1.0 | {len(analysis)} | {validation['pending']} | 待验证 |

---

## 💾 备份状态

{backup_table}

**备份策略**: 每次添加验证前自动备份，保留 30 天

---

## 📅 下次自动执行

| 任务 | 时间 |
|------|------|
| 请求检查 | 每 5-10 分钟 |
| 每日验证 | 今日 09:00 |
| 周度复盘 | 2026-03-13 20:00 |
| 首批验证到期 | 2026-04-07 |

---

## 🚀 快速操作

### 分析新股票

告诉我股票代码，例如：
- "分析 600519"
- "分析腾讯"
- "分析宁德时代"

### 查看记录

- "查看最新分析结果"
- "查看验证队列"
- "查看茅台的所有记录"

---

**系统运行正常，自动化监控中** 🟢

---

*此文档由股票多 Agent 系统自动生成*
*数据位置：agents/stock-coordinator/data/*
"""
    
    with open(DASHBOARD_FILE, 'w', encoding='utf-8') as f:
        f.write(dashboard)
    
    print(f"✅ 仪表盘已更新：{DASHBOARD_FILE}")

if __name__ == '__main__':
    generate_dashboard()
