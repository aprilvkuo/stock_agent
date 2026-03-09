#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建 GitHub Issue Labels

使用方法:
    python3 scripts/create_labels.py
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO", "aprilvkuo/stock_agent")

if not GITHUB_TOKEN:
    print("❌ 错误：GITHUB_TOKEN 未设置")
    sys.exit(1)

try:
    from github import Github, Auth
except ImportError:
    print("❌ 错误：缺少 PyGithub 库")
    print("请运行：pip install PyGithub")
    sys.exit(1)


# 预定义的 Labels
LABELS = [
    # 任务类型
    {"name": "improvement-ticket", "color": "FBCA04", "description": "改进工单"},
    {"name": "task", "color": "0075CA", "description": "常规任务"},
    {"name": "feature", "color": "0E8A16", "description": "新功能"},
    {"name": "bug", "color": "D73A4A", "description": "Bug 修复"},
    
    # 优先级
    {"name": "urgent", "color": "B60205", "description": "紧急任务"},
    {"name": "high-priority", "color": "D93F0B", "description": "高优先级"},
    {"name": "medium-priority", "color": "FBCA04", "description": "中优先级"},
    {"name": "low-priority", "color": "0E8A16", "description": "低优先级"},
    
    # 状态
    {"name": "in-progress", "color": "0075CA", "description": "进行中"},
    {"name": "needs-review", "color": "FBCA04", "description": "需要审查"},
    {"name": "blocked", "color": "D73A4A", "description": "被阻塞"},
    {"name": "completed", "color": "0E8A16", "description": "已完成"},
    
    # 来源
    {"name": "migrated", "color": "C5DEF5", "description": "从旧系统迁移"},
    {"name": "auto-generated", "color": "C5DEF5", "description": "自动生成"},
    
    # Agent 相关
    {"name": "programmer-agent", "color": "1D76DB", "description": "程序员 Agent"},
    {"name": "fundamental-agent", "color": "1D76DB", "description": "基本面 Agent"},
    {"name": "technical-agent", "color": "1D76DB", "description": "技术面 Agent"},
    {"name": "sentiment-agent", "color": "1D76DB", "description": "情绪 Agent"},
    {"name": "coordinator-agent", "color": "1D76DB", "description": "协调 Agent"},
    {"name": "qa-agent", "color": "1D76DB", "description": "质检 Agent"},
    {"name": "cio-agent", "color": "1D76DB", "description": "CIO Agent"},
    {"name": "data-fetcher-agent", "color": "1D76DB", "description": "数据获取 Agent"},
]


def create_labels():
    """创建所有 Labels"""
    print("=" * 60)
    print("🏷️  创建 GitHub Issue Labels")
    print("=" * 60)
    print()
    
    # 初始化 GitHub
    auth = Auth.Token(GITHUB_TOKEN)
    gh = Github(auth=auth)
    repo = gh.get_repo(GITHUB_REPO)
    
    print(f"📦 仓库：{GITHUB_REPO}\n")
    
    # 获取现有 Labels
    existing_labels = {label.name: label for label in repo.get_labels()}
    print(f"📊 现有 Labels: {len(existing_labels)} 个\n")
    
    # 创建或更新 Labels
    created = 0
    updated = 0
    skipped = 0
    
    for label_config in LABELS:
        name = label_config["name"]
        color = label_config["color"]
        description = label_config["description"]
        
        if name in existing_labels:
            # Label 已存在，检查是否需要更新
            existing = existing_labels[name]
            needs_update = False
            
            if existing.color != color:
                needs_update = True
            if existing.description != description:
                needs_update = True
            
            if needs_update:
                try:
                    existing.edit(color=color, description=description)
                    print(f"  ✏️  更新：{name}")
                    updated += 1
                except Exception as e:
                    print(f"  ❌ 更新失败 {name}: {e}")
            else:
                print(f"  ⏭️  跳过：{name} (已存在且无需更新)")
                skipped += 1
        else:
            # 创建新 Label
            try:
                repo.create_label(
                    name=name,
                    color=color,
                    description=description
                )
                print(f"  ✅ 创建：{name}")
                created += 1
            except Exception as e:
                print(f"  ❌ 创建失败 {name}: {e}")
    
    # 显示统计
    print()
    print("=" * 60)
    print("📊 统计")
    print("=" * 60)
    print(f"✅ 新建：{created} 个")
    print(f"✏️  更新：{updated} 个")
    print(f"⏭️  跳过：{skipped} 个")
    print(f"📦 总计：{len(LABELS)} 个")
    print("=" * 60)
    
    print()
    print("✅ Labels 配置完成！")
    print()
    print("🔗 查看 Labels:")
    print(f"   https://github.com/{GITHUB_REPO}/labels")


if __name__ == "__main__":
    create_labels()
