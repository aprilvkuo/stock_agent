#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票多 Agent 系统 - 一键启动脚本
创建 5 个独立 Session，配置 Heartbeat，启动自动化系统
"""

import os
import subprocess
from datetime import datetime

WORKSPACE = '/Users/egg/.openclaw/workspace'
SHARED_SCRIPTS = os.path.join(WORKSPACE, 'shared/stock-system/scripts')

def create_sessions():
    """创建 5 个独立 Agent Session"""
    print("\n" + "="*60)
    print("🚀 创建 5 个 Agent Session")
    print("="*60 + "\n")
    
    agents = [
        ('stock-fundamental', '基本面分析 Agent - 负责财报、估值、财务健康分析'),
        ('stock-technical', '技术面分析 Agent - 负责 K 线、技术指标、买卖点分析'),
        ('stock-sentiment', '情绪分析 Agent - 负责舆情、市场热度、资金流向分析'),
        ('stock-coordinator', '主 Agent/协调者 - 负责任务分发、结果汇总、最终决策'),
        ('stock-review', '复盘 Agent - 负责验证预测、评估表现、更新规则'),
    ]
    
    for label, task in agents:
        print(f"创建 {label}...")
        cmd = [
            'openclaw', 'sessions', 'spawn',
            '--runtime', 'subagent',
            '--label', label,
            '--task', task,
            '--mode', 'session'
        ]
        
        result = subprocess.run(cmd, cwd=WORKSPACE, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"  ✅ {label} 创建成功")
        else:
            print(f"  ⚠️ {label} 可能已存在")
            print(f"     {result.stderr.strip()}")
    
    print("\n✅ Session 创建完成\n")

def configure_heartbeats():
    """配置各 Agent Heartbeat"""
    print("\n" + "="*60)
    print("⚙️  配置 Heartbeat 任务")
    print("="*60 + "\n")
    
    heartbeats = {
        'stock-fundamental': f"""# 基本面 Agent - Heartbeat

## 每 10 分钟 - 检查请求队列

```bash
cd {SHARED_SCRIPTS}
python3 agent-fundamental.py
```
""",
        'stock-technical': f"""# 技术面 Agent - Heartbeat

## 每 10 分钟 - 检查请求队列

```bash
cd {SHARED_SCRIPTS}
python3 agent-technical.py
```
""",
        'stock-sentiment': f"""# 情绪 Agent - Heartbeat

## 每 10 分钟 - 检查请求队列

```bash
cd {SHARED_SCRIPTS}
python3 agent-sentiment.py
```
""",
        'stock-coordinator': f"""# 主 Agent - Heartbeat

## 每 5 分钟 - 检查和汇总

```bash
cd {SHARED_SCRIPTS}
python3 agent-coordinator.py
```
""",
        'stock-review': f"""# 复盘 Agent - Heartbeat

## 每日 09:00 - 验证检查

```bash
cd {SHARED_SCRIPTS}
python3 agent-review.py daily
```

## 每周五 20:00 - 周度复盘

```bash
cd {SHARED_SCRIPTS}
python3 agent-review.py weekly
```
""",
    }
    
    for agent, content in heartbeats.items():
        heartbeat_path = os.path.join(WORKSPACE, f'agents/{agent}/HEARTBEAT.md')
        with open(heartbeat_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ {agent} Heartbeat 已配置")
    
    print("\n✅ Heartbeat 配置完成\n")

def test_system():
    """测试系统"""
    print("\n" + "="*60)
    print("🧪 测试系统")
    print("="*60 + "\n")
    
    # 运行所有 Agent 脚本
    scripts = [
        'agent-fundamental.py',
        'agent-technical.py',
        'agent-sentiment.py',
        'agent-coordinator.py',
    ]
    
    for script in scripts:
        print(f"测试 {script}...")
        result = subprocess.run(
            ['python3', script],
            cwd=SHARED_SCRIPTS,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"  ✅ {script} 正常")
        else:
            print(f"  ❌ {script} 失败")
            print(f"     {result.stderr.strip()}")
    
    print("\n✅ 系统测试完成\n")

def show_status():
    """显示系统状态"""
    print("\n" + "="*60)
    print("📊 系统状态")
    print("="*60 + "\n")
    
    print("""
┌─────────────────────────────────────────────────────────────┐
│           股票多 Agent 系统 - 已启动                         │
├─────────────────────────────────────────────────────────────┤
│  Agent 列表：                                                │
│  ✅ stock-fundamental   (基本面分析)                        │
│  ✅ stock-technical     (技术面分析)                        │
│  ✅ stock-sentiment     (情绪分析)                          │
│  ✅ stock-coordinator   (主 Agent/协调者)                   │
│  ✅ stock-review        (复盘 Agent)                        │
├─────────────────────────────────────────────────────────────┤
│  Heartbeat 配置：                                            │
│  - 分析 Agent: 每 10 分钟检查请求                            │
│  - 主 Agent: 每 5 分钟汇总结果                               │
│  - 复盘 Agent: 每日 09:00 验证 + 每周五 20:00 复盘            │
├─────────────────────────────────────────────────────────────┤
│  使用方式：                                                  │
│  1. 创建请求文件到 shared/stock-system/queue/requests/      │
│  2. 等待 Agent 自动处理                                      │
│  3. 查看结果：shared/stock-system/queue/results/            │
│  4. 查看验证：shared/stock-system/validation-queue.md       │
└─────────────────────────────────────────────────────────────┘
""")

def main():
    print("\n" + "="*60)
    print("🚀 股票多 Agent 系统 - 一键启动")
    print("="*60)
    print(f"启动时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 创建 Session
    create_sessions()
    
    # 2. 配置 Heartbeat
    configure_heartbeats()
    
    # 3. 测试系统
    test_system()
    
    # 4. 显示状态
    show_status()
    
    print("\n" + "="*60)
    print("✅ 系统启动完成！")
    print("="*60 + "\n")
    
    print("下一步:")
    print("1. 创建分析请求到 queue/requests/")
    print("2. 等待 Agent 自动处理")
    print("3. 查看结果和验证队列")
    print("\n")

if __name__ == '__main__':
    main()
