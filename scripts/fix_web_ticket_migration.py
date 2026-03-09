#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
删除迁移错误的 Issues 并重新创建
"""

import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

from github import Github, Auth

auth = Auth.Token(GITHUB_TOKEN)
gh = Github(auth=auth)
repo = gh.get_repo("aprilvkuo/stock_agent")

# 删除有问题的 Issues（19-23）
issue_numbers = [19, 20, 21, 22, 23]

print("🗑️  删除有问题的 Issues...")
for num in issue_numbers:
    try:
        issue = repo.get_issue(num)
        print(f"  删除 #{num}: {issue.title[:50]}")
        issue.edit(state='closed')
        print(f"    ✅ 已关闭")
    except Exception as e:
        print(f"    ❌ 失败：{e}")

print("\n✅ 删除完成！")
print("\n现在可以重新运行迁移脚本：")
print("  python3 scripts/migrate_web_tickets_to_github.py")
