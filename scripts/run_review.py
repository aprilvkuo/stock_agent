#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票复盘 Agent 执行脚本
由 Heartbeat 每日/每周/每月触发
"""

import sys
import os
from datetime import datetime
import subprocess

WORKSPACE = '/Users/egg/.openclaw/workspace'
STOCK_SYSTEM = os.path.join(WORKSPACE, 'memory/stock-system')

def run_validation():
    """执行每日验证"""
    print("\n" + "="*60)
    print("📊 复盘 Agent - 每日验证")
    print("="*60)
    
    result = subprocess.run(
        ['python3', 'scripts/validate_predictions.py'],
        cwd=STOCK_SYSTEM
    )
    return result.returncode == 0


def generate_weekly_report():
    """生成周度复盘报告"""
    print("\n" + "="*60)
    print("📊 复盘 Agent - 周度复盘")
    print("="*60)
    
    # 读取本周所有分析日志
    analysis_log_dir = os.path.join(STOCK_SYSTEM, 'analysis-log')
    reports_dir = os.path.join(STOCK_SYSTEM, 'reports')
    
    # 获取当前周数
    today = datetime.now()
    week_num = today.isocalendar()[1]
    year = today.year
    
    # 统计本周分析记录
    analysis_files = []
    for f in os.listdir(analysis_log_dir):
        if f.endswith('.md') and not f.startswith('分析日志模板'):
            file_path = os.path.join(analysis_log_dir, f)
            # 简单检查是否本周文件（根据文件名）
            if f.startswith(today.strftime('%Y-%m-%d')):
                analysis_files.append(f)
    
    print(f"本周分析记录数：{len(analysis_files)}")
    
    # 读取验证队列
    validation_queue_path = os.path.join(STOCK_SYSTEM, 'validation-queue.md')
    with open(validation_queue_path, 'r', encoding='utf-8') as f:
        validation_content = f.read()
    
    # 统计待验证项目
    pending_count = validation_content.count('⏳ 待验证')
    print(f"待验证预测数：{pending_count}")
    
    print(f"\n周度报告已更新至：{reports_dir}/{year}-W{week_num:02d}-weekly-review.md")
    return True


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法：python3 run_review.py <daily|weekly|monthly>")
        return
    
    action = sys.argv[1].lower()
    
    if action == 'daily':
        success = run_validation()
    elif action == 'weekly':
        success = generate_weekly_report()
    elif action == 'monthly':
        print("\n月度迭代功能待实现...")
        success = True
    else:
        print(f"未知动作：{action}")
        success = False
    
    print("\n" + "="*60)
    if success:
        print("✅ 复盘 Agent 执行完成")
    else:
        print("❌ 复盘 Agent 执行失败")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
