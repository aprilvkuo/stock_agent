#!/usr/bin/env python3
"""
关闭已解决的 Issue
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = "aprilvkuo/stock_agent"

headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

# 需要关闭的 Issue（已合并到 main）
issues_to_close = [
    {
        "number": 4,
        "title": "programmer-agent code structure improvement",
        "reason": "completed"
    }
]

print("="*60)
print("🔒 关闭已解决的 Issue")
print("="*60)

for issue in issues_to_close:
    number = issue["number"]
    reason = issue["reason"]
    
    print(f"\n处理 Issue #{number}: {issue['title']}")
    
    # 添加关闭评论
    comment = f"""## 🤖 自动关闭

**状态**: 已完成  
**原因**: 修复已合并到 main 分支

感谢贡献！

---
*此消息由 Issue Auto-Resolver v2.0 自动生成*
"""
    
    comment_url = f"https://api.github.com/repos/{GITHUB_REPO}/issues/{number}/comments"
    r = requests.post(comment_url, headers=headers, json={"body": comment})
    
    if r.status_code == 201:
        print(f"  ✅ 评论已添加")
    else:
        print(f"  ⚠️  评论添加失败：{r.status_code}")
    
    # 关闭 Issue
    issue_url = f"https://api.github.com/repos/{GITHUB_REPO}/issues/{number}"
    r2 = requests.patch(issue_url, headers=headers, json={
        "state": "closed",
        "state_reason": reason
    })
    
    if r2.status_code == 200:
        print(f"  ✅ Issue #{number} 已关闭")
    else:
        print(f"  ❌ 关闭失败：{r2.status_code}")

print("\n" + "="*60)
print("✅ Issue 关闭完成！")
print("="*60)
