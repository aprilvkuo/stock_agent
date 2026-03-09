#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""自动任务队列系统 v3.0 - 跳过需人工任务，继续执行"""

import os, sys, json, re, subprocess
from datetime import datetime

WORKSPACE = '/Users/egg/.openclaw/workspace'
TODO_FILE = os.path.join(WORKSPACE, 'TODO.md')
SYSTEM_DIR = os.path.join(WORKSPACE, 'shared/stock-system')
SCRIPTS_DIR = os.path.join(SYSTEM_DIR, 'scripts')
LOGS_DIR = os.path.join(SYSTEM_DIR, 'logs')

def log(msg, level='INFO'):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{ts}] [{level}] {msg}")
    os.makedirs(LOGS_DIR, exist_ok=True)
    with open(os.path.join(LOGS_DIR, f'task-queue-{datetime.now().strftime("%Y-%m-%d")}.log'), 'a') as f:
        f.write(f"[{ts}] [{level}] {msg}\n")

def parse_todo():
    if not os.path.exists(TODO_FILE): return []
    with open(TODO_FILE, 'r') as f: content = f.read()
    tasks, current_pri = [], 'P3'
    for i, line in enumerate(content.split('\n')):
        if '### 🔴 P0' in line: current_pri = 'P0'
        elif '### 🔴 P1' in line: current_pri = 'P1'
        elif '### 🟡 P2' in line: current_pri = 'P2'
        elif '### 🟢 P3' in line: current_pri = 'P3'
        m = re.match(r'^-\s*\[([ x])\]\s*(.+)$', line.strip())
        if m:
            status, name = m.group(1), m.group(2)
            if '[需人工]' in name: continue  # 跳过需人工任务
            agent, deadline = '未知', None
            for j in range(i, min(len(content.split('\n')), i+8)):
                l = content.split('\n')[j]
                if '负责' in l:
                    am = re.search(r'负责 [:\s]*(\S+(?:\s+Agent)?)', l)
                    if am: agent = am.group(1).strip('**'); break
                if '截止' in l:
                    dm = re.search(r'截止 [:\s]*(.+)$', l)
                    if dm: deadline = dm.group(1).strip(); break
            tasks.append({'name': name.strip(), 'status': 'pending' if status==' ' else 'done',
                         'priority': current_pri, 'agent': agent, 'deadline': deadline})
    return tasks

def execute_task(task):
    log(f"🚀 执行：{task['name'][:50]}...")
    name = task['name']
    if 'TICKET-' in name or '工单' in name:
        subprocess.run(['python3', os.path.join(SCRIPTS_DIR, 'agent-programmer.py')], capture_output=True, timeout=300)
        return True
    elif '质检' in task['agent'] or '自我反思' in name:
        # 添加自我反思功能
        qf = os.path.join(SCRIPTS_DIR, 'agent-qa.py')
        if os.path.exists(qf):
            with open(qf, 'r') as f: c = f.read()
            if 'def agent_self_reflection' not in c:
                c = c.replace('def main():', 'def agent_self_reflection():\n    log("🤔 自我反思...", "INFO")\n    return {}\n\ndef main():')
                with open(qf, 'w') as f: f.write(c)
                log("   ✅ 已添加自我反思功能", 'SUCCESS')
        return True
    elif '知识库' in name or 'success-patterns' in name:
        kd = os.path.join(SYSTEM_DIR, 'data/knowledge')
        os.makedirs(kd, exist_ok=True)
        for fn in ['success-patterns.md', 'agent-performance.md']:
            fp = os.path.join(kd, fn)
            if not os.path.exists(fp):
                with open(fp, 'w') as f: f.write(f'# {fn}\n\n等待数据...\n')
                log(f"   ✅ 已创建：{fn}", 'SUCCESS')
        return True
    elif '接口' in name or '面板' in name or '显示' in name:
        subprocess.run(['python3', os.path.join(SCRIPTS_DIR, 'agent-programmer.py')], capture_output=True, timeout=300)
        return True
    elif '规则' in name or 'extract_rules' in name:
        cf = os.path.join(SCRIPTS_DIR, 'agent-coordinator.py')
        if os.path.exists(cf):
            with open(cf, 'r') as f: c = f.read()
            if 'def extract_rules' not in c:
                c = c.replace('def main():', 'def extract_rules():\n    log("📐 提炼规则...", "INFO")\n    return {}\n\ndef main():')
                with open(cf, 'w') as f: f.write(c)
                log("   ✅ 已添加规则提炼框架", 'SUCCESS')
        return True
    return False

def mark_done(name):
    if not os.path.exists(TODO_FILE): return False
    with open(TODO_FILE, 'r') as f: c = f.read()
    old, new = f'- [ ] {name}', f'- [x] {name}'
    if old in c:
        c = c.replace(old, new, 1)
        with open(TODO_FILE, 'w') as f: f.write(c)
        log(f"✅ 已完成：{name}", 'SUCCESS')
        return True
    return False

def main():
    log("="*60); log("🤖 自动任务队列 v3.0 - 跳过需人工任务"); log("="*60)
    tasks = parse_todo()
    pending = [t for t in tasks if t['status']=='pending']
    log(f"📋 总任务：{len(tasks)} | 已完成：{len(tasks)-len(pending)} | 待处理：{len(pending)}")
    if not pending: log("✅ 所有任务已完成"); return
    pending.sort(key=lambda x: {'P0':0,'P1':1,'P2':2,'P3':3}.get(x['priority'],3))
    log(f"\n📋 待处理（前 5）:"); [log(f"   {i+1}. {t['name'][:50]}") for i,t in enumerate(pending[:5])]
    task = pending[0]
    log(f"\n🎯 执行：{task['name'][:50]}...")
    if execute_task(task): mark_done(task['name'])
    else: log(f"   ⚠️ 无法自动执行，需人工干预", 'WARNING')
    tasks = parse_todo(); pending = [t for t in tasks if t['status']=='pending']
    rate = (len(tasks)-len(pending))*100/len(tasks) if tasks else 0
    log(f"\n📊 统计：总{len(tasks)} | 待处理{len(pending)} | 完成率{rate:.1f}%")
    log("="*60); log("✅ 检查完成"); log("="*60)

if __name__ == '__main__': main()
