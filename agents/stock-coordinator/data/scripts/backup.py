#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据备份脚本 - 保护重要数据
自动备份验证队列、分析结果、请求记录
"""

import os
import shutil
from datetime import datetime

WORKSPACE = '/Users/egg/.openclaw/workspace'
DATA_DIR = os.path.join(WORKSPACE, 'agents/stock-coordinator/data')
BACKUP_DIR = os.path.join(DATA_DIR, 'backups')

def create_backup():
    """创建数据备份"""
    # 创建备份目录
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(BACKUP_DIR, f'backup_{timestamp}')
    os.makedirs(backup_path, exist_ok=True)
    
    # 备份验证队列
    validation_queue = os.path.join(DATA_DIR, 'validation-queue.md')
    if os.path.exists(validation_queue):
        shutil.copy2(validation_queue, os.path.join(backup_path, 'validation-queue.md'))
        print(f"✅ 已备份 validation-queue.md")
    
    # 备份请求队列
    requests_dir = os.path.join(DATA_DIR, 'queue/requests')
    if os.path.exists(requests_dir) and os.listdir(requests_dir):
        backup_requests = os.path.join(backup_path, 'requests')
        shutil.copytree(requests_dir, backup_requests)
        print(f"✅ 已备份 requests/ ({len(os.listdir(requests_dir))} 个文件)")
    
    # 备份结果队列
    results_dir = os.path.join(DATA_DIR, 'queue/results')
    if os.path.exists(results_dir) and os.listdir(results_dir):
        backup_results = os.path.join(backup_path, 'results')
        shutil.copytree(results_dir, backup_results)
        print(f"✅ 已备份 results/ ({len(os.listdir(results_dir))} 个文件)")
    
    # 备份报告
    reports_dir = os.path.join(DATA_DIR, 'reports')
    if os.path.exists(reports_dir) and os.listdir(reports_dir):
        backup_reports = os.path.join(backup_path, 'reports')
        shutil.copytree(reports_dir, backup_reports)
        print(f"✅ 已备份 reports/ ({len(os.listdir(reports_dir))} 个文件)")
    
    print(f"\n📦 备份完成：{backup_path}")
    return backup_path

def cleanup_old_backups(days=30):
    """清理旧备份（保留最近 30 天）"""
    if not os.path.exists(BACKUP_DIR):
        return
    
    cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
    
    for f in os.listdir(BACKUP_DIR):
        dir_path = os.path.join(BACKUP_DIR, f)
        if os.path.isdir(dir_path) and f.startswith('backup_'):
            # 从文件名解析时间
            try:
                backup_time = datetime.strptime(f.replace('backup_', ''), '%Y%m%d_%H%M%S')
                if backup_time.timestamp() < cutoff:
                    shutil.rmtree(dir_path)
                    print(f"🗑️  已删除旧备份：{f}")
            except:
                pass

def main():
    print(f"\n{'='*50}")
    print(f"💾 数据备份")
    print(f"{'='*50}\n")
    
    # 确保备份目录存在
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    # 创建备份
    backup_path = create_backup()
    
    # 清理旧备份
    print(f"\n清理旧备份...")
    cleanup_old_backups(30)
    
    print(f"\n{'='*50}")
    print(f"✅ 备份完成")
    print(f"{'='*50}\n")
    
    print(f"备份位置：{backup_path}")
    print(f"保留策略：30 天\n")

if __name__ == '__main__':
    main()
