#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
错误通知模块 - Agent 失败时发送通知
"""

import os
import sys
from datetime import datetime

def send_notification(title, message, level='info'):
    """发送系统通知"""
    try:
        # macOS 通知
        import subprocess
        subprocess.run([
            'osascript',
            '-e',
            f'display notification "{message}" with title "{title}" sound name "Glass"'
        ])
        print(f"📬 已发送通知：{title}")
    except Exception as e:
        print(f"发送通知失败：{e}")

def notify_agent_failure(agent_name, error_msg):
    """通知 Agent 执行失败"""
    title = "🚨 Agent 执行失败"
    message = f"{agent_name} 执行出错：{error_msg[:50]}..."
    send_notification(title, message, 'error')

def notify_agent_recovery(agent_name):
    """通知 Agent 恢复运行"""
    title = "✅ Agent 恢复运行"
    message = f"{agent_name} 已恢复正常工作"
    send_notification(title, message, 'success')

def notify_daily_summary(analysis_count, validation_count, accuracy):
    """发送每日摘要"""
    title = "📊 股票系统日报"
    message = f"今日分析{analysis_count}只 | 待验证{validation_count}项 | 准确率{accuracy}%"
    send_notification(title, message, 'info')

if __name__ == '__main__':
    # 测试
    send_notification("测试通知", "这是一条测试消息")
