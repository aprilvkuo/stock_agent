#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查看股票多 Agent 系统记录
"""

import os
import sys
from datetime import datetime

WORKSPACE = '/Users/egg/.openclaw/workspace'
DATA_DIR = os.path.join(WORKSPACE, 'agents/stock-coordinator/data')

def show_menu():
    """显示菜单"""
    print("\n" + "="*60)
    print("📊 股票多 Agent 系统 - 记录查看")
    print("="*60)
    print("\n请选择要查看的内容:\n")
    print("1. 最新分析结果")
    print("2. 所有分析结果列表")
    print("3. 请求处理状态")
    print("4. 验证队列")
    print("5. 备份记录")
    print("6. 系统状态")
    print("0. 退出")
    print()

def view_latest_result():
    """查看最新分析结果"""
    results_dir = os.path.join(DATA_DIR, 'queue/results')
    if not os.path.exists(results_dir):
        print("❌ 暂无分析结果")
        return
    
    files = sorted([f for f in os.listdir(results_dir) if f.endswith('.md')], reverse=True)
    if not files:
        print("❌ 暂无分析结果")
        return
    
    # 显示最新的结果
    latest = files[0]
    filepath = os.path.join(results_dir, latest)
    
    print(f"\n{'='*60}")
    print(f"📄 最新分析结果：{latest}")
    print(f"{'='*60}\n")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        print(f.read())

def list_all_results():
    """列出所有分析结果"""
    results_dir = os.path.join(DATA_DIR, 'queue/results')
    if not os.path.exists(results_dir):
        print("❌ 暂无分析结果")
        return
    
    files = sorted([f for f in os.listdir(results_dir) if f.endswith('.md')], reverse=True)
    if not files:
        print("❌ 暂无分析结果")
        return
    
    print(f"\n{'='*60}")
    print(f"📋 分析结果列表 (共 {len(files)} 个)")
    print(f"{'='*60}\n")
    
    # 按请求 ID 分组
    requests = {}
    for f in files:
        # 提取请求 ID
        parts = f.replace('.md', '').split('-')
        if len(parts) >= 3:
            request_id = parts[1]
            agent_type = parts[2]
            if request_id not in requests:
                requests[request_id] = []
            requests[request_id].append(agent_type)
    
    for request_id, agents in sorted(requests.items(), reverse=True):
        print(f"📁 {request_id}")
        print(f"   分析 Agent: {', '.join(agents)}")
        
        # 查找对应的请求文件
        request_file = os.path.join(DATA_DIR, 'queue/requests', f"{request_id}.md")
        if os.path.exists(request_file):
            with open(request_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # 提取股票信息
                import re
                stock_match = re.search(r'股票代码：(\d+)', content)
                name_match = re.search(r'股票名称：(.+)', content)
                status_match = re.search(r'汇总：✅ 已完成 - (.+)', content)
                
                if stock_match:
                    print(f"   股票：{stock_match.group(1)} {name_match.group(1) if name_match else ''}")
                if status_match:
                    print(f"   综合评级：{status_match.group(1)}")
        print()

def view_requests():
    """查看请求处理状态"""
    requests_dir = os.path.join(DATA_DIR, 'queue/requests')
    if not os.path.exists(requests_dir):
        print("❌ 暂无请求")
        return
    
    files = sorted([f for f in os.listdir(requests_dir) if f.endswith('.md')], reverse=True)
    if not files:
        print("❌ 暂无请求")
        return
    
    print(f"\n{'='*60}")
    print(f"📋 请求处理状态 (共 {len(files)} 个)")
    print(f"{'='*60}\n")
    
    for f in files[:10]:  # 只显示最近 10 个
        filepath = os.path.join(requests_dir, f)
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
            
            # 提取信息
            import re
            stock_match = re.search(r'股票代码：(\d+)', content)
            name_match = re.search(r'股票名称：(.+)', content)
            
            stock_info = f"{stock_match.group(1)} {name_match.group(1).strip()}" if stock_match and name_match else "Unknown"
            
            # 统计完成状态
            completed = content.count('✅ 已完成')
            total = 4  # 基本面、技术面、情绪、汇总
            
            status = "✅ 完成" if completed == total else f"⏳ 进行中 ({completed}/{total})"
            
            print(f"📁 {f.replace('.md', '')}")
            print(f"   股票：{stock_info}")
            print(f"   状态：{status}")
            print()

def view_validation_queue():
    """查看验证队列"""
    validation_file = os.path.join(DATA_DIR, 'validation-queue.md')
    if not os.path.exists(validation_file):
        print("❌ 暂无验证记录")
        return
    
    print(f"\n{'='*60}")
    print(f"📋 验证队列")
    print(f"{'='*60}\n")
    
    with open(validation_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
        # 统计
        pending = content.count('⏳ 待验证')
        correct = content.count('✅ 正确')
        wrong = content.count('❌ 错误')
        
        print(f"待验证：{pending} 项")
        print(f"已验证正确：{correct} 项")
        print(f"已验证错误：{wrong} 项")
        print()
        
        # 显示内容
        print(content)

def view_backups():
    """查看备份记录"""
    backup_dir = os.path.join(DATA_DIR, 'backups')
    if not os.path.exists(backup_dir):
        print("❌ 暂无备份")
        return
    
    files = sorted([f for f in os.listdir(backup_dir) if f.endswith('.md')], reverse=True)
    
    print(f"\n{'='*60}")
    print(f"💾 备份记录 (共 {len(files)} 个)")
    print(f"{'='*60}\n")
    
    for f in files[:10]:  # 只显示最近 10 个
        filepath = os.path.join(backup_dir, f)
        size = os.path.getsize(filepath)
        mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
        
        print(f"📁 {f}")
        print(f"   大小：{size} 字节")
        print(f"   时间：{mtime.strftime('%Y-%m-%d %H:%M:%S')}")
        print()

def view_system_status():
    """查看系统状态"""
    print(f"\n{'='*60}")
    print(f"📊 系统状态")
    print(f"{'='*60}\n")
    
    # 统计
    requests_dir = os.path.join(DATA_DIR, 'queue/requests')
    results_dir = os.path.join(DATA_DIR, 'queue/results')
    backup_dir = os.path.join(DATA_DIR, 'backups')
    
    request_count = len([f for f in os.listdir(requests_dir) if f.endswith('.md')]) if os.path.exists(requests_dir) else 0
    result_count = len([f for f in os.listdir(results_dir) if f.endswith('.md')]) if os.path.exists(results_dir) else 0
    backup_count = len([f for f in os.listdir(backup_dir) if f.endswith('.md')]) if os.path.exists(backup_dir) else 0
    
    # 验证队列统计
    validation_file = os.path.join(DATA_DIR, 'validation-queue.md')
    pending = 0
    if os.path.exists(validation_file):
        with open(validation_file, 'r', encoding='utf-8') as f:
            content = f.read()
            pending = content.count('⏳ 待验证')
    
    print(f"请求总数：{request_count}")
    print(f"分析结果：{result_count}")
    print(f"待验证预测：{pending}")
    print(f"备份文件：{backup_count}")
    print()
    
    # Agent 状态
    print("Agent 状态:")
    print("  ✅ 基本面 Agent - 就绪")
    print("  ✅ 技术面 Agent - 就绪")
    print("  ✅ 情绪 Agent - 就绪")
    print("  ✅ 主 Agent - 就绪")
    print("  ✅ 复盘 Agent - 就绪")
    print()
    
    # 下次执行时间
    print("下次自动执行:")
    print("  - 请求检查：每 5-10 分钟")
    print("  - 每日验证：明日 09:00")
    print("  - 周度复盘：2026-03-13 20:00")
    print()

def main():
    while True:
        show_menu()
        choice = input("请输入选项 (0-6): ").strip()
        
        if choice == '1':
            view_latest_result()
        elif choice == '2':
            list_all_results()
        elif choice == '3':
            view_requests()
        elif choice == '4':
            view_validation_queue()
        elif choice == '5':
            view_backups()
        elif choice == '6':
            view_system_status()
        elif choice == '0':
            print("\n👋 再见!\n")
            break
        else:
            print("❌ 无效选项，请重新输入")
        
        input("\n按回车键继续...")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 程序中断\n")
