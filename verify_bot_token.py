#!/usr/bin/env python3
"""
验证 GitHub Bot Token 配置
"""
import requests
import os

# 获取配置
token = os.getenv("GITHUB_BOT_TOKEN")
username = os.getenv("GITHUB_BOT_USERNAME")
repo = "aprilvkuo/stock_agent"

print("=" * 60)
print("🤖 GitHub Bot Token 验证")
print("=" * 60)
print(f"\n配置信息:")
print(f"  Bot 用户名：{username}")
print(f"  Token 长度：{len(token) if token else 0}")
print(f"  目标仓库：{repo}")

if not token or not username:
    print("\n❌ 配置不完整，请检查 ~/.zshrc")
    exit(1)

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json"
}

# 测试 1: 验证 Bot 身份
print("\n" + "=" * 60)
print("Test 1: 验证 Bot 身份")
print("=" * 60)
r = requests.get("https://api.github.com/user", headers=headers)
if r.status_code == 200:
    user = r.json()
    print(f"✅ 验证成功")
    print(f"   用户名：{user['login']}")
    print(f"   用户 ID: {user['id']}")
    print(f"   账号类型：{user['type']}")
    print(f"   匹配配置：{user['login'] == username}")
else:
    print(f"❌ 验证失败")
    print(f"   状态码：{r.status_code}")
    print(f"   错误：{r.json()}")
    exit(1)

# 测试 2: 检查仓库访问权限
print("\n" + "=" * 60)
print("Test 2: 检查仓库访问权限")
print("=" * 60)
r = requests.get(f"https://api.github.com/repos/{repo}", headers=headers)
if r.status_code == 200:
    repo_data = r.json()
    print(f"✅ 仓库访问成功")
    print(f"   仓库：{repo_data['full_name']}")
    print(f"   权限：{repo_data['permissions']}")
else:
    print(f"❌ 仓库访问失败")
    print(f"   状态码：{r.status_code}")
    print(f"   错误：{r.json()}")
    exit(1)

# 测试 3: 创建测试 Issue
print("\n" + "=" * 60)
print("Test 3: 创建测试 Issue")
print("=" * 60)
test_data = {
    "title": "[BOT TEST] Bot 账号验证测试",
    "body": f"""
# 🤖 Bot 账号测试

**测试时间**: 2026-03-09 19:24  
**Bot 账号**: @{username}

## 测试目的
验证 GitHub Bot Token 配置是否正确。

## 预期结果
- ✅ Issue 创建成功
- ✅ 创建者显示为 Bot 账号
- ✅ 能够正常访问仓库

---
*此 Issue 由自动化测试脚本创建*
"""
}
r = requests.post(f"https://api.github.com/repos/{repo}/issues", 
                  headers=headers, json=test_data)
if r.status_code == 201:
    issue = r.json()
    print(f"✅ Issue 创建成功")
    print(f"   编号：#{issue['number']}")
    print(f"   标题：{issue['title']}")
    print(f"   创建者：{issue['user']['login']}")
    print(f"   链接：{issue['html_url']}")
    
    if issue['user']['login'] == username:
        print(f"\n🎉 Bot 账号验证完全成功！")
        print(f"   Issue 创建者显示为：@{username} ✅")
    else:
        print(f"\n⚠️  Issue 创建者不是 Bot 账号")
        print(f"   实际创建者：{issue['user']['login']}")
else:
    print(f"❌ Issue 创建失败")
    print(f"   状态码：{r.status_code}")
    print(f"   错误：{r.json()}")
    exit(1)

print("\n" + "=" * 60)
print("✅ 所有测试通过！Bot Token 配置成功！")
print("=" * 60)
print(f"\n下一步:")
print(f"1. 查看创建的 Issue: {issue['html_url']}")
print(f"2. 确认 Issue 创建者为：@{username}")
print(f"3. 继续测试完整的改进工单流程")
