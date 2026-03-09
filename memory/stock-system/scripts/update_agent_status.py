#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent 状态更新工具
供各个 Agent 脚本调用，实时更新工作状态到 Web 监控
"""

import requests
import json
from datetime import datetime

MONITOR_URL = "http://localhost:5001"

def update_agent_status(agent_id, status, current_task="", progress=0):
    """
    更新 Agent 状态
    
    Args:
        agent_id: agent 标识 (fundamental/technical/sentiment/risk/cio)
        status: 状态 (idle/running/completed)
        current_task: 当前任务描述
        progress: 进度 (0-100)
    """
    try:
        response = requests.post(
            f"{MONITOR_URL}/api/update-agent",
            json={
                "agent_id": agent_id,
                "status": status,
                "current_task": current_task,
                "progress": progress
            },
            timeout=5
        )
        return response.json().get("success", False)
    except Exception as e:
        print(f"更新状态失败：{e}")
        return False

# ============ 使用示例 ============

if __name__ == "__main__":
    # 示例：开始一个任务
    print("📊 测试更新 Agent 状态...")
    
    # 开始运行
    update_agent_status(
        agent_id="fundamental",
        status="running",
        current_task="分析贵州茅台 (600519) 财报数据",
        progress=25
    )
    print("✅ 已更新：基本面分析师 - 运行中 (25%)")
    
    # 模拟进度更新
    import time
    time.sleep(2)
    
    update_agent_status(
        agent_id="fundamental",
        status="running",
        current_task="分析贵州茅台 (600519) 财报数据",
        progress=75
    )
    print("✅ 已更新：基本面分析师 - 运行中 (75%)")
    
    time.sleep(2)
    
    # 完成任务
    update_agent_status(
        agent_id="fundamental",
        status="idle",
        current_task="分析完成",
        progress=100
    )
    print("✅ 已更新：基本面分析师 - 已完成 (100%)")
    
    print("\n🎉 测试完成！访问 http://localhost:5001 查看效果")
