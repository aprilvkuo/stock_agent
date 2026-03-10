#!/usr/bin/env python3
"""
系统状态快速查看脚本

运行方式：
    python3 scripts/status.py
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = BASE_DIR / "scripts"
LOGS_DIR = BASE_DIR / "analysis-log"
REPORTS_DIR = BASE_DIR / "reports"
VALIDATION_QUEUE = BASE_DIR / "validation-queue.md"
STATUS_FILE = BASE_DIR / "system-health.json"

def get_dir_size(path):
    """计算目录大小"""
    total = 0
    for f in path.rglob("*"):
        if f.is_file():
            total += f.stat().st_size
    return total

def get_file_count(path, pattern="*"):
    """获取文件数量"""
    return len(list(path.glob(pattern)))

def get_recent_analyses(hours=24):
    """获取最近的分析记录"""
    cutoff = datetime.now().timestamp() - (hours * 3600)
    recent = []
    for f in LOGS_DIR.glob("*.md"):
        if f.stat().st_mtime > cutoff:
            recent.append(f.name)
    return recent

def get_pending_validations():
    """获取待验证预测数量"""
    if not VALIDATION_QUEUE.exists():
        return 0
    
    count = 0
    with open(VALIDATION_QUEUE, "r", encoding="utf-8") as f:
        for line in f:
            if "⏳ 待验证" in line:
                count += 1
    return count

def get_health_status():
    """获取健康状态"""
    if not STATUS_FILE.exists():
        return {"status": "unknown", "timestamp": None}
    
    with open(STATUS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def print_status():
    """打印系统状态"""
    print("=" * 60)
    print("📊 股票多 Agent 系统 - 状态概览")
    print("=" * 60)
    
    # 系统基本信息
    print("\n🏷️  系统信息:")
    print(f"   版本：v5.0 (持续优化)")
    print(f"   基座：{BASE_DIR}")
    
    # 持续优化循环状态
    print(f"\n⚡ 持续优化循环:")
    result = subprocess.run(["pgrep", "-f", "continuous_optimizer"], capture_output=True, text=True)
    if result.stdout.strip():
        pids = result.stdout.strip().split("\n")
        print(f"   状态：✅ 运行中 (PID: {', '.join(pids)})")
    else:
        print(f"   状态：❌ 未运行")
        print(f"   启动：python3 scripts/continuous_optimizer.py --background &")
    
    opt_state_file = BASE_DIR / "continuous_optimizer_state.json"
    if opt_state_file.exists():
        try:
            with open(opt_state_file, "r") as f:
                opt_state = json.load(f)
            stats = opt_state.get("stats", {})
            print(f"\n🔄 持续优化统计:")
            print(f"   启动时间：{stats.get('start_time', 'N/A')[:19]}")
            print(f"   快速检查：{stats.get('quick_checks', '持续运行')}")
            print(f"   清理执行：{stats.get('cleanups_run', 0)} 次")
            print(f"   健康检查：{stats.get('health_checks_run', 0)} 次")
            print(f"   完整优化：{stats.get('optimizations_run', 0)} 次")
            print(f"   发现问题：{stats.get('issues_found', 0)} 个")
            print(f"   修复问题：{stats.get('issues_fixed', 0)} 个")
        except:
            print(f"\n🔄 持续优化统计：无法读取")
    
    # 磁盘使用
    total_size = get_dir_size(BASE_DIR)
    print(f"\n💾 磁盘使用:")
    print(f"   总大小：{total_size / (1024 * 1024):.2f} MB")
    
    # 文件统计
    print(f"\n📁 文件统计:")
    print(f"   Python 脚本：{get_file_count(SCRIPTS_DIR, '*.py')} 个")
    print(f"   分析日志：{get_file_count(LOGS_DIR, '*.md')} 个")
    print(f"   JSON 日志：{get_file_count(LOGS_DIR, '*.json')} 个")
    print(f"   报告文件：{get_file_count(REPORTS_DIR, '*.json')} 个")
    
    # 分析活动
    recent = get_recent_analyses()
    print(f"\n📈 分析活动:")
    print(f"   24 小时内：{len(recent)} 次")
    if recent:
        print(f"   最近分析：{recent[-1]}")
    
    # 验证队列
    pending = get_pending_validations()
    print(f"\n⏳ 验证队列:")
    print(f"   待验证：{pending} 项")
    print(f"   首批验证日：2026-04-07")
    
    # 健康状态
    health = get_health_status()
    print(f"\n🏥 健康状态:")
    status_emoji = {"healthy": "✅", "warning": "⚠️", "critical": "❌", "unknown": "❓"}
    print(f"   状态：{status_emoji.get(health['status'], '❓')} {health['status'].upper()}")
    if health.get('timestamp'):
        print(f"   最后检查：{health['timestamp'][:19]}")
    
    # 自动化任务
    print(f"\n🤖 自动化任务:")
    print(f"   ✅ 每 6 小时 - 系统自优化")
    print(f"   ✅ 每 12 小时 - 系统健康检查")
    print(f"   ✅ 每日 00:00 - 项目优化")
    print(f"   ✅ 每日 01:00 - 负责人覆盖检查")
    print(f"   ✅ 每日 09:00 - 预测验证")
    print(f"   ✅ 每周五 20:00 - 周度复盘")
    
    # 快速命令
    print(f"\n⚡ 快速命令:")
    print(f"   分析股票：python3 scripts/auto_agent.py analyze <代码>")
    print(f"   系统优化：python3 scripts/self_optimizer.py")
    print(f"   健康检查：python3 scripts/system_monitor.py")
    print(f"   每日验证：python3 scripts/auto_agent.py daily")
    print(f"   周度复盘：python3 scripts/auto_agent.py weekly")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    print_status()
