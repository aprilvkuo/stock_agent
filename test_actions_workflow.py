#!/usr/bin/env python3
"""
测试 GitHub Actions 自动化工单创建
"""
import requests
import os

# 配置
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = "aprilvkuo/stock_agent"

print("=" * 60)
print("🧪 测试 GitHub Actions 自动化工单创建")
print("=" * 60)

if not GITHUB_TOKEN:
    print("\n❌ GITHUB_TOKEN 未配置")
    print("   请运行：source ~/.zshrc")
    exit(1)

print(f"\n配置信息:")
print(f"  仓库：{REPO}")
print(f"  Token: {GITHUB_TOKEN[:20]}...")

# 测试数据
test_cases = [
    {
        "provider": "programmer",
        "consumer": "coordinator",
        "service_type": "code_structure",
        "score": 2,
        "feedback": "代码规范性不足，需要建立草稿区和正式区的分离"
    },
    {
        "provider": "data-fetcher",
        "consumer": "fundamental",
        "service_type": "financial_data",
        "score": 1,
        "feedback": "数据缺少关键指标（ROE、毛利率等）"
    }
]

for i, test_data in enumerate(test_cases, 1):
    print(f"\n{'=' * 60}")
    print(f"测试 {i}/{len(test_cases)}")
    print(f"{'=' * 60}")
    
    url = f"https://api.github.com/repos/{REPO}/dispatches"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    
    payload = {
        "event_type": "create-improvement-ticket",
        "client_payload": test_data
    }
    
    print(f"\n触发参数:")
    print(f"  乙方：@{test_data['provider']}-agent")
    print(f"  甲方：@{test_data['consumer']}-agent")
    print(f"  类型：{test_data['service_type']}")
    print(f"  评分：{test_data['score']}/5.0")
    print(f"  反馈：{test_data['feedback'][:50]}...")
    
    # 触发 Actions
    r = requests.post(url, headers=headers, json=payload)
    
    if r.status_code == 204:
        print(f"\n✅ Actions 触发成功！")
        print(f"   状态码：204 No Content")
        print(f"   GitHub Actions 正在运行...")
    else:
        print(f"\n❌ Actions 触发失败")
        print(f"   状态码：{r.status_code}")
        print(f"   错误：{r.json()}")

print(f"\n{'=' * 60}")
print("✅ 测试完成！")
print(f"{'=' * 60}")

print(f"\n📋 下一步:")
print(f"1. 访问 Actions 页面查看运行状态:")
print(f"   https://github.com/aprilvkuo/stock_agent/actions")
print(f"\n2. 等待工作流完成（约 30 秒）")
print(f"\n3. 查看创建的 Issue:")
print(f"   https://github.com/aprilvkuo/stock_agent/issues")
print(f"\n4. 确认创建者为：github-actions[bot]")
